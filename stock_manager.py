import subprocess
import random
import time
import os
import pygame

MAX_WINDOWS = 12
MIN_WINDOWS = 8
STOCK_WINDOWS = []

# Get the absolute path to the stock_window.py file
STOCK_WINDOW_PATH = os.path.join(os.path.dirname(__file__), "stock_window.py")

def launch_window():
    proc = subprocess.Popen(["python", STOCK_WINDOW_PATH])
    STOCK_WINDOWS.append(proc)
    print(f"[+] Launched new stock window. Total: {len(STOCK_WINDOWS)}")

def close_window():
    if STOCK_WINDOWS:
        proc = random.choice(STOCK_WINDOWS)
        proc.terminate()
        STOCK_WINDOWS.remove(proc)
        print(f"[-] Closed a stock window. Total: {len(STOCK_WINDOWS)}")

def play_random_song():
    MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
    songs = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav"))]
    song = random.choice(songs)
    full_path = os.path.join(MUSIC_DIR, song)
    pygame.mixer.music.load(full_path)
    pygame.mixer.music.play()
    print(f"[♪] Now playing: {song}")


def main():
    pygame.mixer.init()
    play_random_song()

    for _ in range(MIN_WINDOWS):
        launch_window()

    while True:
        time.sleep(5)

        # Handle music playback
        if not pygame.mixer.music.get_busy():
            play_random_song()

        # Launch or close windows every 15 seconds
        if int(time.time()) % 30 == 0:
            if len(STOCK_WINDOWS) < MAX_WINDOWS and random.random() < 0.6:
                launch_window()
            elif len(STOCK_WINDOWS) > MIN_WINDOWS:
                close_window()


if __name__ == "__main__":
    main()
