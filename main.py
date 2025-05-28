import customtkinter as ctk
import pandas as pd
import os
import random
import string
import CONSTANTS
import numpy as np
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import DJ
from multiprocessing import Process, Pipe

# call the stock manager class in another process
def start_trading(stock_managerConnect):
    import stock_manager
    stock_manager.main(stock_managerConnect)

# call the ad manager class in another process
def start_ads():
    import ad_manager
    ad_manager.main()

class PriceGenerator:
    def __init__(self, starting_price):
        self.prices = [starting_price]
        self.timestamps = [datetime.now()]

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

        self.generator = PriceGenerator(self.user_info['accountMoney'])
        self.price_tag = None

        self.mainConnect, stock_managerConnect = Pipe()
        self._trading_target = start_trading
        self._trading_args = (stock_managerConnect,)
        self._ad_target = start_ads

        # var that tracks how long the game has been running
        self.updateCycle = 0

        self._create_sidebar()
        self._create_header()
        self._create_graph_panel()
        self.after(CONSTANTS.UPDATE_CYCLE, self.update)

    def launch_trading_process(self):
        if not hasattr(self, 'processA') or not self.processA.is_alive():
            # Play crazy music
            musicPlayer.set_mood("crazy")
            musicPlayer.play_random_song()

            self.processA = Process(target=self._trading_target, args=self._trading_args)
            self.processA.start()
        if not hasattr(self, 'processB') or not self.processB.is_alive():
            self.processB = Process(target=self._ad_target)
            self.processB.start()

    def _create_sidebar(self):
        sidebar_color = "#1c1c24"
        btn_color = "#3A7CFD"
        btn_hover = "#5590fa"

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=sidebar_color)
        self.sidebar.pack(side="left", fill="y")

        profile_frame = ctk.CTkFrame(self.sidebar, corner_radius=15, fg_color="#2a2a2a")
        profile_frame.pack(pady=(20, 10), padx=10, fill="x")

        initials = "".join([w[0].upper() for w in self.user_info['username'].split()]) or "U"
        avatar = ctk.CTkLabel(
            profile_frame,
            text=initials,
            width=50, height=50,
            fg_color=btn_color, corner_radius=25,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        avatar.pack(side="left", padx=(10,5), pady=10)

        self.username_label = ctk.CTkLabel(
            profile_frame,
            text=self.user_info['username'],
            justify="left",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.username_label.pack(anchor="w", padx=5, pady=(12,0))

        self.balance_label = ctk.CTkLabel(
            profile_frame,
            text=f"${self.user_info['accountMoney']:,}",
            justify="left",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.balance_label.pack(anchor="w", padx=5, pady=(0,10))

        logo = ctk.CTkLabel(
            self.sidebar,
            text="GLOOMBURG\nTERMINAL",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=btn_color
        )
        logo.pack(pady=(0,20))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=sidebar_color, corner_radius=0)
        nav_frame.pack(fill="x", padx=10)
        icons = {"Balance":"\ud83d\udcca","Portfolio":"\ud83d\udcbc","Trade":"\ud83d\udcc8","Settings":"\u2699\ufe0f"}
        for name in ["Balance", "Portfolio", "Trade", "Settings"]:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icons[name]}  {name}",
                width=180, height=38,
                corner_radius=8,
                fg_color=btn_color,
                hover_color=btn_hover,
                font=ctk.CTkFont(size=14)
            )
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg_color=btn_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg_color=btn_color))
            btn.pack(pady=6)

        self.start_btn = ctk.CTkButton(
            self.sidebar,
            text="\u2b62 Trade Now",
            width=180, height=40,
            corner_radius=8,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.launch_trading_process
        )
        self.start_btn.pack(side="bottom", pady=30)

    def _create_header(self):
        header_bg = "#23252c"
        self.header = ctk.CTkFrame(self, height=60, fg_color=header_bg)
        self.header.pack(side="top", fill="x")

        welcome_label = ctk.CTkLabel(
            self.header,
            text=f"Welcome, {self.user_info['username']}!     |     ID: {self.user_info['userID']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        welcome_label.pack(side="left", padx=20)
        ctk.CTkFrame(self, height=2, fg_color="#44475a").pack(fill="x")

    def _create_graph_panel(self):
        self.graph_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        self.graph_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#0f0f0f")
        self.ax.set_facecolor("#0f0f0f")

        self.ax.set_xlabel("Time", color='gray', fontsize=14)
        self.ax.set_ylabel("Price", color='gray', fontsize=14)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.ax.tick_params(axis='y', colors='gray', labelsize=12)

        self.line, = self.ax.plot([], [], color="#00FF00", linewidth=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.price_tag = None

    def update(self):
        self.updateCycle += 1

        # save user data every fixed numer of cycles
        if self.updateCycle % CONSTANTS.SAVE_CYCLE == 0:
            self.user_info['accountMoney'] = int(self.generator.prices[-1])
            userData = pd.read_csv(CONSTANTS.USER_DATA_FILE)
            userData.loc[userData['userID'] == self.user_info['userID'], 'accountMoney'] = self.user_info['accountMoney']
            userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)
            print(f"[!] User data saved. New balance: ${self.user_info['accountMoney']:.2f}")

        # try to get messages from stock_manager
        if self.mainConnect.poll():
            message = self.mainConnect.recv()
            print(f"[!] Message from stock_manager. {message}!")

        self.generator.add_next()
        y = np.array(self.generator.prices)
        x = np.array([t.strftime("%H:%M:%S") for t in self.generator.timestamps])

        self.line.set_data(np.arange(len(x)), y)
        step = max(1, len(x)//10)
        self.ax.set_xticks(np.arange(len(x))[::step])
        self.ax.set_xticklabels(x[::step], rotation=45, ha='right')
        self.ax.set_xlim(0, len(x))
        self.ax.set_ylim(min(y) * 0.95, max(y) * 1.05)

        self.line.set_color("#00FF00" if y[-1] >= y[-2] else "#FF0000")
        self.ax.set_title(f"Balance: ${y[-1]:.2f}", color='white', fontsize=14, pad=12)

        if self.price_tag:
            self.price_tag.remove()
        self.price_tag = self.ax.annotate(
            f"${y[-1]:.2f}",
            xy=(len(x)-1, y[-1]),
            xytext=(10, 0),
            textcoords='offset points',
            color='white', fontsize=12,
            ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="#222222", ec="#00FF00", lw=1)
        )

        self.balance_label.configure(text=f"${y[-1]:,.2f}")
        self.canvas.draw()
        self.after(CONSTANTS.UPDATE_CYCLE, self.update)


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

        self.label_title = ctk.CTkLabel(
            self.frame,
            text="💼 Gloomburg Terminal",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.label_title.pack(pady=(20, 10))

        self.label_subtitle = ctk.CTkLabel(
            self.frame,
            text="Login or Sign Up to Continue",
            font=ctk.CTkFont(size=14)
        )
        self.label_subtitle.pack(pady=(0, 20))

        self.entry_user = ctk.CTkEntry(
            self.frame,
            placeholder_text="Username",
            width=300, height=40
        )
        self.entry_user.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(
            self.frame,
            placeholder_text="Password",
            show="*",
            width=300, height=40
        )
        self.entry_pass.pack(pady=8)

        self.button_login = ctk.CTkButton(
            self.frame,
            text="Login",
            command=self.login,
            width=300, height=45,
            corner_radius=8
        )
        self.button_login.pack(pady=(20, 8))

        self.button_signup = ctk.CTkButton(
            self.frame,
            text="Sign Up",
            command=self.signup,
            width=300, height=45,
            corner_radius=8,
            fg_color="#3A7CFD",
            hover_color="#5884f5"
        )
        self.button_signup.pack(pady=8)

        self.label_status = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
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
            user_info = new_user.iloc[0].to_dict()
            self.logged_in_user = user_info
            self.label_status.configure(text=f"Signup successful!\nUser ID: {user_id}", text_color="green")
            self.after(1000, self.quit)

    def generate_user_id(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

if __name__ == "__main__":
    print("[!] Game initialized")

    # Play calm music
    musicPlayer = DJ.MusicPlayer()
    musicPlayer.play_random_song()

    # Load or init user data
    if not os.path.exists(CONSTANTS.USER_DATA_FILE) or os.stat(CONSTANTS.USER_DATA_FILE).st_size == 0:
        userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
        userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)
    else:
        userData = pd.read_csv(CONSTANTS.USER_DATA_FILE)
        if userData.empty:
            userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
            userData.to_csv(CONSTANTS.USER_DATA_FILE, index=False)

    # Authentication
    auth = UserAuth(userData)
    auth.mainloop()
    auth.destroy()

    if auth.logged_in_user:
        app = MainApp(auth.logged_in_user)
        app.mainloop()
    else:
        print("[!] Exiting – no auth.")
