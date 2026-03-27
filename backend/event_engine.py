import time
import math
from state import state


class MarketEvent:

    def __init__(self, sentiment, impact, duration, target, volume_spike):

        self.sentiment = sentiment        # -1 to +1
        self.impact = impact              # 0 to 1
        self.duration = duration          # seconds
        self.target = target              # stock or sector
        self.volume_spike = volume_spike

        self.start_time = time.time()

    def decay_factor(self):

        elapsed = time.time() - self.start_time
        return math.exp(-elapsed / self.duration)


class EventEngine:

    def __init__(self):
        self.active_events = []

    def add_event(self, event):
        self.active_events.append(event)

    def get_effect(self, stock):

        drift_adj = 0
        vol_adj = 0
        volume_adj = 0

        for event in self.active_events:

            decay = event.decay_factor()

            # remove dead events
            if decay < 0.05:
                continue

            if event.target == stock or state.sector_map.get(stock) == event.target:

                drift_adj += event.sentiment * event.impact * decay
                vol_adj += event.impact * decay
                volume_adj += event.volume_spike * decay

        return drift_adj, vol_adj, volume_adj
event_engine = EventEngine()