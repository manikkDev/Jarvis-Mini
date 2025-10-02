# 🤖 JARVIS MINI - Complete Setup Instructions

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Python Installation](#python-installation)
3. [Project Setup](#project-setup)
4. [Dependencies Installation](#dependencies-installation)
5. [Additional System Setup](#additional-system-setup)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Features Overview](#features-overview)

---

## 🖥️ System Requirements

- **Operating System**: Windows 10/11 (Primary), macOS, Linux
- **Python Version**: Python 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 500MB free space
- **Internet Connection**: Required for voice recognition, weather, maps, and web features
- **Microphone**: Required for voice commands
- **Speakers/Headphones**: Required for voice responses

---

## 🐍 Python Installation

### Windows:
```bash
# Download Python from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
# Verify installation:
python --version
pip --version
```

### macOS:
```bash
# Install using Homebrew (recommended)
brew install python

# Or download from https://www.python.org/downloads/
# Verify installation:
python3 --version
pip3 --version
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

---

## 📁 Project Setup

### 1. Download/Clone the Project
```bash
# If you have the project folder, navigate to it:
cd "path/to/Jarvis Voice"

# Or if cloning from repository:
git clone <repository-url>
cd jarvis-mini
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows:
python -m venv jarvis_env
jarvis_env\Scripts\activate

---

## 📦 Dependencies Installation

### Core Dependencies
Copy and paste these commands one by one:

```bash
# Essential GUI and Image Processing
pip install tkinter pillow

# Text-to-Speech Engine
pip install pyttsx3

# Speech Recognition
pip install SpeechRecognition pyaudio

# Web Automation and APIs
pip install pywhatkit wikipedia-api

# System Monitoring and Control
pip install psutil screen-brightness-control

# Windows Audio Control (Windows only)
pip install pycaw comtypes

# Data Analysis and Visualization
pip install pandas plotly

# Machine Learning for Fake News Detection
pip install scikit-learn nltk

# Additional Utilities
pip install pathlib
```

### Alternative: Install All at Once
Create a `requirements.txt` file with this content:

```txt
tkinter
pillow>=8.0.0
pyttsx3>=2.90
SpeechRecognition>=3.8.1
pyaudio>=0.2.11
pywhatkit>=5.3
wikipedia-api>=0.5.4
psutil>=5.8.0
screen-brightness-control>=0.11.1
pycaw>=20220416
comtypes>=1.1.10
pandas>=1.3.0
plotly>=5.0.0
scikit-learn>=1.0.0
nltk>=3.6.0
pathlib
```

Then install:
```bash
pip install -r requirements.txt
```

---

## 🔧 Additional System Setup

### 1. Audio Setup (Windows)
```bash
# Install Windows audio dependencies
pip install pycaw comtypes

# For microphone access, you may need to enable microphone permissions:
# Settings > Privacy > Microphone > Allow apps to access microphone
```

### 2. PyAudio Installation (Can be tricky)

#### Windows:
```bash
# Method 1: Try direct installation
pip install pyaudio

# Method 2: If above fails, use precompiled wheel
pip install pipwin
pipwin install pyaudio

# Method 3: Download wheel manually from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then install: pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

#### macOS:
```bash
# Install portaudio first
brew install portaudio
pip install pyaudio
```

#### Linux:
```bash
# Install system dependencies
sudo apt-get install python3-pyaudio
# Or
sudo apt-get install portaudio19-dev python3-all-dev
pip install pyaudio
```

### 3. NLTK Data Download
The application will automatically download required NLTK data on first run, but you can pre-download:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 🚀 Running the Application

### 1. Navigate to Project Directory
```bash
cd "path/to/Jarvis Voice"
```

### 2. Activate Virtual Environment (if using)
```bash
# Windows:
jarvis_env\Scripts\activate

# macOS/Linux:
source jarvis_env/bin/activate
```

### 3. Run the Application
```bash
python main.py
```

### 4. First Run Setup
- The application will automatically download NLTK data
- Grant microphone permissions when prompted
- The splash screen will appear, followed by the main interface

---

## 🛠️ Troubleshooting

### Common Issues and Solutions:

#### 1. PyAudio Installation Error
```bash
# Windows: Install Microsoft Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Alternative: Use conda
conda install pyaudio
```

#### 2. Speech Recognition Not Working
```bash
# Check microphone permissions
# Windows: Settings > Privacy > Microphone
# Ensure internet connection for Google Speech API
```

#### 3. Text-to-Speech Not Working
```bash
# Windows: Check if Windows Speech Platform is installed
# Install SAPI voices if needed
```

#### 4. Import Errors
```bash
# Reinstall specific package
pip uninstall <package-name>
pip install <package-name>

# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### 5. Permission Errors (Windows)
```bash
# Run Command Prompt as Administrator
# Or use PowerShell as Administrator
```

#### 6. Module Not Found Errors
```bash
# Ensure virtual environment is activated
# Check Python path
python -c "import sys; print(sys.path)"
```

---

## 🎯 Features Overview

### Voice Commands
- **Web Browsing**: "Hey Jarvis, open YouTube/Google/Gmail"
- **Search**: "Hey Jarvis, search for [query]"
- **Wikipedia**: "Hey Jarvis, wikipedia [topic]"
- **Weather**: "Hey Jarvis, weather in [city]"
- **Music**: "Hey Jarvis, play [song name]"
- **System Control**: Volume, brightness, battery status
- **Navigation**: "Hey Jarvis, show me [location] on map"

### GUI Features
- Modern dark theme interface
- Real-time system monitoring
- Interactive weather cards
- Professional Google Maps integration
- Animated GIF support
- Comprehensive command documentation

### Technical Features
- Multi-threaded speech processing
- Thread-safe audio engine
- Real-time system monitoring
- Machine learning fake news detection
- Data visualization with Plotly
- Cross-platform compatibility

---

## 📞 Support

### If you encounter issues:

1. **Check Dependencies**: Ensure all packages are installed correctly
2. **Update Python**: Make sure you're using Python 3.8+
3. **Check Permissions**: Microphone and system access permissions
4. **Internet Connection**: Required for speech recognition and web features
5. **System Compatibility**: Some features are Windows-specific

### System-Specific Notes:

#### Windows:
- Requires Windows 10/11 for full functionality
- Some audio features use Windows-specific APIs
- May need Visual C++ redistributables

#### macOS:
- Use `python3` and `pip3` commands
- May need Xcode command line tools
- Some system control features may be limited

#### Linux:
- Install system audio dependencies
- May need additional permissions for system control
- Test microphone access with `arecord`

---

## 🔄 Updates and Maintenance

### Keeping Dependencies Updated:
```bash
# Update all packages
pip list --outdated
pip install --upgrade <package-name>

# Or update all at once
pip freeze > current_requirements.txt
pip install -r requirements.txt --upgrade
```

### Performance Optimization:
- Close unnecessary applications for better speech recognition
- Ensure stable internet connection
- Use SSD storage for faster loading
- Allocate sufficient RAM (8GB recommended)

---

## 🎉 You're Ready!

Once setup is complete, you can:
1. Launch the application with `python main.py`
2. Use voice commands starting with "Hey Jarvis"
3. Explore the GUI features and cards
4. Check the "About" section for complete command list

**Enjoy your personal AI assistant! 🤖✨**