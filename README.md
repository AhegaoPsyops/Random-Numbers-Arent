# 🙅‍♀️ Random Numbers Aren't 🙅‍♀️

## 📖 Description
Fully Python-based GUI as well as terminal application that generates psuedo-random numbers using images captured real-time using the webcam. The system calculates PRNG keys from image pixels and evaluates entropy to ensure randomness.

Predictive Analysis of Secure PRNGS (generated via object unpredictability) and using AI/ML Group Repository for designs and central project.

## ✨ Features
- Capture images using a webcam
- Generate PRNG keys based on random pixels from images
- Graphical user interface for easy interaction
- Threading design to allow for long-running tasks without freezing the GUI

## 💽 Technologies and Dependencies
- **Python 3.10+**
- **Packages:**
    - `numpy`
    - `opencv-python (cv2)`
    - `FreeSimpleGUI` or `PySimpleGUI`
- **Testing:**
    - `pytest`
    - `unittest.mock`

## ⚙️ Installation
- **Setup 1: Clone from github**
```
git clone https://github.com/AhegaoPsyops/Random-Numbers-Arent.git
cd Random-Numbers-Arent
pip install -r requirements.txt
```
*Optional: Create Virtual Environment:*
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
- **Setup 2: Desktop App**
    1. Download the executable file from the 'dist/' folder
    2. Launch the GUI by double clicking the executable (this can be moved anywhere on your computer)

- **Notes**
    - The standalone app contains everything needed, so Python and dependencies do *not* need to be installed on the target machine for this method.
    - For macOS/Linux, ensure the executable has permissions to run (`chmod +x PRNG_GUI` on Linux/macOS)

## 🐍 Usage
- **Controls and Workflow**
    - Spacebare: Take PNG photos
    - Q: Close webcam and analyze
    - C: Clear captured images
    - Generate PRNG: Start PRNG generation thread
    - Average Entropy: Calculate and display average entropy
- **!!Important Note!!**
    - The cursor *MUST* be within the webcam window for the keyboard shortcuts to work correctly.

## 🧪 Testing
- **How to run tests:**
    - `pytest tests/ -v`
- **Notes:**
    - Tests cover Encrypt functions and GUI workflows.
    - Uses mocks to simulate webcam and GUI events.

## 🏗️ Project Structure
- **File Structure:**
```
Random-Numbers-Arent/
├── Encryption/
|   ├── Encrypt.py         
|   ├── PRNG_GUI.py        
|   └── tests/             
│       ├── test_Encrypt.py
│       └── test_PRNG_GUI.py
├── IstmV2.py
└── README.md
```
## 👥 Contributing
- **Basic Guidelines**
    - Feel free to fork the repo, create a branch, or submit a pull request
    - Write tests for any new functionality
    - Maintain optimized and robust coding methods

## 🤝 Acknowledgements
- **Authors:**
    - Fathia Tafesh
    - Josephine Benson
    - Ethan Dykes
- **Resources Used**
    - Incredible Pytest tutorial by Tech With Tim on YouTube: https://www.youtube.com/watch?v=EgpLj86ZHFQ
    - Description of the "lava lamp PRNG generators": https://www.cloudflare.com/learning/ssl/lava-lamp-encryption/
    - Some Debugging was assisted by ChatGPT Artificial Intelligence
- **Thank Yous**
    - Fathia - Thank you for being such a great Team Lead!! 💖💖💖
    - Ethan - Thank you for wrangling the AI 👏👏👏
    - Professor Faruk - Thank you for the opportunity to create such a creative project! 🫡🫡🫡
    - Silicon Graphics Inc. - Thank you for the inspiration from your concept
    - LavaRnd - Also Thanks for inspiration
    - My mother and father becuase I love them :)