# Changelog: Rebranding para ÆVALIS

**Data:** 23 de outubro de 2025  
**Versão:** 2.0.0 (Rebranding)  
**Status:** ⚠️ **PREPARADO** (Aguardando ativação via flag `BRAND_ENABLE_NEW=True`)

---

## 📋 Resumo Executivo

Este documento descreve o rebranding completo do sistema de **"IF SADD"** para **"ÆVALIS — Sistema de Avaliação Docente"**.

### Mudanças Principais

- **Nome curto:** ÆVALIS (marca registrada)
- **Nome completo:** Sistema de Avaliação Docente
- **Novos assets:** 3 logos SVG (curta, estendida, glass)
- **Infraestrutura:** Sistema parametrizável com fallback para marca antiga

---

## 🎨 Novos Assets de Marca

### Logos Adicionadas

| Arquivo | Uso Recomendado | Dimensões | Formato |
|---------|-----------------|-----------|---------|
| `static/assets/logo_curta.svg` | Navbar, cabeçalhos compactos | Otimizado para 120×40px | SVG |
| `static/assets/logo_extend.svg` | Página de login, rodapés, headers | Otimizado para 300×80px | SVG |
| `static/assets/logo_glass.svg` | Fundos escuros, transparentes | Otimizado para 200×200px | SVG |

### Arquivo Antigo (Mantido para Fallback)

- `static/assets/saad_logo.svg` → Mantido como fallback quando `BRAND_ENABLE_NEW=False`

---

## 🔧 Infraestrutura Técnica

### 1. Configurações em `setup/settings.py`

```python
# Flag de ativação (padrão: False)
BRAND_ENABLE_NEW = config("BRAND_ENABLE_NEW", cast=bool, default=False)

# Nomes da marca
BRAND_NAME_FULL = "Sistema de Avaliação Docente"
BRAND_NAME_SHORT = "ÆVALIS"
BRAND_NAME_OLD = "IF SADD"

# Paths dos assets (com fallback automático)
BRAND_ASSETS = {
    "logo_curta": "assets/logo_curta.svg" if BRAND_ENABLE_NEW else "assets/saad_logo.svg",
    "logo_extend": "assets/logo_extend.svg" if BRAND_ENABLE_NEW else "assets/saad_logo.svg",
    "logo_glass": "assets/logo_glass.svg" if BRAND_ENABLE_NEW else "assets/saad_logo.svg",
}

# Textos de acessibilidade
BRAND_ALT_TEXT = {
    "logo_curta": f"{BRAND_NAME_SHORT} — {BRAND_NAME_FULL}" if BRAND_ENABLE_NEW else BRAND_NAME_OLD,
    # ... (ver settings.py completo)
}
```

### 2. Context Processor (`setup/brand.py`)

Injeta variáveis de marca em todos os templates automaticamente:

```django
{{ brand.name_short }}   → "ÆVALIS" ou "IF SADD"
{{ brand.name_full }}    → "Sistema de Avaliação Docente"
{{ brand.logo_curta }}   → Path da logo (com fallback automático)
{{ brand.alt.logo_curta }} → Texto alt para acessibilidade
```

---

## 📝 Arquivos Modificados

### Templates Atualizados (24 arquivos)

#### Principais
- `templates/inicial.html` → Logo navbar + título dinâmico
- `templates/perfil.html` → Logo navbar + título
- `templates/registration/login.html` → Logo extend (header) + logo glass (aside) + títulos

#### Templates de Gerenciamento (9 arquivos)
- `gerenciar_usuarios.html`
- `gerenciar_cursos.html`
- `gerenciar_disciplinas.html`
- `gerenciar_turmas.html`
- `gerenciar_periodos.html`
- `gerenciar_questionarios.html`
- `gerenciar_categorias.html`
- `gerenciar_ciclos.html`
- `gerenciar_alunos_turma.html`

#### Admin (3 arquivos)
- `admin/admin_hub.html`
- `admin/gerenciar_configuracao.html`
- `admin/dashboard_gestao_ciclos.html`

