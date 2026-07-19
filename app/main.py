from dbHandler import session
from typing import Annotated
from sqlalchemy import select
from utils import hashed_password
from models import User, Invoice, Item
from fastapi import FastAPI, Form, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
import utils
from uvicorn import run
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


App = FastAPI()
App.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@App.get("/header")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}

@App.get("/", response_class = HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request = request, name="index.html")

@App.get("/register", response_class = HTMLResponse)
async def register_view(request: Request, user_agent: Annotated[str | None, Header()] = None):
    utils.print_red( request.headers)
    return templates.TemplateResponse(request = request, name="register.html")

@App.get("/success", response_class= HTMLResponse)
async def success(request: Request):
    return templates.TemplateResponse(request=request, name="success_register.html")

@App.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    ico: str = Form(...),
    phone: str | None = Form(default=None),
):
    existing = session.execute(
        select(User).where((User.username == username) | (User.email == email))
    ).scalar_one_or_none()

    if existing is not None:
        return RedirectResponse(
            url="/register",
            status_code=status.HTTP_303_SEE_OTHER,
            headers = {"test-1":"dsdfsdf"}
        )

    user = User(
        username=username, email=email,
        password_hash=hashed_password(password),
        first_name=first_name, last_name=last_name,
        ico=ico, phone=phone,
    )
    session.add(user)
    session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@App.get("/users/me")
def read_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    return {"username": credentials.username, "password": credentials.password, "credentails":credentials}


@App.get("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}