# ÆVALIS — Sistema de Avaliação Docente

[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11.9-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sobre o Projeto

O **ÆVALIS** (Sistema de Avaliação Docente) é uma aplicação web desenvolvida em Django para o Instituto Federal de Mato Grosso (IFMT). O sistema permite a gestão completa e avaliação de desempenho de professores por alunos, seguindo a Resolução 87/2023 que regulamenta a avaliação de desempenho docente.

### ✨ Principais Funcionalidades

#### 🔐 Autenticação e Segurança
- **Login SUAP OAuth2**: Integração com o Sistema Unificado de Administração Pública do IFMT
- **Login Tradicional**: Suporte para usuários e senha convencionais
- **Auto-login Inteligente**: Detecta e autentica automaticamente usuários já cadastrados
- **Sistema de Roles**: Quatro perfis de usuário (Admin, Coordenador, Professor, Aluno) com permissões granulares

#### 👥 Gestão Administrativa
- **Gerenciamento de Usuários**: CRUD completo com controle de roles e perfis
- **Cursos e Disciplinas**: Administração da estrutura acadêmica
- **Períodos Letivos**: Controle de semestres e anos letivos
- **Turmas**: Gestão de turmas com professores e alunos matriculados
- **Matrículas**: Sistema de vínculo aluno-turma com controle de status

#### 📊 Sistema de Avaliações
- **Ciclos de Avaliação**: Períodos configuráveis com datas de início e fim
- **Questionários Personalizáveis**: Criação de perguntas por categorias
- **Avaliações Anônimas**: Resposta de alunos sem identificação
- **Relatórios por Professor**: Visualização de médias e desempenho
- **Soft Delete**: Preservação de dados históricos mesmo após exclusão

#### 🔔 Sistema de Lembretes (Em Desenvolvimento)
- **Notificações por Email**: Lembretes automáticos sobre prazos de avaliação
- **Configuração Flexível**: Definição de dias antes do fim do ciclo para envio
- **SendGrid Integration**: Sistema de envio de emails em massa

#### 🎨 Interface e Experiência
- **Design Responsivo**: Interface adaptativa para desktop, tablet e mobile
- **Branding Customizável**: Sistema de marca com logos e cores personalizáveis
- **Mensagens de Feedback**: Sistema de notificações para ações do usuário
- **WhiteNoise**: Servir arquivos estáticos com compressão e cache

### 🏗️ Arquitetura do Sistema

- **Backend**: Django 5.2.6 com Python 3.11.9
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla) com templates Django
- **Banco de Dados**: PostgreSQL (produção via Vercel) / SQLite3 (desenvolvimento)
- **Autenticação**: Python Social Auth + Django Auth (dual authentication)
- **Deploy**: Vercel com Serverless Functions
- **Static Files**: WhiteNoise com manifest e compressão
- **Email**: SendGrid para notificações

## 📚 Documentação

Para informações detalhadas sobre instalação, configuração, deployment e práticas de desenvolvimento, consulte a **[pasta de documentação](./docs/README.md)**.

### 📖 Documentos Principais

| Documento | Descrição |
|-----------|-----------|
| **[Setup Rápido](./docs/SETUP_RAPIDO.md)** | Guia de instalação e configuração inicial |
| **[Deploy Vercel](./docs/DEPLOY_VERCEL.md)** | Instruções completas para deploy em produção |
| **[Gerenciamento de Roles](./docs/ROLES_MANUAIS.md)** | Manual de roles automáticas vs manuais |
| **[Arquivos Estáticos](./docs/STATIC_FILES_README.md)** | Configuração e solução de problemas com assets |
| **[Sistema de Lembretes](./docs/SISTEMA_LEMBRETES.md)** | Configuração de notificações por email |
| **[Estrutura de Testes](./docs/ESTRUTURA_TESTES.md)** | Guia completo sobre testes automatizados |
| **[Changelog Branding](./docs/CHANGELOG_BRANDING.md)** | Histórico de mudanças na identidade visual |

### 👥 Sistema de Permissões

O sistema utiliza 4 roles baseadas no `django-role-permissions` com permissões específicas:

#### 🔧 **Admin**
- ✅ Acesso total ao sistema
- ✅ Gerenciamento completo de usuários e roles
- ✅ Configuração do site e parâmetros globais
- ✅ Acesso ao painel administrativo Django

#### 📊 **Coordenador**
- ✅ Gestão de cursos, disciplinas e turmas
- ✅ Criação e configuração de ciclos de avaliação
- ✅ Gerenciamento de questionários
- ✅ Visualização de relatórios gerais
- ❌ Sem acesso a gerenciamento de usuários

