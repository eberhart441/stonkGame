# stock_manager.py
import time, random
import CONSTANTS
from multiprocessing import Process, Pipe
from stock_window import run_window
import os
import signal

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
        # Kill all stock window processes
        for w in STOCK_WINDOWS:
            try:
                if w['proc'].is_alive():
                    w['proc'].terminate()
                    # Give it a moment to terminate gracefully
                    w['proc'].join(timeout=0.5)
                    if w['proc'].is_alive():
                        # Force kill if still alive
                        os.kill(w['proc'].pid, signal.SIGKILL)
            except Exception as e:
                print(f"[!] Error terminating process: {e}")
            
            try:
                w['conn'].close()
            except Exception:
                pass
        
        # Clear the list
        STOCK_WINDOWS.clear()
        
        # Also kill any ad windows that might be hanging around
        try:
            import ad_manager
            for w in ad_manager.AD_WINDOWS:
                try:
                    w['proc'].terminate()
                except:
                    pass
            ad_manager.AD_WINDOWS.clear()
        except:
            pass
            
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
            try:
                w['conn'].close()
            except:
                pass
    STOCK_WINDOWS[:] = alive

def main(stock_managerConnect = 0):
    # spin up the minimum windows
    for _ in range(CONSTANTS.MIN_WINDOWS):
        launch_window()

    try:
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
                    if w in STOCK_WINDOWS:
                        STOCK_WINDOWS.remove(w)

            # collect status updates from all windows     
            status_list = [
                {'ticker': w['info']['ticker'], 'price': w['info']['price'], 'name': w['info'].get('name', '')}
                for w in STOCK_WINDOWS
                if w['info']['ticker'] is not None
            ]

            # send status updates to the main app if connected
            if stock_managerConnect and hasattr(stock_managerConnect, 'send'):
                try:
                    stock_managerConnect.send(status_list)
                except Exception as e:
                    print(f"[!] Failed to send status: {e}")
                    break

    except KeyboardInterrupt:
        print("[!] Stock manager interrupted")
    finally:
        blow_up_everything()

if __name__ == "__main__":
    main()