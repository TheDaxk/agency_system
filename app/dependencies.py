from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.models.user import User
from app.services.auth import AuthService

security = HTTPBearer()

def get_session():
    from main import engine
    with Session(engine) as session:
        yield session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    session: Session = Depends(get_session)
) -> User:
    """Dependency para obter usuário atual"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    user_id = payload.get("sub")
    
    user = session.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    return user