#### 👨‍🏫 **Professor**
- ✅ Visualização de suas próprias avaliações
- ✅ Acesso a relatórios de desempenho pessoal
- ✅ Gerenciamento de perfil
- ❌ Sem permissão para editar estrutura acadêmica

#### 🎓 **Aluno**
- ✅ Responder avaliações dentro dos ciclos ativos
- ✅ Visualizar turmas em que está matriculado
- ✅ Gerenciamento de perfil básico
- ❌ Acesso restrito apenas às próprias avaliações

> **Nota**: As roles são atribuídas automaticamente via SUAP OAuth2 baseadas no campo `tipo_usuario`, mas podem ser gerenciadas manualmente por administradores.

## 🚀 Como Executar o Projeto

### 📋 Pré-requisitos

- Python 3.11.9+ (especificado em `runtime.txt`)
- pip (gerenciador de pacotes Python)
- Git
- PostgreSQL (produção) ou SQLite3 (desenvolvimento)

### 🔧 Instalação e Configuração

#### � Variáveis de Ambiente Necessárias

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```env
# Django Core
SECRET_KEY=sua-chave-secreta-django-aqui
DEBUG=True

# Banco de Dados PostgreSQL (Produção)
DB_NAME=nome_do_banco
DB_USER=usuario_postgres
DB_PASSWORD=senha_postgres
DB_HOST=host_do_banco
DB_PORT=5432

# Autenticação SUAP OAuth2
SOCIAL_AUTH_SUAP_KEY=sua_chave_api_suap
SOCIAL_AUTH_SUAP_SECRET=seu_secret_api_suap

# Email (SendGrid) - Opcional
SENDGRID_API_KEY=sua_chave_sendgrid
DEFAULT_FROM_EMAIL=noreply@seudominio.com
ADMIN_EMAIL=admin@seudominio.com

# Branding (Opcional)
BRAND_ENABLE_NEW=True
```

> **⚠️ IMPORTANTE**: 
> - **Nunca commite** o arquivo `.env` no repositório!
> - Use `.env.example` como referência para as variáveis necessárias
> - Em produção, gere uma `SECRET_KEY` complexa e segura

#### 🚀 Instalação Automatizada (Recomendada)

**Não disponível neste projeto**. Use a instalação manual abaixo.

#### 📋 Instalação Manual

##### 1. Clone o repositório
```bash
git clone https://github.com/K6IK9/AeVALIS.SGAD.git
cd avaliacao_docente_suap
```

##### 2. Crie e ative um ambiente virtual
```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

##### 3. Instale as dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

##### 4. Configure as variáveis de ambiente
```bash
# Copie o template de exemplo
cp .env.example .env

# Edite o .env com suas configurações
nano .env  # ou use seu editor preferido
```

##### 5. Execute as migrações do banco de dados
```bash
python manage.py makemigrations
python manage.py migrate
```

##### 6. Colete arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

##### 7. Crie um superusuário (Admin)
```bash
python manage.py createsuperuser
```
Forneça:
- **Username** (será usado para login)
- **Email** (opcional, mas recomendado)
- **Password** (mínimo 8 caracteres)

##### 8. Execute o servidor de desenvolvimento
```bash
python manage.py runserver
```

✅ **O sistema estará disponível em**: `http://127.0.0.1:8000/`

### 🔑 Configurando OAuth2 com SUAP

Para habilitar login com SUAP, você precisa:

1. **Registrar aplicação no SUAP**:
   - Acesse o painel de desenvolvedores do SUAP IFMT
   - Crie uma nova aplicação OAuth2
   - Copie `Client ID` e `Client Secret`

2. **Configurar no `.env`**:
   ```env
   SOCIAL_AUTH_SUAP_KEY=seu_client_id_aqui
   SOCIAL_AUTH_SUAP_SECRET=seu_client_secret_aqui
   ```

3. **Configurar URL de callback**:
   - Desenvolvimento: `http://127.0.0.1:8000/complete/suap/`
   - Produção: `https://seudominio.com/complete/suap/`

> **Nota**: Em desenvolvimento, certificados SSL são automaticamente desabilitados para conexões SUAP. **NÃO USE EM PRODUÇÃO!**

### 🎯 Acessando o Sistema

#### 📱 Interface Principal
- **URL**: `http://127.0.0.1:8000/`
- **Login**: Use credenciais do superusuário ou login SUAP (se configurado)

