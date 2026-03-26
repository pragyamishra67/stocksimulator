from state import state


class CandleEngine:

    def __init__(self):
        self.tick_counter = {s: 0 for s in state.stock_prices}
        self.candle_size = 10

    def update(self):

        if not state.tick_data:
            return

        tick = state.tick_data[-1]

        stock = tick["stock"]
        price = tick["price"]
        volume = tick["volume"]

        if stock not in state.current_candle:

            state.current_candle[stock] = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume
            }

        else:

            candle = state.current_candle[stock]

            candle["high"] = max(candle["high"], price)
            candle["low"] = min(candle["low"], price)
            candle["close"] = price
            candle["volume"] += volume

        self.tick_counter[stock] += 1

        if self.tick_counter[stock] >= self.candle_size:

            state.candle_data[stock].append(
                state.current_candle[stock]
            )

            del state.current_candle[stock]
            self.tick_counter[stock] = 0