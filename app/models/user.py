from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    CLIENT = "client"

class User(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str
    name: str
    role: Role = Role.OPERATIONAL
    active: bool = True
    avatar: Optional[str] = None
    permissions: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class UserCreate(SQLModel):
    email: str
    password: str
    name: str
    role: Role = Role.OPERATIONAL

class UserUpdate(SQLModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[Role] = None
    active: Optional[bool] = None
    avatar: Optional[str] = None
    permissions: Optional[dict] = None

class UserResponse(SQLModel):
    id: str
    email: str
    name: str
    role: Role
    active: bool
    avatar: Optional[str] = None
    created_at: datetime

