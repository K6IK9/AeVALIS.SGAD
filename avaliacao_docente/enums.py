"""
Enums centralizados para choices em models.

Usando django.db.models.TextChoices para type-safety e autocomplete.

Benefícios:
    - Centralização: Um único lugar para cada conjunto de choices
    - Type-safe: IDE oferece autocomplete
    - Facilita mudanças: Alterar em um lugar atualiza todos os usos
    - Consistência: Garante mesmos valores em todo o sistema
"""

from django.db import models


class StatusTurma(models.TextChoices):
    """
    Status possíveis para o modelo Turma.

    Valores:
        ATIVA: Turma em andamento
        ENCERRADA: Turma finalizada normalmente
        CANCELADA: Turma cancelada antes do término

    Uso:
        class Turma(models.Model):
            status = models.CharField(
                max_length=20,
                choices=StatusTurma.choices,
                default=StatusTurma.ATIVA
            )

        # Na view/form:
        if turma.status == StatusTurma.ATIVA:
            print("Turma está ativa")
    """

    ATIVA = "ativa", "Ativa"
    ENCERRADA = "encerrada", "Encerrada"
    CANCELADA = "cancelada", "Cancelada"


class StatusMatricula(models.TextChoices):
    """
    Status possíveis para o modelo MatriculaTurma.

    Valores:
        ATIVO: Aluno matriculado e cursando
        TRANCADO: Matrícula trancada temporariamente
        CONCLUIDO: Aluno concluiu a disciplina
        CANCELADO: Matrícula cancelada

    Uso:
        class MatriculaTurma(models.Model):
            status = models.CharField(
                max_length=20,
                choices=StatusMatricula.choices,
                default=StatusMatricula.ATIVO
            )
    """

    ATIVO = "ativo", "Ativo"
    TRANCADO = "trancado", "Trancado"
    CONCLUIDO = "concluido", "Concluído"
    CANCELADO = "cancelado", "Cancelado"


class StatusAvaliacao(models.TextChoices):
    """
    Status possíveis para o modelo AvaliacaoDocente.

    Valores:
        PENDENTE: Avaliação criada mas não iniciada
        EM_ANDAMENTO: Aluno começou a responder
        CONCLUIDA: Avaliação finalizada
        EXPIRADA: Prazo expirou sem conclusão

    Uso:
        class AvaliacaoDocente(models.Model):
            status = models.CharField(
                max_length=20,
                choices=StatusAvaliacao.choices,
                default=StatusAvaliacao.PENDENTE
            )

        # Verificação:
        if avaliacao.status == StatusAvaliacao.CONCLUIDA:
            # Processar resultados
            pass
    """

    PENDENTE = "pendente", "Pendente"
    EM_ANDAMENTO = "em_andamento", "Em Andamento"
    CONCLUIDA = "concluida", "Concluída"
    EXPIRADA = "expirada", "Expirada"


class TurnoDisciplina(models.TextChoices):
    """
    Turnos possíveis para o modelo Turma.

    Valores:
        MATUTINO: Manhã
        VESPERTINO: Tarde
        NOTURNO: Noite

    Uso:
        class Turma(models.Model):
            turno = models.CharField(
                max_length=20,
                choices=TurnoDisciplina.choices,
                default=TurnoDisciplina.MATUTINO
            )

        # Filtro:
        turmas_noturnas = Turma.objects.filter(
            turno=TurnoDisciplina.NOTURNO
        )
    """

    MATUTINO = "matutino", "Matutino"
    VESPERTINO = "vespertino", "Vespertino"
    NOTURNO = "noturno", "Noturno"


class TipoPergunta(models.TextChoices):
    """
    Tipos de pergunta para avaliação docente.

    Valores:
        ESCALA_LIKERT: Escala de 1 a 5 (Discordo Totalmente a Concordo Totalmente)
        MULTIPLA_ESCOLHA: Pergunta de múltipla escolha (A/B/C/D)
        TEXTO_CURTO: Resposta textual curta (até 200 caracteres)
        TEXTO_LONGO: Resposta textual longa (comentário aberto)

    Uso:
        class PerguntaAvaliacao(models.Model):
            tipo_pergunta = models.CharField(
                max_length=20,
                choices=TipoPergunta.choices,
                default=TipoPergunta.ESCALA_LIKERT
            )

        # Renderização condicional:
        if pergunta.tipo_pergunta == TipoPergunta.ESCALA_LIKERT:
            # Mostrar escala 1-5
            pass
        elif pergunta.tipo_pergunta == TipoPergunta.TEXTO_LONGO:
            # Mostrar textarea
            pass
    """

    ESCALA_LIKERT = "escala_likert", "Escala Likert (1-5)"
    MULTIPLA_ESCOLHA = "multipla_escolha", "Múltipla Escolha"
    TEXTO_CURTO = "texto_curto", "Texto Curto"
    TEXTO_LONGO = "texto_longo", "Texto Longo"


class TipoDisciplina(models.TextChoices):
    """
    Tipos de disciplina no curso.

    Valores:
        OBRIGATORIA: Disciplina obrigatória do curso
        OPTATIVA: Disciplina opcional
        ELETIVA: Disciplina eletiva de livre escolha

    Uso:
        class Disciplina(models.Model):
            disciplina_tipo = models.CharField(
                max_length=20,
                choices=TipoDisciplina.choices,
                default=TipoDisciplina.OBRIGATORIA
            )
    """

    OBRIGATORIA = "Obrigatória", "Obrigatória"
    OPTATIVA = "Optativa", "Optativa"
    ELETIVA = "Eletiva", "Eletiva"


class MetodoEnvioEmail(models.TextChoices):
    """
    Métodos de envio de email para lembretes.

    Valores:
        SMTP: Envio via servidor SMTP configurado
        SENDGRID: Envio via API SendGrid
        MAILGUN: Envio via API Mailgun
        CONSOLE: Saída no console (apenas desenvolvimento)

    Uso:
        class ConfiguracaoSite(models.Model):
            metodo_envio_email = models.CharField(
                max_length=20,
                choices=MetodoEnvioEmail.choices,
                default=MetodoEnvioEmail.SMTP
            )
    """

    SMTP = "smtp", "SMTP"
    SENDGRID = "sendgrid", "SendGrid"
    MAILGUN = "mailgun", "Mailgun"
    CONSOLE = "console", "Console (Dev)"
