# Sistema de Avaliação Docente - Configuração de Arquivos Estáticos

## 🚨 IMPORTANTE: Problemas com Imagens/Assets

Se você baixou este projeto e as imagens não estão carregando, siga estas instruções:

### 📋 Pré-requisitos

1. Python 3.8+
2. Django 4.2+
3. Todas as dependências do `requirements.txt`

### 🔧 Configuração Rápida

Execute o script de configuração automática:

```bash
python setup_static_files.py
```

### 🔧 Configuração Manual

Se o script automático não funcionar, execute os seguintes comandos:

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar banco de dados
python manage.py migrate

# 3. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 4. Iniciar servidor
python manage.py runserver
```

### 📁 Estrutura de Arquivos Estáticos

```
projeto/
├── static/                    # Arquivos estáticos fonte
│   ├── assets/               # Imagens e ícones
│   │   ├── saad_logo.svg    # Logo principal
│   │   ├── perfil.svg       # Ícone de perfil
│   │   ├── email.svg        # Ícone de email
│   │   ├── eye.svg          # Ícone de visualização
│   │   └── ...              # Outros assets
│   └── image.png            # Imagem adicional
├── staticfiles/              # Arquivos coletados (gerado automaticamente)
└── media/                    # Uploads de usuários
```

### 🔍 Verificação de Problemas

1. **Imagens não carregam**: Verifique se existe `static/assets/` com os arquivos SVG
2. **Erro 404 em /static/**: Execute `python manage.py collectstatic`
3. **Paths incorretos**: Certifique-se de que `STATICFILES_DIRS` aponta para o diretório correto

### 🛠️ Solução de Problemas Comuns

#### Problema: "Static files not found"
```bash
# Solução
python manage.py collectstatic --clear --noinput
```

#### Problema: "Assets não carregam"
```bash
# Verifique se os arquivos existem
ls static/assets/

# Se não existirem, copie do diretório staticfiles
cp -r staticfiles/assets static/
```

#### Problema: "Permission denied"
```bash
# No Windows
icacls static /grant Everyone:F /T

# No Linux/Mac
chmod -R 755 static/
```

### 🔗 URLs de Arquivos Estáticos

- **Desenvolvimento**: `http://127.0.0.1:8000/static/`
- **Produção**: Configurado via `STATIC_ROOT`

### 📝 Configurações Importantes

No arquivo `settings.py`:

```python
# Configurações de arquivos estáticos
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

No arquivo `urls.py`:

```python
# Servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
```

### 🎯 Teste Rápido

Após a configuração, teste acessando:
- `http://127.0.0.1:8000/static/assets/saad_logo.svg`
- `http://127.0.0.1:8000/static/assets/perfil.svg`

Se os arquivos carregarem diretamente, o problema está resolvido!

### 📞 Suporte

Se ainda houver problemas:
1. Verifique os logs do Django
2. Certifique-se de que `DEBUG = True` em desenvolvimento
3. Verifique se o diretório `static/assets/` existe e contém os arquivos SVG

---

## 🚀 Executar o Projeto

Após configurar os arquivos estáticos:

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000`