#### ⚙️ Painel Administrativo Django
- **URL**: `http://127.0.0.1:8000/admin/`
- **Acesso**: Apenas para superusuários
- **Funcionalidades**: Gerenciamento direto do banco de dados

#### 🏠 Admin Hub (Interface Customizada)
- **URL**: `http://127.0.0.1:8000/admin-hub/`
- **Acesso**: Usuários com role `admin` ou `coordenador`
- **Funcionalidades**: Interface amigável para gestão acadêmica

### 📊 Configuração Inicial do Sistema

Após criar o superusuário, siga esta sequência para configurar o sistema:

#### 1️⃣ **Criar Cursos** (`/admin-hub/cursos/`)
- Nome completo do curso
- Sigla/código
- Modalidade (Técnico, Graduação, etc.)

#### 2️⃣ **Criar Disciplinas** (`/admin-hub/disciplinas/`)
- Nome da disciplina
- Código
- Vincular ao curso
- Carga horária

#### 3️⃣ **Definir Períodos Letivos** (`/admin-hub/periodos/`)
- Ano letivo
- Semestre (1 ou 2)
- Datas de início e fim

#### 4️⃣ **Cadastrar Professores**
- Criar usuários com role `professor`
- Preencher perfil de professor (área de atuação, titulação, etc.)

#### 5️⃣ **Criar Turmas** (`/admin-hub/turmas/`)
- Vincular: Disciplina + Professor + Período
- Definir código da turma
- Configurar horários (opcional)

#### 6️⃣ **Matricular Alunos nas Turmas** (`/admin-hub/turmas/<id>/alunos/`)
- Cadastrar alunos como usuários
- Vincular alunos às turmas específicas
- Definir status da matrícula (Ativo/Concluído/Trancado)

#### 7️⃣ **Configurar Questionário de Avaliação** (`/admin-hub/questionarios/`)
- Criar categorias de perguntas (Didática, Metodologia, Relacionamento, etc.)
- Adicionar perguntas vinculadas às categorias
- Definir ordem de exibição

#### 8️⃣ **Criar Ciclos de Avaliação** (`/admin-hub/ciclos/`)
- Definir período de vigência (data_inicio, data_fim)
- Vincular ao período letivo
- Ativar questionário padrão

#### 9️⃣ **Configurar Sistema de Lembretes** (Opcional)
- Acessar configurações do site
- Definir dias antes do fim do ciclo para lembrete
- Configurar método de envio (Email/Interface)
- Testar envio de emails

> **✅ Pronto!** Com esses passos, o sistema estará pronto para que alunos respondam avaliações durante os ciclos ativos.

### 🛠️ Scripts Auxiliares

O projeto inclui scripts na pasta `/scripts/` para auxiliar em tarefas específicas:

#### 📋 Scripts Disponíveis

| Script | Função | Execução |
|--------|---------|----------|
| `popular_banco_dados.py` | Popula banco com dados fictícios para testes | `python -m scripts.popular_banco_dados` |
| `atualizar_ciclos_encerrado.py` | Atualiza status de ciclos expirados | `python -m scripts.atualizar_ciclos_encerrado` |
| `validar_calculos_media.py` | Valida cálculos de média das avaliações | `python -m scripts.validar_calculos_media` |
| `auditoria_models.py` | Analisa estrutura de models e relacionamentos | `python -m scripts.auditoria_models` |
| `update_brand_titles.py` | Atualiza títulos de páginas com nova marca | `python -m scripts.update_brand_titles` |

#### 🧪 Testes Manuais

Scripts exploratórios em `/scripts/manual_tests/`:

```bash
# Testar refatoração de turma
python -m scripts.manual_tests.test_refatoracao_turma

# Testar soft delete
python -m scripts.manual_tests.test_soft_delete
```

> 💡 **Dica**: Execute `python -m scripts.popular_banco_dados` após a configuração inicial para ter dados de teste no sistema! 


### 🔧 Desenvolvimento

