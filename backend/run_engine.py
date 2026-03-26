import time
from market_engine import MarketEngine
from candle_engine import CandleEngine
from state import state


engine = MarketEngine()
candle_engine = CandleEngine()


while True:

    engine.generate_tick()
    candle_engine.update()

    print("\nLive Prices:")
    for k, v in state.stock_prices.items():
        print(k, round(v, 2))

    print("Candles formed:")
    for k in state.candle_data:
        print(k, len(state.candle_data[k]))

    time.sleep(1)