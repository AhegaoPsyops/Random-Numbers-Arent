
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Make sure the parent folder is in sys.path to import Encrypt and PRNG_GUI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import PRNG_GUI
import Encrypt

# --------------------------
# Helper: fake window object
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
            return ('__CLOSED__', {})  # make loop exit safely

    def __getitem__(self, key):
        # Return self for update calls
        return self

    def update(self, *args, **kwargs):
        """
        Accept any positional or keyword arguments,
        just store them for inspection if needed.
        """
        if args:
            # store first positional argument as 'text'
            self.updates['text'] = args[0]
        self.updates.update(kwargs)

    def close(self):
        self.closed = True

# --------------------------
# Test 1: Generate PRNG starts thread
# --------------------------
def test_generate_prng_starts_thread():
    with patch("PRNG_GUI.threading.Thread") as mock_thread, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking"):

        # Mock window.read() events: Generate PRNG -> Exit
        mock_window = FakeWindow([("Generate PRNG", {}), ("Exit", {})])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_thread.assert_called_once()
        # check thread target is correct
        target_func = mock_thread.call_args[1]['target']
        assert target_func.__name__ == "Encryption_thread"

# --------------------------
# Test 2: Thread done calls analyzeImages
# --------------------------
def test_thread_done_calls_analyze_images():
    with patch("PRNG_GUI.Encrypt.analyzeImages", return_value="FAKEKEY") as mock_analyze, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking") as mock_popup:

        # Simulate "-THREAD DONE-" event, then exit
        mock_window = FakeWindow([
            ("-THREAD DONE-", {"-THREAD DONE-": 0}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_analyze.assert_called_once()
        mock_popup.assert_called_once_with("Raw Key: FAKEKEY\nKey Length: 1000", grab_anywhere=True)

# --------------------------
# Test 3: Average Entropy button
# --------------------------
def test_average_entropy_button():
    with patch("PRNG_GUI.Encrypt.entropy", return_value=5.55) as mock_entropy, \
         patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking") as mock_popup:

        # Simulate clicking Average Entropy then Exit
        mock_window = FakeWindow([
            ("Average Entropy", {}),
            ("Predict PRNG", {}),
            ("Exit", {})
        ])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        mock_entropy.assert_called_once()
        mock_popup.assert_called_once_with(
            "The average entropy of these images are: 5.5500",
            grab_anywhere=True
        )

# --------------------------
# Test 4: Average Entropy with no images
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
# Test 5: GUI exits correctly
# --------------------------
def test_gui_exit():
    with patch("PRNG_GUI.sg.Window") as mock_window_class, \
         patch("PRNG_GUI.sg.popup_non_blocking"):

        # Immediately close
        mock_window = FakeWindow([(PRNG_GUI.sg.WIN_CLOSED, {})])
        mock_window_class.return_value = mock_window

        PRNG_GUI.the_gui()

        assert mock_window.closed == True
