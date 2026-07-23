from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()



invoice_tags = Table(
    "invoice_tags",
    Base.metadata,
    Column("invoice_id", Integer, ForeignKey("invoices.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    ico = Column(String, nullable=True)           
    phone = Column(String, nullable=True)
    bank_account = Column(String, nullable=True)     
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice",
        back_populates="owner_shortcut",
        cascade="all, delete-orphan"
    )
    tags = relationship("Tag", back_populates="owner", cascade="all, delete-orphan")
    def __repr__(self):
        return self.username

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, nullable=False)  
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_shortcut = relationship("User", back_populates="invoices")
    customer_name = Column(String, nullable=False)
    customer_address = Column(String, nullable=False)
    customer_ico = Column(String, nullable=True)
    date_issued = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)

    variable_symbol = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    pdf_path = Column(String, nullable=True)  
    items = relationship(
        "Item",
        back_populates="invoice_shortcut",
        cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=invoice_tags, back_populates="invoices")

   
 
    def __repr__(self):
        return f"{self.invoice_number} - {self.customer_name} - {self.customer_ico}"

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tags")
 
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
 
    invoices = relationship("Invoice", secondary=invoice_tags, back_populates="tags")

class Item(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice_shortcut = relationship("Invoice", back_populates="items")
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    unit_price = Column(Float, nullable=False)       
   
    def __repr__(self):
        return f"{self.name} - quantity {self.quantity}"


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    expiration = Column(DateTime, nullable=False)
 
    user = relationship("User", back_populates="sessions")
 
    def __repr__(self):
        return f"{self.user_id} until {self.expiration}"