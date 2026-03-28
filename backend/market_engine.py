import numpy as np
from datetime import datetime


class MarketEngine:

    def __init__(self, state, event_engine):
        self.state = state
        self.event_engine = event_engine

        # GBM parameters
        self.mu = 0.0001
        self.sigma = 0.01
        self.dt = 1

    def generate_tick(self, candle_engine):

        state = self.state

        # -------- GLOBAL NOISE --------
        market_noise = np.random.normal()

        sector_noise = {
            "IT": np.random.normal(),
            "BANK": np.random.normal(),
            "AUTO": np.random.normal()
        }

        # -------- LOOP OVER STOCKS --------
        for stock in state.stock_prices:

            # ✅ CORRECT: use SAME event engine everywhere
            drift_adj, vol_adj, volume_adj = self.event_engine.get_effect(stock)

            price = state.stock_prices[stock]

            # -------- NOISE --------
            individual_noise = np.random.normal()

            noise = (
                0.4 * market_noise +
                0.4 * sector_noise[state.sector_map[stock]] +
                0.2 * individual_noise
            )

            # -------- DRIFT & VOL --------
            mu_eff = self.mu + drift_adj
            sigma_eff = self.sigma + vol_adj

            # -------- PRICE UPDATE (GBM) --------
            new_price = price * np.exp(
                (mu_eff - 0.5 * sigma_eff**2) * self.dt +
                sigma_eff * np.sqrt(self.dt) * noise
            )

            # -------- VOLUME --------
            volume = int(
                state.base_volume[stock] *
                (1 + np.random.uniform(-0.25, 0.25) + volume_adj)
            )

            # -------- UPDATE STATE --------
            state.stock_prices[stock] = new_price

            state.tick_data.append({
                "time": datetime.now(),
                "stock": stock,
                "price": new_price,
                "volume": volume
            })

            # -------- UPDATE CANDLE --------
            candle_engine.update(stock, new_price, volume)