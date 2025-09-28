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



from rugcheck import rugcheck

if __name__ == '__main__':
    token = '6YLjbpxyXRumYC13gTfdLjXKMg2H6QmmyakHBJyDpump'
    rc = rugcheck(token)
    print(f'rc: {rc.to_json()}')
    # asyncio.run(run())