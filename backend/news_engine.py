import time
import json
import re
from google import genai
from event_engine import MarketEvent   # ✅ ADD THIS


class NewsEngine:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    # -------- MAIN FUNCTION --------
    def generate_news(self):

        prompt = self._build_prompt()

        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                raw_text = (response.text or "").strip()

                if not raw_text:
                    print("⚠️ Empty response from Gemini")
                    return None

                parsed = self._safe_parse(raw_text)

                if self.validate(parsed):
                    return parsed
                else:
                    print("⚠️ Invalid structure from Gemini")
                    return None

            except Exception as e:
                print(f"⚠️ Gemini error (attempt {attempt+1}):", e)

                if "429" in str(e):
                    print("⚠️ Rate limit caught! Aborting retry to maintain cadence.")
                    return None
                else:
                    time.sleep(1)

        return None

    # -------- PROMPT --------
    def _build_prompt(self):
        return """
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

    # -------- SAFE PARSE --------
    def _safe_parse(self, text):

        try:
            return json.loads(text)
        except:
            pass

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

        if "headline" not in data or "sentiment" not in data or "target" not in data:
            return False

        data.setdefault("impact", 0.3)
        data.setdefault("duration", 30)
        data.setdefault("volume_spike", 0.2)

        return True


# -------- CONVERTER (FIXED) --------
def news_to_event(news):

    # ✅ Clamp values (VERY IMPORTANT)
    sentiment = max(min(news.get("sentiment", 0), 1), -1)
    impact = min(max(news.get("impact", 0.3), 0), 1)
    duration = max(5, news.get("duration", 30))
    volume_spike = min(max(news.get("volume_spike", 0.2), 0), 1)

    # ✅ RETURN OBJECT, NOT DICT
    return MarketEvent(
        sentiment=sentiment,
        impact=impact,
        duration=duration,
        target=news.get("target", "IT"),
        volume_spike=volume_spike
    )