import subprocess
import random
import time
import os

MAX_WINDOWS = 12
MIN_WINDOWS = 8
STOCK_WINDOWS = []

# Get the absolute path to the stock_window.py file
STOCK_WINDOW_PATH = os.path.join(os.path.dirname(__file__), "stock_window.py")

def launch_window():
    proc = subprocess.Popen(["python", STOCK_WINDOW_PATH])
    STOCK_WINDOWS.append({'proc': proc, 'launched_at': time.time()})
    print(f"[+] Launched new stock window. Total: {len(STOCK_WINDOWS)}")

def close_window():
    if STOCK_WINDOWS:
        w = random.choice(STOCK_WINDOWS)
        w['proc'].terminate()
        STOCK_WINDOWS.remove(w)
        print(f"[-] Closed a stock window. Total: {len(STOCK_WINDOWS)}")

def cleanup_windows():
    global STOCK_WINDOWS
    alive = []
    for w in STOCK_WINDOWS:
        if w['proc'].poll() is None:  # Still running
            alive.append(w)
        else:
            print("[-] Window closed by user or crashed.")
    STOCK_WINDOWS = alive

def main():
    for _ in range(MIN_WINDOWS):
        launch_window()

    while True:
        time.sleep(5)
        cleanup_windows()

        while len(STOCK_WINDOWS) < MIN_WINDOWS:
            print("[!] Window count dropped. Respawning...")
            launch_window()

        # Random behavior every 30 seconds
        if int(time.time()) % 30 == 0:
            if len(STOCK_WINDOWS) < MAX_WINDOWS and random.random() < 0.6:
                launch_window()
            elif len(STOCK_WINDOWS) > MIN_WINDOWS:
                close_window()

if __name__ == "__main__":
    main()
