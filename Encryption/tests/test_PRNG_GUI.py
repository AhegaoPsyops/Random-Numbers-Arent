import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Ensure parent folder is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import PRNG_GUI
import Encrypt

# --------------------------
# Fake GUI Window
# --------------------------
class FakeWindow:
    def __init__(self, read_side_effect):
        self.read_side_effect = iter(read_side_effect)
        self.updates = {}
        self.closed = False

    def read(self):
        try:
            return next(self.read_side_effect)
        except StopIteration:
            return ("__CLOSED__", {})  # exit loop safely

    def __getitem__(self, key):
        return self  # used for label.update()

    def update(self, *args, **kwargs):
        if args:
            self.updates['text'] = args[0]
        self.updates.update(kwargs)

    def write_event_value(self, event, value):
        """Not really used here, but required for thread simulation."""
        pass

    def close(self):
        self.closed = True


# --------------------------
# Test 1: Thread starts
# --------------------------
def test_generate_prng_starts_thread():
    with patch("PRNG_GUI.threading.Thread") as mock_thread, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking"):

        mock_window = FakeWindow([
            ("Generate PRNG", {}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        # Thread should be started exactly once
        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]["target"].__name__ == "Encryption_thread"


# --------------------------
# Test 2: Thread done triggers analyzeImages
# --------------------------
def test_thread_done_calls_analyze_images():
    with patch("PRNG_GUI.Encrypt.analyzeImages", return_value="FAKEKEY") as mock_analyze, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking") as mock_popup:

        # Thread completion format changed → must include {"ok": True, "id": N}
        mock_window = FakeWindow([
            ("-THREAD DONE-", {"-THREAD DONE-": {"ok": True, "id": 0}}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_analyze.assert_called_once()

        # Popup text changed due to error-handling: key length is now len() based
        mock_popup.assert_called_once_with(
            "Raw Key: FAKEKEY\nKey Length: 7",  # len("FAKEKEY") = 7
            grab_anywhere=True
        )


# --------------------------
# Test 3: Average Entropy button
# --------------------------
def test_average_entropy_button():
    with patch("PRNG_GUI.Encrypt.entropy", return_value=5.55) as mock_entropy, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking") as mock_popup:

        mock_window = FakeWindow([
            ("Average Entropy", {}),
            ("Predict PRNG", {}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_entropy.assert_called_once()
        mock_popup.assert_called_once_with(
            "The average entropy of these images is: 5.5500",
            grab_anywhere=True
        )


# --------------------------
# Test 4: No images for entropy
# --------------------------
def test_average_entropy_no_images():
    with patch("PRNG_GUI.Encrypt.entropy", return_value=None) as mock_entropy, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking") as mock_popup:

        mock_window = FakeWindow([
            ("Average Entropy", {}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_entropy.assert_called_once()
        mock_popup.assert_called_once_with(
            "No images in directory",
            grab_anywhere=True
        )


# --------------------------
# Test 5: GUI exits normally
# --------------------------
def test_gui_exit():
    with patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking"):

        mock_window = FakeWindow([
            (PRNG_GUI.sg.WIN_CLOSED, {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        assert mock_window.closed is True
