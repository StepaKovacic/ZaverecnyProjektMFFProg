from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base
from models import User, Invoice, Item 
from datetime import date

engine = create_engine("sqlite:///../data/db/invoices.db")
Base.metadata.create_all(engine)  

session = Session(engine)


# TODO: pridat mechanismus pro unique username, invoice num atd 