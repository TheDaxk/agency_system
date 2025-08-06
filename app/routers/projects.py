from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from app.models.user import User
from app.dependencies import get_current_user, get_session

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Criar novo projeto"""
    project = Project(**project_data.dict())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os projetos"""
    statement = select(Project)
    projects = session.exec(statement).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter projeto por ID"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Atualizar projeto"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    project_dict = project_data.dict(exclude_unset=True)
    for key, value in project_dict.items():
        setattr(project, key, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Deletar projeto"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado"
        )
    
    session.delete(project)
    session.commit()
    return {"message": "Projeto deletado com sucesso"}