#### Avaliações (8 arquivos)
- `avaliacoes/listar_avaliacoes.html`
- `avaliacoes/relatorio_avaliacoes.html`
- `avaliacoes/responder_avaliacao.html`
- `avaliacoes/visualizar_avaliacao.html`
- `avaliacoes/editar_questionario_perguntas.html`
- `avaliacoes/detalhe_ciclo.html`
- `avaliacoes/relatorio_professores.html`
- `avaliacoes/detalhe_professor_relatorio.html`

#### Emails (1 arquivo)
- `emails/notificacao_avaliacao.html` → Footer dinâmico

#### Registro
- `registration/register.html` → Título + menção institucional

### Documentação Atualizada (3 arquivos)

- `README.md` → Título principal atualizado para "ÆVALIS"
- `docs/STATIC_FILES_README.md` → Estrutura de assets atualizada
- `docs/DEPLOY_VERCEL.md` → URLs de teste atualizadas (pendente)

### Código Python

- `setup/settings.py` → Adicionadas configurações de branding (linhas 284-307)
- `setup/brand.py` → **Novo arquivo** - Context processor de branding

---

## 🚀 Como Ativar a Nova Marca

### Passo 1: Configurar Variável de Ambiente

Adicione ao arquivo `.env`:

```env
BRAND_ENABLE_NEW=True
```

### Passo 2: Verificar Assets

Confirme que os novos SVGs existem:

```bash
ls -lh static/assets/logo*.svg
```

Saída esperada:
```
-rw-r--r-- 1 user user  12K Oct 23 20:00 logo_curta.svg
-rw-r--r-- 1 user user  18K Oct 23 20:00 logo_extend.svg
-rw-r--r-- 1 user user  15K Oct 23 20:00 logo_glass.svg
-rw-r--r-- 1 user user  20K Oct 01 10:00 saad_logo.svg  ← fallback
```

### Passo 3: Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### Passo 4: Reiniciar Servidor

```bash
python manage.py runserver
```

### Passo 5: Validar Visualmente

Acesse:
- Login: `http://127.0.0.1:8000/accounts/login/` → Deve exibir logo ÆVALIS
- Inicial: `http://127.0.0.1:8000/` → Navbar com logo_curta
- Perfil: `http://127.0.0.1:8000/perfil/` → Navbar com logo_curta

---

## 🔄 Rollback (Reverter para Marca Antiga)

### Opção 1: Desativar via .env

```env
BRAND_ENABLE_NEW=False
```

Reinicie o servidor → Volta para "IF SADD" automaticamente.

### Opção 2: Rollback Git

```bash
git revert HEAD~1  # Reverte último commit de branding
python manage.py collectstatic --noinput
```

---

## 🎯 Deploy em Produção

### Vercel / Railway / Render

1. **Adicionar variável de ambiente:**
   - Painel → Settings → Environment Variables
   - Adicionar: `BRAND_ENABLE_NEW=True`

2. **Cache Busting:**
   - WhiteNoise já gerencia versioning automático
   - Assets terão hash único: `logo_curta.abc123.svg`

3. **CDN (se aplicável):**
   ```bash
   # Limpar cache Cloudflare/Vercel
   vercel env pull  # Atualizar variáveis locais
   ```

4. **Validação Pós-Deploy:**
   - Testar `/static/assets/logo_curta.svg` → Deve retornar 200
   - Inspecionar HTML → `<title>` deve exibir "ÆVALIS"
   - Verificar alt/title dos `<img>` → Acessibilidade OK

---

## ✅ Checklist de Validação

### Visual
- [ ] Login exibe logo ÆVALIS estendida no header
- [ ] Login exibe logo glass no aside
- [ ] Navbar (inicial/perfil) exibe logo curta
- [ ] Títulos de páginas exibem "ÆVALIS" no navegador
- [ ] Emails HTML exibem "Sistema de Avaliação Docente" no footer

### Técnico
- [ ] Nenhum erro 404 em `/static/assets/`
- [ ] `alt` e `title` textos corretos (acessibilidade)
- [ ] Logos escalam corretamente (SVG responsivo)
- [ ] Modo escuro/claro funciona (se aplicável)