#### Estrutura do Projeto
```
avaliacao_docente_suap/
├── avaliacao_docente/              # App principal Django
│   ├── models/                     # Models modularizados
│   │   ├── __init__.py            # Exportações dos models
│   │   ├── base.py                # BaseModel (classe base)
│   │   ├── mixins.py              # Mixins reutilizáveis (Timestamp, SoftDelete, etc)
│   │   ├── managers.py            # Custom managers (SoftDeleteManager)
│   │   ├── models_originais.py   # Models concretos do sistema
│   │   └── lembretes.py           # Models de notificações
│   ├── views.py                   # Views (CBV e FBV)
│   ├── forms.py                   # Formulários Django
│   ├── urls.py                    # URLs do app
│   ├── services.py                # Lógica de negócio
│   ├── signals.py                 # Signals (pré/pós save)
│   ├── utils.py                   # Utilitários gerais
│   ├── auth_pipeline.py           # Pipeline customizado OAuth2
│   ├── middleware.py              # Middlewares (SocialAuth, Messages)
│   ├── enums.py                   # Enumerações (StatusMatricula, etc)
│   ├── templatetags/              # Custom template tags
│   ├── management/commands/       # Comandos customizados
│   ├── migrations/                # Migrações do banco
│   └── tests/                     # Testes automatizados
│       ├── test_core.py          # Testes principais
│       ├── test_abstracoes.py    # Testes de mixins
│       └── test_refatoracao_turma.py
├── setup/                          # Configurações Django
│   ├── settings.py                # Settings principal
│   ├── urls.py                    # URLs raiz
│   ├── roles.py                   # Definição de roles
│   ├── brand.py                   # Context processor de branding
│   ├── wsgi.py                    # WSGI para produção
│   └── asgi.py                    # ASGI (async)
├── suap_backend/                   # Backend OAuth2 SUAP
│   └── backends.py                # Classe SuapOAuth2
├── templates/                      # Templates globais
│   ├── registration/              # Login, logout
│   ├── avaliacoes/                # Templates de avaliação
│   ├── partials/                  # Componentes reutilizáveis
│   └── *.html                     # Templates de CRUD
├── static/                         # Assets fonte
│   ├── css/                       # Estilos customizados
│   ├── js/                        # Scripts JavaScript
│   └── assets/                    # Imagens, logos, ícones
├── staticfiles/                    # Arquivos coletados (gerado)
├── scripts/                        # Scripts auxiliares
│   ├── popular_banco_dados.py
│   ├── atualizar_ciclos_encerrado.py
│   └── manual_tests/              # Testes exploratórios
├── docs/                           # Documentação técnica
├── .env                            # Variáveis de ambiente (não commitado)
├── .env.example                    # Template de .env
├── requirements.txt                # Dependências Python
├── runtime.txt                     # Versão Python para Vercel
├── vercel.json                     # Configuração Vercel
├── vercel-build.sh                # Script de build Vercel
└── manage.py                       # CLI Django
```

#### Comandos Úteis

```bash
# 🗄️ Banco de Dados
python manage.py makemigrations          # Criar migrações
python manage.py migrate                 # Aplicar migrações
python manage.py showmigrations          # Listar status de migrações
python manage.py dbshell                 # Shell do banco de dados

# 👤 Usuários
python manage.py createsuperuser         # Criar superusuário
python manage.py changepassword <user>   # Alterar senha de usuário

# 🧪 Testes
python manage.py test                           # Todos os testes
python manage.py test avaliacao_docente         # Testes do app
python manage.py test avaliacao_docente.tests.test_core  # Módulo específico
python manage.py test --verbosity=2             # Com mais detalhes
python manage.py test --keepdb                  # Reutilizar banco de teste

# 📁 Arquivos Estáticos
python manage.py collectstatic --noinput  # Coletar para staticfiles/
python manage.py findstatic <arquivo>     # Localizar arquivo estático

# 🔍 Desenvolvimento
python manage.py shell                    # Shell Python com Django
python manage.py shell_plus               # Shell com models carregados (se django-extensions)
python manage.py runserver                # Servidor desenvolvimento
python manage.py runserver 0.0.0.0:8000  # Acessível externamente

# 🛠️ Utilitários
python manage.py check                    # Verificar erros no projeto
python manage.py diffsettings             # Comparar settings com padrão
python manage.py inspectdb               # Gerar models a partir do DB
python manage.py sqlmigrate avaliacao_docente 0001  # Ver SQL de migração

# 📊 Scripts Customizados
python -m scripts.popular_banco_dados     # Popular com dados de teste
python -m scripts.atualizar_ciclos_encerrado  # Atualizar ciclos expirados
```

### 🛠️ Tecnologias e Dependências

#### Backend
- **Django 5.2.6** - Framework web Python
- **Python 3.11.9** - Linguagem de programação
- **psycopg2-binary 2.9.10** - Driver PostgreSQL
- **django-role-permissions 3.2.0** - Sistema de roles e permissões
- **social-auth-app-django 5.4.2** - Autenticação social (OAuth2)
- **social-auth-core 4.5.4** - Core do social auth
- **python-decouple 3.8** - Gerenciamento de configurações/.env

