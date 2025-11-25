from Encrypt import createImages, analyzeImages, main, create_folder, image_taker, clear_images, save_frame
import pytest
import cv2 as cv 

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


def test_createImages():
    #TODO
    return

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

def test_main():
    #TODO
    return