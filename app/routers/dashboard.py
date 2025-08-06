from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.models.project import Project
from app.models.client import Client
from app.models.financial import FinancialEntry, EntryType
from app.models.user import User
from app.dependencies import get_current_user, get_session
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter métricas do dashboard"""
    
    # Contar projetos por status
    projects_statement = select(Project.status, func.count(Project.id)).group_by(Project.status)
    projects_by_status = session.exec(projects_statement).all()
    
    # Contar total de clientes
    clients_statement = select(func.count(Client.id))
    total_clients = session.exec(clients_statement).first()
    
    # Calcular receitas e despesas do mês atual
    current_month = datetime.now().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    # Receitas do mês
    income_statement = select(func.sum(FinancialEntry.amount)).where(
        FinancialEntry.type == EntryType.INCOME,
        FinancialEntry.date >= current_month,
        FinancialEntry.date < next_month
    )
    monthly_income = session.exec(income_statement).first() or 0
    
    # Despesas do mês
    expense_statement = select(func.sum(FinancialEntry.amount)).where(
        FinancialEntry.type == EntryType.EXPENSE,
        FinancialEntry.date >= current_month,
        FinancialEntry.date < next_month
    )
    monthly_expenses = session.exec(expense_statement).first() or 0
    
    # Lucro líquido
    net_profit = monthly_income - monthly_expenses
    
    return {
        "projects_by_status": dict(projects_by_status),
        "total_clients": total_clients,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "net_profit": net_profit,
        "profit_margin": (net_profit / monthly_income * 100) if monthly_income > 0 else 0
    }

@router.get("/recent-projects")
async def get_recent_projects(
    limit: int = 5,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter projetos recentes"""
    statement = select(Project).order_by(Project.created_at.desc()).limit(limit)
    projects = session.exec(statement).all()
    return projects

@router.get("/financial-summary")
async def get_financial_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter resumo financeiro dos últimos 6 meses"""
    
    summaries = []
    for i in range(6):
        # Calcular o mês
        month_date = datetime.now().replace(day=1) - timedelta(days=30 * i)
        next_month = (month_date + timedelta(days=32)).replace(day=1)
        
        # Receitas do mês
        income_statement = select(func.sum(FinancialEntry.amount)).where(
            FinancialEntry.type == EntryType.INCOME,
            FinancialEntry.date >= month_date,
            FinancialEntry.date < next_month
        )
        income = session.exec(income_statement).first() or 0
        
        # Despesas do mês
        expense_statement = select(func.sum(FinancialEntry.amount)).where(
            FinancialEntry.type == EntryType.EXPENSE,
            FinancialEntry.date >= month_date,
            FinancialEntry.date < next_month
        )
        expenses = session.exec(expense_statement).first() or 0
        
        summaries.append({
            "month": month_date.strftime("%Y-%m"),
            "income": income,
            "expenses": expenses,
            "profit": income - expenses
        })
    
    return summaries[::-1]  # Reverter para ordem cronológica

@router.get("/revenue-by-client")
async def get_revenue_by_client(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter receita por cliente"""
    
    # Buscar receitas com cliente associado
    query = select(
        Client.name,
        func.sum(FinancialEntry.amount).label("total_revenue")
    ).join(
        FinancialEntry, Client.id == FinancialEntry.client_id
    ).where(
        FinancialEntry.type == EntryType.INCOME
    ).group_by(Client.id, Client.name).order_by(func.sum(FinancialEntry.amount).desc())
    
    results = session.exec(query).all()
    
    return [
        {
            "client_name": result[0],
            "total_revenue": float(result[1])
        }
        for result in results
    ]

@router.get("/project-timeline")
async def get_project_timeline(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter timeline de projetos"""
    
    # Buscar projetos com prazo nos próximos 30 dias
    end_date = datetime.now() + timedelta(days=30)
    
    query = select(Project).where(
        Project.deadline.isnot(None),
        Project.deadline <= end_date,
        Project.status.in_(["planning", "in_progress", "review"])
    ).order_by(Project.deadline)
    
    projects = session.exec(query).all()
    
    timeline_data = []
    for project in projects:
        # Buscar nome do cliente
        client_query = select(Client.name).where(Client.id == project.client_id)
        client_name = session.exec(client_query).first() or "Cliente não encontrado"
        
        timeline_data.append({
            "id": project.id,
            "title": project.title,
            "client_name": client_name,
            "deadline": project.deadline.isoformat(),
            "status": project.status,
            "priority": project.priority,
            "progress": project.progress
        })
    
    return timeline_data

@router.get("/financial-categories")
async def get_financial_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obter categorias financeiras com totais"""
    
    # Receitas por categoria
    income_query = select(
        FinancialEntry.category,
        func.sum(FinancialEntry.amount).label("total")
    ).where(
        FinancialEntry.type == EntryType.INCOME
    ).group_by(FinancialEntry.category)
    
    income_results = session.exec(income_query).all()
    
    # Despesas por categoria
    expense_query = select(
        FinancialEntry.category,
        func.sum(FinancialEntry.amount).label("total")
    ).where(
        FinancialEntry.type == EntryType.EXPENSE
    ).group_by(FinancialEntry.category)
    
    expense_results = session.exec(expense_query).all()
    
    return {
        "income_categories": [
            {
                "category": result[0],
                "total": float(result[1])
            }
            for result in income_results
        ],
        "expense_categories": [
            {
                "category": result[0],
                "total": float(result[1])
            }
            for result in expense_results
        ]
    }

