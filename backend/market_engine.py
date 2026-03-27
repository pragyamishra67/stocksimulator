from event_engine import EventEngine

event_engine = EventEngine()

import numpy as np
from datetime import datetime
from state import state


class MarketEngine:

    def __init__(self):

        self.mu = 0.0001
        self.sigma = 0.01
        self.dt = 1

    def generate_tick(self):

        market_noise = np.random.normal()

        sector_noise = {
            "IT": np.random.normal(),
            "BANK": np.random.normal(),
            "AUTO": np.random.normal()
        }

        for stock in state.stock_prices:
            drift_adj, vol_adj, volume_adj = event_engine.get_effect(stock)

            price = state.stock_prices[stock]

            individual_noise = np.random.normal()

            noise = (
                0.4 * market_noise +
                0.4 * sector_noise[state.sector_map[stock]] +
                0.2 * individual_noise
            )

            mu_eff = self.mu + drift_adj
            sigma_eff = self.sigma + vol_adj

            new_price = price * np.exp(
                (mu_eff - 0.5 * sigma_eff**2) * self.dt +
                   sigma_eff * np.sqrt(self.dt) * noise
            )
            volume = int(
                        state.base_volume[stock] *
                        (1 + np.random.uniform(-0.25, 0.25) + volume_adj)
                        )

            state.stock_prices[stock] = new_price

            state.tick_data.append({
                "time": datetime.now(),
                "stock": stock,
                "price": new_price,
                "volume": volume
            })