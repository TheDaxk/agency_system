# 🚀 Instruções de Deploy

## Opções de Deploy

### 1. Deploy Local (Desenvolvimento)

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Executar aplicação
python main.py
```

Acesse: http://localhost:8000

### 2. Deploy em Servidor (Produção)

#### Usando Uvicorn + Nginx

1. **Instalar dependências no servidor**:
```bash
pip install -r requirements.txt
```

2. **Configurar variáveis de ambiente**:
```bash
# Editar .env com configurações de produção
SECRET_KEY=sua_chave_secreta_super_forte
DATABASE_URL=sqlite:///./production.db
ENVIRONMENT=production
```

3. **Executar com Uvicorn**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

4. **Configurar Nginx** (opcional):
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Deploy com Docker

1. **Criar Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Build e Run**:
```bash
docker build -t sistema-gestao .
docker run -p 8000:8000 sistema-gestao
```

### 4. Deploy na Nuvem

#### Heroku
```bash
# Criar Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git add .
git commit -m "Deploy inicial"
heroku create seu-app-name
git push heroku main
```

#### Railway
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### DigitalOcean App Platform
1. Conectar repositório GitHub
2. Configurar build command: `pip install -r requirements.txt`
3. Configurar run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Configurações de Produção

### Variáveis de Ambiente (.env)
```env
# Segurança
SECRET_KEY=sua_chave_secreta_muito_forte_aqui
ENVIRONMENT=production

# Banco de dados
DATABASE_URL=sqlite:///./production.db
# Para PostgreSQL: postgresql://user:pass@host:port/db

# CORS (se necessário)
ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Logs
LOG_LEVEL=INFO
```

### Banco de Dados

#### SQLite (Padrão)
- Arquivo local: `database.db`
- Ideal para pequenas aplicações
- Backup: copiar arquivo `.db`

#### PostgreSQL (Recomendado para produção)
```bash
# Instalar driver
pip install psycopg2-binary

# Configurar DATABASE_URL
DATABASE_URL=postgresql://user:password@host:port/database
```

### SSL/HTTPS

Para produção, configure SSL:

1. **Certbot (Let's Encrypt)**:
```bash
sudo certbot --nginx -d seu-dominio.com
```

2. **Cloudflare** (recomendado):
- Configure DNS no Cloudflare
- Ative SSL/TLS automático
- Configure regras de redirecionamento

### Backup

#### Banco de dados
```bash
# SQLite
cp database.db backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump database_name > backup_$(date +%Y%m%d).sql
```

#### Arquivos
```bash
# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz sistema_gestao_agencia/
```

### Monitoramento

#### Logs
```bash
# Ver logs em tempo real
tail -f logs/app.log

# Logs do Uvicorn
uvicorn main:app --log-file logs/uvicorn.log
```

#### Health Check
Endpoint disponível: `GET /health`

### Performance

#### Otimizações
1. **Cache**: Implementar Redis para cache
2. **CDN**: Usar Cloudflare para assets estáticos
3. **Compressão**: Ativar gzip no Nginx
4. **Workers**: Usar múltiplos workers Uvicorn

#### Configuração Nginx otimizada
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    # Compressão
    gzip on;
    gzip_types text/css application/javascript application/json;
    
    # Cache de assets estáticos
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy para aplicação
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Checklist de Deploy

- [ ] Dependências instaladas
- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados configurado
- [ ] SSL/HTTPS configurado
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Testes de funcionalidade
- [ ] Performance otimizada

## Troubleshooting

### Problemas Comuns

1. **Erro de permissão no banco**:
```bash
chmod 664 database.db
chown www-data:www-data database.db
```

2. **Porta já em uso**:
```bash
lsof -i :8000
kill -9 PID
```

3. **Dependências não encontradas**:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Logs de Debug
```bash
# Executar em modo debug
uvicorn main:app --reload --log-level debug
```

## Suporte

Sistema testado e validado para produção. Todas as funcionalidades estão operacionais.

---

**Deploy realizado com sucesso! 🎉**

