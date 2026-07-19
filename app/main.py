from dbHandler import session_db
# TA SESSION JE TROHCU PRASARNA 
from typing import Annotated
from sqlalchemy import select
from utils import hashed_password
from models import User, Invoice, Item
from fastapi import FastAPI, Form, status, Header, Cookie
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

from authHandling import  create_session, get_user_id_from_session, delete_session

security = HTTPBasic()


App = FastAPI()
App.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@App.get("/header")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}

@App.get("/", response_class = HTMLResponse)
async def index(request: Request, session_token: str | None = Cookie(default=None)):
    # pokud existuje token 
    if session_token:
        user_id = get_user_id_from_session(token=session_token)
        print(user_id)

        user_info = session_db.query(User).filter(User.id == user_id).one_or_none()
        print(user_info.first_name)
    return templates.TemplateResponse(request = request, name="index.html", context={"username":user_id})

@App.get("/register", response_class = HTMLResponse)
async def register_view(request: Request, user_agent: Annotated[str | None, Header()] = None):
    utils.print_red( request.headers)
    return templates.TemplateResponse(request = request, name="register.html")

@App.get("/success", response_class= HTMLResponse)
async def success(request: Request):
    return templates.TemplateResponse(request=request, name="success_register.html")

# def get_db():
#     pass
@App.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    # session depends na db
    first_name: str = Form(...),
    last_name: str = Form(...),
    ico: str = Form(...),
    phone: str | None = Form(default=None),
):


    # TODO:  PREDELAT PRES SQLACLECHY EXC INTEGRITY ERROR S TIM ZE UZ V MODELECH MAM UNIQUE=TREU
    existing_mail = session_db.execute(
        select(User).where(User.email == email)).scalar_one_or_none()

    existing_username = session.execute(
        select(User).where(User.username == username)).scalar_one_or_none()

    if existing_mail is not None:
        return templates.TemplateResponse(request = request, name="register.html", context={"problem":"email"})

    if existing_username is not None:
        return templates.TemplateResponse(request = request, name="register.html", context={"problem":"username"})
    

    user = User(
        username=username, email=email,
        password_hash=hashed_password(password),
        first_name=first_name, last_name=last_name,
        ico=ico, phone=phone,
    )
    session_db.add(user)
    session_db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@App.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse(request=request, name="login.html", context={"error":error})

@App.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    user = session_db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
 
    utils.print_red("dostali jsem se na post login")
    if user is None: # s tim ze se hashe rovnaji 
        return RedirectResponse(
            url="/login?error=Nesprávné+jméno+nebo+heslo",
            status_code=status.HTTP_303_SEE_OTHER,
        )
 
    token = create_session(user.id)
    redirect = RedirectResponse(url="/success", status_code=status.HTTP_303_SEE_OTHER)
    redirect.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  
        max_age=60 * 60 * 24 * 7,
    )
    print(f"logged in as {username}")
    return redirect
 
 
@App.post("/logout")
async def logout(session_token: str | None = Cookie(default=None)):
    if session_token:
        delete_session(session_token)
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie("session_token")
    return redirect