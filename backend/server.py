from fastapi import FastAPI, WebSocket
import asyncio
import json

app = FastAPI()
clients = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)

    try:
        while True:
            await asyncio.sleep(1)
    except:
        clients.remove(ws)

async def broadcast(data):
    for client in clients:
        await client.send_text(json.dumps(data))

# Test loop
@app.on_event("startup")
async def start_simulation():

    async def loop():
        while True:
            test_data = {
                "type": "test",
                "value": 123,
                "time": asyncio.get_event_loop().time()
            }

            await broadcast(test_data)

            print("Broadcasting:", test_data)

            await asyncio.sleep(1)

    asyncio.create_task(loop())