import sys
import os

sys.path.append("D:/stocksimulator")

import time
import random

from market_engine import MarketEngine
from candle_engine import CandleEngine
from state import state

from analytics.risk_engine import RiskEngine
from analytics.pattern_engine import PatternEngine

from event_engine import MarketEvent, event_engine

from news_engine import NewsEngine, news_to_event
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

news_engine = NewsEngine(api_key)

engine = MarketEngine()
candle_engine = CandleEngine()

risk_engine = RiskEngine()
pattern_engine = PatternEngine()

test_event = MarketEvent(
    sentiment=0.8,       # strong positive
    impact=0.6,          # medium-strong impact
    duration=30,         # lasts 30 seconds
    target="IT",         # affects TCS & INFY
    volume_spike=0.5     # volume increase
)

event_engine.add_event(test_event)


while True:

    # -------- MARKET UPDATE --------
    engine.generate_tick(candle_engine)
    event_engine.update()

    print("\n========== MARKET SNAPSHOT ==========")

    print("\nLive Prices:")
    for stock, price in state.stock_prices.items():
        print(stock, round(price, 2))

    if state.tick_data:
        last = state.tick_data[-1]
        print("\nLatest Tick Volume:", last["stock"], last["volume"])

    print("\nCandles formed:")
    for stock in state.stock_prices:
        print(stock, len(state.candle_data[stock]))

    print("\nAnalytics:")
    for stock in state.stock_prices:
        ratio = risk_engine.get_ratio(stock)
        pattern = pattern_engine.detect(stock)
        print(stock, "RiskRatio:", round(ratio, 4), "Pattern:", pattern)

    # 🔥 NEWS BLOCK MUST BE HERE (INSIDE LOOP)
    print("\n--- DEBUG START ---")

    news = news_engine.generate_news()
    print("RAW NEWS:", news)

    is_valid = news_engine.validate(news)
    print("IS VALID:", is_valid)

    if is_valid:
        print("HEADLINE:", news.get("headline"))
        event = news_to_event(news)
        event_engine.add_event(event)
    else:
        print("❌ FAILED VALIDATION")

    print("--- DEBUG END ---")

    time.sleep(1)