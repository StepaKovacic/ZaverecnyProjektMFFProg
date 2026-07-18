from dbHandler import session
from models import User, Invoice, Item
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from uvicorn import run
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

App = FastAPI()
App.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@App.get("/", response_class = HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request = request, name="index.html")

