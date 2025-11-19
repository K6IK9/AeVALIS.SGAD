# 🚀 INSTRUÇÕES RÁPIDAS - ÆVALIS Sistema de Avaliação Docente

## � Pré-requisitos

- Python 3.11.9+
- pip (gerenciador de pacotes Python)
- Git
- PostgreSQL (produção) ou SQLite3 (desenvolvimento)

---

## ⚡ Configuração Rápida

### 1. Clonar o Repositório

```bash
git clone https://github.com/K6IK9/AeVALIS.SGAD.git
cd avaliacao_docente_suap
```

### 2. Criar Ambiente Virtual

```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar .env com suas configurações
nano .env  # ou use seu editor preferido
```

**Variáveis essenciais:**
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_NAME=nome_do_banco
DB_USER=usuario
DB_PASSWORD=senha
DB_HOST=localhost
DB_PORT=5432
```

### 5. Configurar Banco de Dados

```bash
# Aplicar migrações
python manage.py migrate

# Criar superusuário (Admin)
python manage.py createsuperuser
```

### 6. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 7. Executar Servidor

```bash
python manage.py runserver
```

✅ **Acesse**: http://127.0.0.1:8000/

---

## 🩺 Troubleshooting Rápido

### Problema: Imagens/CSS não carregam

```bash
# Coletar arquivos estáticos novamente
python manage.py collectstatic --clear --noinput

# Verificar estrutura
ls static/assets/  # Deve conter logo_curta.svg, logo_extend.svg, etc.
```

### Problema: Erro de SECRET_KEY

```bash
# Gerar nova chave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Adicionar ao .env
echo "SECRET_KEY=<chave_gerada>" >> .env
```

### Problema: Erro de migração

```bash
# Verificar status
python manage.py showmigrations

# Recriar migrações
python manage.py migrate --run-syncdb
```

---

## 📚 Documentação Completa

Para configuração detalhada e solução de problemas:

- **[README.md](../README.md)** - Documentação principal do projeto
- **[STATIC_FILES_README.md](./STATIC_FILES_README.md)** - Arquivos estáticos e assets
- **[DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)** - Deploy em produção
- **[ROLES_MANUAIS.md](./ROLES_MANUAIS.md)** - Sistema de permissões
- **[SISTEMA_LEMBRETES.md](./SISTEMA_LEMBRETES.md)** - Lembretes automáticos
- **[ESTRUTURA_TESTES.md](./ESTRUTURA_TESTES.md)** - Testes automatizados

---

## 🧪 Próximos Passos

1. **Popular banco com dados de teste:**
   ```bash
   python -m scripts.popular_banco_dados
   ```

2. **Acessar Admin Hub:**
   - URL: http://127.0.0.1:8000/admin-hub/
   - Login com o superusuário criado

3. **Configurar sistema:**
   - Criar cursos e disciplinas
   - Cadastrar professores e alunos
   - Configurar ciclos de avaliação

4. **Executar testes:**
   ```bash
   python manage.py test avaliacao_docente
   ```

---

💡 **Dica**: Para deploy em produção, consulte [DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)
