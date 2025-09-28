import asyncio
import websockets
import json

async def run():
    uri = "wss://pumpportal.fun/api/data"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        # можно также подписаться на другие каналы
        # await ws.send(json.dumps({"method": "subscribeTokenTrade", "keys": ["TOKEN_MINT_ADDRESS"]}))
        async for msg in ws:
            data = json.loads(msg)
            print("New event:", data)


if __name__ == '__main__':
    asyncio.run(run())