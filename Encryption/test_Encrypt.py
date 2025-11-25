from Encrypt import createImages, analyzeImages, create_folder, image_taker, clear_images, save_frame
import pytest
from unittest.mock import patch, MagicMock
import cv2 as cv 

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

    def fake_imwrite(path, frame):
        saved[path] = True
        return True

    monkeypatch.setattr(cv, "imwrite", fake_imwrite)

    frame = "fake_frame_data"
    output = tmp_path / "test.png"

    assert save_frame(frame, str(output))
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


def test_analyzeImages():
    #TODO
    return