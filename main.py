import customtkinter as ctk
import pandas as pd
import os
import random
import string
import numpy as np
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import DJ
import stock_manager

# Placeholder price generator – replace with your actual generator
class PriceGenerator:
    def __init__(self, starting_price):
        self.prices = [starting_price]
        self.timestamps = [datetime.now()]
    def add_next(self):
        last = self.prices[-1]
        # simulate small random walk
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

        # price generator for account balance
        self.generator = PriceGenerator(self.user_info['accountMoney'])
        self.price_tag = None

        # build UI
        self._create_sidebar()
        self._create_header()
        self._create_graph_panel()

        # start updating graph every second
        self.after(1000, self.update_graph)

    def _create_sidebar(self):
        sidebar_color = "#1c1c24"
        btn_color = "#3A7CFD"
        btn_hover = "#5590fa"

        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color=sidebar_color)
        self.sidebar.pack(side="left", fill="y")

        # Logo
        logo = ctk.CTkLabel(
            self.sidebar,
            text="GLOOMBURG\nTERMINAL",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=btn_color
        )
        logo.pack(pady=(30,20))

        # Navigation buttons frame
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color=sidebar_color, corner_radius=0)
        nav_frame.pack(fill="x", padx=10)
        for name in ["Dashboard", "Portfolio", "Market", "Settings"]:
            btn = ctk.CTkButton(
                nav_frame,
                text=name,
                width=160,
                height=38,
                corner_radius=8,
                fg_color=btn_color,
                hover_color=btn_hover,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(pady=6)

        # spacer
        ctk.CTkFrame(self.sidebar, height=20, fg_color=sidebar_color).pack(fill="x")

        # Start Trading button at bottom
        self.start_btn = ctk.CTkButton(
            self.sidebar,
            text="⭢ Trade Now",
            width=160,
            height=40,
            corner_radius=8,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.start_trading
        )
        self.start_btn.pack(side="bottom", pady=30)

    def _create_header(self):
        header_bg = "#23252c"
        self.header = ctk.CTkFrame(self, height=60, fg_color=header_bg)
        self.header.pack(side="top", fill="x")

        welcome_label = ctk.CTkLabel(
            self.header,
            text=(
                f"Welcome, {self.user_info['username']}!     "
                f"|     ID: {self.user_info['userID']}   "
            ),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        welcome_label.pack(side="left", padx=20)

        # Divider line
        ctk.CTkFrame(self, height=2, fg_color="#44475a").pack(fill="x")

    def _create_graph_panel(self):
        self.graph_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        self.graph_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#0f0f0f")
        self.ax.set_facecolor("#0f0f0f")

        # Axis styling shit
        self.ax.set_xlabel("Time", color='gray', fontsize=14)
        self.ax.set_ylabel("Price", color='gray', fontsize=14)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.ax.tick_params(axis='y', colors='gray', labelsize=12)

        # Initial line shit
        self.line, = self.ax.plot([], [], color="#00FF00", linewidth=2)

        # Canvas making
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Price tag placeholder
        self.price_tag = None

    def update_graph(self):
        # add new data point
        self.generator.add_next()
        y = np.array(self.generator.prices)
        x = np.array([t.strftime("%H:%M:%S") for t in self.generator.timestamps])

        self.line.set_data(np.arange(len(x)), y)
        # adjust ticks
        step = max(1, len(x)//10)
        self.ax.set_xticks(np.arange(len(x))[::step])
        self.ax.set_xticklabels(x[::step], rotation=45, ha='right')

        # set limits
        self.ax.set_xlim(0, len(x))
        self.ax.set_ylim(min(y) * 0.95, max(y) * 1.05)

        # color by trend
        if len(y) > 1:
            color = "#00FF00" if y[-1] >= y[-2] else "#FF0000"
            self.line.set_color(color)

        # title
        self.ax.set_title(
            f"Balance: ${y[-1]:.2f}",
            color='white', fontsize=14, pad=12
        )

        # annotation of latest price
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

        self.canvas.draw()
        self.after(1000, self.update_graph)

    def start_trading(self):
        # music setup
        musicPlayer = DJ.MusicPlayer()
        musicPlayer.set_mood("crazy")
        musicPlayer.play_random_song()
        
        #call stock manager
        stock_manager.main()

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
            width=300,
            height=40
        )
        self.entry_user.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(
            self.frame,
            placeholder_text="Password",
            show="*",
            width=300,
            height=40
        )
        self.entry_pass.pack(pady=8)

        self.button_login = ctk.CTkButton(
            self.frame,
            text="Login",
            command=self.login,
            width=300,
            height=45,
            corner_radius=8
        )
        self.button_login.pack(pady=(20, 8))

        self.button_signup = ctk.CTkButton(
            self.frame,
            text="Sign Up",
            command=self.signup,
            width=300,
            height=45,
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

    def generate_user_id(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
            account_money = random.randint(1_000_000, 1_500_000)
            new_user = pd.DataFrame(
                [[username, password, user_id, account_money]],
                columns=['username', 'password', 'userID', 'accountMoney']
            )
            self.userData = pd.concat([self.userData, new_user], ignore_index=True)
            self.userData.to_csv("userData.csv", index=False)
            user_info = new_user.iloc[0].to_dict()
            self.logged_in_user = user_info
            self.label_status.configure(text=f"Signup successful!\nUser ID: {user_id}", text_color="green")
            self.after(1000, self.quit)

if __name__ == "__main__":
    print("[!] Game initialized")

    # Play calm music
    musicPlayer = DJ.MusicPlayer()
    musicPlayer.play_random_song()

    # Initialize or load user data
    if not os.path.exists("userData.csv") or os.stat("userData.csv").st_size == 0:
        userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
        userData.to_csv("userData.csv", index=False)
        print("[!] No existing user data. Creating Empty file...")
    else:
        userData = pd.read_csv("userData.csv")
        if userData.empty:
            userData = pd.DataFrame(columns=['username', 'password', 'userID', 'accountMoney'])
            userData.to_csv("userData.csv", index=False)
        print("[!] Retreiving user data...")
    

    # Run authentication 
    print("[!] Running authentication...")
    auth = UserAuth(userData)
    auth.mainloop()  # quit() brings us here
    auth.destroy()   # clean up

    # If login/signup succeeded, launch main app with user info
    if auth.logged_in_user:
        app = MainApp(auth.logged_in_user)
        app.mainloop()
    else:
        print("No user authenticated. Exiting.")