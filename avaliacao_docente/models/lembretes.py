"""
Modelos para sistema de lembretes automáticos de avaliação.

Implementa a funcionalidade de envio automático de e-mails aos alunos
até que cada turma atinja 10% de respostas no ciclo.
"""

from django.db import models
from django.utils import timezone
from .base import BaseModel
from .mixins import TimestampMixin


class JobLembreteCicloTurma(BaseModel, TimestampMixin):
    """
    Job de envio de lembretes para uma turma em um ciclo específico.

    Rastreia o progresso de envio de lembretes para garantir que
    cada turma atinja o limiar mínimo de respostas (10%).
    """

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_execucao", "Em Execução"),
        ("completo", "Completo"),
        ("pausado", "Pausado"),
        ("erro", "Erro"),
    ]

    ciclo = models.ForeignKey(
        "CicloAvaliacao",
        on_delete=models.CASCADE,
        related_name="jobs_lembrete",
        verbose_name="Ciclo de Avaliação",
    )

    turma = models.ForeignKey(
        "Turma",
        on_delete=models.CASCADE,
        related_name="jobs_lembrete",
        verbose_name="Turma",
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pendente", verbose_name="Status"
    )

    proximo_envio_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Próximo Envio Em",
        help_text="Data/hora do próximo disparo de lembretes",
    )

    total_alunos_aptos = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Alunos Aptos",
        help_text="Total de alunos matriculados ativos na turma",
    )

    total_respondentes = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Respondentes",
        help_text="Alunos distintos que já responderam",
    )

    taxa_resposta_atual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Taxa de Resposta Atual (%)",
        help_text="Percentual de alunos que já responderam",
    )

    total_emails_enviados = models.PositiveIntegerField(
        default=0, verbose_name="Total de E-mails Enviados"
    )

    total_falhas = models.PositiveIntegerField(
        default=0, verbose_name="Total de Falhas"
    )

    rodadas_executadas = models.PositiveIntegerField(
        default=0,
        verbose_name="Rodadas Executadas",
        help_text="Número de vezes que a tarefa foi executada",
    )

    ultima_execucao = models.DateTimeField(
        null=True, blank=True, verbose_name="Última Execução"
    )

    mensagem_erro = models.TextField(
        blank=True,
        verbose_name="Mensagem de Erro",
        help_text="Detalhes do último erro ocorrido",
    )

    class Meta:
        verbose_name = "Job de Lembrete por Turma"
        verbose_name_plural = "Jobs de Lembrete por Turma"
        ordering = ["-data_criacao"]
        unique_together = [["ciclo", "turma"]]
        indexes = [
            models.Index(fields=["status", "proximo_envio_em"]),
            models.Index(fields=["ciclo", "turma"]),
        ]

    def __str__(self):
        return f"Job Lembrete: {self.ciclo.nome} - {self.turma.codigo}"

    def atingiu_limiar(self, limiar_percentual=10.0):
        """Verifica se a turma atingiu o limiar mínimo de respostas."""
        return self.taxa_resposta_atual >= limiar_percentual

    def pode_executar(self):
        """Verifica se o job pode ser executado agora."""
        if self.status not in ["pendente", "em_execucao"]:
            return False

        if self.proximo_envio_em and timezone.now() < self.proximo_envio_em:
            return False

        return True


class NotificacaoLembrete(BaseModel, TimestampMixin):
    """
    Registro individual de notificação enviada a um aluno.

    Rastreia cada e-mail enviado para controlar limites por aluno
    e garantir que não enviamos spam.
    """

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("enviado", "Enviado"),
        ("falhou", "Falhou"),
        ("ignorado", "Ignorado"),
    ]

    job = models.ForeignKey(
        JobLembreteCicloTurma,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name="Job de Lembrete",
    )

    aluno = models.ForeignKey(
        "PerfilAluno",
        on_delete=models.CASCADE,
        related_name="notificacoes_lembrete",
        verbose_name="Aluno",
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pendente", verbose_name="Status"
    )

    rodada = models.PositiveIntegerField(
        default=1,
        verbose_name="Rodada",
        help_text="Número sequencial do lembrete enviado ao aluno",
    )

    tentativas = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentativas",
        help_text="Quantidade de tentativas de envio",
    )

    enviado_em = models.DateTimeField(null=True, blank=True, verbose_name="Enviado Em")

    mensagem_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID da Mensagem",
        help_text="Message-ID do e-mail enviado",
    )

    motivo_falha = models.TextField(blank=True, verbose_name="Motivo da Falha")

    class Meta:
        verbose_name = "Notificação de Lembrete"
        verbose_name_plural = "Notificações de Lembrete"
        ordering = ["-data_criacao"]
        indexes = [
            models.Index(fields=["job", "aluno"]),
            models.Index(fields=["status", "enviado_em"]),
        ]

    def __str__(self):
        return f"Lembrete: {self.aluno.user.get_full_name()} - Rodada {self.rodada}"
