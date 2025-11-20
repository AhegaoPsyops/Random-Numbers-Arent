from Encrypt import createImages, analyzeImages, main
import pytest

def test_createImages():
    #TODO
    return

def test_webcam_opens(capsys):
    ##run created images to get output
    createImages()
    ##captures the output in terminal
    captured = capsys.readouterr()  
    ##asserts correct message is outputed that proves the webcam is open
    assert captured == "Webcam opened successfully."

def test_analyzeImages():
    #TODO
    return

def test_main():
    #TODO
    return