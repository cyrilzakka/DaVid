<p align="center">
  <img src="https://github.com/cyrilzakka/DaVid/blob/main/DaVid-banner@2x.png" alt="DaVid logo"/>
</p>


## About
DaVid is a simple cross-platform GUI for annotating robotic and endoscopic surgical actions for use in deep-learning research.

#### Features
* Simple and lightweight interface for loading and annotating surgical frames for Windows, Linux and macOS.
* Joystick controls for intuitive and rapid action annotation. 
* Keyboard shortcuts support.
* Hassle-free data export. 

## Installation
In order to run DaVid, you'll first have to make sure you're running Python 3.5 or above.
``` sh
python -V
```
After downloading and unzipping the contents of this repository, navigate to the destination folder and install dependencies using:
``` sh
cd DaVid-main
pip install –upgrade pip
pip install -r requirements.txt
```
You can now launch DaVid with:
``` sh
python DaVid.py
```

## Download (Coming soon)
Alternatively, you can download pre-compiled versions of the application for macOS and Windows from [here](https://github.com/cyrilzakka/DaVid/releases). 

## Usage
1. After launching DaVid, select a video file and wait while frames are extracted and saved. Note that this process only happens once per video and should take up to a few minutes.
2. For the current frame move the controls accordingly.
3. That's it! Move on to the next frame.
