"""
Testes unitários para sistema de lembretes de avaliação por e-mail.

Testa:
1. Envio de e-mail na criação do ciclo
2. Envio de e-mail 2 dias antes do encerramento
3. Prevenção de duplicação de envios
4. Filtros de alunos (ativos vs inativos, responderam vs não responderam)
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core import mail
from datetime import timedelta
from io import StringIO
from django.core.management import call_command

from avaliacao_docente.models import (
    CicloAvaliacao,
    PeriodoLetivo,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    PerfilAluno,
    Curso,
    Disciplina,
    PerfilProfessor,
    Turma,
    MatriculaTurma,
    LembreteAvaliacao,
    RespostaAvaliacao,
    AvaliacaoDocente,
)


class LembreteEmailCriacaoCicloTest(TestCase):
    """Testes de envio de e-mail na criação do ciclo"""

    def setUp(self):
        """Configuração inicial"""
        # Criar usuários
        self.usuario_admin = User.objects.create_user(
            username="admin_test", password="test_pass_123", email="admin@test.com"
        )

        self.usuario_aluno1 = User.objects.create_user(
            username="aluno1",
            password="test_pass_456",
            email="aluno1@test.com",
            first_name="Aluno",
            last_name="Um",
        )

        self.usuario_aluno2 = User.objects.create_user(
            username="aluno2",
            password="test_pass_789",
            email="aluno2@test.com",
            first_name="Aluno",
            last_name="Dois",
        )

        self.usuario_professor = User.objects.create_user(
            username="prof1", password="test_pass_321", email="prof@test.com"
        )

        # Criar perfis
        self.aluno1 = PerfilAluno.objects.create(user=self.usuario_aluno1)

        self.aluno2 = PerfilAluno.objects.create(user=self.usuario_aluno2)

        self.professor = PerfilProfessor.objects.create(
            user=self.usuario_professor, registro_academico="1234567"
        )

        # Criar estrutura acadêmica
        self.periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)

        self.curso = Curso.objects.create(
            curso_nome="Curso Teste", curso_sigla="CT", coordenador_curso=self.professor
        )

        self.disciplina = Disciplina.objects.create(
            disciplina_nome="Disciplina Teste",
            disciplina_sigla="DT01",
            disciplina_tipo="Obrigatória",
            # curso obtido via disciplina
            periodo_letivo=self.periodo,
            professor=self.professor,
        )

        self.turma = Turma.objects.create(
            codigo_turma="T01",
            turno="noturno",
            disciplina=self.disciplina,
            # curso obtido via disciplina
            # periodo_letivo obtido via disciplina
        )

        # Matricular alunos
        MatriculaTurma.objects.create(aluno=self.aluno1, turma=self.turma, ativo=True)

        MatriculaTurma.objects.create(aluno=self.aluno2, turma=self.turma, ativo=True)

        # Criar questionário
        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Teste", descricao="Teste"
        )

        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.usuario_admin
        )

        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste?", tipo="likert", categoria=self.categoria
        )

        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        # Datas
        self.now = timezone.now()

    def test_envia_email_ao_criar_ciclo(self):
        """Verifica se e-mail é enviado ao criar ciclo"""
        # Limpar inbox
        mail.outbox = []

        # Criar ciclo
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now + timedelta(days=1),
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        # Adicionar turma
        ciclo.turmas.add(self.turma)

        # Verificar que e-mails foram enviados
        self.assertEqual(len(mail.outbox), 2)  # 2 alunos

        # Verificar destinatários
        emails_enviados = [msg.to[0] for msg in mail.outbox]
        self.assertIn("aluno1@test.com", emails_enviados)
        self.assertIn("aluno2@test.com", emails_enviados)

        # Verificar assunto
        self.assertIn("Nova Avaliação Docente Disponível", mail.outbox[0].subject)

        # Verificar registro de lembrete
        self.assertTrue(
            LembreteAvaliacao.objects.filter(
                ciclo=ciclo, tipo="criacao", total_enviados=2
            ).exists()
        )

    def test_nao_envia_email_se_ciclo_encerrado(self):
        """Não envia e-mail se ciclo já está encerrado"""
        mail.outbox = []

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Encerrado",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=30),
            data_fim=self.now - timedelta(days=1),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
            encerrado=True,
        )

        ciclo.turmas.add(self.turma)

        # Não deve enviar e-mails
        self.assertEqual(len(mail.outbox), 0)

        # Não deve criar registro
        self.assertFalse(
            LembreteAvaliacao.objects.filter(ciclo=ciclo, tipo="criacao").exists()
        )

    def test_nao_duplica_email_criacao(self):
        """Garante que e-mail de criação não é enviado duas vezes"""
        mail.outbox = []

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now + timedelta(days=1),
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        ciclo.turmas.add(self.turma)

        # Primeiro envio
        self.assertEqual(len(mail.outbox), 2)

        # Simular tentativa de reenvio criando registro manualmente
        LembreteAvaliacao.objects.create(ciclo=ciclo, tipo="criacao", total_enviados=2)

        mail.outbox = []

        # Tentar adicionar turma novamente (não deve enviar)
        ciclo.turmas.add(self.turma)

        self.assertEqual(len(mail.outbox), 0)


class LembreteEmailDoisDiasTest(TestCase):
    """Testes do comando enviar_lembretes_dois_dias"""

    def setUp(self):
        """Configuração inicial"""
        # Reutilizar setup similar ao teste anterior
        self.usuario_admin = User.objects.create_user(
            username="admin_test", password="test_pass_123", email="admin@test.com"
        )

        self.usuario_aluno1 = User.objects.create_user(
            username="aluno1",
            password="test_pass_456",
            email="aluno1@test.com",
            first_name="Aluno",
            last_name="Um",
        )

        self.usuario_aluno2 = User.objects.create_user(
            username="aluno2",
            password="test_pass_789",
            email="aluno2@test.com",
            first_name="Aluno",
            last_name="Dois",
        )

        self.usuario_professor = User.objects.create_user(
            username="prof1", password="test_pass_321", email="prof@test.com"
        )

        self.aluno1 = PerfilAluno.objects.create(user=self.usuario_aluno1)

        self.aluno2 = PerfilAluno.objects.create(user=self.usuario_aluno2)

        self.professor = PerfilProfessor.objects.create(
            user=self.usuario_professor, registro_academico="1234567"
        )

        self.periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)

        self.curso = Curso.objects.create(
            curso_nome="Curso Teste", curso_sigla="CT", coordenador_curso=self.professor
        )

        self.disciplina = Disciplina.objects.create(
            disciplina_nome="Disciplina Teste",
            disciplina_sigla="DT01",
            disciplina_tipo="Obrigatória",
            # curso obtido via disciplina
            periodo_letivo=self.periodo,
            professor=self.professor,
        )

        self.turma = Turma.objects.create(
            codigo_turma="T01",
            turno="noturno",
            disciplina=self.disciplina,
            # curso obtido via disciplina
            # periodo_letivo obtido via disciplina
        )

        MatriculaTurma.objects.create(aluno=self.aluno1, turma=self.turma, ativo=True)

        MatriculaTurma.objects.create(aluno=self.aluno2, turma=self.turma, ativo=True)

        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Teste", descricao="Teste"
        )

        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.usuario_admin
        )

        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste?", tipo="likert", categoria=self.categoria
        )

        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        self.now = timezone.now()

    def test_envia_lembrete_dois_dias_antes(self):
        """Verifica envio de lembrete 2 dias antes do encerramento"""
        mail.outbox = []

        # Criar ciclo que encerra em 2 dias
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo 2 Dias",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=2),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        ciclo.turmas.add(self.turma)

        # Limpar e-mails de criação
        mail.outbox = []

        # Executar comando
        out = StringIO()
        call_command("enviar_lembretes_dois_dias", stdout=out)

        # Verificar envio
        self.assertEqual(len(mail.outbox), 2)  # 2 alunos sem resposta

        # Verificar assunto
        self.assertIn("LEMBRETE", mail.outbox[0].subject)
        self.assertIn("2 dias", mail.outbox[0].subject)

        # Verificar registro
        self.assertTrue(
            LembreteAvaliacao.objects.filter(
                ciclo=ciclo, tipo="dois_dias", total_enviados=2
            ).exists()
        )

    def test_nao_envia_para_quem_respondeu(self):
        """Não envia lembrete para alunos que já responderam"""
        mail.outbox = []

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo 2 Dias",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=2),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        ciclo.turmas.add(self.turma)

        # Criar avaliação
        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.professor,
            disciplina=self.disciplina,
        )

        # Aluno1 responde
        RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.aluno1,
            pergunta=self.pergunta,
            resposta_likert=1.0,
        )

        # Limpar e-mails de criação
        mail.outbox = []

        # Executar comando
        call_command("enviar_lembretes_dois_dias", stdout=StringIO())

        # Deve enviar apenas para aluno2
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], "aluno2@test.com")

    def test_nao_duplica_lembrete_dois_dias(self):
        """Garante que lembrete de 2 dias não é enviado duas vezes"""
        mail.outbox = []

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo 2 Dias",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=2),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        ciclo.turmas.add(self.turma)

        mail.outbox = []

        # Primeira execução
        call_command("enviar_lembretes_dois_dias", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 2)

        mail.outbox = []

        # Segunda execução (não deve enviar)
        call_command("enviar_lembretes_dois_dias", stdout=StringIO())
        self.assertEqual(len(mail.outbox), 0)

    def test_dry_run_nao_envia_emails(self):
        """Verifica que modo dry-run não envia e-mails"""
        mail.outbox = []

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo 2 Dias",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=2),
            questionario=self.questionario,
            criado_por=self.usuario_admin,
        )

        ciclo.turmas.add(self.turma)

        mail.outbox = []

        # Executar em modo dry-run
        call_command("enviar_lembretes_dois_dias", "--dry-run", stdout=StringIO())

        # Não deve enviar e-mails
        self.assertEqual(len(mail.outbox), 0)

        # Não deve criar registro
        self.assertFalse(
            LembreteAvaliacao.objects.filter(ciclo=ciclo, tipo="dois_dias").exists()
        )
