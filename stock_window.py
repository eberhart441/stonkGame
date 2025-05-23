import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from collections import deque
import datetime

firstName = ["Alpha ", "Amity ", "Trump ", "The Best ", "King ", "Infinite ", "Cash ", "American ", "Eagle ", "Sigma ", "Holy ", "Patriot ", "Fresh ", "Giga ", "Super ", "Royal ", "Web3 ", "Bob's ", "Uncle Joe's ", "Mommy's ", "Daddy's ", "Cyber ", "Naughty ", "Enron2 ", "Communist ", "Socialist ", "Sketchy ", "Underground "]
secondName = ["Defense ", "Markets ", "Coffee ", "Burgers ", "Auto ", "Brokerage ", "Realestate ", "Banking ", "Electroncs ", "Technology ", "News ", "Food ", "Farming ", "Fishing ", "Bands ", "Crypto ", "Bitcoin ", "NFT ", "AI ", "Cybersecurity ", "Cookie ", "Petroleum ", "Lumber ", "Security ", "Rocks ", "Corn ", "Beans ", "University "]
thirdName = ["Trust", "LLC", "Enterprise", "Co", "Incorporated.", "Corp", "Inc", "Conglomerate", "United", "Company", "Buisness", "Ltd", "Empire", "World Wide", "of America", "of China", "for sigmas", "of Russia"]

def generate_ticker_from_name(name):
    return ''.join(word[0] for word in name.split() if word[0].isalpha()).upper()

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
        self.timestamps = deque([datetime.datetime.now()], maxlen=maxlen)

        raw_name = (
            random.choice(firstName)
            + random.choice(secondName)
            + random.choice(thirdName)
        )
        self.name = raw_name.strip()
        self.ticker = generate_ticker_from_name(self.name)

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
        self.timestamps.append(datetime.datetime.now())
        return x_new

class stock_window(ctk.CTk):
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

        mean_price = random.uniform(20, 200)
        start_price = random.uniform(mean_price * 0.9, mean_price * 1.1)

        self.generator = StockGenerator(
            start_price=start_price,
            mean_price=mean_price,
            drift=random.uniform(-0.02, 0.05),
            mean_reversion_strength=random.uniform(0.02, 0.15),
            volatility=random.uniform(0.5, 5.0)
        )

        self.generator.generate_stock_series(250)

        self._create_widgets()
        self.update_graph()
        self._ticker_loop()

    def _create_widgets(self):
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.patch.set_facecolor("#0f0f0f")
        self.ax.set_facecolor("#0f0f0f")

        self.ax.set_xlabel("Time", color='gray', fontsize=16)
        self.ax.set_ylabel("Price", color='gray', fontsize=16)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
        self.ax.tick_params(axis='x', colors='gray', labelsize=10, rotation=45)
        self.ax.tick_params(axis='y', colors='gray', labelsize=12)

        self.line, = self.ax.plot([], [], color="#00FF00", linewidth=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.price_tag = None

    def update_graph(self):
        self.generator.add_next()
        y = np.array(self.generator.prices)
        x = np.array([t.strftime("%H:%M:%S") for t in self.generator.timestamps])

        self.line.set_data(np.arange(len(x)), y)
        self.ax.set_xticks(np.arange(len(x))[::max(1, len(x)//10)])
        self.ax.set_xticklabels(x[::max(1, len(x)//10)])

        self.ax.set_xlim(0, len(x))
        self.ax.set_ylim(min(y) * 0.95, max(y) * 1.05)

        color = "#00FF00" if y[-1] >= y[-2] else "#FF0000"
        self.line.set_color(color)

        self.ax.set_title(
            f"{self.generator.ticker} – {self.generator.name} – ${y[-1]:.2f}",
            color='white',
            fontsize=18
        )

        if self.price_tag:
            self.price_tag.remove()

        self.price_tag = self.ax.annotate(
            f"${y[-1]:.2f}",
            xy=(len(x) - 1, y[-1]),
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
        self.after(1000, self._ticker_loop)

if __name__ == "__main__":
    app = stock_window()
    app.mainloop()
