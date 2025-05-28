# main.py
UPDATE_CYCLE = 1000 # milliseconds
TRADE_CYCLE = 90 # seconds
SAVE_CYCLE = 30 # seconds

MIN_MONEY = 100_000
MAX_MONEY = 10_000_000

USER_DATA_FILE = "Resources/userData.csv"

# stock_manager.py
MAX_WINDOWS = 12
MIN_WINDOWS = 8
NEW_WINDOW_INTERVAL = 30  # seconds
NEW_WINDOW_PROBABILITY = 0.6  # Probability of opening a new window

# stock_window.py

# ad_manager.py
MAX_AD_WINDOWS = 6
MIN_AD_WINDOWS = 2
NEW_AD_WINDOW_INTERVAL = 20  # seconds
NEW_AD_WINDOW_PROBABILITY = 0.8  # Probability of opening a new ad window

# DJ