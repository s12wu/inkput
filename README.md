# Inkput

https://github.com/user-attachments/assets/7994263e-e8bd-441d-aef8-2c4c7feedb03

Enter text on your Linux desktop using handwriting recognition.
This is based on PellelNitram's handwriting recognition implementation - all credits should go to them. (see below)

All I did was modify the UI to be a floating window and type out the detected text.


This is built for, but probably not limited to, the Pine64 PineNote running the Debian trixie GNOME image.
It **works on wayland** by using ydotool and its root daemon to enter the text.

To work with a German QWERTZ layout, this program simply swaps "Y" with "Z" and vice-versa. Other special characters are of course still messed up. Disable this by setting `QWERTZ=False` in `inkput.py`.

This is still a very early quick and dirty test.

## usage
 - Write into the drawing area. Click "Predict" to recognize the text and type it out.
 - "Reset strokes" to clear the drawing area.
 - click and drag the "drag" button to move the window. This is necessary since it has no title bar
 - click "exit" to quit the program
 - "Return", "Space" and "Backspace" to type these keys

## future features
 - minimize / hide the window
 - Maybe add a function edit the text before typing to correct misspellings?
 - Run a spell checker?
 - ...

## known problems
 - buttons ignore the 2x scaling on first run after reboot, subsequent runs are fine
 - sometimes the pen keeps drawing even if not pressing on the surface

## installation
The original project recommended the use of conda, but I had success just using the system Python 3.12 (trixie repos November 2024) and a venv.

### setup inkput

Clone this repo and cd to it

```bash
git clone --recurse-submodules https://github.com/s12wu/inkput
cd inkput

sudo apt install python3-pip python3-venv python3-tk
python -m venv venv
source venv/bin/activate

cd OnlineHTR
pip install -r requirements.txt
pip install -e .
cd ..
```

> Download the model weights [here](https://lellep.xyz/blog/online-htr.html?utm_campaign=githubWeights#the-model-weights) and place it in `models/dataIAMOnDB_featuresLinInterpol20DxDyDtN_decoderGreedy/` after unpacking it.


### build + install ydotool
```bash
sudo apt install cmake scdoc
git clone https://github.com/ReimuNotMoe/ydotool
cd ydotool
mkdir build
cd build
cmake .. -DSYSTEMD_SYSTEM_SERVICE=ON -DSYSTEMD_USER_SERVICE=OFF
sudo make install
sudo mv /usr/local/lib/systemd/user/ydotoold.service /lib/systemd/system/

# edit the service file.
sudo nano /lib/systemd/system/ydotoold.service
# change
ExecStart=/usr/local/bin/ydotoold
# to
ExecStart=/usr/local/bin/ydotoold -p /tmp/.ydotool_socket -P 666
# this specifies the socked ydotool can use to communicate. -P 666 sets the necessary permissions

sudo systemctl start ydotoold.service # enable as well if you want it to run it on system startup

# verify ydotool is working
YDOTOOL_SOCKET=/tmp/.ydotool_socket ydotool type "hello world" 
 > hello world
```

### run
cd to the repo folder
```bash
source venv/bin/activate # if not done yet
python inkput.py
```

It takes about 30 seconds to start until the window appears.

## menu item
`start_inkput.sh` changes to the directory, activates the venv and calls `inkput.py`.

Edit it to cd to the directory you cloned the repository to.

Install the menu editor (`sudo apt install alacarte`). Create a new item, and browse for the start_inkput.sh script.

# Integration into the on screen keyboard (GNOME only)
I tried integrating this into a fork of gjs-osk. The Idea is: instead of having this window floating around, the OSK by design already hides and shows as needed.

To use this: Install the on screen keyboad from [here](https://github.com/s12wu/gjs-osk).

Activathe the venv and run `inkput_daemon.py`.

Installation of ydotool is **not** necessary, since the gnome extension handles the input stuff.

## closing thoughts
In the last few weeks, I haven't found myself using handwriting input at all.
I basically need keyboard input for two scenarios:
- For example, when quickly typing in a web url or search term, the [vanilla gjs-osk](https://github.com/Vishram1123/gjs-osk) is already miles ahead of the default gnome keyboard. Handwriting is about as fast (in the case of the Tkinter UI) or much slower (in the case of the OSK integration, just watch the video over there) and quickly becomes annoying due to recognition errors.
- For writing longer texts, e.g. an email, I simply take out a Bluetooth keyboard, which is much faster and more precise.

