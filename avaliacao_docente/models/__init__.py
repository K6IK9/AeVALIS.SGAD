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
    ConfiguracaoSite,
    CicloAvaliacao,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    Curso,
    Disciplina,
    Turma,
    HorarioTurma,
    AvaliacaoDocente,
    PerfilProfessor,
    PerfilAluno,
    MatriculaTurma,
    RespostaAvaliacao,
    PeriodoLetivo,
)

from .lembretes import JobLembreteCicloTurma, NotificacaoLembrete, LembreteAvaliacao

__all__ = [
    # Base classes
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditoriaMixin",
    "OrderingMixin",
    "SoftDeleteManager",
    "ActiveManager",
    # Models originais
    "ConfiguracaoSite",
    "CicloAvaliacao",
    "QuestionarioAvaliacao",
    "CategoriaPergunta",
    "PerguntaAvaliacao",
    "QuestionarioPergunta",
    "Curso",
    "Disciplina",
    "Turma",
    "HorarioTurma",
    "AvaliacaoDocente",
    "PerfilProfessor",
    "PerfilAluno",
    "MatriculaTurma",
    "RespostaAvaliacao",
    "PeriodoLetivo",
    # Lembretes
    "JobLembreteCicloTurma",
    "NotificacaoLembrete",
    "LembreteAvaliacao",
]
