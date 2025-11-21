# 🧪 Estrutura de Testes - ÆVALIS

## 📋 Visão Geral

O projeto ÆVALIS possui uma suíte completa de testes automatizados organizados em módulos específicos, garantindo a qualidade e confiabilidade do sistema.

---

## 📁 Estrutura de Arquivos

```
avaliacao_docente/
├── tests/
│   ├── __init__.py
│   ├── test_core.py                 # Testes principais
│   ├── test_abstracoes.py           # Testes de mixins e classes base
│   └── test_refatoracao_turma.py    # Testes de regressão
```

---

## 📝 Módulos de Teste

### 1. **test_core.py** - Testes Principais

#### Models
- ✅ Criação e validação de modelos
- ✅ Relacionamentos entre entidades
- ✅ Métodos customizados dos models
- ✅ Propriedades computadas

**Cobertura:**
- `Curso`, `Disciplina`, `Turma`, `MatriculaTurma`
- `CicloAvaliacao`, `AvaliacaoDocente`, `RespostaAvaliacao`
- `PerfilProfessor`, `PerfilAluno`
- `QuestionarioAvaliacao`, `PerguntaAvaliacao`

#### Views
- ✅ Autenticação e permissões
- ✅ CRUD completo de entidades
- ✅ Listagens e filtros
- ✅ Formulários e validações

#### Forms
- ✅ Validação de campos
- ✅ Lógica de formulários customizados
- ✅ Clean methods

#### Integração
- ✅ Fluxo completo de avaliação
- ✅ Sistema de roles e permissões
- ✅ OAuth2 SUAP (mocks)

---

### 2. **test_abstracoes.py** - Testes de Mixins

#### SoftDeleteMixin
- ✅ Deleção lógica (soft delete)
- ✅ Preservação de dados históricos
- ✅ Managers customizados (all_with_deleted, only_deleted)
- ✅ Restauração de objetos deletados

#### TimestampMixin
- ✅ Criação automática de timestamps
- ✅ Atualização automática do `atualizado_em`
- ✅ Imutabilidade do `criado_em`

#### BaseModel
- ✅ Representação string (__str__)
- ✅ Herança correta de mixins
- ✅ Comportamento padrão de models

#### AuditoriaMixin
- ✅ Rastreamento de usuário criador
- ✅ Rastreamento de usuário modificador
- ✅ Auditoria completa de mudanças

#### OrderingMixin
- ✅ Ordenação customizada
- ✅ Reordenação automática
- ✅ Posicionamento relativo

---

### 3. **test_refatoracao_turma.py** - Testes de Regressão

#### Campos Refatorados
- ✅ Relacionamento `professor` (FK → FK direta)
- ✅ Relacionamento `alunos` (M2M → através de MatriculaTurma)
- ✅ Métodos de contagem de alunos

#### Compatibilidade
- ✅ Migrations aplicadas corretamente
- ✅ Dados existentes preservados
- ✅ Queries otimizadas (N+1 resolvido)

#### Performance
- ✅ Redução de queries em listagens
- ✅ Select/Prefetch related otimizados
- ✅ Contagens eficientes

---

## 🚀 Executando os Testes

### Todos os Testes

```bash
# Executar todos os testes do app
python manage.py test avaliacao_docente

# Com verbosidade aumentada
python manage.py test avaliacao_docente --verbosity=2

# Manter banco de dados entre execuções (mais rápido)
python manage.py test avaliacao_docente --keepdb
```

### Módulos Específicos

```bash
# Apenas testes principais
python manage.py test avaliacao_docente.tests.test_core

# Apenas testes de abstrações
python manage.py test avaliacao_docente.tests.test_abstracoes

# Apenas testes de regressão
python manage.py test avaliacao_docente.tests.test_refatoracao_turma
```

### Testes Individuais

```bash
# Teste específico por classe
python manage.py test avaliacao_docente.tests.test_core.TurmaModelTest

# Teste específico por método
python manage.py test avaliacao_docente.tests.test_core.TurmaModelTest.test_criacao_turma
```

### Testes Paralelos

```bash
# Executar testes em paralelo (mais rápido em máquinas multi-core)
python manage.py test avaliacao_docente --parallel=auto

# Especificar número de processos
python manage.py test avaliacao_docente --parallel=4
```

---

## 📊 Cobertura de Testes

### Gerar Relatório de Cobertura

```bash
# Instalar coverage
pip install coverage

# Executar testes com cobertura
coverage run --source='avaliacao_docente' manage.py test avaliacao_docente

# Relatório no terminal
coverage report

# Relatório HTML interativo
coverage html
# Abrir: htmlcov/index.html
```

### Meta de Cobertura

- **Atual**: ~75-80%
- **Meta**: ≥85%
- **Crítico**: Models e services devem ter ≥90%

---

## 🧪 Scripts de Validação Manual

Além dos testes automatizados, existem scripts exploratórios para validação manual:

### Localização

```
scripts/
└── manual_tests/
    ├── __init__.py
    ├── test_refatoracao_turma.py  # Validação end-to-end de refatoração
    └── test_soft_delete.py        # Validação de soft delete
```

### Execução

```bash
# Validação de refatoração de turma
python -m scripts.manual_tests.test_refatoracao_turma

# Validação de soft delete
python -m scripts.manual_tests.test_soft_delete
```

