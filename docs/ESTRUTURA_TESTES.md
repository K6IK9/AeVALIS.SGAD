# Estrutura de Testes - Guia Rápido

## 📁 Organização Atual

### ✅ Testes Automatizados
Localização: `avaliacao_docente/tests/`

```
avaliacao_docente/
└── tests/
    ├── __init__.py           # Docstring do pacote (sem reexports)
    ├── test_core.py          # Testes principais (49 testes)
    ├── test_abstracoes.py    # Testes de mixins (28 testes)
    └── test_refatoracao_turma.py  # Testes de regressão Turma (8 testes)
```

**Como rodar:**
```bash
python manage.py test avaliacao_docente
```

### ✅ Scripts de Validação Manual
Localização: `scripts/manual_tests/`

```
scripts/
└── manual_tests/
    ├── __init__.py
    ├── test_refatoracao_turma.py  # Testes funcionais end-to-end
    └── test_soft_delete.py        # Validação de soft delete
```

**Como rodar:**
```bash
python -m scripts.manual_tests.test_refatoracao_turma
python -m scripts.manual_tests.test_soft_delete
```

### ⚠️ Arquivos Legados (apenas wrappers)
Localização: `docs/test_*.py`

Estes arquivos apenas redirecionam para os novos módulos em `scripts/manual_tests/`.
Mantidos temporariamente para compatibilidade com scripts antigos.

## 🔧 Mudanças Aplicadas

### Removidos (causavam conflito):
- ❌ `avaliacao_docente/tests.py` (arquivo, conflitava com diretório)
- ❌ `avaliacao_docente/tests_abstracoes.py` (wrapper redundante)
- ❌ `avaliacao_docente/tests_refatoracao_turma.py` (wrapper redundante)

### Simplificado:
- ✅ `avaliacao_docente/tests/__init__.py` (apenas docstring, sem reexports wildcard)

## 📊 Status dos Testes

### Descoberta de Testes: ✅ OK
**85 testes descobertos** sem erros de ImportError.

### Falhas Conhecidas (funcionais, não estruturais):
1. **Testes de abstrações (8 erros)**: 
   - Campo `matricula` foi renomeado para `registro_academico` no modelo
   - Precisa atualizar fixtures em `test_abstracoes.py`

2. **Testes de ciclos/questionários (9 erros)**:
   - Validação requer perguntas cadastradas no questionário
   - Fixtures precisam criar `PerguntaAvaliacao` antes de `CicloAvaliacao`

3. **Testes de views (4 erros)**:
   - URL `gerenciar_roles` não existe (rota foi removida ou renomeada)
   - Atualizar ou remover testes dessas views

4. **Testes de forms (2 falhas)**:
   - Formulários precisam de perfis válidos antes da validação
   - Ajustar fixtures para criar dependências

5. **Teste soft delete (1 falha)**:
   - Turma não tem campo `ativo` (soft delete pode não estar implementado)
   - Revisar expectativa do teste

## 🎯 Próximos Passos

1. Corrigir fixtures de testes (campo `matricula` → `registro_academico`)
2. Ajustar fábricas de objetos para criar dependências completas
3. Remover ou atualizar testes de rotas inexistentes
4. Documentar decisões sobre soft delete em Turma

## 📝 Convenções

- ✅ Testes unitários/integração: `avaliacao_docente/tests/test_*.py`
- ✅ Scripts exploratórios: `scripts/manual_tests/test_*.py`
- ✅ Nomenclatura: sempre prefixo `test_` para descoberta automática
- ✅ Sem wrappers de importação na raiz do app
