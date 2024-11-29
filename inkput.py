#!/usr/bin/env python

from tkinter import Tk
from tkinter import Button, Text, Label
from tkinter import messagebox
from tkinter import N, W, E, S
from pathlib import Path
import argparse

import torch

import os, subprocess

from OnlineHTR.src.models.carbune_module import LitModule1
from OnlineHTR.src.utils.io import load_alphabet
from OnlineHTR.src.utils.io import get_best_checkpoint_path
from OnlineHTR.src.data.tokenisers import AlphabetMapper
from OnlineHTR.src.data.acquisition import reset_strokes
from OnlineHTR.src.data.acquisition import Sketchpad
from OnlineHTR.src.data.acquisition import predict

QWERTZ = True

def parse_cli_args() -> dict:
    """Parse command-line arguments for this script."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-dot-radius', '--dot-radius', type=int,
                        default=3)
    parser.add_argument('-model-folder-path', '--model-folder-path', type=Path,
                        default=Path('OnlineHTR/models/dataIAMOnDB_featuresLinInterpol20DxDyDtN_decoderGreedy'))
    args = parser.parse_args()
    
    return vars(args)

def test_ydotool():
    """Check if ydotool is available and can find its daemon"""
    try:
        ret = subprocess.run(['ydotool', 'type', ''],
                                      env=dict(os.environ, YDOTOOL_SOCKET="/tmp/.ydotool_socket"),
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
    except FileNotFoundError:
        return False, "ydotool not found."
    if ret.returncode:
        return False, "ydotool returned: " + ret.stdout.decode()    
    else:
        return True, ""
 
    

def type_key(code):
    subprocess.call(['ydotool', 'key', f'{code}:1', f'{code}:0'], env=dict(os.environ, YDOTOOL_SOCKET="/tmp/.ydotool_socket"))


def run_and_type(global_strokes, prediction_field, alphabet, model, decoder, alphabet_mapper):
    text = predict(global_strokes, prediction_field, alphabet, model, decoder, alphabet_mapper)
    print(text)
    
    # quick and dirty translation from german QWERTZ to QWERTY
    # we just swap Y and Z, since that's the most prominent problem when entering text
    if QWERTZ:
        replacements = str.maketrans("YyZz",
                                     "ZzYy")
        
        translated = text.translate(replacements)
        
        print("Translated", text, "to", translated)
      
    else:
        translated = text

    subprocess.call(['ydotool', 'type', translated], env=dict(os.environ, YDOTOOL_SOCKET="/tmp/.ydotool_socket"))




class App(Tk):
    def __init__(self, args):
        super().__init__()
    
        # =====
        # Model
        # =====

        BASE_PATH = Path(args['model_folder_path'])
        CHECKPOINT_PATH = get_best_checkpoint_path( BASE_PATH / 'checkpoints' )

        model = LitModule1.load_from_checkpoint(CHECKPOINT_PATH)

        model.eval()

        checkpoint = torch.load(CHECKPOINT_PATH, map_location=lambda storage, loc: storage, weights_only=False)

        alphabet = load_alphabet(BASE_PATH / 'alphabet.json')
        alphabet_mapper = AlphabetMapper( alphabet )
        decoder = checkpoint['hyper_parameters']['decoder']
        
        
        # ==
        # UI
        # ==

        global_strokes = []

        self.title("Draw and Type")
        self.geometry("1024x512+100+100")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.overrideredirect(True) # floating window

        sketch = Sketchpad(self, global_strokes, args['dot_radius'], cursor="none")
        sketch.grid(column=0, row=0, sticky=(N, W, E, S))

        prediction_field = Text(self, height=4, width=100)
        prediction_field.place(x=300, y=400)
        prediction_field.tag_configure('big', font=('Arial', 20, 'bold'))

        """self.plot_button = Button(
            self, text="Plot strokes",
            command=lambda: plot_strokes(global_strokes))
        self.plot_button.place(x=50,y=50)

        self.store_button = Button(
            self, text="Store strokes",
            command=lambda: store_strokes(global_strokes))
        self.store_button.place(x=220,y=50)"""

        self.reset_button = Button(
            self, text="Reset strokes",
            command=lambda: reset_strokes(global_strokes, sketch, prediction_field))
        self.reset_button.place(x=800,y=50)

        self.predict_button = Button(
            self, text="Predict!",
            bg='black',
            fg='white',
            font=('Arial', 20, 'bold'),
            command=lambda: run_and_type(global_strokes, prediction_field, alphabet,
                                    model, decoder, alphabet_mapper))
        self.predict_button.place(x=50,y=400)
        
        
        self.grip = Button(self, text="drag", cursor="hand1")
        self.grip.place(x=50, y=50)
        self.grip.bind("<ButtonPress-1>", self.start_move)
        self.grip.bind("<ButtonRelease-1>", self.stop_move)
        self.grip.bind("<B1-Motion>", self.do_move)

        
        self.exit_button = Button(self, text="Exit", command=self.destroy) 
        self.exit_button.place(x=140, y=50)
        
        # for key codes see
        # https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
        Button(self, text="Return", command=lambda: type_key(28)).place(x=230, y=50)
        Button(self, text="Space", command=lambda: type_key(57)).place(x=350, y=50)
        Button(self, text="Backspace", command=lambda: type_key(14)).place(x=460, y=50)


    # for dragging around the window since it has no decoration
    # https://stackoverflow.com/questions/4055267/tkinter-mouse-drag-a-window-without-borders-eg-overridedirect1

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
    


if __name__ == '__main__':

    args = parse_cli_args()
    
    # check if ydotool is available
    available, text = test_ydotool()
    if not available:
        messagebox.showerror("ydotool error", text)

    else:
        app=App(args)
        app.mainloop()
    
