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
│   │   ├── logo_curta.svg   # Logo ÆVALIS compacta (navbar) - 120x120
│   │   ├── logo_extend.svg  # Logo ÆVALIS estendida (login/header) - 350x110
│   │   ├── logo_glass.svg   # Logo ÆVALIS glass (transparente) - 350x110
│   │   ├── saad_logo.svg    # Logo antiga (fallback)
│   │   ├── favicon-192.png  # Favicon PWA Android - 192x192
│   │   ├── favicon-512.png  # Favicon PWA splash - 512x512
│   │   ├── apple-touch-icon.png  # Favicon iOS - 180x180
│   │   ├── perfil.svg       # Ícone de perfil
│   │   ├── email.svg        # Ícone de email
│   │   ├── eye.svg          # Ícone de visualização
│   │   └── ...              # Outros assets
│   ├── image.png            # Imagem adicional
│   └── favicon.ico          # Favicon multi-resolução (16/32/48/64)
├── staticfiles/              # Arquivos coletados (gerado automaticamente)
└── media/                    # Uploads de usuários
```

### 🎨 Sobre os Favicons

Os favicons foram otimizados para garantir legibilidade em tamanhos pequenos:

- **favicon.ico**: Multi-resolução (16x16, 32x32, 48x64, 64x64)
  - Usa verde vibrante (#00FD94) para 16x16 e 32x32
  - Usa verde médio (#376F6C) para 48x48 e 64x64
  - Inclui "A" do ÆVALIS simplificado com 3 barras vermelhas (#F02D3A)

- **favicon-192.png / favicon-512.png**: Para PWA e Android
- **apple-touch-icon.png**: Para dispositivos iOS

Os favicons são incluídos automaticamente via `{% include 'partials/favicon_meta.html' %}` em todos os templates.

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
- **Assets de marca**: 
  - Logo curta: `/static/assets/logo_curta.svg`
  - Logo estendida: `/static/assets/logo_extend.svg`
  - Logo glass: `/static/assets/logo_glass.svg`
  - Favicons: `/static/favicon.ico`, `/static/assets/favicon-192.png`, etc.

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
