import numpy as np
from datetime import datetime


class MarketEngine:

    def __init__(self, state, event_engine):
        self.state = state
        self.event_engine = event_engine

        # FIX 1: remove positive drift bias
        self.mu = 0.0
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

            drift_adj, vol_adj, volume_adj = self.event_engine.get_effect(stock)

            price = state.stock_prices[stock]

            # -------- NOISE --------
            individual_noise = np.random.normal()

            noise = (
                0.4 * market_noise +
                0.4 * sector_noise[state.sector_map[stock]] +
                0.2 * individual_noise
            )

            # -------- MEAN REVERSION (CRITICAL FIX) --------
            base_price = state.base_prices[stock]
            reversion = -0.001 * (price - base_price) / base_price

            # -------- DRIFT & VOL --------
            mu_eff = self.mu + drift_adj + reversion
            sigma_eff = self.sigma + vol_adj

            # -------- GBM CHANGE --------
            change = (
                (mu_eff - 0.5 * sigma_eff**2) * self.dt +
                sigma_eff * np.sqrt(self.dt) * noise
            )

            # -------- CLAMP EXTREME MOVES (CRITICAL FIX) --------
            change = np.clip(change, -0.02, 0.02)

            new_price = price * (1 + change)

            # -------- SAFETY: prevent zero/negative --------
            new_price = max(new_price, 1)

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
            candle_engine.process_tick(stock, new_price, volume)