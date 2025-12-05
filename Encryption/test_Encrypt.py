from Encrypt import createImages, analyzeImages, create_folder, image_taker, clear_images, save_frame, entropy
import pytest
from unittest.mock import patch, MagicMock
import cv2 as cv 
import numpy as np
import os
import shutil

# Constants to match your code (replace with your actual key codes)
IMAGE_TAKER_ORD = 32  # space
ANALYZE_IMG_ORD = ord('q')
CLEAR_IMAGES_ORD = ord('c')

@patch('cv2.VideoCapture')              # mock webcam
@patch('cv2.imshow')                     # mock GUI window
@patch('cv2.waitKey')                    # mock key presses
@patch('Encrypt.create_folder')          # mock folder creation
@patch('Encrypt.image_taker')            # mock image saving
@patch('Encrypt.analyzeImages')          # mock analyze
@patch('Encrypt.clear_images')           # mock clear


def test_createImages(mock_clear, mock_analyze, mock_image_taker, mock_create_folder,
                      mock_waitKey, mock_imshow, mock_VideoCapture):

    # Mock webcam
    mock_cap = MagicMock()
    mock_VideoCapture.return_value = mock_cap
    mock_cap.read.return_value = (True, "fake_frame")
    
    # Add an extra 0 for the final cv.waitKey call at the end
    mock_waitKey.side_effect = [IMAGE_TAKER_ORD, ANALYZE_IMG_ORD, 0]
    
    # Mock folder creation
    mock_create_folder.return_value = "fake_folder"
    
    # Call the function
    createImages()
    
    # Assertions
    mock_create_folder.assert_called_once_with("captured_images")
    mock_image_taker.assert_called_once()
    mock_analyze.assert_called_once()
    mock_cap.release.assert_called_once()
    mock_imshow.assert_called()

### To mock the webcam
class FakeCapture:
    def __init__(self, frames):
        self.frames = frames
        self.index = 0

    def read(self):
        if self.index < len(self.frames):
            frame = self.frames[self.index]
            self.index += 1
            return True, frame
        return False, None

def test_image_taker(tmp_path, monkeypatch):
    fake_frames = ["f1", "f2", "f3"]
    capture = FakeCapture(fake_frames)

    # Fake imwrite
    saved = []
    monkeypatch.setattr(cv, "imwrite", lambda path, frame: saved.append((path, frame)) or True)

    counter = image_taker(
        num_photos=3,
        capture=capture,
        save_folder=str(tmp_path),
        delay=0,
        counter=0
    )

    assert counter == 3
    assert len(saved) == 3


def test_save_frame(monkeypatch, tmp_path):

    saved = {}

    # Correct signature: imwrite(path, frame)
    def fake_imwrite(path, frame):
        saved[path] = True
        return True

    monkeypatch.setattr(cv, "imwrite", fake_imwrite)

    frame = "fake_frame_data"
    output = tmp_path / "test.png"

    assert save_frame(str(output), frame)
    assert str(output) in saved



def test_clear_images(tmp_path):
    folder = tmp_path / "images"
    folder.mkdir()

    # create fake images
    (folder / "opencv_frame_0.png").touch()
    (folder / "opencv_frame_1.png").touch()

    clear_images(str(folder))

    # After clearing, folder should be empty
    assert len(list(folder.glob("*.png"))) == 0


@patch("Encrypt.os.listdir")
@patch("Encrypt.os.path.join")
@patch("Encrypt.cv.imread")
@patch("Encrypt.rand.randint")
@patch("Encrypt.entropy")

def test_analyzeImages(
    mock_entropy, mock_randint, mock_imread, mock_join, mock_listdir
):
    # Pretend directory has 2 image files
    mock_listdir.return_value = ["opencv_frame_0.png", "opencv_frame_1.png"]

    # Fake os.path.join
    mock_join.side_effect = lambda folder, name: f"{folder}/{name}"

    # Fake images as numpy arrays
    img1 = np.array([
        [[10, 20, 30], [40, 50, 60]],
        [[70, 80, 90], [100, 110, 120]]
    ])

    img2 = np.array([
        [[1, 2, 3], [4, 5, 6]],
        [[7, 8, 9], [10, 11, 12]]
    ])

    mock_imread.side_effect = [img1, img2]

    # Always choose pixel (0,0)
    mock_randint.return_value = 0

    from Encrypt import analyzeImages
    result = analyzeImages()

    # Expected calculation:
    # img1 pixel [10,20,30] -> R,G,B = 20,30,10
    # img2 pixel [1,2,3]    -> R,G,B = 2,3,1
    expected = "203010231"

    assert result == expected
    mock_entropy.assert_called_once()

def test_create_folder(tmp_path):
    # Arrange: pick a folder name inside pytest's temporary directory
    folder_name = tmp_path / "captured_images"

    # Act: call your function with the full path as a string
    created = create_folder(str(folder_name))

    # Assert: the folder should now exist
    assert os.path.exists(created)
    assert os.path.isdir(created)

    # Assert: returned path should match exactly
    assert created == str(folder_name)

    # Act again: calling a second time should NOT raise errors or recreate
    created_again = create_folder(str(folder_name))

    # Assert: the folder still exists and the same path is returned
    assert created_again == str(folder_name)
    assert os.path.isdir(created_again)

@patch("os.listdir")
@patch("os.path.join")
@patch("Encrypt.cv.calcHist")
@patch("Encrypt.cv.imread")
def test_entropy(mock_imread, mock_calcHist, mock_join, mock_listdir):
    # Pretend the folder contains 2 images
    mock_listdir.return_value = ["opencv_frame_0.png", "opencv_frame_1.png"]

    # Fake join
    mock_join.side_effect = lambda folder, name: f"{folder}/{name}"

    # Fake grayscale image: a 2x2 image
    fake_img = np.array([
        [10, 10],
        [20, 20]
    ], dtype=np.uint8)

    # imread returns this same valid image each time
    mock_imread.return_value = fake_img

    # Fake histogram: 256 bins
    # Only intensities 10 and 20 exist with 2 pixels each (total 4 pixels)
    hist = np.zeros((256, 1), dtype=np.float32)
    hist[10] = 2
    hist[20] = 2

    mock_calcHist.return_value = hist

    # Expected Shannon entropy:
    # p(10) = 2/4 = 0.5
    # p(20) = 2/4 = 0.5
    # entropy = - Σ p log2 p = 1.0 per image
    # total entropy = 2.0
    # avg_entropy = entropy / 20 = 2 / 20 = 0.1
    expected = 0.1

    result = entropy()

    assert abs(result - expected) < 1e-6