### Documentação
- [ ] README.md atualizado
- [ ] STATIC_FILES_README.md atualizado
- [ ] CHANGELOG_BRANDING.md criado (este arquivo)

### Deploy
- [ ] Variável `BRAND_ENABLE_NEW` configurada
- [ ] `collectstatic` executado
- [ ] Cache limpo (CDN)
- [ ] Testes de navegação OK

---

## 📊 Impacto e Métricas

### Arquivos Alterados
- **Templates:** 24 arquivos
- **Documentação:** 3 arquivos
- **Python:** 2 arquivos (settings.py, brand.py novo)
- **Assets novos:** 3 SVGs

### Linhas de Código
- **Adicionadas:** ~150 linhas (configs + context processor + docs)
- **Modificadas:** ~80 linhas (templates)
- **Removidas:** 0 linhas (mantido fallback)

### Compatibilidade
- ✅ **Retrocompatível:** Flag padrão `False` mantém marca antiga
- ✅ **Rollback seguro:** Um comando `.env` reverte mudanças
- ✅ **Zero breaking changes:** Usuários existentes não afetados

---

## 🐛 Troubleshooting

### Problema: Logo não aparece após ativar flag

**Solução:**
```bash
# 1. Verificar arquivos
ls static/assets/logo*.svg

# 2. Coletar estáticos novamente
python manage.py collectstatic --clear --noinput

# 3. Limpar cache do navegador
# Ctrl+Shift+R (Chrome/Firefox)
```

### Problema: Título ainda mostra "IF SADD"

**Solução:**
```python
# Verificar no Django shell
python manage.py shell

>>> from django.conf import settings
>>> settings.BRAND_ENABLE_NEW
# Deve retornar True

>>> settings.BRAND_NAME_SHORT
# Deve retornar 'ÆVALIS'
```

Se retornar `False`, verifique `.env` e reinicie o servidor.

### Problema: Erro "brand not defined" em template

**Solução:**
```python
# Verificar context processor em settings.py
TEMPLATES[0]['OPTIONS']['context_processors']
# Deve conter: 'setup.brand.brand_context'
```

---

## 📧 Suporte

Para dúvidas ou problemas relacionados ao rebranding:

1. **Revisar este documento:** CHANGELOG_BRANDING.md
2. **Verificar configurações:** `setup/settings.py` (linhas 284-307)
3. **Consultar context processor:** `setup/brand.py`
4. **Abrir issue:** GitHub Issues com label `branding`

---

## 📅 Timeline

| Data | Ação | Responsável | Status |
|------|------|-------------|--------|
| 2025-10-23 | Criação dos novos SVGs | Design | ✅ Completo |
| 2025-10-23 | Infraestrutura de branding | Dev | ✅ Completo |
| 2025-10-23 | Atualização de templates | Dev | ✅ Completo |
| 2025-10-23 | Atualização de docs | Dev | ✅ Completo |
| 2025-10-23 | Validação local | Dev | ⏳ Pendente |
| TBD | Ativação em produção | Admin | ⏸️ Aguardando aprovação |

---

## 🎨 Guia de Estilo (Brand Guidelines)

### Uso Correto das Logos

#### Logo Curta (`logo_curta.svg`)
- **Contexto:** Navbars, cabeçalhos compactos, ícones
- **Tamanho mínimo:** 80×30px
- **Espaçamento:** 10px de margin ao redor
- **Background:** Cores claras (branco, cinza-claro)

#### Logo Estendida (`logo_extend.svg`)
- **Contexto:** Headers de login, rodapés, apresentações
- **Tamanho mínimo:** 200×60px
- **Espaçamento:** 20px de margin ao redor
- **Background:** Cores claras ou neutras

#### Logo Glass (`logo_glass.svg`)
- **Contexto:** Fundos escuros, overlays, transparências
- **Tamanho mínimo:** 150×150px
- **Espaçamento:** 15px de margin ao redor
- **Background:** Cores escuras ou gradientes

### Cores da Marca (A definir)

> **Nota:** Aguardando definição oficial da paleta de cores ÆVALIS.

---

**Última atualização:** 23 de outubro de 2025  
**Versão do documento:** 1.0  
**Autor:** Equipe AeVALIS
