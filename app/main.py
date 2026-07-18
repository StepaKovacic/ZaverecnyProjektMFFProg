from dbHandler import session 
from models import User, Invoice, Item


user = User(
    username="stepanKralMatematiky",
    email="stepan.kral.matematiky@example.com",
    password_hash="Frantisek444",
    first_name="Štěpán",
    last_name="Noha",
    ico="2243456",
)
session.add(user)
session.commit() 
print(user.id)