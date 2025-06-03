import customtkinter as ctk
import pandas as pd
import os
import random
import string
import numpy as np
from datetime import datetime
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multiprocessing import Process, Pipe
from tkinter import ttk

# my own modules
import stock_manager
import ad_manager
import DJ
import CONSTANTS

# call the stock manager class in another process
def start_trading(stock_managerConnect):
    stock_manager.main(stock_managerConnect)

# call the ad manager class in another process
def start_ads():
    ad_manager.main()

class PriceGenerator:
    def __init__(self, starting_price, maxlen=250):
        self.prices = deque([starting_price], maxlen=maxlen)
        self.timestamps = deque([datetime.now()], maxlen=maxlen)

    def add_next(self):
        last = self.prices[-1]
        new_price = last * (1 + random.uniform(-0.001, 0.001))
        self.prices.append(new_price)
        self.timestamps.append(datetime.now())

class MainApp(ctk.CTk):
    def __init__(self, user_info):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.user_info = user_info
        self.title(f"Gloomburg Terminal - {self.user_info['username']}")
        self.geometry("1000x700")
        self.bind("<FocusIn>", lambda e: self.lower())  # to lower the window when clicked

        self.generator = PriceGenerator(self.user_info['accountMoney'])
        self.price_tag = None

        self.mainConnect, stock_managerConnect = Pipe()
        self._trading_target = start_trading
        self._trading_args = (stock_managerConnect,)
        self._ad_target = start_ads

        self.updateCycle = 0

        self._create_sidebar()
        self._create_header()
        self._create_graph_panel()
        self._create_portfolio_panel()
        self._create_market_orders_panel()
        self._create_settings_panel()

        self.active_panel = None
        self.switch_panel("Balance")  # start with the Balance panel

        self.after(CONSTANTS.UPDATE_CYCLE, self.update)

    def launch_trading_process(self):
        if not hasattr(self, 'processA') or not self.processA.is_alive():
            musicPlayer.set_mood("crazy")
            musicPlayer.play_random_song()
            self.processA = Process(target=self._trading_target, args=self._trading_args)
            self.processA.start()
        if not hasattr(self, 'processB') or not self.processB.is_alive():
            self.processB = Process(target=self._ad_target)
            self.processB.start()

        self.start_btn.configure(state="disabled", text="\u2b62 Trading in progress...")
        self.after(CONSTANTS.MARKET_OPEN, self.end_trading_process)

    def end_trading_process(self):
            stock_manager.blow_up_everything()      # tear down any stray windows
            if hasattr(self, 'processA') and self.processA.is_alive():
                print("[!] Terminating A process...")
                self.processA.terminate()
                self.processA.join(timeout=5)
                if self.processA.is_alive():
                    print("[!] Force killing process A")
                    self.processA.kill()
            if hasattr(self, 'processB') and self.processB.is_alive():
                print("[!] Terminating B process...")
                self.processB.terminate()
                self.processB.join()
            self.start_btn.configure(state="normal", text="\u2b62 Trade Now")
            musicPlayer.set_mood("calm")
            musicPlayer.play_random_song()

    def _create_sidebar(self):
        sidebar_color = "#1c1c24"
        btn_color = "#3A7CFD"
        btn_hover = "#5590fa"

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=sidebar_color)
        self.sidebar.pack(side="left", fill="y")

        profile_frame = ctk.CTkFrame(self.sidebar, corner_radius=15, fg_color="#2a2a2a")
        profile_frame.pack(pady=(20, 10), padx=10, fill="x")

        initials = "".join([w[0].upper() for w in self.user_info['username'].split()]) or "U"
        avatar = ctk.CTkLabel(profile_frame, text=initials, width=50, height=50,
                              fg_color=btn_color, corner_radius=25,
                              font=ctk.CTkFont(size=20, weight="bold"))
        avatar.pack(side="left", padx=(10,5), pady=10)

        self.username_label = ctk.CTkLabel(profile_frame, text=self.user_info['username'],
                                           justify="left", font=ctk.CTkFont(size=14, weight="bold"))
        self.username_label.pack(anchor="w", padx=5, pady=(12,0))

        self.balance_label = ctk.CTkLabel(profile_frame,
                                          text=f"${self.user_info['accountMoney']:,}",
                                          justify="left", font=ctk.CTkFont(size=14, weight="bold"))
        self.balance_label.pack(anchor="w", padx=5, pady=(0,10))

        logo = ctk.CTkLabel(self.sidebar, text="GLOOMBURG\nTERMINAL",
                            font=ctk.CTkFont(size=26, weight="bold"), text_color=btn_color)
        logo.pack(pady=(0,20))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=sidebar_color, corner_radius=0)
        nav_frame.pack(fill="x", padx=10)
        icons = {"Balance":"\ud83d\udcca","Portfolio":"\ud83d\udcbc","Market Orders":"\ud83d\udcc8","Settings":"\u2699\ufe0f"}
        for name in ["Balance", "Portfolio", "Market Orders", "Settings"]:
            btn = ctk.CTkButton(nav_frame,
                                text=f"{icons[name]}  {name}",
                                width=180, height=38,
                                corner_radius=8,
                                fg_color=btn_color,
                                hover_color=btn_hover,
                                font=ctk.CTkFont(size=14),
                                command=lambda n=name: self.switch_panel(n))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg_color=btn_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg_color=btn_color))
            btn.pack(pady=6)

        self.start_btn = ctk.CTkButton(self.sidebar, text="\u2b62 Trade Now",
                                       width=180, height=40,
                                       corner_radius=8,
                                       fg_color=btn_color,
                                       hover_color=btn_hover,
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       command=self.launch_trading_process)
        self.start_btn.pack(side="bottom", pady=30)

    def _create_header(self):
        header_bg = "#23252c"
        self.header = ctk.CTkFrame(self, height=60, fg_color=header_bg)
        self.header.pack(side="top", fill="x")

        welcome_label = ctk.CTkLabel(self.header,
                                     text=f"Welcome, {self.user_info['username']}!     |     ID: {self.user_info['userID']}",
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color="white")
        welcome_label.pack(side="left", padx=20)
        ctk.CTkFrame(self, height=2, fg_color="#44475a").pack(fill="x")

    
    def switch_panel(self, panel_name):
        for frame in (self.graph_frame, self.portfolio_frame, self.market_orders_frame, self.settings_frame):
            frame.pack_forget()

        # show and refresh the one we need
        if panel_name == "Balance":
            self.graph_frame.pack(fill="both", expand=True, padx=15, pady=15)
            # Switch to balance axis
            self._switch_to_balance_view()
        elif panel_name == "Portfolio":
            self.graph_frame.pack(fill="both", expand=True, padx=15, pady=15)
            self._switch_to_portfolio_view()
            if self.mainConnect.poll():
                try:
                    status_list = self.mainConnect.recv()
                    self.update_portfolio(status_list)
                except Exception as e:
                    print(f"[!] Failed to receive portfolio data: {e}")
            else:
                # Show "waiting for data" message
                self.update_portfolio(None)
        elif panel_name == "Market Orders":
            self.market_orders_frame.pack(fill="both", expand=True, padx=15, pady=15)
        elif panel_name == "Settings":
            self.settings_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.active_panel = panel_name  # keep track of the active panel
        self.title(f"Gloomburg Terminal - {self.user_info['username']} | {panel_name}")

    def _create_graph_panel(self):
        self.graph_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)

        # Create figure with separate axes for balance and portfolio
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.fig.patch.set_facecolor("#0f0f0f")
        
        # Balance axis (line chart)
        self.balance_ax = self.fig.add_subplot(111)
        self.balance_ax.set_facecolor("#0f0f0f")
        self.balance_ax.set_xlabel("Time", color='gray', fontsize=14)
        self.balance_ax.set_ylabel("Price", color='gray', fontsize=14)
        self.balance_ax.spines["top"].set_visible(False)
        self.balance_ax.spines["right"].set_visible(False)
        self.balance_ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.balance_ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.balance_ax.tick_params(axis='y', colors='gray', labelsize=12)
        
        # Initialize the line plot
        self.line, = self.balance_ax.plot([], [], color="#00FF00", linewidth=2)
        
        # Portfolio axis (bar chart) - initially None, created when needed
        self.portfolio_ax = None
        
        # Current active axis
        self.ax = self.balance_ax  # Default to balance axis
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.price_tag = None

    def _switch_to_balance_view(self):
        """Switch the graph to show the balance line chart"""
        # Clear the figure and recreate balance axis
        self.fig.clear()
        
        self.balance_ax = self.fig.add_subplot(111)
        self.balance_ax.set_facecolor("#0f0f0f")
        self.balance_ax.set_xlabel("Time", color='gray', fontsize=14)
        self.balance_ax.set_ylabel("Price", color='gray', fontsize=14)
        self.balance_ax.spines["top"].set_visible(False)
        self.balance_ax.spines["right"].set_visible(False)
        self.balance_ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.balance_ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.balance_ax.tick_params(axis='y', colors='gray', labelsize=12)
        
        # Recreate the line plot
        self.line, = self.balance_ax.plot([], [], color="#00FF00", linewidth=2)
        self.ax = self.balance_ax
        self.price_tag = None
        
        # Force an immediate update to show current data
        self._update_balance_graph()
        self.canvas.draw()

    def _switch_to_portfolio_view(self):
        """Switch the graph to show the portfolio bar chart"""
        # Clear the figure and recreate portfolio axis
        self.fig.clear()
        
        self.portfolio_ax = self.fig.add_subplot(111)
        self.portfolio_ax.set_facecolor("#0f0f0f")
        self.ax = self.portfolio_ax

    def _update_balance_graph(self):
        """Update the balance graph with current data"""
        try:
            y = np.array(self.generator.prices)
            x = np.array([t.strftime("%H:%M:%S") for t in self.generator.timestamps])
            
            if len(y) == 0:
                return
                
            # Update the line data
            self.line.set_data(np.arange(len(x)), y)
            
            step = max(1, len(x)//10)
            self.balance_ax.set_xticks(np.arange(len(x))[::step])
            self.balance_ax.set_xticklabels(x[::step], rotation=45, ha='right')
            
            self.balance_ax.set_xlim(0, len(x))
            self.balance_ax.set_ylim(min(y) * 0.95, max(y) * 1.05)
            
            # Update line color based on trend
            if len(y) > 1:
                self.line.set_color("#00FF00" if y[-1] >= y[-2] else "#FF0000")
            else:
                self.line.set_color("#00FF00")
            
            # Update title
            self.balance_ax.set_title(f"Balance: ${y[-1]:.2f}", color='white', fontsize=14, pad=12)
            
            # Update price tag
            if self.price_tag:
                self.price_tag.remove()
            self.price_tag = self.balance_ax.annotate(
                f"${y[-1]:.2f}",
                xy=(len(x)-1, y[-1]),
                xytext=(10, 0),
                textcoords='offset points',
                color='white', fontsize=12,
                ha='left', va='center',
                bbox=dict(boxstyle="round,pad=0.2", fc="#222222", ec="#00FF00", lw=1)
            )
            
        except Exception as e:
            print(f"[!] Error updating balance graph: {e}")

    def _create_portfolio_panel(self):
        self.portfolio_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)

        # ttk Treeview for holdings
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1f1f28",
                        fieldbackground="#1f1f28",
                        foreground="white",
                        rowheight=25)
        style.map('Treeview', background=[('selected', '#3A7CFD')])

        cols = ("Symbol", "Shares", "Avg Cost", "Current", "Value", "P/L")
        self.tree = ttk.Treeview(self.portfolio_frame,
                                 columns=cols,
                                 show="headings",
                                 selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # optional total footer
        self.total_label = ctk.CTkLabel(self.portfolio_frame,
                                        text="Total Value: $0.00",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(pady=(0,10))

    def _create_market_orders_panel(self):
        self.market_orders_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        ctk.CTkLabel(self.market_orders_frame, text="Market order options will go here", text_color="gray").pack(pady=20)

    def _create_settings_panel(self):
        self.settings_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        ctk.CTkLabel(self.settings_frame, text="Settings options will go here", text_color="gray").pack(pady=20)

    def update(self):
        # Always update the generator first
        self.generator.add_next()
        
        if hasattr(self, 'active_panel'):
            if self.active_panel == "Balance":
                self._update_balance_graph()
                # Redraw the canvas
                self.canvas.draw()
                    
            elif self.active_panel == "Portfolio":
                # Check for incoming data from stock_manager for portfolio
                if self.mainConnect.poll():
                    try:
                        status_list = self.mainConnect.recv()
                        self.update_portfolio(status_list)
                    except Exception as e:
                        print(f"[!] Failed to receive portfolio data: {e}")

        # Update balance label in sidebar
        try:
            current_balance = int(self.generator.prices[-1])
            self.balance_label.configure(text=f"${current_balance:,}")
            self.user_info['accountMoney'] = current_balance
        except Exception as e:
            print(f"[!] Error updating balance label: {e}")

        # Save accountMoney periodically
        self.updateCycle += 1
        if self.updateCycle % CONSTANTS.SAVE_CYCLE == 0:
            try:
                userData = pd.read_csv(CONSTANTS.USER_DATA_FILE)
                userData.loc[userData['userID'] == self.user_info['userID'], 'accountMoney'] = self.user_info['accountMoney']
                userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)
            except Exception as e:
                print(f"[!] Error saving user data: {e}")

        # Schedule next update
        self.after(CONSTANTS.UPDATE_CYCLE, self.update)

    def update_portfolio(self, data=None):
        if self.ax != self.portfolio_ax:
            self._switch_to_portfolio_view()
        
        if not data:
            self.portfolio_ax.clear()
            self.portfolio_ax.set_facecolor("#0f0f0f")
            self.portfolio_ax.text(
                0.5, 0.5, 
                "Waiting for portfolio data...", 
                ha="center", va="center", 
                color="gray", fontsize=14, 
                transform=self.portfolio_ax.transAxes
            )
            self.canvas.draw()
            return
        
        try:
            # Filter out invalid data and extract valid ticker/price pairs
            valid_data = []
            for d in data:
                if isinstance(d, dict):
                    ticker = d.get('ticker', 'N/A')
                    price = d.get('price', None)
                    
                    # Only include entries with valid price data
                    if price is not None:
                        try:
                            # Convert to float to ensure it's numeric
                            price_float = float(price)
                            if not (price_float != price_float):  # Check for NaN
                                valid_data.append({'ticker': str(ticker), 'price': price_float})
                        except (ValueError, TypeError):
                            print(f"[!] Invalid price for {ticker}: {price}")
                            continue
                    else:
                        print(f"[!] None price for ticker: {ticker}")
            
            # Check if we have any valid data after filtering
            if not valid_data:
                self.portfolio_ax.clear()
                self.portfolio_ax.set_facecolor("#0f0f0f")
                self.portfolio_ax.text(
                    0.5, 0.5, 
                    "No valid price data", 
                    ha="center", va="center", 
                    color="orange", fontsize=14, 
                    transform=self.portfolio_ax.transAxes
                )
                self.canvas.draw()
                return
            
            # Extract validated data
            tickers = [d['ticker'] for d in valid_data]
            prices = [d['price'] for d in valid_data]
            self.portfolio_ax.clear()
            self.portfolio_ax.set_facecolor("#0f0f0f")
            x_positions = list(range(len(tickers)))
            
            bars = self.portfolio_ax.bar(x_positions, prices, 
                                    edgecolor="white", 
                                    color="#3A7CFD",
                                    alpha=0.8)
            
            self.portfolio_ax.set_xticks(x_positions)
            self.portfolio_ax.set_xticklabels(tickers, rotation=45, ha='right')
            
            self.portfolio_ax.tick_params(axis='x', colors='gray', rotation=45)
            self.portfolio_ax.tick_params(axis='y', colors='gray')
            self.portfolio_ax.spines["top"].set_visible(False)
            self.portfolio_ax.spines["right"].set_visible(False)
            self.portfolio_ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)

            self.portfolio_ax.set_xlabel("Ticker", color='gray', fontsize=12)
            self.portfolio_ax.set_ylabel("Price ($)",  color='gray', fontsize=12)
            self.portfolio_ax.set_title("Portfolio Stock Prices", color='white', fontsize=14, pad=12)
            
            if prices:
                max_price = max(prices)
                for i, (ticker, price) in enumerate(zip(tickers, prices)):
                    self.portfolio_ax.text(i, price + (max_price * 0.01), 
                                        f'${price:.1f}', 
                                        ha='center', va='bottom', 
                                        color='white', fontsize=8)

            self.canvas.draw_idle()
            self.canvas.flush_events()
            
        except Exception as e:
            print(f"[!] Error updating portfolio chart: {e}")
            print(f"[!] Raw data received: {data}")
            import traceback
            traceback.print_exc()
            
            # Show error message on chart
            try:
                self.portfolio_ax.clear()
                self.portfolio_ax.set_facecolor("#0f0f0f")
                self.portfolio_ax.text(
                    0.5, 0.5, 
                    f"Chart Error: {str(e)[:50]}...", 
                    ha="center", va="center", 
                    color="red", fontsize=12, 
                    transform=self.portfolio_ax.transAxes
                )
                self.canvas.draw()
            except:
                pass
 
