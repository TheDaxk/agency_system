from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum
from uuid import uuid4

class EntryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class FinancialEntry(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    type: EntryType
    description: str
    category: str
    amount: float
    date: date
    status: str = Field(default="pending")
    client_id: Optional[str] = Field(default=None, foreign_key="client.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class FinancialEntryCreate(SQLModel):
    type: EntryType
    description: str
    category: str
    amount: float
    date: date
    status: str = "pending"
    client_id: Optional[str] = None

class FinancialEntryUpdate(SQLModel):
    description: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    status: Optional[str] = None

class FinancialEntryResponse(SQLModel):
    id: str
    type: EntryType
    description: str
    category: str
    amount: float
    date: date
    status: str
    client_id: Optional[str] = None
    created_at: datetime

