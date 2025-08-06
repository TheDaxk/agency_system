from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.models.client import Client, ClientCreate, ClientUpdate, ClientResponse
from app.models.user import User
from app.dependencies import get_current_user, get_session

router = APIRouter()

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Criar novo cliente"""
    client = Client(**client_data.dict())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os clientes"""
    statement = select(Client)
    clients = session.exec(statement).all()
    return clients

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter cliente por ID"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return client

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Atualizar cliente"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    client_dict = client_data.dict(exclude_unset=True)
    for key, value in client_dict.items():
        setattr(client, key, value)
    
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Deletar cliente"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    session.delete(client)
    session.commit()
    return {"message": "Cliente deletado com sucesso"}

