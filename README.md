# 🚀 Sistema de Gestão para Agência Digital

Sistema SaaS completo desenvolvido em **Python (FastAPI)** para gestão de agências digitais, com todas as funcionalidades especificadas nos documentos fornecidos.

## ✨ Funcionalidades Principais

### 🔐 Autenticação e Usuários
- Sistema de login/registro seguro com JWT
- Controle de acesso por níveis de usuário
- Sessões persistentes

### 📊 Dashboard Executivo
- Métricas em tempo real (receitas, lucros, clientes)
- Gráficos interativos com Chart.js
- Resumo financeiro dos últimos 6 meses
- Projetos por status e timeline

### 👥 Gestão de Clientes
- CRUD completo com validação
- Busca e filtros avançados
- Histórico de projetos por cliente
- Status ativo/inativo

### 📋 Gestão de Projetos
- Visualização Kanban interativa
- Controle de status e prioridades
- Barras de progresso visuais
- Prazos e deadlines
- Associação com clientes

### 💰 Módulo Financeiro
- Controle de receitas e despesas
- Categorização de transações
- Relatórios por período
- Cálculo automático de lucros
- Gráficos de fluxo de caixa

### 📄 Relatórios PDF
- Relatórios de cliente completos
- Relatórios financeiros detalhados
- Relatórios de projeto
- Geração de faturas/orçamentos
- Templates profissionais

## 🛠️ Tecnologias

- **Backend**: FastAPI + SQLModel + SQLite
- **Frontend**: Jinja2 + HTMX + Bootstrap 5
- **Gráficos**: Chart.js
- **PDFs**: ReportLab
- **Autenticação**: JWT
- **Banco**: SQLite (pode ser migrado para PostgreSQL)

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
cp .env.example .env
# Editar .env conforme necessário
```

### 3. Executar
```bash
python main.py
```

### 4. Acessar
- **Sistema**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 👤 Usuário de Teste

Crie um usuário através da página de registro ou use:
- **Email**: admin@agenciahub.com
- **Senha**: 123456

## 📱 Responsividade

Sistema totalmente responsivo para desktop, tablet e mobile.

## 🔒 Segurança

- JWT tokens para autenticação
- Validação de dados em todas as rotas
- Controle de acesso por níveis
- Headers de segurança configurados

## 📊 Estrutura do Projeto

```
sistema_gestao_agencia/
├── app/
│   ├── models/          # Modelos de dados
│   ├── routers/         # Rotas da API
│   ├── services/        # Serviços de negócio
│   ├── templates/       # Templates HTML
│   └── static/          # CSS, JS, imagens
├── main.py              # Arquivo principal
├── requirements.txt     # Dependências
├── .env.example         # Exemplo de configuração
└── README.md           # Este arquivo
```

## 🎯 Status do Projeto

✅ **COMPLETO** - Todas as funcionalidades implementadas e testadas

- ✅ Sistema de autenticação
- ✅ Dashboard com métricas
- ✅ Gestão de clientes
- ✅ Gestão de projetos (Kanban + Lista)
- ✅ Módulo financeiro
- ✅ Geração de relatórios PDF
- ✅ Interface responsiva
- ✅ APIs RESTful completas

## 📞 Suporte

Sistema pronto para uso em produção. Todas as funcionalidades foram testadas e validadas.

---

**Desenvolvido para AgênciaHub** 🎨

