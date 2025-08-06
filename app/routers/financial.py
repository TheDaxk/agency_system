from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.models.financial import FinancialEntry, FinancialEntryCreate, FinancialEntryUpdate, FinancialEntryResponse
from app.models.user import User
from app.dependencies import get_current_user, get_session

router = APIRouter()

@router.post("/", response_model=FinancialEntryResponse)
async def create_financial_entry(
    entry_data: FinancialEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Criar nova entrada financeira"""
    entry = FinancialEntry(**entry_data.dict())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

@router.get("/", response_model=List[FinancialEntryResponse])
async def get_financial_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todas as entradas financeiras"""
    statement = select(FinancialEntry)
    entries = session.exec(statement).all()
    return entries

@router.get("/{entry_id}", response_model=FinancialEntryResponse)
async def get_financial_entry(
    entry_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter entrada financeira por ID"""
    entry = session.get(FinancialEntry, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada financeira não encontrada"
        )
    return entry

@router.put("/{entry_id}", response_model=FinancialEntryResponse)
async def update_financial_entry(
    entry_id: str,
    entry_data: FinancialEntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Atualizar entrada financeira"""
    entry = session.get(FinancialEntry, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada financeira não encontrada"
        )
    
    entry_dict = entry_data.dict(exclude_unset=True)
    for key, value in entry_dict.items():
        setattr(entry, key, value)
    
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

@router.delete("/{entry_id}")
async def delete_financial_entry(
    entry_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Deletar entrada financeira"""
    entry = session.get(FinancialEntry, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entrada financeira não encontrada"
        )
    
    session.delete(entry)
    session.commit()
    return {"message": "Entrada financeira deletada com sucesso"}

