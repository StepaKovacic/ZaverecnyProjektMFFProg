from dbHandler import session_db
# TA SESSION JE TROHCU PRASARNA 
from typing import Annotated
from sqlalchemy import select
from utils import hashed_password
from models import User, Invoice, Item, Tag
from fastapi import FastAPI, Form, status, Header, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
import utils
from pathlib import Path
from uvicorn import run
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import HTTPException, UploadFile
from authHandling import  create_session, get_user_id_from_session, delete_session
from datetime import date



def required_login(session_token: str | None = Cookie(default=None)) -> User:
    if session_token is None:
        raise HTTPException(status_code=401, detail="Nejsi přihlášen")
    user_id = get_user_id_from_session(session_token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Session vypršela")
    user = session_db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Uživatel neexistuje")
    return user




security = HTTPBasic()


App = FastAPI()
App.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")






@App.get("/", response_class = HTMLResponse)
async def index(request: Request, session_token: str | None = Cookie(default=None)):
    # pokud existuje token 
    if session_token:
        user_id = get_user_id_from_session(token=session_token)
        print(user_id)

        user_info = session_db.query(User).filter(User.id == user_id).one_or_none()

        return templates.TemplateResponse(request = request, name="index.html", context={"username":user_id})

    else:

        return templates.TemplateResponse(request = request, name="index.html")

@App.get("/register", response_class = HTMLResponse)
async def register_view(request: Request, user_agent: Annotated[str | None, Header()] = None):
    utils.print_red( request.headers)
    return templates.TemplateResponse(request = request, name="register.html")

@App.get("/success", response_class= HTMLResponse)
async def success(request: Request):
    return templates.TemplateResponse(request=request, name="success_register.html")

# def get_db():
#     pass
@App.get("/invoices/{invoice_id}/delete")
async def delete_invoice(request:Request,
                         invoice_id:str,
                         current_user: User = Depends(required_login),
                         ):
    invoice = session_db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="404")
    if invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")
    if invoice is not None:
        session_db.delete(invoice)
        session_db.commit()
        target_file = Path(f"../data/invoices/invoice_{invoice.invoice_number}.pdf")
    
        if target_file.exists():
                target_file.unlink()
    return RedirectResponse(f"/invoices") 
@App.get("/invoices/new")
async def new_invoice_form(request: Request, current_user: User = Depends(required_login)):
    error = request.query_params.get("error")
    return templates.TemplateResponse(request=request, name="invoice_form.html", context={"error": error})

@App.post("/invoices/new")
async def create_invoice(
    current_user: User = Depends(required_login),

    customer_name: str = Form(...),
    customer_address: str = Form(...),
    date_issued: date = Form(...),
    date_due: date = Form(...),
    variable_symbol: str | None = Form(default=None),
    customer_ico: str = Form(),
):
    invoice_number = utils.generate_inv_num(current_user.id)
    invoice = Invoice(
        invoice_number=invoice_number,
        owner_id=current_user.id,
        customer_name=customer_name,
        customer_address=customer_address,
        date_issued=date_issued,
        date_due=date_due,
        variable_symbol=variable_symbol,
        customer_ico=customer_ico,
    )
    session_db.add(invoice)
    session_db.commit()
 
    return RedirectResponse(url=f"/invoices/{invoice.id}", status_code=status.HTTP_303_SEE_OTHER)

@App.get("/invoices/{invoice_id}/items/delete/{item_id}")
async def delete_item(request: Request,
                        
                      invoice_id:str,
                 
                      item_id: str, 
                      current_user: User = Depends(required_login),):
    
    item = session_db.get(Item, item_id)
    invoice = session_db.get(Invoice, invoice_id)
    if item is None:
        raise HTTPException(status_code=404, detail="404")
    if item is not None:
        if item.invoice_id != invoice.id:
            raise HTTPException(status_code=400, detail="400")
        if invoice.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="403")
        session_db.delete(item)
        session_db.commit()
        
        target_file = Path(f"../data/invoices/invoice_{invoice.invoice_number}.pdf")
    
        if target_file.exists():
                target_file.unlink()
                print("Soubor smazán.")
    print("neco se stalo")
    return RedirectResponse(f"/invoices/{invoice_id}")
@App.get("/invoices/{invoice_id}/items/new", response_class=HTMLResponse)
async def new_item_form(request: Request, invoice_id: int, current_user: User = Depends(required_login)):
    # todo delte old pdf 
  
    invoice = session_db.get(Invoice, invoice_id)
    if invoice is None:

        raise HTTPException(status_code=404, detail="neni")
    if invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")
    return templates.TemplateResponse(request=request, name="item_form.html", context={"invoice": invoice})

