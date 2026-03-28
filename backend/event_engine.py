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

    # ✅ THIS IS THE IMPORTANT PART
    def update(self):

        updated_events = []

        for event in self.active_events:

            # decay impact
            event["impact"] *= event["decay"]

            # reduce duration
            event["duration"] -= 1

            # keep only active events
            if event["duration"] > 0 and abs(event["impact"]) > 0.01:
                updated_events.append(event)

        self.active_events = updated_events

event_engine = EventEngine()