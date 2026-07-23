from pydantic import BaseModel
from typing import Annotated
from annotated_doc import Doc
from datetime import datetime, timedelta

import bcrypt
import secrets

from dbHandler import session_db as db_session
from models import Session, User

SESSION_TTL = timedelta(days=7)
class HTTPBasicCredentials(BaseModel):
    username: Annotated[str, Doc("The HTTP Basic username.")]
    password: Annotated[str, Doc("The HTTP Basic password.")]


class REGISTERCredentials(BaseModel):
    username: Annotated[str, Doc("The HTTP Basic username.")]
    password: Annotated[str, Doc("The HTTP Basic password.")]
    email: Annotated[str, Doc("The HTTP Basic username.")]
    first_name: Annotated[str, Doc("first name ")]
    last_name: Annotated[str, Doc("last name")]


def create_session(user_id: int):
    token = secrets.token_urlsafe(32)  
    new_session = Session(
        token=token,
        user_id=user_id,
        expiration=datetime.utcnow() + SESSION_TTL,
    )
    db_session.add(new_session)
    db_session.commit()
    return token


def get_user_id_from_session(token: str):
    existing = db_session.query(Session).filter(Session.token == token).one_or_none()
    if existing is None:
        return None
    if existing.expiration < datetime.utcnow():
        db_session.delete(existing)
        db_session.commit()
        return None

    existing.expiration = datetime.utcnow() + SESSION_TTL
    db_session.commit()

    return existing.user_id




def delete_session(token: str):
    existing = db_session.query(Session).filter(Session.token == token).one_or_none()
    if existing is not None:
        db_session.delete(existing)
        db_session.commit()
