#!/usr/bin/env python

import socket
import os
import json

from pathlib import Path
import argparse

import torch

import os, subprocess

from OnlineHTR.src.models.carbune_module import LitModule1
from OnlineHTR.src.utils.io import load_alphabet
from OnlineHTR.src.utils.io import get_best_checkpoint_path
from OnlineHTR.src.data.tokenisers import AlphabetMapper
from OnlineHTR.src.data.acquisition import reset_strokes
from OnlineHTR.src.data.acquisition import predict

def parse_cli_args() -> dict:
    """Parse command-line arguments for this script."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-dot-radius', '--dot-radius', type=int,
                        default=3)
    parser.add_argument('-model-folder-path', '--model-folder-path', type=Path,
                        default=Path('OnlineHTR/models/dataIAMOnDB_featuresLinInterpol20DxDyDtN_decoderGreedy'))
    args = parser.parse_args()
    
    return vars(args)


if __name__ == '__main__':
    args = parse_cli_args()

    BASE_PATH = Path(args['model_folder_path'])
    CHECKPOINT_PATH = get_best_checkpoint_path( BASE_PATH / 'checkpoints' )

    model = LitModule1.load_from_checkpoint(CHECKPOINT_PATH)

    model.eval()

    checkpoint = torch.load(CHECKPOINT_PATH, map_location=lambda storage, loc: storage, weights_only=False)

    alphabet = load_alphabet(BASE_PATH / 'alphabet.json')
    alphabet_mapper = AlphabetMapper( alphabet )
    decoder = checkpoint['hyper_parameters']['decoder']


    socket_path = "/tmp/gnome_to_python.sock"

    if os.path.exists(socket_path):
        os.remove(socket_path)


    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
        server.bind(socket_path)
        server.listen(1)
        
        print("ready")
        
        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(100000).decode()

                strokes = json.loads(data)

                # negate y axis
                strokes = [[[point[0], -point[1], point[2]] for point in stroke] for stroke in strokes]

                text = predict(strokes, alphabet, model, decoder, alphabet_mapper)

                print(f"Received: {data}")
                print(f"text: {text}")

                text = "" if text is None else text
                print(f"clean: {text}")
                conn.sendall(text.encode())