#### Frontend
- **HTML5** - Estrutura semântica
- **CSS3** - Estilos (Flexbox, Grid, Custom Properties)
- **JavaScript (Vanilla)** - Interatividade sem frameworks
- **Font Awesome 6** - Ícones
- **Google Fonts** - Tipografia (Inter, Poppins)

#### Infraestrutura
- **WhiteNoise 6.7.0** - Servir arquivos estáticos com compressão
- **SendGrid 6.11.0** - Envio de emails transacionais
- **Vercel** - Plataforma de deploy serverless
- **PostgreSQL** - Banco de dados relacional (produção)
- **SQLite3** - Banco de dados (desenvolvimento)

#### Desenvolvimento
- **Git** - Controle de versão
- **GitHub** - Repositório remoto
- **VSCode** - Editor recomendado
- **Python Black** - Formatador de código (recomendado)
- **Flake8** - Linter Python (recomendado)

## 🔧 Troubleshooting

### �️ Scripts de Apoio

O projeto inclui vários scripts úteis para instalação e diagnóstico:

#### 📁 Scripts Disponíveis

| Script | Descrição | Uso |
|--------|-----------|-----|
| `setup_projeto.py` | **Setup automático completo** - Configura todo o projeto do zero | `python setup_projeto.py` |
| `diagnose_static.py` | **Diagnóstico de arquivos estáticos** - Identifica problemas com imagens/CSS | `python diagnose_static.py` |
| `setup_static_files.py` | **Configuração específica de assets** - Resolve problemas com arquivos estáticos | `python setup_static_files.py` |

#### 🚀 Como Usar os Scripts

**Para primeira instalação:**
```bash
python setup_projeto.py
```

**Para problemas com imagens/CSS:**
```bash
python diagnose_static.py
```

**Para reconfigurar apenas arquivos estáticos:**
```bash
python setup_static_files.py
```

#### 📋 Documentação Adicional

- **[docs/SETUP_RAPIDO.md](./docs/SETUP_RAPIDO.md)**: Instruções rápidas para instalação
- **[docs/STATIC_FILES_README.md](./docs/STATIC_FILES_README.md)**: Documentação detalhada sobre arquivos estáticos
- **[Documentação completa](./docs/README.md)**: Todos os manuais e práticas de desenvolvimento

### �🖼️ Problemas com Carregamento de Imagens/Arquivos Estáticos

Se as imagens ou arquivos CSS/JS não estiverem carregando, siga estes passos:

#### 1. Execute o diagnóstico automático
```bash
python diagnose_static.py
```

#### 2. Ou configure manualmente os arquivos estáticos
```bash
python setup_static_files.py
```

#### 3. Verificar configurações de arquivos estáticos no settings.py
```python
# Certifique-se de que estas configurações estão no settings.py:
import os

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Para arquivos de mídia (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### 4. Coletar arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

#### 5. Verificar URLs principais
No arquivo `setup/urls.py`, certifique-se de que há:
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # suas URLs aqui
]

# Adicionar estas linhas para servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 6. Verificar estrutura de pastas
Certifique-se de que a estrutura está assim:
```
avaliacao_docente_novo/
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ...
├── media/              # Para uploads de usuários
└── staticfiles/        # Gerado pelo collectstatic
```


---

## 🧪 Testes

### Estrutura de Testes

O projeto possui uma suíte completa de testes em `avaliacao_docente/tests/`:

- **test_core.py**: Testes principais de models, views, forms e integração
- **test_abstracoes.py**: Testes de mixins (SoftDelete, Timestamp, BaseModel)
- **test_refatoracao_turma.py**: Testes de regressão após refatoração

### Executando Testes

```bash
# Todos os testes do app
python manage.py test avaliacao_docente

# Módulo específico
python manage.py test avaliacao_docente.tests.test_core

# Com verbosidade aumentada
python manage.py test avaliacao_docente --verbosity=2

# Mantendo banco de dados de teste (acelera reruns)
python manage.py test --keepdb

# Testes paralelos (mais rápido)
python manage.py test --parallel=auto
```

### Scripts de Validação Manual

Scripts exploratórios em `/scripts/manual_tests/`:

```bash
# Testar refatoração de turma
python -m scripts.manual_tests.test_refatoracao_turma

