from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.models.user import User, UserCreate, UserResponse
from app.services.auth import AuthService, Token, LoginRequest
from app.dependencies import get_session

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registrar novo usuário"""
    # Verificar se email já existe
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar novo usuário
    hashed_password = AuthService.get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        role=user_data.role
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """Login do usuário"""
    # Buscar usuário por email
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    
    if not user or not AuthService.verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Criar tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    """Renovar token de acesso"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    user_id = payload.get("sub")
    
    # Verificar se usuário ainda existe e está ativo
    user = session.get(User, user_id)
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    # Criar novos tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
    """Obter dados do usuário atual"""
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    user_id = payload.get("sub")
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user

