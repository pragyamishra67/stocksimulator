import random
from collections import defaultdict

class MarketState:

    def __init__(self):

        self.stock_prices = {
            "TCS": 3900,
            "INFY": 1600,
            "HDFCBANK": 1500,
            "MARUTI": 12500
        }

        self.sector_map = {
            "TCS": "IT",
            "INFY": "IT",
            "HDFCBANK": "BANK",
            "MARUTI": "AUTO"
        }

        self.base_volume = {
            "TCS": 2000,
            "INFY": 1800,
            "HDFCBANK": 2500,
            "MARUTI": 1500
        }

        self.tick_data = []
        self.candle_data = defaultdict(list)
        self.current_candle = {}
        self.base_prices = self.stock_prices.copy()

state = MarketState()