**Quando usar:**
- ✅ Após mudanças estruturais grandes
- ✅ Antes de deploy em produção
- ✅ Para testes exploratórios
- ✅ Validação de comportamento real no banco

---

## 🔍 Boas Práticas

### 1. **Nomear Testes Claramente**

```python
# ✅ Bom
def test_turma_com_professor_ativo_permite_criacao(self):
    pass

# ❌ Ruim
def test_turma1(self):
    pass
```

### 2. **Usar Fixtures e Factories**

```python
from django.test import TestCase

class TurmaTestCase(TestCase):
    def setUp(self):
        """Setup executado antes de cada teste"""
        self.curso = Curso.objects.create(nome="Informática")
        self.disciplina = Disciplina.objects.create(nome="Python")
        self.professor = User.objects.create_user(username="prof1")
        
    def test_criacao_turma(self):
        turma = Turma.objects.create(
            codigo="INFO-2024-1",
            disciplina=self.disciplina,
            professor=self.professor
        )
        self.assertEqual(turma.codigo, "INFO-2024-1")
```

### 3. **Testar Edge Cases**

```python
def test_turma_sem_alunos_retorna_zero(self):
    """Turma sem matrículas deve retornar contagem 0"""
    turma = self.criar_turma()
    self.assertEqual(turma.count_alunos_matriculados(), 0)

def test_turma_com_alunos_inativos_nao_conta(self):
    """Matrículas inativas não devem ser contadas"""
    turma = self.criar_turma()
    self.criar_matricula(turma, status='trancada')
    self.assertEqual(turma.count_alunos_matriculados(), 0)
```

### 4. **Isolar Testes**

```python
# ✅ Cada teste é independente
def test_A(self):
    turma = self.criar_turma()
    # ...

def test_B(self):
    turma = self.criar_turma()  # Nova turma, não reutiliza test_A
    # ...
```

### 5. **Usar Assertions Apropriadas**

```python
# Igualdade
self.assertEqual(turma.codigo, "INFO-2024")

# Verdadeiro/Falso
self.assertTrue(turma.is_active)
self.assertFalse(turma.is_encerrada)

# Existência
self.assertIsNone(turma.data_encerramento)
self.assertIsNotNone(turma.professor)

# Contém
self.assertIn(aluno, turma.alunos_matriculados())

# Exceções
with self.assertRaises(ValidationError):
    turma.codigo = ""
    turma.full_clean()
```

---

## 🐛 Debugging de Testes

### Imprimir Output Durante Testes

```python
def test_exemplo(self):
    turma = self.criar_turma()
    print(f"Turma criada: {turma.codigo}")  # Visível com --verbosity=2
    self.assertEqual(turma.codigo, "TEST")
```

### Usar Debugger

```python
def test_exemplo(self):
    turma = self.criar_turma()
    import pdb; pdb.set_trace()  # Breakpoint
    self.assertEqual(turma.codigo, "TEST")
```

### Ver Queries SQL

```python
from django.test.utils import override_settings
from django.db import connection

@override_settings(DEBUG=True)
def test_queries(self):
    turma = Turma.objects.select_related('professor').get(id=1)
    print(len(connection.queries))  # Número de queries
    print(connection.queries)        # Detalhes das queries
```

---

## 📈 Métricas de Qualidade

### Critérios de Aceitação

- ✅ **100% dos testes passando**
- ✅ **Tempo de execução < 30s** (sem --keepdb)
- ✅ **Cobertura ≥ 85%**
- ✅ **Zero warnings** no output
- ✅ **Sem testes desabilitados** (@skip sem justificativa)

### Executar Checks de Qualidade

```bash
# Linting (se configurado)
flake8 avaliacao_docente/tests/

# Type checking (se configurado)
mypy avaliacao_docente/tests/

# Testes + cobertura + lint
coverage run manage.py test avaliacao_docente && coverage report && flake8 avaliacao_docente/
```

---

## 📚 Recursos Adicionais

### Documentação Oficial Django

- [Testing in Django](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Testing Tools](https://docs.djangoproject.com/en/5.2/topics/testing/tools/)
- [Advanced Testing](https://docs.djangoproject.com/en/5.2/topics/testing/advanced/)

### Bibliotecas Úteis

- **pytest-django**: Framework alternativo de testes
- **factory-boy**: Geração de fixtures complexas
- **faker**: Dados falsos realistas
- **freezegun**: Congelar tempo para testes temporais

---

## 🆘 Troubleshooting

### Problema: Testes falhando com "Database not found"

**Solução:**
```bash
# Recriar banco de testes
python manage.py test --keepdb=False
```

### Problema: Testes lentos

**Soluções:**
```bash
# Usar --keepdb para reutilizar banco
python manage.py test --keepdb

# Executar em paralelo
python manage.py test --parallel=auto

# Testar apenas módulo específico
python manage.py test avaliacao_docente.tests.test_core
```

### Problema: Fixtures conflitando

**Solução:**
```python
# Limpar dados entre testes
def tearDown(self):
    Turma.objects.all().delete()
    User.objects.all().delete()
```

---

## 📞 Suporte

**Documentação:** `/docs/ESTRUTURA_TESTES.md`  
**Issues:** [GitHub Issues](https://github.com/K6IK9/AeVALIS.SGAD/issues) com label `testes`

---

**Última atualização:** Novembro 2025  
**Versão:** 1.0.0
