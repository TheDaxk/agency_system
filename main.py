from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Importar modelos
from app.models.user import User, Role
from app.models.client import Client
from app.models.project import Project, Priority
from app.models.financial import FinancialEntry, EntryType
from app.models.service import Service

# Configuração do banco de dados
SUPABASE_URL = "https://omcushqikzcjnigvmugi.supabase.co"
SUPABASE_KEY = "sb_secret_5jenHsdjI2a_BWQGsiPBsw_dpoqSV77"
DATABASE_URL = "postgresql://postgres:Pg3Nk1jGppLGaVuz@db.omcushqikzcjnigvmugi.supabase.co:5432/postgres"

if not DATABASE_URL:
    logger.error("DATABASE_URL não configurado!")
    raise ValueError("DATABASE_URL não configurado!")

logger.info(f"Conectando ao banco: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})

def create_db_and_tables():
    logger.info("Criando tabelas no banco...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tabelas criadas com sucesso!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Gestão para Agência Digital",
    description="Sistema SaaS completo para gestão de agência digital",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="app/templates")
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Importar e incluir routers após a criação da app
from app.routers import auth, clients, projects, financial, dashboard, reports

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(financial.router, prefix="/api/financial", tags=["financial"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Rota principal
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota de login
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Rota do dashboard
@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Rota de clientes
@app.get("/clients")
async def clients_page(request: Request):
    return templates.TemplateResponse("clients.html", {"request": request})

# Rota de projetos
@app.get("/projects")
async def projects_page(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request})

# Rota financeiro
@app.get("/financial")
async def financial_page(request: Request):
    return templates.TemplateResponse("financial.html", {"request": request})

# Rota de relatórios
@app.get("/reports")
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

# Health check para Railway
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "message": "Sistema de Gestão AgênciaHub está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Porta dinâmica para Railway
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        reload=False,  # Desabilitar reload em produção
        log_level="info"
    )
