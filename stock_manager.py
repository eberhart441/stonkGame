# stock_manager.py
import time, random
import CONSTANTS
from multiprocessing import Process, Pipe
from stock_window import run_window

STOCK_WINDOWS = []  # each entry: {'proc', 'conn', 'info'}

def launch_window():
    parent_conn, child_conn = Pipe()
    p = Process(target=run_window, args=(child_conn,), daemon=True)
    p.start()
    STOCK_WINDOWS.append({
        'proc': p,
        'conn': parent_conn,
        'info': {'ticker': None, 'price': None}
    })
    print(f"[+] Launched new stock window. Total: {len(STOCK_WINDOWS)}")

# close everything and clear all data
def blow_up_everything():
    print("[!] Blowing up ALL stock windows and data!!!")
    try:
        for w in STOCK_WINDOWS:
            try:
                w['proc'].terminate()
            except Exception:
                pass
            try:
                w['conn'].close()
            except Exception:
                pass
        STOCK_WINDOWS.clear()
        print("[!] All stock windows terminated and data cleared.")
    except Exception as e:
        print(f"[!] Error during stock_manager cleanup: {e}")

def cleanup_windows():
    alive = []
    for w in STOCK_WINDOWS:
        if w['proc'].is_alive():
            alive.append(w)
        else:
            print("[-] Window died.")
    STOCK_WINDOWS[:] = alive

def main(stock_managerConnect = 0):
    # spin up the minimum windows
    for _ in range(CONSTANTS.MIN_WINDOWS):
        launch_window()

    while True:
        time.sleep(1)
        cleanup_windows()

        # keep minimum windows running
        while len(STOCK_WINDOWS) < CONSTANTS.MIN_WINDOWS:
            print("[!] Respawning…")
            launch_window()

        # random spawn/kill behavior
        if int(time.time()) % CONSTANTS.NEW_WINDOW_INTERVAL == 0:
            if len(STOCK_WINDOWS) < CONSTANTS.MAX_WINDOWS and random.random() < CONSTANTS.NEW_WINDOW_PROBABILITY:
                launch_window()
            elif len(STOCK_WINDOWS) > CONSTANTS.MIN_WINDOWS:
                # kill a random one
                w = random.choice(STOCK_WINDOWS)
                w['proc'].terminate()
                STOCK_WINDOWS.remove(w)
                print(f"[-] Closed a stock window. Total: {len(STOCK_WINDOWS)}")

        # check for updates from all windows and clean up dead ones
        for w in STOCK_WINDOWS.copy():
            try:
                if w['conn'].poll():
                    data = w['conn'].recv()
                    w['info'].update(data)
            except (BrokenPipeError, EOFError):
                print("[!] Detected dead pipe—cleaning up this window.")
                try: w['proc'].terminate()
                except: pass
                try: w['conn'].close()
                except: pass
                STOCK_WINDOWS.remove(w)

        # collect status updates from all windows     
        status_list = [
            {'ticker': w['info']['ticker'], 'price': w['info']['price']}
            for w in STOCK_WINDOWS
        ]

        # send status updates to the stock manager if connected
        if stock_managerConnect and hasattr(stock_managerConnect, 'send'):
            try:
                stock_managerConnect.send(status_list)
            except Exception as e:
                print(f"[!] Failed to send status: {e}")

        # print out the current status of the windows
        #print("[!] Current stock windows status:")
        #for w in STOCK_WINDOWS:
        #    print(f"  Ticker: {w['info']['ticker']}, Price: {w['info']['price']}")

if __name__ == "__main__":
    main()
