from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from typing import Optional
from datetime import datetime, date
from enum import Enum
from uuid import uuid4

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Project(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str
    description: Optional[str] = None
    client_id: str = Field(foreign_key="client.id")
    status: str = Field(default="Orçamento")
    priority: Priority = Priority.MEDIUM
    start_date: date
    end_date: date
    value: Optional[float] = None
    assigned_to: Optional[str] = Field(default=None, foreign_key="user.id")
    board_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ProjectCreate(SQLModel):
    title: str
    description: Optional[str] = None
    client_id: str
    status: str = "Orçamento"
    priority: Priority = Priority.MEDIUM
    start_date: date
    end_date: date
    value: Optional[float] = None
    assigned_to: Optional[str] = None

class ProjectUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[Priority] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    value: Optional[float] = None
    assigned_to: Optional[str] = None

class ProjectResponse(SQLModel):
    id: str
    title: str
    description: Optional[str] = None
    client_id: str
    status: str
    priority: Priority
    start_date: date
    end_date: date
    value: Optional[float] = None
    assigned_to: Optional[str] = None
    created_at: datetime

class Board(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    statuses: dict = Field(default_factory=dict, sa_column=Column(JSON))  # Array de status customizados
    color: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