class UserAuth(ctk.CTk):
    def __init__(self, userData):
        super().__init__()
        self.userData = userData
        self.logged_in_user = None
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Gloomburg Terminal Login")
        self.geometry("500x550")
        self.resizable(False, False)
        self._create_widgets()

    def _create_widgets(self):
        self.frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#2a2a2a")
        self.frame.pack(expand=True, fill="both", padx=40, pady=40)

        self.label_title = ctk.CTkLabel(self.frame, text="💼 Gloomburg Terminal",
                                        font=ctk.CTkFont(size=26, weight="bold"))
        self.label_title.pack(pady=(20, 10))

        self.label_subtitle = ctk.CTkLabel(self.frame, text="Login or Sign Up to Continue",
                                           font=ctk.CTkFont(size=14))
        self.label_subtitle.pack(pady=(0, 20))

        self.entry_user = ctk.CTkEntry(self.frame, placeholder_text="Username",
                                       width=300, height=40)
        self.entry_user.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(self.frame, placeholder_text="Password",
                                       show="*", width=300, height=40)
        self.entry_pass.pack(pady=8)

        self.button_login = ctk.CTkButton(self.frame, text="Login",
                                          command=self.login,
                                          width=300, height=45,
                                          corner_radius=8)
        self.button_login.pack(pady=(20, 8))

        self.button_signup = ctk.CTkButton(self.frame, text="Sign Up",
                                           command=self.signup,
                                           width=300, height=45,
                                           corner_radius=8,
                                           fg_color="#3A7CFD",
                                           hover_color="#5884f5")
        self.button_signup.pack(pady=8)

        self.label_status = ctk.CTkLabel(self.frame, text="", font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=(20, 10))

    def login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        user_row = self.userData[
            (self.userData['username'] == username) &
            (self.userData['password'] == password)
        ]
        if not user_row.empty:
            user_info = user_row.iloc[0].to_dict()
            self.logged_in_user = user_info
            self.label_status.configure(text=f"Welcome back, {username}!", text_color="green")
            self.after(1000, self.quit)
        else:
            self.label_status.configure(text="Incorrect username or password", text_color="red")

    def signup(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        if username in self.userData['username'].values:
            self.label_status.configure(text="Username already exists", text_color="orange")
        else:
            user_id = self.generate_user_id()
            account_money = random.randint(CONSTANTS.MIN_MONEY, CONSTANTS.MAX_MONEY)
            new_user = pd.DataFrame(
                [[username, password, user_id, account_money]],
                columns=['username', 'password', 'userID', 'accountMoney']
            )
            self.userData = pd.concat([self.userData, new_user], ignore_index=True)
            self.userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)
            self.logged_in_user = new_user.iloc[0].to_dict()
            self.label_status.configure(text=f"Signup successful!\nUser ID: {user_id}", text_color="green")
            self.after(1000, self.quit)

    def generate_user_id(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

if __name__ == "__main__":
    print("[!] Game initialized")

    global musicPlayer
    musicPlayer = DJ.MusicPlayer()
    musicPlayer.play_random_song()

    if not os.path.exists(CONSTANTS.USER_DATA_FILE) or os.stat(CONSTANTS.USER_DATA_FILE).st_size == 0:
        userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
        userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)
    else:
        userData = pd.read_csv(CONSTANTS.USER_DATA_FILE)
        if userData.empty:
            userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
            userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)

    auth = UserAuth(userData)
    auth.mainloop()
    auth.destroy()

    if auth.logged_in_user:
        app = MainApp(auth.logged_in_user)
        app.mainloop()
    else:
        print("[!] Exiting – no auth.")
