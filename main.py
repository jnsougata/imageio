import codecs
import jinja2
import secrets
import asyncio
from deta import Deta
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, JSONResponse



app = FastAPI()
app.base = Deta().Base("imageio")
app.drive = Deta().Drive("imageio")
pages = Jinja2Templates(directory="static")


def wrap_drive_put(name, data):
    return app.drive.put(name, data, content_type="application/octet-stream")

def wrap_base_put(key, value):
    return app.base.put(value, key, expire_in=60*60*24*7)


class ContentResponse(Response):
    def __init__(self, path: str, **kwargs):
        with open(path, "rb") as f:
            content = f.read()
        super().__init__(content=content, **kwargs)


@app.get("/")
async def index(request: Request):
    return pages.TemplateResponse("index.html", {"request": request})

@app.get("/assets/{name}")
async def file(name: str):
    return ContentResponse(f"./assets/{name}", media_type="application/octet-stream")

@app.get("/scripts/{name}")
async def file(name: str):
    return ContentResponse(f"./scripts/{name}", media_type="text/javascript")

@app.get("/styles/{name}")
async def file(name: str):
    return ContentResponse(f"./styles/{name}", media_type="text/css")

@app.post("/upload/{name}")
async def save(request: Request, name: str):
    code = secrets.token_hex(8)
    data = await request.json()
    image_data = data["data"].split(",")[1].encode("utf-8")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, wrap_base_put, code, name)
    await loop.run_in_executor(None, wrap_drive_put, f"{code}_{name}", codecs.decode(image_data, "base64"))
    return JSONResponse({"status": "ok", "hash": f"{code}_{name}"})

    
@app.get("/{filename}")
async def file(filename: str):

    if "_" not in filename:
        return Response(status_code=404, content="Image Expired", media_type="text/plain")
    
    code, _ = filename.split("_")
    item = app.base.get(code)
    if not item:
        try:
            app.drive.delete(filename)
        finally:
            return Response(status_code=404, content="Image Expired", media_type="text/plain")

    buff = app.drive.get(filename)
    if not buff:
        return Response(status_code=404, content="Not Found", media_type="text/plain")
    return Response(content=buff.read(), media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
