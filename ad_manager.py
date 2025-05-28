import subprocess
import random
import time
import os
import CONSTANTS

AD_WINDOWS = []

# Get the absolute path to the stock_window.py file
AD_WINDOW_PATH = os.path.join(os.path.dirname(__file__), "stock_window.py")

def launch_window():
    proc = subprocess.Popen(["python", AD_WINDOW_PATH])
    AD_WINDOWS.append({'proc': proc, 'launched_at': time.time()})
    print(f"[+] Launched new ad window. Total: {len(AD_WINDOWS)}")

def close_window():
    if AD_WINDOWS:
        w = random.choice(AD_WINDOWS)
        w['proc'].terminate()
        AD_WINDOWS.remove(w)
        print(f"[-] Closed an ad window. Total: {len(AD_WINDOWS)}")

def cleanup_windows():
    global AD_WINDOWS
    alive = []
    for w in AD_WINDOWS:
        if w['proc'].poll() is None:  # Still running
            alive.append(w)
        else:
            print("[-] Window closed by user or crashed.")
    AD_WINDOWS = alive

def main(stock_managerConnect=0):
    for _ in range(CONSTANTS.MIN_AD_WINDOWS):
        launch_window()

    while True:
        time.sleep(1)
        cleanup_windows()

        while len(AD_WINDOWS) < CONSTANTS.MIN_AD_WINDOWS:
            print("[!] Window count dropped. Respawning...")
            launch_window()

        # Random behavior every set amount of seconds
        if int(time.time()) % CONSTANTS.NEW_AD_WINDOW_INTERVAL == 0:
            if len(AD_WINDOWS) < CONSTANTS.MAX_AD_WINDOWS and random.random() < CONSTANTS.NEW_AD_WINDOW_PROBABILITY:
                launch_window()
            elif len(AD_WINDOWS) > CONSTANTS.MIN_AD_WINDOWS:
                close_window()

        try:
            # send data through pipe
            stock_managerConnect.send(len(AD_WINDOWS))
        except Exception as e:
            print(f"[!] Error sending data: {e}")

if __name__ == "__main__":
    main()
