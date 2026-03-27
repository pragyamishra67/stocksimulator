import sys
import os

sys.path.append("D:/stocksimulator")

import time

from market_engine import MarketEngine
from candle_engine import CandleEngine
from state import state

from analytics.risk_engine import RiskEngine
from analytics.pattern_engine import PatternEngine

from event_engine import MarketEvent, event_engine


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

    engine.generate_tick()
    candle_engine.update()

    print("\n========== MARKET SNAPSHOT ==========")

    print("\nLive Prices:")
    for stock, price in state.stock_prices.items():
        print(stock, round(price, 2))

    # Latest volume info
    if state.tick_data:
        last = state.tick_data[-1]
        print("\nLatest Tick Volume:",
              last["stock"],
              last["volume"])

    # Candle count for ALL stocks
    print("\nCandles formed:")
    for stock in state.stock_prices:
        print(stock, len(state.candle_data[stock]))

    # ⭐ Analytics block (VERY IMPORTANT)
    print("\nAnalytics:")
    for stock in state.stock_prices:

        ratio = risk_engine.get_ratio(stock)
        pattern = pattern_engine.detect(stock)

        print(stock,
              "RiskRatio:", round(ratio, 4),
              "Pattern:", pattern)

    print("\nTotal ticks:", len(state.tick_data))

    time.sleep(1)