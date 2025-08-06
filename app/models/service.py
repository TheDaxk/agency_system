from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Service(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    category: str
    price: float
    description: Optional[str] = None
    color: Optional[str] = None  # Cor para categorização visual
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ServiceCreate(SQLModel):
    name: str
    category: str
    price: float
    description: Optional[str] = None
    color: Optional[str] = None

class ServiceUpdate(SQLModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None

class ServiceResponse(SQLModel):
    id: str
    name: str
    category: str
    price: float
    description: Optional[str] = None
    color: Optional[str] = None
    active: bool
    created_at: datetime

# Modelo para relatórios/declarações
class Report(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    client_id: str = Field(foreign_key="client.id")
    services: dict = Field(default_factory=dict, sa_column=Column(JSON))  # Array de serviços
    total_value: float
    generated_by: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

