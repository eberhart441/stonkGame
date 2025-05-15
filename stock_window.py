import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from collections import deque

firstName = ["Alpha ", "King ", "Infinite ", "Cash ", "American ", "Eagle ", "Sigma ", "Holy ", "Patriot ", "Fresh ", "Giga ", "Super ", "Royal ", "Web3 ", "Bob's", "Uncle Joe's ", "Mommy's ", "Daddy's ", "Cyber "]
secondName = ["Defense ", "Markets ", "Coffee ", "Burgers ", "Auto ", "Brokerage ", "Realestate ", "Banking ", "Electroncs ", "Technology ", "News ", "Food ", "Farming ", "Fishing ", "Bands ", "Crypto ", "Bitcoin ", "NFT ", "AI ", "Cybersecurity "]
thirdName = ["Trust", "LLC", "Enterprise", ".Co", "Incorporated.", "Corp", ".Inc", "Conglomerate", "United", "Company", "Buisness", ".Ltd"]

class StockGenerator:
    def __init__(
        self,
        start_price: float = 100.0,
        drift: float = 0.01,
        mean_price: float = 100.0,
        mean_reversion_strength: float = 0.1,
        volatility: float = 1.0,
        dt: float = 1.0,
        maxlen: int = 250
    ):
        self.drift = drift
        self.mean_price = mean_price
        self.mean_reversion_strength = mean_reversion_strength
        self.volatility = volatility
        self.dt = dt
        self.maxlen = maxlen
        self.prices = deque([start_price], maxlen=maxlen)
        self.name = (
            random.choice(firstName)
            + random.choice(secondName)
            + random.choice(thirdName)
        )

    def generate_stock_series(self, length: int) -> list[float]:
        for _ in range(1, length):
            self.add_next()
        return list(self.prices)

    def add_next(self) -> float:
        x = self.prices[-1]
        reversion = self.mean_reversion_strength * (self.mean_price - x) * self.dt
        shock = self.volatility * np.sqrt(self.dt) * np.random.randn()
        x_new = x + self.drift * self.dt + reversion + shock
        x_new = max(x_new, 0.01)
        self.prices.append(x_new)
        return x_new

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title(f"Stock Tracker – {random.randint(1000,9999)}")

        # Randomize size and position
        width = random.randint(400, 900)
        height = random.randint(300, 700)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = random.randint(0, screen_width - width)
        y = random.randint(0, screen_height - height)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # stock generator instance with deque-based prices
        self.generator = StockGenerator(
            start_price=random.uniform(10, 300),
            drift=random.uniform(-0.02, 0.05),  # most drift slightly up or down
            mean_price=random.uniform(20, 200),
            mean_reversion_strength=random.uniform(0.02, 0.15),  # realistic range
            volatility=random.uniform(0.5, 5.0)  # still varies, but won't go FTX
        )


        self.generator.prices = deque(self.generator.generate_stock_series(250), maxlen=250)

        self._create_widgets()
        self.update_graph()
        self._ticker_loop()

    def _create_widgets(self):
        # Frame for the stock chart
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Matplotlib figure setup
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#0f0f0f")
        self.ax.set_facecolor("#0f0f0f")
        self.ax.set_title(self.generator.name, color='white', fontsize=20)
        self.ax.set_xlabel("Time", color='gray', fontsize=16)
        self.ax.set_ylabel("Price", color='gray', fontsize=16)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.ax.tick_params(axis='x', colors='gray', labelsize=12)
        self.ax.tick_params(axis='y', colors='gray', labelsize=12)

        # Plot line (empty initially), stored as self.line
        self.line, = self.ax.plot([], [], color="#00FF00", linewidth=2)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.price_tag = None  # placeholder for price annotation

    def update_graph(self):
        self.generator.add_next()
        y = np.array(self.generator.prices)
        x = np.arange(len(y))

        self.line.set_data(x, y)
        self.ax.set_xlim(0, len(y))
        self.ax.set_ylim(min(y) * 0.95, max(y) * 1.05)

        # Remove old price tag if it exists
        if self.price_tag:
            self.price_tag.remove()

        self.price_tag = self.ax.annotate(
            f"${y[-1]:.2f}",
            xy=(len(y) - 1, y[-1]),
            xytext=(10, 0),
            textcoords='offset points',
            color='white',
            fontsize=12,
            ha='left',
            va='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="black", ec="green", lw=1)
        )

        self.canvas.draw()

    def _ticker_loop(self):
        self.update_graph()
        self.after(1000, self._ticker_loop)  # run again in 1 sec


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
