import codecs
import jinja2
import secrets
from deta import Deta
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.db = Deta().Drive("imageio")
pages = Jinja2Templates(directory="static")

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
    app.db.put(f"{code}_{name}", codecs.decode(image_data, "base64"), content_type="application/octet-stream")
    return JSONResponse({"status": "ok", "hash": f"{code}_{name}"})


@app.get("/{name}")
async def file(name: str):
    buffer = app.db.get(name)
    return Response(content=buffer.read(), media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app")
