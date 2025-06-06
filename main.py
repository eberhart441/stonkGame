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
import subprocess
import sys
import platform

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
        
        # Portfolio tracking
        self.portfolio = {}  # {ticker: {'shares': int, 'avg_cost': float}}
        self.available_stocks = {}  # {ticker: {'name': str, 'price': float}}
        self.cash_balance = float(self.user_info['accountMoney'])
        self.is_trading_active = False

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
            self.is_trading_active = True
        if not hasattr(self, 'processB') or not self.processB.is_alive():
            self.processB = Process(target=self._ad_target)
            self.processB.start()

        self.start_btn.configure(state="disabled", text="\u2b62 Trading in progress...")
        self.trading_end_time = datetime.now().timestamp() + (CONSTANTS.MARKET_OPEN / 1000)
        self.after(CONSTANTS.MARKET_OPEN, self.end_trading_process)

    def end_trading_process(self):
        # Sell all positions before closing
        self.sell_all_positions()
        
        # Terminate processes FIRST to stop spawning new windows
        if hasattr(self, 'processA') and self.processA.is_alive():
            print("[!] Terminating stock manager process...")
            self.processA.terminate()
            self.processA.join(timeout=2)
            if self.processA.is_alive():
                print("[!] Force killing stock manager process")
                self.processA.kill()
                
        if hasattr(self, 'processB') and self.processB.is_alive():
            print("[!] Terminating ad manager process...")
            self.processB.terminate()
            self.processB.join(timeout=2)
            if self.processB.is_alive():
                print("[!] Force killing ad manager process")
                self.processB.kill()
        
        # Now close all windows using a more aggressive approach
        import subprocess
        import sys
        import platform
        
        print("[!] Closing all popup windows...")
        
        # Platform-specific window closing
        if platform.system() == "Windows":
            # Kill all python processes that are stock_window.py or ad_window.py
            try:
                # Get the current process ID to avoid killing ourselves
                current_pid = os.getpid()
                
                # Use taskkill to close windows by window title patterns
                subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq Stock Tracker*"], 
                             capture_output=True, shell=True)
                subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq Random Ad*"], 
                             capture_output=True, shell=True)
                
                # Also try to kill by process name if they're still running
                result = subprocess.run(["wmic", "process", "where", 
                                       f"name='python.exe' and processid!={current_pid}", 
                                       "get", "processid,commandline"], 
                                       capture_output=True, text=True, shell=True)
                
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line and ('stock_window.py' in line or 'ad_window.py' in line):
                        parts = line.split()
                        if parts:
                            pid = parts[-1]
                            if pid.isdigit() and int(pid) != current_pid:
                                subprocess.run(["taskkill", "/F", "/PID", pid], 
                                             capture_output=True, shell=True)
            except Exception as e:
                print(f"[!] Error closing windows on Windows: {e}")
                
        else:  # Unix-like systems (Linux, macOS)
            try:
                # Kill all python processes running stock_window.py or ad_window.py
                current_pid = os.getpid()
                
                # Find and kill stock windows
                result = subprocess.run(["pgrep", "-f", "stock_window.py"], 
                                      capture_output=True, text=True)
                for pid in result.stdout.strip().split('\n'):
                    if pid and pid.isdigit() and int(pid) != current_pid:
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                
                # Find and kill ad windows
                result = subprocess.run(["pgrep", "-f", "ad_window.py"], 
                                      capture_output=True, text=True)
                for pid in result.stdout.strip().split('\n'):
                    if pid and pid.isdigit() and int(pid) != current_pid:
                        subprocess.run(["kill", "-9", pid], capture_output=True)
                        
            except Exception as e:
                print(f"[!] Error closing windows on Unix: {e}")
        
        self.is_trading_active = False
        self.available_stocks.clear()
        
        # Update the market orders display to show no stocks available
        if self.active_panel == "Market Orders":
            self.update_market_orders_display()
            
        self.start_btn.configure(state="normal", text="\u2b62 Trade Now")
        musicPlayer.set_mood("calm")
        musicPlayer.play_random_song()

    def sell_all_positions(self):
        """Sell all positions at current market prices"""
        if not self.portfolio:
            return
            
        total_proceeds = 0
        for ticker, holding in list(self.portfolio.items()):
            if ticker in self.available_stocks:
                current_price = self.available_stocks[ticker]['price']
                proceeds = holding['shares'] * current_price
                total_proceeds += proceeds
                print(f"[!] Auto-sold {holding['shares']} shares of {ticker} at ${current_price:.2f} for ${proceeds:.2f}")
        
        self.portfolio.clear()
        self.cash_balance += total_proceeds
        print(f"[!] All positions closed. Total proceeds: ${total_proceeds:.2f}")

    def buy_stock(self, ticker, shares):
        """Execute a buy order"""
        if ticker not in self.available_stocks:
            return False, "Stock not available"
        
        price = self.available_stocks[ticker]['price']
        total_cost = price * shares
        
        if total_cost > self.cash_balance:
            return False, "Insufficient funds"
        
        # Update cash balance
        self.cash_balance -= total_cost
        
        # Update portfolio
        if ticker in self.portfolio:
            # Calculate new average cost
            old_shares = self.portfolio[ticker]['shares']
            old_cost = self.portfolio[ticker]['avg_cost']
            new_shares = old_shares + shares
            new_avg_cost = ((old_shares * old_cost) + (shares * price)) / new_shares
            
            self.portfolio[ticker]['shares'] = new_shares
            self.portfolio[ticker]['avg_cost'] = new_avg_cost
        else:
            self.portfolio[ticker] = {
                'shares': shares,
                'avg_cost': price
            }
        
        # Update generator to reflect new total value
        self.update_generator_price()
        
        return True, f"Bought {shares} shares of {ticker} at ${price:.2f}"

    def sell_stock(self, ticker, shares):
        """Execute a sell order"""
        if ticker not in self.portfolio:
            return False, "You don't own this stock"
        
        if ticker not in self.available_stocks:
            return False, "Cannot get current price"
            
        if shares > self.portfolio[ticker]['shares']:
            return False, "Insufficient shares"
        
        price = self.available_stocks[ticker]['price']
        proceeds = price * shares
        
        # Update cash balance
        self.cash_balance += proceeds
        
        # Update portfolio
        self.portfolio[ticker]['shares'] -= shares
        if self.portfolio[ticker]['shares'] == 0:
            del self.portfolio[ticker]
        
        # Update generator to reflect new total value
        self.update_generator_price()
        
        return True, f"Sold {shares} shares of {ticker} at ${price:.2f}"

    def update_generator_price(self):
        """Update the generator price to reflect total account value"""
        total_value = self.cash_balance
        
        # Add portfolio value
        for ticker, holding in self.portfolio.items():
            if ticker in self.available_stocks:
                total_value += holding['shares'] * self.available_stocks[ticker]['price']
        
        # Update the generator's latest price
        if len(self.generator.prices) > 0:
            self.generator.prices[-1] = total_value

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
        
        # Add countdown timer label
        self.countdown_label = ctk.CTkLabel(self.header,
                                          text="",
                                          font=ctk.CTkFont(size=16, weight="bold"),
                                          text_color="#FF5555")
        self.countdown_label.pack(side="right", padx=20)
        
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
            self.portfolio_frame.pack(fill="both", expand=True, padx=15, pady=15)
            self.update_portfolio_table()
        elif panel_name == "Market Orders":
            self.market_orders_frame.pack(fill="both", expand=True, padx=15, pady=15)
            self.update_market_orders_display()
        elif panel_name == "Settings":
            self.settings_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.active_panel = panel_name
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
        self.balance_ax.set_ylabel("Account Value", color='gray', fontsize=14)
        self.balance_ax.spines["top"].set_visible(False)
        self.balance_ax.spines["right"].set_visible(False)
        self.balance_ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.balance_ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.balance_ax.tick_params(axis='y', colors='gray', labelsize=12)
        
        # Initialize the line plot
        self.line, = self.balance_ax.plot([], [], color="#00FF00", linewidth=2)
        
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
        self.balance_ax.set_ylabel("Account Value", color='gray', fontsize=14)
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
            
            # Update title with cash and total
            portfolio_value = sum(h['shares'] * self.available_stocks.get(t, {}).get('price', 0) 
                                for t, h in self.portfolio.items())
            total_value = self.cash_balance + portfolio_value
            self.balance_ax.set_title(
                f"Total: ${total_value:,.2f} (Cash: ${self.cash_balance:,.2f}, Stocks: ${portfolio_value:,.2f})", 
                color='white', fontsize=14, pad=12
            )
            
            # Update price tag
            if self.price_tag:
                self.price_tag.remove()
            self.price_tag = self.balance_ax.annotate(
                f"${y[-1]:,.2f}",
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

        cols = ("Ticker", "Shares", "Avg Cost", "Current", "Value", "P/L", "P/L %")
        self.portfolio_tree = ttk.Treeview(self.portfolio_frame,
                                 columns=cols,
                                 show="headings",
                                 selectmode="browse")
        for c in cols:
            self.portfolio_tree.heading(c, text=c)
            self.portfolio_tree.column(c, anchor="center", width=100)
        self.portfolio_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Sell controls
        sell_frame = ctk.CTkFrame(self.portfolio_frame, fg_color="#2a2a2a")
        sell_frame.pack(fill="x", padx=10, pady=(0,10))
        
        ctk.CTkLabel(sell_frame, text="Sell Shares:").pack(side="left", padx=5)
        self.sell_shares_entry = ctk.CTkEntry(sell_frame, width=80, placeholder_text="Shares")
        self.sell_shares_entry.pack(side="left", padx=5)
        
        self.sell_btn = ctk.CTkButton(sell_frame, text="Sell Selected", width=100,
                                      command=self.execute_sell_order)
        self.sell_btn.pack(side="left", padx=5)
        
        self.sell_status_label = ctk.CTkLabel(sell_frame, text="", text_color="gray")
        self.sell_status_label.pack(side="left", padx=10)

        # Total footer
        self.portfolio_total_label = ctk.CTkLabel(self.portfolio_frame,
                                        text="Total Value: $0.00",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.portfolio_total_label.pack(pady=(0,10))

    def _create_market_orders_panel(self):
        self.market_orders_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        
        # Available stocks display
        stocks_label = ctk.CTkLabel(self.market_orders_frame, 
                                   text="Available Stocks", 
                                   font=ctk.CTkFont(size=16, weight="bold"))
        stocks_label.pack(pady=(10,5))
        
        # Treeview for available stocks
        style = ttk.Style(self)
        style.configure("Market.Treeview",
                        background="#1f1f28",
                        fieldbackground="#1f1f28",
                        foreground="white",
                        rowheight=25)
        
        cols = ("Ticker", "Company", "Price")
        self.market_tree = ttk.Treeview(self.market_orders_frame,
                                       columns=cols,
                                       show="headings",
                                       selectmode="browse",
                                       style="Market.Treeview",
                                       height=10)
        for c in cols:
            self.market_tree.heading(c, text=c)
            if c == "Company":
                self.market_tree.column(c, anchor="w", width=300)
            else:
                self.market_tree.column(c, anchor="center", width=100)
        self.market_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Order entry frame
        order_frame = ctk.CTkFrame(self.market_orders_frame, fg_color="#2a2a2a")
        order_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(order_frame, text="Buy Order:").pack(side="left", padx=5)
        
        self.shares_entry = ctk.CTkEntry(order_frame, width=80, placeholder_text="Shares")
        self.shares_entry.pack(side="left", padx=5)
        
        self.buy_btn = ctk.CTkButton(order_frame, text="Buy Selected", width=100,
                                     command=self.execute_buy_order)
        self.buy_btn.pack(side="left", padx=5)
        
        self.order_status_label = ctk.CTkLabel(order_frame, text="", text_color="gray")
        self.order_status_label.pack(side="left", padx=10)
        
        # Cash display
        self.cash_label = ctk.CTkLabel(self.market_orders_frame, 
                                      text=f"Available Cash: ${self.cash_balance:,.2f}",
                                      font=ctk.CTkFont(size=14, weight="bold"))
        self.cash_label.pack(pady=(0,10))

    def _create_settings_panel(self):
        self.settings_frame = ctk.CTkFrame(self, fg_color="#1f1f28", corner_radius=8)
        ctk.CTkLabel(self.settings_frame, text="Settings options will go here", text_color="gray").pack(pady=20)

    def execute_buy_order(self):
        """Execute a buy order from the market orders panel"""
        selection = self.market_tree.selection()
        if not selection:
            self.order_status_label.configure(text="Please select a stock", text_color="red")
            return
            
        try:
            shares = int(self.shares_entry.get())
            if shares <= 0:
                raise ValueError("Shares must be positive")
        except ValueError:
            self.order_status_label.configure(text="Invalid share amount", text_color="red")
            return
        
        item = self.market_tree.item(selection[0])
        ticker = item['values'][0]
        
        success, message = self.buy_stock(ticker, shares)
        if success:
            self.order_status_label.configure(text=message, text_color="green")
            self.shares_entry.delete(0, 'end')
            self.update_market_orders_display()
        else:
            self.order_status_label.configure(text=message, text_color="red")

    def execute_sell_order(self):
        """Execute a sell order from the portfolio panel"""
        selection = self.portfolio_tree.selection()
        if not selection:
            self.sell_status_label.configure(text="Please select a position", text_color="red")
            return
            
        try:
            shares = int(self.sell_shares_entry.get())
            if shares <= 0:
                raise ValueError("Shares must be positive")
        except ValueError:
            self.sell_status_label.configure(text="Invalid share amount", text_color="red")
            return
        
        item = self.portfolio_tree.item(selection[0])
        ticker = item['values'][0]
        
        success, message = self.sell_stock(ticker, shares)
        if success:
            self.sell_status_label.configure(text=message, text_color="green")
            self.sell_shares_entry.delete(0, 'end')
            self.update_portfolio_table()
        else:
            self.sell_status_label.configure(text=message, text_color="red")

    def update_market_orders_display(self):
        """Update the market orders display with available stocks"""
        # Save current selection
        selected_items = self.market_tree.selection()
        selected_ticker = None
        if selected_items:
            item = self.market_tree.item(selected_items[0])
            selected_ticker = item['values'][0] if item['values'] else None
        
        # Clear existing items
        for item in self.market_tree.get_children():
            self.market_tree.delete(item)
        
        # Add available stocks and restore selection
        for ticker, info in sorted(self.available_stocks.items()):
            item_id = self.market_tree.insert("", "end", values=(
                ticker,
                info['name'],
                f"${info['price']:.2f}"
            ))
            
            # Restore selection if this was the selected ticker
            if ticker == selected_ticker:
                self.market_tree.selection_set(item_id)
                self.market_tree.focus(item_id)
        
        # Update cash label
        self.cash_label.configure(text=f"Available Cash: ${self.cash_balance:,.2f}")

    def update_portfolio_table(self):
        """Update the portfolio table with current holdings"""
        # Save current selection
        selected_items = self.portfolio_tree.selection()
        selected_ticker = None
        if selected_items:
            item = self.portfolio_tree.item(selected_items[0])
            selected_ticker = item['values'][0] if item['values'] else None
        
        # Clear existing items
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
        
        total_value = 0
        total_pl = 0
        
        # Add portfolio items
        for ticker, holding in sorted(self.portfolio.items()):
            shares = holding['shares']
            avg_cost = holding['avg_cost']
            
            if ticker in self.available_stocks:
                current_price = self.available_stocks[ticker]['price']
                value = shares * current_price
                pl = value - (shares * avg_cost)
                pl_pct = (pl / (shares * avg_cost)) * 100
                
                # Color based on P/L
                tag = "profit" if pl >= 0 else "loss"
                
                item_id = self.portfolio_tree.insert("", "end", values=(
                    ticker,
                    shares,
                    f"${avg_cost:.2f}",
                    f"${current_price:.2f}",
                    f"${value:,.2f}",
                    f"${pl:+,.2f}",
                    f"{pl_pct:+.1f}%"
                ), tags=(tag,))
                
                # Restore selection if this was the selected ticker
                if ticker == selected_ticker:
                    self.portfolio_tree.selection_set(item_id)
                    self.portfolio_tree.focus(item_id)
                
                total_value += value
                total_pl += pl
            else:
                # Stock not available (market might be closed)
                value = shares * avg_cost
                item_id = self.portfolio_tree.insert("", "end", values=(
                    ticker,
                    shares,
                    f"${avg_cost:.2f}",
                    "N/A",
                    f"${value:,.2f}",
                    "N/A",
                    "N/A"
                ))
                
                # Restore selection if this was the selected ticker
                if ticker == selected_ticker:
                    self.portfolio_tree.selection_set(item_id)
                    self.portfolio_tree.focus(item_id)
                
                total_value += value
        
        # Configure tags
        self.portfolio_tree.tag_configure("profit", foreground="#00FF00")
        self.portfolio_tree.tag_configure("loss", foreground="#FF0000")
        
        # Update total label
        self.portfolio_total_label.configure(
            text=f"Total Value: ${total_value:,.2f} | Total P/L: ${total_pl:+,.2f}"
        )

    def update(self):
        # Always update the generator first
        self.generator.add_next()
        
        # Update generator to reflect actual account value
        self.update_generator_price()
        
        # Update countdown timer if trading is active
        if self.is_trading_active and hasattr(self, 'trading_end_time'):
            remaining = self.trading_end_time - datetime.now().timestamp()
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                self.countdown_label.configure(text=f"⏱️ Trading ends in: {minutes:02d}:{seconds:02d}")
            else:
                self.countdown_label.configure(text="⏱️ Trading ending...")
        else:
            self.countdown_label.configure(text="")
        
        # Check for stock data from stock_manager
        if self.mainConnect.poll():
            try:
                status_list = self.mainConnect.recv()
                # Update available stocks
                for stock_info in status_list:
                    if isinstance(stock_info, dict) and stock_info.get('ticker') and stock_info.get('price'):
                        ticker = stock_info['ticker']
                        self.available_stocks[ticker] = {
                            'name': stock_info.get('name', ticker),
                            'price': float(stock_info['price'])
                        }
            except Exception as e:
                print(f"[!] Failed to receive stock data: {e}")
        
        if hasattr(self, 'active_panel'):
            if self.active_panel == "Balance":
                self._update_balance_graph()
                self.canvas.draw()
            elif self.active_panel == "Portfolio":
                self.update_portfolio_table()
            elif self.active_panel == "Market Orders":
                self.update_market_orders_display()

        # Update balance label in sidebar with total account value
        try:
            total_value = self.cash_balance
            for ticker, holding in self.portfolio.items():
                if ticker in self.available_stocks:
                    total_value += holding['shares'] * self.available_stocks[ticker]['price']
            
            self.balance_label.configure(text=f"${int(total_value):,}")
            self.user_info['accountMoney'] = int(total_value)
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