import google.generativeai as genai
import json
import re
import time


class NewsEngine:

    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("geminipro")

    # -------- MAIN FUNCTION --------
    def generate_news(self):

        prompt = """
        Generate a realistic financial market news event.

        STRICT RULES:
        - Output ONLY valid JSON
        - No explanation
        - No markdown
        - No extra text

        JSON FORMAT:
        {
          "headline": string,
          "sentiment": float between -1 and 1,
          "impact": float between 0 and 1,
          "target": one of ["IT", "BANK", "AUTO"],
          "duration": integer between 20 and 60,
          "volume_spike": float between 0 and 1
        }
        """

        for attempt in range(3):  # retry 3 times
            try:
                response = self.model.generate_content(prompt)
                raw_text = response.text.strip()
                return self._safe_parse(raw_text)

            except Exception as e:
                print(f"⚠️ Gemini error (attempt {attempt+1}):", e)
                time.sleep(1)

        return None

    # -------- SAFE PARSING --------
    def _safe_parse(self, text):

        # Try direct JSON
        try:
            return json.loads(text)
        except:
            pass

        # Try extracting JSON block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None

        return None

    # -------- VALIDATION --------
    def validate(self, data):

        if not data:
            return False

        required_keys = [
            "headline",
            "sentiment",
            "impact",
            "target",
            "duration",
            "volume_spike"
        ]

        # Check keys
        for key in required_keys:
            if key not in data:
                return False

        # Type checks
        if not isinstance(data["sentiment"], (int, float)):
            return False

        if not isinstance(data["impact"], (int, float)):
            return False

        if not isinstance(data["duration"], int):
            return False

        if not isinstance(data["volume_spike"], (int, float)):
            return False

        # Range checks
        if not -1 <= data["sentiment"] <= 1:
            return False

        if not 0 <= data["impact"] <= 1:
            return False

        if not 0 <= data["volume_spike"] <= 1:
            return False

        if not 20 <= data["duration"] <= 60:
            return False

        # Target check
        if data["target"] not in ["IT", "BANK", "AUTO"]:
            return False

        return True


# -------- CONVERTER FUNCTION --------
from event_engine import MarketEvent


def news_to_event(news):
    scaled_impact = news["impact"] * 2
    scaled_impact = min(scaled_impact, 1)

    return MarketEvent(
        sentiment=news["sentiment"],
        impact=scaled_impact,
        duration=news["duration"],
        target=news["target"],
        volume_spike=news["volume_spike"]
    )