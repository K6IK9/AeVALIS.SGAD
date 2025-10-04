"""
Package de models modularizado.

Estrutura:
    - base.py: BaseModel com comportamento padrão
    - mixins.py: Mixins reutilizáveis (Timestamp, SoftDelete, etc)
    - managers.py: Custom managers (SoftDeleteManager, etc)
    - models_originais.py: Models concretos do sistema

Importações conveniência:
    from avaliacao_docente.models import BaseModel, TimestampMixin, Turma
"""

# Abstrações (novas)
from .base import BaseModel
from .mixins import (
    TimestampMixin,
    SoftDeleteMixin,
    AuditoriaMixin,
    OrderingMixin,
)
from .managers import (
    SoftDeleteManager,
    ActiveManager,
)

# Models concretos (existentes)
from .models_originais import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    PeriodoLetivo,
    Disciplina,
    Turma,
    MatriculaTurma,
    HorarioTurma,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    ConfiguracaoSite,
)

__all__ = [
    # Abstrações
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditoriaMixin",
    "OrderingMixin",
    "SoftDeleteManager",
    "ActiveManager",
    # Models concretos
    "PerfilAluno",
    "PerfilProfessor",
    "Curso",
    "PeriodoLetivo",
    "Disciplina",
    "Turma",
    "MatriculaTurma",
    "HorarioTurma",
    "QuestionarioAvaliacao",
    "CategoriaPergunta",
    "PerguntaAvaliacao",
    "QuestionarioPergunta",
    "CicloAvaliacao",
    "AvaliacaoDocente",
    "RespostaAvaliacao",
    "ConfiguracaoSite",
]
