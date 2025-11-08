"""
Testes unitários para views de reativação de ciclos.

Testa as funcionalidades:
1. View reativar_ciclo - reativação manual
2. View editar_ciclo_simples - reativação automática ao editar datas
3. Permissões de acesso (coordenador/admin)
4. Mensagens de feedback ao usuário
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rolepermissions.roles import assign_role

from avaliacao_docente.models import (
    CicloAvaliacao,
    PeriodoLetivo,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    PerfilProfessor,
)


class ReativarCicloViewTest(TestCase):
    """Testes da view reativar_ciclo"""

    def setUp(self):
        """Configuração inicial"""
        # Criar usuários
        self.admin_user = User.objects.create_user(
            username="admin_reativ",
            password="admin_pass_secure_123",
            email="admin@test.com",
            is_staff=True,
        )
        assign_role(self.admin_user, "admin")

        self.coord_user = User.objects.create_user(
            username="coord_reativ",
            password="coord_pass_secure_456",
            email="coord@test.com",
        )
        assign_role(self.coord_user, "coordenador")
        PerfilProfessor.objects.create(
            user=self.coord_user, registro_academico="COORD001"
        )

        self.aluno_user = User.objects.create_user(
            username="aluno_reativ", password="aluno_pass_secure_789"
        )
        assign_role(self.aluno_user, "aluno")

        # Criar dados necessários
        self.periodo = PeriodoLetivo.objects.create(nome="2024.2", ano=2024, semestre=2)

        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Test", descricao="Teste"
        )

        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Test", criado_por=self.admin_user
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

        # Criar ciclo encerrado
        self.ciclo_encerrado = CicloAvaliacao.objects.create(
            nome="Ciclo Encerrado Test",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=20),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=2),
        )

        self.client = Client()

    def test_reativar_ciclo_como_admin_sucesso(self):
        """Testa reativação de ciclo por admin com sucesso"""
        self.client.login(username="admin_reativ", password="admin_pass_secure_123")

        # Verificar estado inicial
        self.assertTrue(self.ciclo_encerrado.encerrado)

        # Fazer POST para reativar
        response = self.client.post(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id])
        )

        # Verificar redirecionamento
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"/avaliacoes/ciclo/{self.ciclo_encerrado.id}/", response.url)

        # Verificar que ciclo foi reativado
        self.ciclo_encerrado.refresh_from_db()
        self.assertFalse(self.ciclo_encerrado.encerrado)
        self.assertIsNone(self.ciclo_encerrado.data_encerramento)

    def test_reativar_ciclo_como_coordenador_sucesso(self):
        """Testa reativação de ciclo por coordenador com sucesso"""
        self.client.login(username="coord_reativ", password="coord_pass_secure_456")

        response = self.client.post(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id])
        )

        self.assertEqual(response.status_code, 302)
        self.ciclo_encerrado.refresh_from_db()
        self.assertFalse(self.ciclo_encerrado.encerrado)

    def test_reativar_ciclo_como_aluno_negado(self):
        """Testa que aluno não pode reativar ciclo"""
        self.client.login(username="aluno_reativ", password="aluno_pass_secure_789")

        response = self.client.post(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id])
        )

        # Deve redirecionar para início
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.url)

        # Ciclo deve permanecer encerrado
        self.ciclo_encerrado.refresh_from_db()
        self.assertTrue(self.ciclo_encerrado.encerrado)

    def test_reativar_ciclo_sem_login_redireciona(self):
        """Testa que usuário não logado é redirecionado"""
        response = self.client.post(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id])
        )

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_reativar_ciclo_ja_ativo_retorna_info(self):
        """Testa reativar ciclo que já está ativo"""
        # Reativar primeiro
        self.ciclo_encerrado.encerrado = False
        self.ciclo_encerrado.data_encerramento = None
        self.ciclo_encerrado.save()

        self.client.login(username="admin_reativ", password="admin_pass_secure_123")

        response = self.client.post(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id]), follow=True
        )

        # Verificar que há mensagem informativa
        messages = list(response.context["messages"])
        self.assertTrue(any("já está ativo" in str(m) for m in messages))

    def test_reativar_ciclo_metodo_get_retorna_erro(self):
        """Testa que método GET não reativa ciclo"""
        self.client.login(username="admin_reativ", password="admin_pass_secure_123")

        response = self.client.get(
            reverse("reativar_ciclo", args=[self.ciclo_encerrado.id])
        )

        # Deve redirecionar
        self.assertEqual(response.status_code, 302)

        # Ciclo não deve ser reativado
        self.ciclo_encerrado.refresh_from_db()
        self.assertTrue(self.ciclo_encerrado.encerrado)

    def test_reativar_ciclo_com_data_fim_passada_avisa(self):
        """Testa que reativar ciclo com data_fim passada mostra aviso"""
        # Criar ciclo com data fim no passado
        ciclo_passado = CicloAvaliacao.objects.create(
            nome="Ciclo Passado",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=30),
            data_fim=self.now - timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=3),
        )

        self.client.login(username="admin_reativ", password="admin_pass_secure_123")

        response = self.client.post(
            reverse("reativar_ciclo", args=[ciclo_passado.id]), follow=True
        )

        # Verificar que há mensagem de aviso sobre data passada
        messages = list(response.context["messages"])
        self.assertTrue(
            any("já passou" in str(m) or "finalizado" in str(m) for m in messages)
        )

        # Ciclo deve estar reativado mas com status finalizado
        ciclo_passado.refresh_from_db()
        self.assertFalse(ciclo_passado.encerrado)
        self.assertEqual(ciclo_passado.status, "finalizado")

    def test_reativar_ciclo_inexistente_retorna_404(self):
        """Testa reativar ciclo que não existe"""
        self.client.login(username="admin_reativ", password="admin_pass_secure_123")

        response = self.client.post(reverse("reativar_ciclo", args=[99999]))

        self.assertEqual(response.status_code, 404)


class EditarCicloReativacaoAutomaticaTest(TestCase):
    """Testes de reativação automática ao editar ciclo"""

    def setUp(self):
        """Configuração inicial"""
        self.admin_user = User.objects.create_user(
            username="admin_edit",
            password="admin_edit_pass_secure_321",
            email="adminedit@test.com",
            is_staff=True,
        )
        assign_role(self.admin_user, "admin")

        self.periodo = PeriodoLetivo.objects.create(nome="2024.2", ano=2024, semestre=2)

        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Edit", descricao="Teste Edit"
        )

        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Edit", criado_por=self.admin_user
        )

        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta edit?", tipo="likert", categoria=self.categoria
        )

        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        self.now = timezone.now()

        self.client = Client()
        self.client.login(username="admin_edit", password="admin_edit_pass_secure_321")

    def test_editar_data_fim_para_futuro_reativa_automaticamente(self):
        """Testa que editar data_fim para futuro reativa ciclo encerrado"""
        # Criar ciclo encerrado
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Para Editar",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=2),
        )

        # Editar ciclo com nova data_fim no futuro
        nova_data_fim = self.now + timedelta(days=30)
        response = self.client.post(
            reverse("editar_ciclo_simples", args=[ciclo.id]),
            {
                "nome": ciclo.nome,
                "periodo_letivo": self.periodo.id,
                "questionario": self.questionario.id,
                "data_inicio": ciclo.data_inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": nova_data_fim.strftime("%Y-%m-%dT%H:%M"),
                "enviar_lembrete_email": False,
            },
            follow=True,
        )

        # Verificar que ciclo foi reativado
        ciclo.refresh_from_db()
        self.assertFalse(ciclo.encerrado)
        self.assertIsNone(ciclo.data_encerramento)
        self.assertEqual(ciclo.status, "em_andamento")

        # Verificar mensagem de reativação
        messages = list(response.context["messages"])
        self.assertTrue(any("reativado automaticamente" in str(m) for m in messages))

    def test_editar_data_fim_para_passado_nao_reativa(self):
        """Testa que editar data_fim para passado não reativa ciclo"""
        # Criar ciclo encerrado com data atual
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Encerrado Edit",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=20),
            data_fim=self.now - timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=7),
        )

        # Editar ciclo com nova data_fim ainda no passado
        nova_data_fim = self.now - timedelta(days=2)
        self.client.post(
            reverse("editar_ciclo_simples", args=[ciclo.id]),
            {
                "nome": ciclo.nome,
                "periodo_letivo": self.periodo.id,
                "questionario": self.questionario.id,
                "data_inicio": ciclo.data_inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": nova_data_fim.strftime("%Y-%m-%dT%H:%M"),
                "enviar_lembrete_email": False,
            },
        )

        # Verificar que ciclo permanece encerrado
        ciclo.refresh_from_db()
        self.assertTrue(ciclo.encerrado)
        self.assertIsNotNone(ciclo.data_encerramento)

    def test_editar_ciclo_ativo_nao_altera_status(self):
        """Testa que editar ciclo ativo não afeta seu status"""
        # Criar ciclo ativo (não encerrado)
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Ativo Edit",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Editar nome apenas
        self.client.post(
            reverse("editar_ciclo_simples", args=[ciclo.id]),
            {
                "nome": "Ciclo Ativo Editado",
                "periodo_letivo": self.periodo.id,
                "questionario": self.questionario.id,
                "data_inicio": ciclo.data_inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": ciclo.data_fim.strftime("%Y-%m-%dT%H:%M"),
                "enviar_lembrete_email": False,
            },
        )

        # Verificar que permanece ativo
        ciclo.refresh_from_db()
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "em_andamento")

    def test_editar_ciclo_salva_turmas_manytomany(self):
        """Testa que edição salva corretamente as turmas (ManyToMany)"""
        from avaliacao_docente.models import Turma, Disciplina, Curso

        # Criar dados para turma
        coord_prof = PerfilProfessor.objects.create(
            user=self.admin_user, registro_academico="PROF001"
        )

        curso = Curso.objects.create(
            curso_nome="Curso Teste",
            curso_sigla="CT",
            coordenador_curso=coord_prof,
        )

        disciplina = Disciplina.objects.create(
            disciplina_nome="Disciplina Test",
            disciplina_sigla="DT",
            disciplina_tipo="Obrigatória",
            curso=curso,
            professor=coord_prof,
            periodo_letivo=self.periodo,
        )

        turma = Turma.objects.create(
            codigo_turma="TURMA001", disciplina=disciplina, turno="matutino"
        )

        # Criar ciclo sem turmas
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Sem Turmas",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Editar ciclo adicionando turma
        response = self.client.post(
            reverse("editar_ciclo_simples", args=[ciclo.id]),
            {
                "nome": ciclo.nome,
                "periodo_letivo": self.periodo.id,
                "questionario": self.questionario.id,
                "data_inicio": ciclo.data_inicio.strftime("%Y-%m-%dT%H:%M"),
                "data_fim": ciclo.data_fim.strftime("%Y-%m-%dT%H:%M"),
                "turmas": [turma.id],
                "enviar_lembrete_email": False,
            },
        )

        # Verificar que turma foi adicionada
        ciclo.refresh_from_db()
        self.assertEqual(ciclo.turmas.count(), 1)
        self.assertIn(turma, ciclo.turmas.all())
