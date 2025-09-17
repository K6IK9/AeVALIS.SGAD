# 🚀 Deploy no Vercel - Guia Atualizado

## 📋 Pré-requisitos

1. **Conta no Vercel** - [vercel.com](https://vercel.com)
2. **Banco PostgreSQL** - Neon, Railway, ou outro provedor
3. **Repositório Git** - GitHub, GitLab, ou Bitbucket

## 🛠️ Configuração Passo a Passo

### 1. Preparar o Banco de Dados

Crie um banco PostgreSQL em um dos provedores:
- **Neon** (recomendado) - [neon.tech](https://neon.tech)
- **Railway** - [railway.app](https://railway.app)
- **Supabase** - [supabase.com](https://supabase.com)

### 2. Configurar Variáveis de Ambiente no Vercel

No dashboard do Vercel, vá em:
**Project Settings → Environment Variables**

Adicione as seguintes variáveis:

```
SECRET_KEY=sua-chave-secreta-super-segura-aqui-minimo-50-caracteres
DEBUG=False
DB_NAME=nome_do_seu_banco
DB_USER=usuario_do_banco
DB_PASSWORD=senha_do_banco
DB_HOST=host_do_banco
DB_PORT=5432
```

### 3. Deploy Automático

1. Conecte seu repositório ao Vercel
2. O Vercel detectará automaticamente que é um projeto Python
3. As configurações do `vercel.json` serão aplicadas
4. O script `vercel-build.py` executará automaticamente:
   - Migrações do banco
   - Coleta de arquivos estáticos

### 4. Verificação de Arquivos Estáticos

Após o deploy, acesse:
- `/debug-static/` - Página de debug para testar imagens
- `/static/assets/saad_logo.svg` - Teste direto de arquivos

## 🔧 Configurações Importantes

### Arquivos de Configuração

- `vercel.json` - Configuração principal do Vercel (apenas 1 build)
- `package.json` - Script de build automático
- `vercel-build.py` - Script Python de build
- `requirements.txt` - Dependências Python (incluindo WhiteNoise)
- `.vercelignore` - Arquivos ignorados no deploy

### WhiteNoise para Arquivos Estáticos

O projeto usa WhiteNoise para servir arquivos estáticos em produção:
- Compressão automática
- Cache de longa duração
- Serving eficiente de SVG, PNG, CSS, JS

### Limitações do Vercel (Hobby Plan)

- **Timeout**: 10 segundos por request (configurado para 30s)
- **Memória**: 1024 MB
- **Tamanho**: 250 MB por deploy
- **Bandwidth**: 100 GB/mês

## 🐛 Troubleshooting

### Imagens Não Carregam
```
1. Verifique se DEBUG=False no Vercel
2. Acesse /debug-static/ para testar
3. Confirme que WhiteNoise está no MIDDLEWARE
4. Verifique se collectstatic rodou no build
```

### Erro de Timeout
```
Configurado maxDuration: 30 no vercel.json
CONN_MAX_AGE = 0 para conexões não persistentes
```

### Arquivos Estáticos não Encontrados
```
Verify STATIC_URL = "/static/"
Check STATIC_ROOT = BASE_DIR / "staticfiles"
Ensure WhiteNoise middleware order
```

### Erro de Build
```
Check vercel-build.py logs
Verify environment variables
Test locally: python vercel-build.py
```

## 📚 Recursos Úteis

- [Vercel Python Runtime](https://vercel.com/docs/runtimes/python)
- [Django on Vercel](https://vercel.com/guides/deploying-django-with-vercel)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)

## 🆘 Comandos Úteis

```bash
# Deploy manual
vercel --prod

# Ver logs
vercel logs

# Baixar variáveis de ambiente
vercel env pull

# Testar build localmente
python vercel-build.py

# Testar arquivos estáticos
python manage.py collectstatic --dry-run
```

## 🎯 Principais Mudanças

1. **Apenas 1 build** no vercel.json (removido conflito)
2. **WhiteNoise** gerencia arquivos estáticos
3. **Script Python** para build (vercel-build.py)
4. **Debug page** para testar imagens (/debug-static/)
5. **Configurações otimizadas** para produção
