from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.models.financial import FinancialEntry
from app.models.service import Service, Report, ServiceCreate, ServiceUpdate, ServiceResponse
from app.dependencies import get_current_user, get_session
from app.services.pdf_generator import PDFGenerator
import os

router = APIRouter()
pdf_generator = PDFGenerator()

# Rotas para serviços
@router.post("/services", response_model=ServiceResponse)
async def create_service(
    service_data: ServiceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Criar novo serviço"""
    service = Service(**service_data.dict())
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

@router.get("/services", response_model=List[ServiceResponse])
async def get_services(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os serviços"""
    statement = select(Service).where(Service.active == True)
    services = session.exec(statement).all()
    return services

@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service_data: ServiceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Atualizar serviço"""
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    
    service_dict = service_data.dict(exclude_unset=True)
    for key, value in service_dict.items():
        setattr(service, key, value)
    
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

# Rotas para relatórios em PDF
@router.get("/client/{client_id}")
async def generate_client_report(
    client_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Gerar relatório de cliente em PDF"""
    
    # Buscar cliente
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Buscar projetos do cliente
    projects_query = select(Project).where(Project.client_id == client_id)
    projects = session.exec(projects_query).all()
    
    # Buscar dados financeiros do cliente
    financial_query = select(FinancialEntry).where(FinancialEntry.client_id == client_id)
    financial_data = session.exec(financial_query).all()
    
    # Converter para dicionários
    client_data = {
        "id": client.id,
        "name": client.name,
        "contact_name": client.contact_name,
        "email": client.email,
        "phone": client.phone,
        "city": client.city,
        "active": client.active
    }
    
    projects_data = []
    for project in projects:
        projects_data.append({
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "priority": project.priority,
            "value": project.value,
            "progress": project.progress
        })
    
    financial_data_list = []
    for entry in financial_data:
        financial_data_list.append({
            "type": entry.type.value,
            "amount": entry.amount,
            "category": entry.category,
            "date": entry.date
        })
    
    # Gerar PDF
    pdf_path = pdf_generator.generate_client_report(
        client_data, projects_data, financial_data_list, session
    )
    
    # Retornar arquivo
    filename = f"relatorio_cliente_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type='application/pdf',
        background=lambda: pdf_generator.cleanup_temp_file(pdf_path)
    )

@router.get("/financial")
async def generate_financial_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Gerar relatório financeiro em PDF"""
    
    # Definir datas padrão (último mês)
    if not end_date:
        end_date_obj = datetime.now()
    else:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    if not start_date:
        start_date_obj = end_date_obj - timedelta(days=30)
    else:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Gerar PDF
    pdf_path = pdf_generator.generate_financial_report(start_date_obj, end_date_obj, session)
    
    # Retornar arquivo
    filename = f"relatorio_financeiro_{start_date_obj.strftime('%Y%m%d')}_{end_date_obj.strftime('%Y%m%d')}.pdf"
    
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type='application/pdf',
        background=lambda: pdf_generator.cleanup_temp_file(pdf_path)
    )

@router.get("/project/{project_id}")
async def generate_project_report(
    project_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Gerar relatório de projeto em PDF"""
    
    # Buscar projeto
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Buscar cliente
    client = session.get(Client, project.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Buscar serviços do projeto
    services_query = select(Service).where(Service.project_id == project_id)
    services = session.exec(services_query).all()
    
    # Converter para dicionários
    project_data = {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "priority": project.priority,
        "value": project.value,
        "progress": project.progress,
        "created_at": project.created_at.strftime('%d/%m/%Y') if project.created_at else None,
        "deadline": project.deadline.strftime('%d/%m/%Y') if project.deadline else None,
        "notes": project.notes
    }
    
    client_data = {
        "id": client.id,
        "name": client.name,
        "contact_name": client.contact_name,
        "email": client.email
    }
    
    services_data = []
    for service in services:
        services_data.append({
            "description": service.description,
            "status": service.status,
            "value": service.value,
            "date": service.date.strftime('%d/%m/%Y') if service.date else None
        })
    
    # Gerar PDF
    pdf_path = pdf_generator.generate_project_report(
        project_data, client_data, services_data, session
    )
    
    # Retornar arquivo
    filename = f"relatorio_projeto_{project.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type='application/pdf',
        background=lambda: pdf_generator.cleanup_temp_file(pdf_path)
    )

@router.post("/invoice")
async def generate_invoice(
    invoice_data: dict,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Gerar fatura/orçamento em PDF"""
    
    client_id = invoice_data.get('client_id')
    project_id = invoice_data.get('project_id')
    
    if not client_id or not project_id:
        raise HTTPException(status_code=400, detail="client_id e project_id são obrigatórios")
    
    # Buscar cliente e projeto
    client = session.get(Client, client_id)
    project = session.get(Project, project_id)
    
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Buscar serviços
    services_query = select(Service).where(Service.project_id == project_id)
    services = session.exec(services_query).all()
    
    # Converter para dicionários
    client_data = {
        "name": client.name,
        "contact_name": client.contact_name,
        "email": client.email
    }
    
    project_data = {
        "title": project.title
    }
    
    services_data = []
    for service in services:
        services_data.append({
            "description": service.description,
            "quantity": 1,  # Padrão
            "value": service.value or 0
        })
    
    # Gerar PDF
    pdf_path = pdf_generator.generate_invoice(
        client_data, project_data, services_data, invoice_data
    )
    
    # Retornar arquivo
    doc_type = invoice_data.get('type', 'invoice')
    doc_name = 'fatura' if doc_type == 'invoice' else 'orcamento'
    filename = f"{doc_name}_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type='application/pdf',
        background=lambda: pdf_generator.cleanup_temp_file(pdf_path)
    )

# Rotas para relatórios/declarações (compatibilidade)
@router.post("/generate")
async def generate_report(
    client_id: str,
    services: List[dict],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Gerar relatório/declaração"""
    
    # Calcular valor total
    total_value = sum(service.get("price", 0) * service.get("quantity", 1) for service in services)
    
    # Criar registro do relatório
    report = Report(
        client_id=client_id,
        services={"items": services},
        total_value=total_value,
        generated_by=current_user.id
    )
    
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return {
        "report_id": report.id,
        "total_value": total_value,
        "message": "Relatório gerado com sucesso"
    }

@router.get("/")
async def get_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Listar todos os relatórios"""
    statement = select(Report).order_by(Report.created_at.desc())
    reports = session.exec(statement).all()
    return reports

@router.get("/{report_id}")
async def get_report(
    report_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter relatório por ID"""
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relatório não encontrado"
        )
    return report

