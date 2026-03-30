# backend/server.py

from fastapi import FastAPI, WebSocket
import asyncio
import json
import time
import os
from dotenv import load_dotenv

# -------- LOAD ENV --------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")


# -------- IMPORT YOUR SYSTEM --------
from market_engine import MarketEngine
from candle_engine import CandleEngine
from event_engine import EventEngine
from news_engine import NewsEngine, news_to_event
from state import state


app = FastAPI()
clients = []


# -------- WEBSOCKET ENDPOINT --------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    print("Client connected")

    try:
        while True:
            await asyncio.sleep(1)
    except:
        clients.remove(ws)
        print("Client disconnected")


# -------- BROADCAST FUNCTION --------
async def broadcast(data):
    for client in clients:
        await client.send_text(json.dumps(data))


# -------- INITIALIZE SYSTEM --------
event_engine = EventEngine(state.sector_map)
engine = MarketEngine(state, event_engine)
candle_engine = CandleEngine()
news_engine = NewsEngine(API_KEY)


# -------- MAIN SIMULATION LOOP --------
@app.on_event("startup")
async def start_simulation():

    async def loop():

        last_news_time = 0

        while True:

            # -------- MARKET UPDATE --------
            engine.generate_tick(candle_engine)

            # -------- EVENT CLEANUP --------
            event_engine.cleanup()

            # -------- SEND TICK DATA --------
            for stock, price in state.stock_prices.items():
                await broadcast({
                    "type": "tick",
                    "stock": stock,
                    "price": price,
                    "time": time.time()
                })

            # -------- SEND CANDLE DATA --------
            for stock in state.stock_prices:
                if state.candle_data[stock]:
                    candle = state.candle_data[stock][-1]

                    await broadcast({
                        "type": "candle",
                        "stock": stock,
                        "open": candle["open"],
                        "high": candle["high"],
                        "low": candle["low"],
                        "close": candle["close"],
                        "volume": candle["volume"],
                        "time": time.time()
                    })

            # -------- NEWS GENERATION --------
            current_time = time.time()

            if current_time - last_news_time > 20:

                print("Generating news...")

                news = news_engine.generate_news()

                if news and news_engine.validate(news):

                    event = news_to_event(news)
                    event_engine.add_event(event)

                    await broadcast({
                        "type": "news",
                        "headline": news["headline"],
                        "target": news["target"],
                        "time": current_time
                    })

                last_news_time = time.time()

            # -------- LOOP DELAY --------
            await asyncio.sleep(1)

    asyncio.create_task(loop())