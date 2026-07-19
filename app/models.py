from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

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
    invoices = relationship(
        "Invoice",
        back_populates="owner_shortcut",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return self.username

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False)  
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_shortcut = relationship("User", back_populates="invoices")
    customer_name = Column(String, nullable=False)
    customer_address = Column(String, nullable=False)
    customer_ico = Column(String, nullable=True)
    date_issued = Column(Date, nullable=False)
    date_due = Column(Date, nullable=False)
    date_taxable_supply = Column(Date, nullable=False)  
    variable_symbol = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    pdf_path = Column(String, nullable=True)  
    items = relationship(
        "Item",
        back_populates="invoice_shortcut",
        cascade="all, delete-orphan"
    )
 
    def __repr__(self):
        return f"{self.invoice_number} - {self.customer_name} - {self.customer_ico}"

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