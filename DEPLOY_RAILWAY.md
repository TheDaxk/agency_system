# 🚀 Deploy na Railway - Instruções Completas

## Pré-requisitos

1. **Conta na Railway**: Crie uma conta em [railway.app](https://railway.app)
2. **Git**: Certifique-se de ter o Git instalado
3. **Node.js**: Para instalar a Railway CLI

## Método 1: Deploy via GitHub (Recomendado)

### 1. Criar Repositório no GitHub

1. Acesse [github.com](https://github.com) e crie um novo repositório
2. Nome sugerido: `sistema-gestao-agencia`
3. Deixe como público ou privado (sua escolha)
4. **NÃO** inicialize com README, .gitignore ou licença

### 2. Fazer Push do Código

```bash
# No diretório do projeto
git remote add origin https://github.com/SEU_USUARIO/sistema-gestao-agencia.git
git branch -M main
git push -u origin main
```

### 3. Deploy na Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Conecte sua conta GitHub se necessário
5. Selecione o repositório `sistema-gestao-agencia`
6. A Railway detectará automaticamente que é um projeto Python
7. O deploy iniciará automaticamente

### 4. Configurar Variáveis de Ambiente

Na Railway, vá para seu projeto e clique em **"Variables"**:

```env
SECRET_KEY=sua_chave_secreta_super_forte_aqui_mude_em_producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./database.db
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=*
LOG_LEVEL=INFO
```

### 5. Configurar Domínio (Opcional)

1. Na Railway, vá para **"Settings"**
2. Em **"Domains"**, clique em **"Generate Domain"**
3. Ou adicione seu domínio customizado

## Método 2: Deploy via Railway CLI

### 1. Instalar Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login na Railway

```bash
railway login
```

### 3. Inicializar Projeto

```bash
# No diretório do projeto
railway init
```

### 4. Deploy

```bash
railway up
```

### 5. Configurar Variáveis

```bash
railway variables set SECRET_KEY=sua_chave_secreta_super_forte
railway variables set ENVIRONMENT=production
railway variables set DEBUG=False
```

## Configurações Automáticas

O projeto já está configurado com:

- ✅ **Procfile**: Define como executar a aplicação
- ✅ **railway.json**: Configurações específicas da Railway
- ✅ **runtime.txt**: Especifica Python 3.11
- ✅ **requirements.txt**: Todas as dependências
- ✅ **Health check**: Endpoint `/health` para monitoramento
- ✅ **Porta dinâmica**: Usa variável `$PORT` da Railway
- ✅ **CORS configurado**: Para acesso externo

## Verificação do Deploy

Após o deploy, verifique:

1. **Status**: Projeto deve estar "Active" na Railway
2. **Logs**: Verifique se não há erros nos logs
3. **Health check**: Acesse `https://seu-dominio.railway.app/health`
4. **Sistema**: Acesse `https://seu-dominio.railway.app`

## Banco de Dados

### SQLite (Padrão)
- Funciona imediatamente
- Dados são perdidos a cada redeploy
- Ideal para testes

### PostgreSQL (Recomendado para Produção)
1. Na Railway, clique em **"New"** → **"Database"** → **"PostgreSQL"**
2. Copie a `DATABASE_URL` gerada
3. Atualize a variável `DATABASE_URL` no projeto
4. Redeploy o projeto

## Monitoramento

### Logs
```bash
railway logs
```

### Métricas
- CPU, RAM e Network disponíveis no dashboard da Railway

### Alertas
- Configure notificações no dashboard

## Domínio Customizado

### 1. Configurar DNS
Aponte seu domínio para a Railway:
```
CNAME: seu-dominio.com → seu-projeto.railway.app
```

### 2. Adicionar na Railway
1. Vá para **"Settings"** → **"Domains"**
2. Clique em **"Custom Domain"**
3. Digite seu domínio
4. Aguarde verificação SSL automática

## Backup e Manutenção

### Backup do Código
- Código está seguro no GitHub
- Railway mantém histórico de deploys

### Backup do Banco (SQLite)
```bash
railway run python -c "import shutil; shutil.copy('database.db', 'backup.db')"
```

### Atualizações
```bash
git add .
git commit -m "Atualização do sistema"
git push origin main
# Deploy automático na Railway
```

## Troubleshooting

### Build Falha
- Verifique `requirements.txt`
- Confirme Python 3.11 no `runtime.txt`

### Aplicação Não Inicia
- Verifique logs: `railway logs`
- Confirme `Procfile` está correto

### Erro 503
- Aplicação pode estar iniciando
- Aguarde alguns minutos

### Banco de Dados
- Para PostgreSQL, confirme `DATABASE_URL`
- Para SQLite, dados são temporários

## URLs Importantes

Após o deploy, você terá:

- **Sistema Principal**: `https://seu-projeto.railway.app`
- **API Docs**: `https://seu-projeto.railway.app/docs`
- **Health Check**: `https://seu-projeto.railway.app/health`
- **Dashboard**: `https://seu-projeto.railway.app/dashboard`

## Custos

- **Hobby Plan**: $5/mês por serviço
- **Pro Plan**: $20/mês com mais recursos
- **Uso**: Baseado em CPU/RAM/Network

## Suporte

- **Documentação**: [docs.railway.app](https://docs.railway.app)
- **Discord**: Comunidade Railway
- **GitHub Issues**: Para problemas do código

---

## ✅ Checklist de Deploy

- [ ] Conta Railway criada
- [ ] Repositório GitHub criado
- [ ] Código enviado para GitHub
- [ ] Projeto criado na Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado com sucesso
- [ ] Health check funcionando
- [ ] Sistema acessível via browser
- [ ] Domínio configurado (opcional)
- [ ] Banco de dados configurado
- [ ] Backup configurado

**🎉 Seu sistema estará online e acessível 24/7!**

