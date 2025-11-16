from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import uvicorn

from routers.testRout import router as testRouter
from routers.oilPricesRouter.OilPricesRouter import oilrouter
from routers.gsmDeliveryNBCTX.gsmDeliveryRouter import gsmnbCTXrouter
from routers.gsmMegionRouter.gsmMegionRouter import gsmMegionrouter
from routers.gsmNBRouter.gsmNBRouter import gsmNBrouter
from routers.gsmOthersRouter.gsmOthersRouter import AllTransprout

from dotenv import load_dotenv
import os
#import datetime

load_dotenv()

TOKEN = os.getenv("TG_TOKEN")
SERG_NIKO = os.getenv("SERG_NIKO")
ME = os.getenv("CHAT_ID")

app = FastAPI()


app.include_router(testRouter)
app.include_router(oilrouter)
app.include_router(gsmnbCTXrouter)
app.include_router(gsmMegionrouter)
app.include_router(gsmNBrouter)
app.include_router(AllTransprout)


@app.get("/")
async def root():
    # response = ping('db-duplicate')
    # if response is None:
    #     return {"Failed to ping": {container_name}}
    # else:
    #     return {"Ping": f"{container_name}, {response}ms"}
    html = """
    <html>
    <head>
    </head>
    <body>
    <img src="https://i.imgur.com/lVlPvCB.gif"/>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


"""

@app.post("/")
async def post_root(request: Request):
    try:
        if not TOKEN or not SERG_NIKO:
            raise HTTPException(status_code=500, detail="Telegram not configured")

        data = {
            "path": str(request.url.path),
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "body": await request.json()
        }

        message = (
            f"Новый запрос:\n"
            f"Метод: {data['method']}\n"
            f"Путь: {data['path']}\n"
            f"Заголовки: {data['headers']}\n"
            f"Параметры: {data['query_params']}\n"
            f"Тело: {data['body']}"
        )
        telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        for i in (ME, SERG_NIKO):
            payload = {
                "chat_id": i,
                "text": message,
                "parse_mode": "HTML"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(telegram_url, json=payload)
                response.raise_for_status()

        return {"status": "success", "message": "Request data sent to Telegram"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

"""

"""
@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    tags=["amoCRM"],
)
async def proxy(path: str, request: Request):
    raw_body = await request.body()
    raw_text = raw_body.decode("utf-8", errors="replace")

    _response = {
        "[date]": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "[method]": request.method,
        "[content_type]": request.headers.get("content-Type", ""),
        "[content_length]": len(raw_body),
        "[raw]": raw_text,
    }
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for i in (ME, SERG_NIKO):
        payload = {
            "chat_id": i,
            "text": _response,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(telegram_url, json=payload)
            response.raise_for_status()

    return JSONResponse(content=_response)
"""

def main():
    uvicorn.run(app, host="0.0.0.0", port=8001)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
