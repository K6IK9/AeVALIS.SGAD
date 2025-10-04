"""
Mixins para funcionalidades transversais nos models.

Mixins são classes abstratas que fornecem campos e métodos
reutilizáveis para múltiplos models.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class TimestampMixin(models.Model):
    """
    Adiciona campos automáticos de timestamp.

    Campos:
        - data_criacao: Auto-preenchido na criação (auto_now_add=True)
        - data_atualizacao: Auto-atualizado a cada save (auto_now=True)

    Usado em: Turma, QuestionarioAvaliacao, PerguntaAvaliacao,
              CicloAvaliacao, AvaliacaoDocente (5 modelos)

    Exemplo:
        class MeuModel(BaseModel, TimestampMixin):
            nome = models.CharField(max_length=100)
    """

    data_criacao = models.DateTimeField(
        "Data de Criação",
        auto_now_add=True,
        help_text="Data e hora de criação do registro",
    )
    data_atualizacao = models.DateTimeField(
        "Data de Atualização",
        auto_now=True,
        help_text="Data e hora da última atualização",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Adiciona capacidade de soft delete (exclusão lógica).

    Campos:
        - ativo: Boolean indicando se registro está ativo
        - data_exclusao: Timestamp de quando foi desativado

    Métodos:
        - soft_delete(): Desativa o registro
        - restore(): Reativa o registro
        - is_deleted: Property que indica se está deletado

    Usado em: Turma, MatriculaTurma, AvaliacaoDocente (3 modelos)

    Nota: Use em conjunto com SoftDeleteManager para filtrar
          automaticamente registros inativos nas queries.

    Exemplo:
        class MeuModel(BaseModel, SoftDeleteMixin):
            nome = models.CharField(max_length=100)
            objects = SoftDeleteManager()
            all_objects = models.Manager()
    """

    ativo = models.BooleanField(
        "Ativo",
        default=True,
        db_index=True,  # Índice para performance em filtros
        help_text="Indica se o registro está ativo no sistema",
    )
    data_exclusao = models.DateTimeField(
        "Data de Exclusão",
        null=True,
        blank=True,
        help_text="Data e hora em que o registro foi desativado",
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """
        Desativa o registro (soft delete).

        Marca ativo=False e registra data_exclusao.
        O registro permanece no banco de dados.

        Exemplo:
            turma.soft_delete()
            assert turma.ativo == False
        """
        self.ativo = False
        self.data_exclusao = timezone.now()
        self.save(skip_validation=True)  # Não validar ao deletar

    def restore(self):
        """
        Reativa o registro previamente desativado.

        Marca ativo=True e limpa data_exclusao.

        Exemplo:
            turma.restore()
            assert turma.ativo == True
            assert turma.data_exclusao is None
        """
        self.ativo = True
        self.data_exclusao = None
        self.save(skip_validation=True)

    @property
    def is_deleted(self):
        """
        Verifica se o registro está deletado (ativo=False).

        Retorna:
            bool: True se deletado, False se ativo

        Exemplo:
            if turma.is_deleted:
                print("Turma foi deletada")
        """
        return not self.ativo


class AuditoriaMixin(models.Model):
    """
    Adiciona campos de auditoria (quem criou/modificou).

    Campos:
        - criado_por: FK para User que criou o registro
        - atualizado_por: FK para User que fez última modificação

    Nota: Requer middleware ou signals para popular automaticamente.
          Por padrão, deve ser preenchido manualmente nas views/forms.

    Uso futuro: Aplicar em modelos críticos que requerem rastreamento.

    Exemplo:
        class MeuModel(BaseModel, AuditoriaMixin):
            nome = models.CharField(max_length=100)

        # Na view:
        obj = MeuModel(nome="Teste")
        obj.criado_por = request.user
        obj.save()
    """

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_criados",
        verbose_name="Criado Por",
        help_text="Usuário que criou este registro",
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_atualizados",
        verbose_name="Atualizado Por",
        help_text="Usuário que fez a última atualização",
    )

    class Meta:
        abstract = True


class OrderingMixin(models.Model):
    """
    Adiciona campo de ordenação manual.

    Campo:
        - ordem: IntegerField para ordenação customizada

    Útil para listas que usuário pode reordenar manualmente
    (ex: perguntas em questionário, itens em menu).

    Exemplo:
        class Pergunta(BaseModel, OrderingMixin):
            texto = models.CharField(max_length=200)

            class Meta:
                ordering = ['ordem', 'id']
    """

    ordem = models.IntegerField(
        "Ordem",
        default=0,
        db_index=True,
        help_text="Ordem de exibição (menor valor aparece primeiro)",
    )

    class Meta:
        abstract = True