# Testar soft delete
python -m scripts.manual_tests.test_soft_delete
```

---

## 🚀 Deploy em Produção

### Vercel (Plataforma Recomendada)

O projeto está configurado para deploy no Vercel com PostgreSQL:

1. **Criar conta** no [Vercel](https://vercel.com)
2. **Importar repositório** do GitHub
3. **Configurar variáveis de ambiente**:
   - Adicionar todas as variáveis do `.env.example`
   - Gerar nova `SECRET_KEY` para produção
   - Configurar credenciais do banco PostgreSQL

4. **Deploy automático**:
   ```bash
   git push origin main  # Deploy automático via GitHub
   ```

5. **Executar migrações**:
   ```bash
   vercel env pull .env.vercel  # Baixar variáveis de ambiente
   python manage.py migrate     # Aplicar migrações
   ```

### Configuração Vercel

O arquivo `vercel.json` já está configurado:

```json
{
    "builds": [{
        "src": "setup/wsgi.py",
        "use": "@vercel/python",
        "config": { "maxLambdaSize": "15mb", "runtime": "python3.11" }
    }],
    "routes": [{"src": "/(.*)", "dest": "setup/wsgi.py"}]
}
```

### Checklist Pré-Deploy

- [ ] `DEBUG = False` em produção
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] Variáveis de ambiente definidas no Vercel
- [ ] Banco PostgreSQL provisionado
- [ ] SendGrid API Key configurada (se usar emails)
- [ ] SUAP OAuth2 credentials atualizadas com URL de produção
- [ ] `python manage.py collectstatic` executado no build
- [ ] Migrações aplicadas no banco de produção

📘 **Documentação Completa**: Veja [docs/DEPLOY_VERCEL.md](./docs/DEPLOY_VERCEL.md) para instruções detalhadas.

---

## 🤝 Contribuindo

### Workflow de Contribuição

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/seu-usuario/AeVALIS.SGAD.git
   ```
3. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/minha-feature
   ```
4. **Faça commit** das mudanças:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade X"
   ```
5. **Push** para seu fork:
   ```bash
   git push origin feature/minha-feature
   ```
6. **Abra um Pull Request** no repositório original

### Padrões de Commit

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Atualização de documentação
- `style:` Formatação de código
- `refactor:` Refatoração sem mudança de funcionalidade
- `test:` Adição ou correção de testes
- `chore:` Tarefas de manutenção

### Padrões de Código

- **Python**: Seguir [PEP 8](https://pep8.org/)
- **Django**: Seguir [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- **Formatação**: Use `black` (recomendado)
- **Linting**: Use `flake8` ou `pylint`
- **Docstrings**: Formato Google ou NumPy

### Executando Code Quality

```bash
# Formatar código
black .

# Linting
flake8 avaliacao_docente setup

# Type checking (opcional)
mypy avaliacao_docente
```

---

## 📞 Suporte e Contato

### 📚 Documentação
- **Documentação Completa**: [/docs/README.md](./docs/README.md)
- **FAQ**: [/docs/SETUP_RAPIDO.md](./docs/SETUP_RAPIDO.md)

### 🐛 Reportando Bugs
- Abra uma [Issue no GitHub](https://github.com/K6IK9/AeVALIS.SGAD/issues)
- Inclua: descrição do erro, steps to reproduce, ambiente (SO, Python, Django)

### 💡 Solicitando Features
- Abra uma [Issue de Feature Request](https://github.com/K6IK9/AeVALIS.SGAD/issues/new)
- Descreva o caso de uso e benefícios esperados

### 👥 Equipe
- **Desenvolvedor Principal**: [K6IK9](https://github.com/K6IK9)
- **Instituição**: Instituto Federal de Mato Grosso (IFMT)

---

## 📝 Licença

Este projeto está sob a licença especificada no arquivo [LICENSE](LICENSE).

---

## 📊 Estatísticas do Projeto

![GitHub repo size](https://img.shields.io/github/repo-size/K6IK9/AeVALIS.SGAD)
![GitHub language count](https://img.shields.io/github/languages/count/K6IK9/AeVALIS.SGAD)
![GitHub top language](https://img.shields.io/github/languages/top/K6IK9/AeVALIS.SGAD)
![GitHub last commit](https://img.shields.io/github/last-commit/K6IK9/AeVALIS.SGAD)

---

<p align="center">
  <strong>Desenvolvido com ❤️ para o Instituto Federal de Mato Grosso</strong>
  <br>
  <sub>ÆVALIS - Sistema de Avaliação Docente</sub>
</p>