@App.post("/invoices/{invoice_id}/items")
async def create_item(
    invoice_id: int,
    current_user: User = Depends(required_login),
    name: str = Form(...),
    quantity: float = Form(...),
    unit_price: float = Form(...),

):
    invoice = session_db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="404")
    if invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")
 
    item = Item(
        invoice_id=invoice_id,
        name=name,
        quantity=quantity,
        unit_price=unit_price,
    )
    session_db.add(item) 
    session_db.commit()
    invoice_for_item = session_db.get(Invoice, invoice_id)
    target_file = Path(f"../data/invoices/invoice_{invoice_for_item.invoice_number}.pdf")
    
    if target_file.exists():
            target_file.unlink()
            print("Soubor smazán.")
 
    return RedirectResponse(url=f"/invoices/{invoice_id}/items/new", status_code=status.HTTP_303_SEE_OTHER)



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

    existing_username = session_db.execute(
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
    if user is None or utils.hashed_password(password) != user.password_hash:
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
        max_age=10e6,
    )
    print(f"logged in as {username}")
    return redirect
 
 
@App.get("/logout")
async def logout(session_token: str | None = Cookie(default=None)):
    if session_token:
        delete_session(session_token)
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie("session_token")
    return redirect

@App.get("/invoices")
async def invoices_view(request: Request, current_user: User = Depends(required_login)):
    print("yes")
    invoices = session_db.query(Invoice).filter(Invoice.owner_id == current_user.id).all()

    context = {"invoices":[{"id":i.id ,"invoice_number":i.invoice_number, "customer_name":i.customer_name, "tags":i.tags} for i in invoices]}
    return templates.TemplateResponse(request=request, name = "all_invoices.html", context=context )


@App.get("/invoices/{invoice_id}")
async def inoice_mine(request: Request,
                      invoice_id:str,
                       current_user: User = Depends(required_login)):
    invoice_for_user = session_db.get(Invoice, invoice_id)

    print(invoice_for_user.owner_id)
    print(current_user.id)
    if current_user.id == invoice_for_user.owner_id:
        context = vars(invoice_for_user)
        return templates.TemplateResponse(request=request, name = "invoice.html", context={"invoice":invoice_for_user, "user_tags":current_user.tags})
    else:
        raise HTTPException(status_code=403, detail="403") 


@App.get("/invoices/{invoice_id}/pdf")
async def pdf_invoice(request: Request,
                      invoice_id:str,
                       current_user: User = Depends(required_login)):
    invoice_for_user = session_db.get(Invoice, invoice_id)
    print(invoice_for_user.owner_id)
    print(current_user.id)





    path = f"../data/invoices/invoice_{invoice_for_user.invoice_number}.pdf"


  
    target_file = Path(path) 

    if not target_file.exists():
        utils.generate_invoice(invoice_for_user.id, invoice_for_user.invoice_number)
        # if not target_file.exists():
        #     # todo presmerovat na unsuccess
        #     raise FileNotFoundError(f"furt nic")
    print("nasel jsem fr")

    if current_user.id == invoice_for_user.owner_id:

        return FileResponse(path)
    else:
        raise HTTPException(status_code=403, detail="403") 



@App.get("/tags")
async def get_all_tags(request: Request, 
                       current_user: User = Depends(required_login)):
    tags = session_db.query(Tag).filter(Tag.owner_id == current_user.id).all() 
   
    return templates.TemplateResponse(request=request, name="all_tags.html", context={"tags":[i for i in tags ]})

@App.get("/tags/new")
async def create_tag_view(request:Request):
    return templates.TemplateResponse(request=request, name="create_tag.html")

@App.post("/tags/new")
async def create_tag(
    current_user: User = Depends(required_login),
    color: str = Form(...),
    name: str = Form(...),
    
    ):
    session_db.add(Tag(name=name, color=color, owner=current_user))
    session_db.commit()
    return RedirectResponse(url="/tags", status_code=status.HTTP_303_SEE_OTHER)

@App.get("/tags/{id}/delete")
async def delete_tag(request:Request, 
                     id: str,
                     current_user: User = Depends(required_login),):
    tag = session_db.get(Tag, id)
    if tag is None:
        raise HTTPException(status_code=404, detail="404")
    if tag is not None:
        if tag.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="403")
        session_db.delete(tag)
        session_db.commit()
    return RedirectResponse("/tags")


@App.post("/invoices/{invoice_id}/tags")
async def assign_tag(
    invoice_id: int,
    current_user: User = Depends(required_login),
    tag_id: int = Form(...),
):
    invoice = session_db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="404")
    if invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")

    tag = session_db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="404")
    if tag.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")

    if tag not in invoice.tags:
        invoice.tags.append(tag)
        session_db.commit()

    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=status.HTTP_303_SEE_OTHER)

@App.get("/invoices/{invoice_id}/tags/{tag_id}/remove")
async def unassign_tag(
    invoice_id: int,
    tag_id: int,
    current_user: User = Depends(required_login),
):
    invoice = session_db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="404")
    if invoice.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="403")

    tag = session_db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="404")
    
    if tag in invoice.tags:
        invoice.tags.remove(tag)
        session_db.commit()


    else:
        raise HTTPException(status_code=403, detail="403")

    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=status.HTTP_303_SEE_OTHER)