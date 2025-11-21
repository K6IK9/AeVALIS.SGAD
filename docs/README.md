# 📚 Documentação do Sistema de Avaliação Docente

Este diretório contém toda a documentação técnica, manuais e práticas de desenvolvimento do projeto.

## 📋 Índice da Documentação

### 🚀 Setup e Instalação
- **[SETUP_RAPIDO.md](./SETUP_RAPIDO.md)** - Instruções rápidas para configuração inicial do projeto
- **[STATIC_FILES_README.md](./STATIC_FILES_README.md)** - Configuração e solução de problemas com arquivos estáticos

### 🧪 Testes e Desenvolvimento
- **[ESTRUTURA_TESTES.md](./ESTRUTURA_TESTES.md)** - Guia completo sobre estrutura e execução de testes

### 🔧 Deploy e Produção
- **[DEPLOY_VERCEL.md](./DEPLOY_VERCEL.md)** - Guia completo para deploy no Vercel com banco PostgreSQL

### 👥 Gerenciamento de Usuários e Roles
- **[ROLES_MANUAIS.md](./ROLES_MANUAIS.md)** - Manual sobre gerenciamento de roles manuais vs automáticas

### 🧪 Testes e Validação

#### Testes Automatizados
Os testes unitários e de integração estão organizados em `avaliacao_docente/tests/`:
- **test_core.py**: Testes principais (models, views, forms, integração)
- **test_abstracoes.py**: Testes de mixins (SoftDelete, Timestamp, BaseModel)
- **test_refatoracao_turma.py**: Testes de regressão da refatoração de Turma

**Como executar:**
```bash
# Rodar todos os testes do app
python manage.py test avaliacao_docente

# Rodar módulo específico
python manage.py test avaliacao_docente.tests.test_core

# Com verbosidade aumentada
python manage.py test avaliacao_docente --verbosity=2
```

#### Scripts de Validação Manual
Scripts executáveis para cenários exploratórios em `scripts/manual_tests/`:
- **test_refatoracao_turma.py**: Testes funcionais end-to-end da refatoração
- **test_soft_delete.py**: Validação de preservação de dados no soft delete

**Como executar:**
```bash
# Executar script de validação manual
python -m scripts.manual_tests.test_refatoracao_turma
python -m scripts.manual_tests.test_soft_delete
```

**Nota:** Arquivos legados em `docs/test_*.py` são apenas wrappers de compatibilidade que redirecionam para os novos módulos.

## 📖 Como Usar Esta Documentação

1. **Novo no projeto?** Comece com `SETUP_RAPIDO.md`
2. **Problemas com imagens?** Veja `STATIC_FILES_README.md`
3. **Fazendo deploy?** Consulte `DEPLOY_VERCEL.md`
4. **Gerenciando usuários?** Leia `ROLES_MANUAIS.md`
5. **Desenvolvendo filtros?** Consulte os arquivos de padronização

## 🏠 Voltar ao Projeto

Para voltar à documentação principal do projeto, consulte o [README.md](../README.md) na raiz do repositório.