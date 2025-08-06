from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Client(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    contact_name: str
    city: str
    phone: str
    email: Optional[str] = None
    payment_data: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    avatar: Optional[str] = None
    status: str = Field(default="active")
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ClientCreate(SQLModel):
    name: str
    contact_name: str
    city: str
    phone: str
    email: Optional[str] = None
    payment_data: Optional[dict] = None
    notes: Optional[str] = None

class ClientUpdate(SQLModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    payment_data: Optional[dict] = None
    avatar: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ClientResponse(SQLModel):
    id: str
    name: str
    contact_name: str
    city: str
    phone: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime

