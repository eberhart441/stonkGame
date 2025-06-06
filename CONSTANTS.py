# main.py
UPDATE_CYCLE = 1000 # milliseconds
TRADE_CYCLE = 90 # seconds
SAVE_CYCLE = 30 # seconds
MARKET_OPEN = 90_000 # milliseconds

MIN_MONEY = 1_000_000
MAX_MONEY = 10_000_000

USER_DATA_FILE = "Resources/userData.csv"

# stock_manager.py
MAX_WINDOWS = 5
MIN_WINDOWS = 3
NEW_WINDOW_INTERVAL = 30  # seconds
NEW_WINDOW_PROBABILITY = 0.6  # Probability of opening a new window

# stock_window.py

# ad_manager.py
MAX_AD_WINDOWS = 2
MIN_AD_WINDOWS = 1
NEW_AD_WINDOW_INTERVAL = 20  # seconds
NEW_AD_WINDOW_PROBABILITY = 0.7  # Probability of opening a new ad window

# DJ