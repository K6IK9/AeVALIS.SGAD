from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role
from .models import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    Disciplina,
    PeriodoLetivo,
    Turma,
    MatriculaTurma,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    ComentarioAvaliacao,
)
from .views import gerenciar_perfil_usuario
import datetime


class UserRoleTestCase(TestCase):
    """Testes para o sistema de roles e perfis"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="teste123456",
            email="teste@exemplo.com",
            first_name="Teste",
            last_name="Usuario",
            password="senha123",
        )

    def test_user_creation(self):
        """Testa criação básica de usuário"""
        self.assertEqual(self.user.username, "teste123456")
        self.assertEqual(self.user.email, "teste@exemplo.com")

    def test_assign_aluno_role(self):
        """Testa atribuição de role aluno"""
        assign_role(self.user, "aluno")
        self.assertTrue(has_role(self.user, "aluno"))
        self.assertFalse(has_role(self.user, "professor"))
        self.assertFalse(has_role(self.user, "admin"))

    def test_assign_professor_role(self):
        """Testa atribuição de role professor"""
        assign_role(self.user, "professor")
        self.assertTrue(has_role(self.user, "professor"))
        self.assertFalse(has_role(self.user, "aluno"))
        self.assertFalse(has_role(self.user, "admin"))

    def test_assign_coordenador_role(self):
        """Testa atribuição de role coordenador"""
        assign_role(self.user, "coordenador")
        self.assertTrue(has_role(self.user, "coordenador"))
        self.assertFalse(has_role(self.user, "aluno"))
        self.assertFalse(has_role(self.user, "professor"))

    def test_assign_admin_role(self):
        """Testa atribuição de role admin"""
        assign_role(self.user, "admin")
        self.assertTrue(has_role(self.user, "admin"))
        self.assertFalse(has_role(self.user, "aluno"))
        self.assertFalse(has_role(self.user, "professor"))

    def test_role_change(self):
        """Testa mudança de roles"""
        # Começar como aluno
        assign_role(self.user, "aluno")
        self.assertTrue(has_role(self.user, "aluno"))

        # Mudar para professor
        remove_role(self.user, "aluno")
        assign_role(self.user, "professor")
        self.assertFalse(has_role(self.user, "aluno"))
        self.assertTrue(has_role(self.user, "professor"))


class PerfilManagementTestCase(TestCase):
    """Testes para gerenciamento automático de perfis"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="teste987654",
            email="teste2@exemplo.com",
            first_name="Teste",
            last_name="Perfil",
            password="senha123",
        )

    def test_create_aluno_profile(self):
        """Testa criação automática de perfil de aluno"""
        mensagens = gerenciar_perfil_usuario(self.user, "aluno")
        self.user.refresh_from_db()

        self.assertTrue(hasattr(self.user, "perfil_aluno"))
        self.assertFalse(hasattr(self.user, "perfil_professor"))
        self.assertIn("Perfil de aluno criado", " ".join(mensagens))

    def test_create_professor_profile(self):
        """Testa criação automática de perfil de professor"""
        mensagens = gerenciar_perfil_usuario(self.user, "professor")
        self.user.refresh_from_db()

        self.assertTrue(hasattr(self.user, "perfil_professor"))
        self.assertFalse(hasattr(self.user, "perfil_aluno"))
        self.assertIn("Perfil de professor criado", " ".join(mensagens))

    def test_coordenador_gets_professor_profile(self):
        """Testa que coordenador recebe perfil de professor"""
        mensagens = gerenciar_perfil_usuario(self.user, "coordenador")
        self.user.refresh_from_db()

        self.assertTrue(hasattr(self.user, "perfil_professor"))
        self.assertFalse(hasattr(self.user, "perfil_aluno"))

    def test_admin_has_no_profile(self):
        """Testa que admin não tem perfil específico"""
        mensagens = gerenciar_perfil_usuario(self.user, "admin")
        self.user.refresh_from_db()

        self.assertFalse(hasattr(self.user, "perfil_professor"))
        self.assertFalse(hasattr(self.user, "perfil_aluno"))

    def test_profile_switching_aluno_to_professor(self):
        """Testa troca de perfil de aluno para professor"""
        # Criar como aluno
        gerenciar_perfil_usuario(self.user, "aluno")
        self.user.refresh_from_db()
        self.assertTrue(hasattr(self.user, "perfil_aluno"))

        # Trocar para professor
        mensagens = gerenciar_perfil_usuario(self.user, "professor")
        self.user.refresh_from_db()

        self.assertFalse(hasattr(self.user, "perfil_aluno"))
        self.assertTrue(hasattr(self.user, "perfil_professor"))
        self.assertIn("Perfil de aluno removido", " ".join(mensagens))
        self.assertIn("Perfil de professor criado", " ".join(mensagens))

    def test_profile_switching_professor_to_admin(self):
        """Testa que professor vira admin perde o perfil"""
        # Criar como professor
        gerenciar_perfil_usuario(self.user, "professor")
        self.user.refresh_from_db()
        self.assertTrue(hasattr(self.user, "perfil_professor"))

        # Trocar para admin
        mensagens = gerenciar_perfil_usuario(self.user, "admin")
        self.user.refresh_from_db()

        self.assertFalse(hasattr(self.user, "perfil_professor"))
        self.assertFalse(hasattr(self.user, "perfil_aluno"))
        self.assertIn("Perfil de professor removido de admin", " ".join(mensagens))


class ModelTestCase(TestCase):
    """Testes para os modelos do sistema"""

    def setUp(self):
        # Criar usuários de teste
        self.user_professor = User.objects.create_user(
            username="prof123456",
            email="prof@exemplo.com",
            first_name="Professor",
            last_name="Teste",
            password="senha123",
        )

        self.user_aluno = User.objects.create_user(
            username="aluno123456",
            email="aluno@exemplo.com",
            first_name="Aluno",
            last_name="Teste",
            password="senha123",
        )

        # Criar perfis
        self.perfil_professor = PerfilProfessor.objects.create(
            user=self.user_professor, registro_academico="PROF001"
        )

        self.perfil_aluno = PerfilAluno.objects.create(
            user=self.user_aluno, situacao="Ativo"
        )

        # Criar período letivo - usar get_or_create para evitar duplicatas
        self.periodo, created = PeriodoLetivo.objects.get_or_create(
            ano=2024, semestre=1, defaults={"nome": "Período 2024.1"}
        )

        # Criar curso
        self.curso = Curso.objects.create(
            curso_nome="Informática",
            curso_sigla="INFO",
            coordenador_curso=self.perfil_professor,
        )

    def test_perfil_professor_creation(self):
        """Testa criação de perfil de professor"""
        self.assertEqual(self.perfil_professor.user, self.user_professor)
        self.assertEqual(self.perfil_professor.registro_academico, "PROF001")
        self.assertEqual(str(self.perfil_professor), "Professor Teste (PROF001)")

    def test_perfil_aluno_creation(self):
        """Testa criação de perfil de aluno"""
        self.assertEqual(self.perfil_aluno.user, self.user_aluno)
        self.assertEqual(self.perfil_aluno.situacao, "Ativo")
        self.assertEqual(self.perfil_aluno.matricula, "aluno123456")
        self.assertEqual(self.perfil_aluno.nome_completo, "Aluno Teste")

    def test_periodo_letivo_creation(self):
        """Testa criação de período letivo"""
        self.assertEqual(self.periodo.nome, "Período 2024.1")
        self.assertEqual(self.periodo.ano, 2024)
        self.assertEqual(self.periodo.semestre, 1)
        self.assertEqual(str(self.periodo), "Período 2024.1 - 2024.1")

    def test_curso_creation(self):
        """Testa criação de curso"""
        self.assertEqual(self.curso.curso_nome, "Informática")
        self.assertEqual(self.curso.curso_sigla, "INFO")
        self.assertEqual(self.curso.coordenador_curso, self.perfil_professor)
        self.assertEqual(str(self.curso), "Informática (INFO)")

    def test_disciplina_creation(self):
        """Testa criação de disciplina"""
        disciplina = Disciplina.objects.create(
            disciplina_nome="Programação I",
            disciplina_sigla="PROG1",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
        )

        self.assertEqual(disciplina.disciplina_nome, "Programação I")
        self.assertEqual(disciplina.disciplina_sigla, "PROG1")
        self.assertEqual(disciplina.disciplina_tipo, "Obrigatória")
        self.assertEqual(disciplina.curso, self.curso)
        self.assertEqual(disciplina.professor, self.perfil_professor)
        self.assertEqual(str(disciplina), "Programação I (PROG1)")

    def test_turma_creation_and_codigo_generation(self):
        """Testa criação de turma e geração automática de código"""
        disciplina = Disciplina.objects.create(
            disciplina_nome="Algoritmos",
            disciplina_sigla="ALG",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
        )

        turma = Turma.objects.create(
            disciplina=disciplina,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
            turno="matutino",
        )

        # Código deve ser gerado automaticamente
        self.assertEqual(turma.codigo_turma, "ALG-2024.1-MAT")
        self.assertEqual(turma.status, "ativa")
        self.assertEqual(str(turma), "ALG-2024.1-MAT - Algoritmos")

    def test_matricula_turma_creation(self):
        """Testa criação de matrícula em turma"""
        disciplina = Disciplina.objects.create(
            disciplina_nome="Banco de Dados",
            disciplina_sigla="BD",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
        )

        turma = Turma.objects.create(
            disciplina=disciplina,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
            turno="noturno",
        )

        matricula = MatriculaTurma.objects.create(aluno=self.perfil_aluno, turma=turma)

        self.assertEqual(matricula.aluno, self.perfil_aluno)
        self.assertEqual(matricula.turma, turma)
        self.assertEqual(matricula.status, "ativa")
        self.assertEqual(str(matricula), "Aluno Teste em BD-2024.1-NOT")

    def test_turma_count_alunos_excludes_admin(self):
        """Testa que contagem de alunos exclui admins"""
        # Criar disciplina e turma
        disciplina = Disciplina.objects.create(
            disciplina_nome="Redes",
            disciplina_sigla="RED",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
        )

        turma = Turma.objects.create(
            disciplina=disciplina,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
            turno="vespertino",
        )

        # Matricular aluno normal
        MatriculaTurma.objects.create(aluno=self.perfil_aluno, turma=turma)

        # Criar admin com perfil de aluno (cenário que não deveria existir)
        admin_user = User.objects.create_user(
            username="admin123456", email="admin@exemplo.com", password="senha123"
        )
        assign_role(admin_user, "admin")

        admin_perfil_aluno = PerfilAluno.objects.create(
            user=admin_user, situacao="Ativo"
        )

        MatriculaTurma.objects.create(aluno=admin_perfil_aluno, turma=turma)

        # Contagem deve excluir o admin
        self.assertEqual(turma.count_alunos_matriculados(), 1)  # Só o aluno normal
        self.assertEqual(turma.matriculas.count(), 2)  # Total incluindo admin


class ViewTestCase(TestCase):
    """Testes para as views do sistema"""

    def setUp(self):
        self.client = Client()

        # Criar admin
        self.admin_user = User.objects.create_user(
            username="admin123456",
            email="admin@exemplo.com",
            first_name="Admin",
            last_name="Sistema",
            password="senha123",
        )
        assign_role(self.admin_user, "admin")

        # Criar coordenador
        self.coord_user = User.objects.create_user(
            username="coord123456",
            email="coord@exemplo.com",
            first_name="Coordenador",
            last_name="Teste",
            password="senha123",
        )
        assign_role(self.coord_user, "coordenador")
        gerenciar_perfil_usuario(self.coord_user, "coordenador")

        # Criar aluno
        self.aluno_user = User.objects.create_user(
            username="aluno123456",
            email="aluno@exemplo.com",
            first_name="Aluno",
            last_name="Teste",
            password="senha123",
        )
        assign_role(self.aluno_user, "aluno")
        gerenciar_perfil_usuario(self.aluno_user, "aluno")

    def test_admin_hub_access_admin(self):
        """Testa acesso ao admin hub como admin"""
        self.client.login(username="admin123456", password="senha123")
        response = self.client.get(reverse("admin_hub"))
        self.assertEqual(response.status_code, 200)

    def test_admin_hub_access_coordenador(self):
        """Testa acesso ao admin hub como coordenador"""
        self.client.login(username="coord123456", password="senha123")
        response = self.client.get(reverse("admin_hub"))
        self.assertEqual(response.status_code, 200)

    def test_admin_hub_access_denied_aluno(self):
        """Testa que aluno não acessa admin hub"""
        self.client.login(username="aluno123456", password="senha123")
        response = self.client.get(reverse("admin_hub"))
        # AdminHubView tem controle de acesso - aluno deve ser redirecionado
        self.assertEqual(response.status_code, 302)

    def test_gerenciar_roles_access_admin(self):
        """Testa acesso ao gerenciamento de roles como admin"""
        self.client.login(username="admin123456", password="senha123")
        response = self.client.get(reverse("gerenciar_roles"))
        self.assertEqual(response.status_code, 200)

    def test_gerenciar_roles_access_coordenador(self):
        """Testa acesso ao gerenciamento de roles como coordenador"""
        self.client.login(username="coord123456", password="senha123")
        response = self.client.get(reverse("gerenciar_roles"))
        self.assertEqual(response.status_code, 200)

    def test_gerenciar_roles_denied_aluno(self):
        """Testa que aluno não acessa gerenciamento de roles"""
        self.client.login(username="aluno123456", password="senha123")
        response = self.client.get(reverse("gerenciar_roles"))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_role_change_via_form(self):
        """Testa mudança de role via formulário"""
        self.client.login(username="admin123456", password="senha123")

        response = self.client.post(
            reverse("gerenciar_roles"),
            {"usuario": self.aluno_user.id, "role": "professor"},
        )

        self.assertEqual(response.status_code, 302)  # Redirect após sucesso

        # Verificar mudança
        self.aluno_user.refresh_from_db()
        self.assertTrue(has_role(self.aluno_user, "professor"))
        self.assertFalse(has_role(self.aluno_user, "aluno"))


class FormTestCase(TestCase):
    """Testes para os formulários do sistema"""

    def setUp(self):
        # Criar professor para usar nos formulários
        self.professor_user = User.objects.create_user(
            username="prof123456", email="prof@exemplo.com", password="senha123"
        )
        self.perfil_professor = PerfilProfessor.objects.create(
            user=self.professor_user, registro_academico="PROF001"
        )

        # Criar período letivo - usar get_or_create para evitar duplicatas
        self.periodo, created = PeriodoLetivo.objects.get_or_create(
            ano=2024, semestre=1, defaults={"nome": "Período 2024.1"}
        )

        # Criar curso - usar nome único para testes
        self.curso = Curso.objects.create(
            curso_nome="Engenharia de Testes",
            curso_sigla="ENG_TEST",
            coordenador_curso=self.perfil_professor,
        )

    def test_periodo_letivo_form_valid(self):
        """Testa formulário válido de período letivo"""
        from .forms import PeriodoLetivoForm

        form_data = {"nome": "Período 2024.2", "ano": 2024, "semestre": 2}
        form = PeriodoLetivoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_periodo_letivo_form_duplicate(self):
        """Testa validação de período duplicado"""
        from .forms import PeriodoLetivoForm

        # Tentar criar período que já existe
        form_data = {"nome": "Período 2024.1 Duplicado", "ano": 2024, "semestre": 1}
        form = PeriodoLetivoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Já existe um período cadastrado", str(form.errors))

    def test_curso_form_valid(self):
        """Testa formulário válido de curso"""
        from .forms import CursoForm

        form_data = {
            "curso_nome": "Ciência da Computação",
            "curso_sigla": "CC",
            "coordenador_curso": self.perfil_professor.id,
        }
        form = CursoForm(data=form_data)
        if not form.is_valid():
            print(f"Erros no CursoForm: {form.errors}")
        self.assertTrue(form.is_valid())

    def test_disciplina_form_valid(self):
        """Testa formulário válido de disciplina"""
        from .forms import DisciplinaForm

        form_data = {
            "disciplina_nome": "Estruturas de Dados",
            "disciplina_sigla": "ED",
            "disciplina_tipo": "Obrigatória",
            "curso": self.curso.id,
            "professor": self.perfil_professor.id,
            "periodo_letivo": self.periodo.id,
        }
        form = DisciplinaForm(data=form_data)
        if not form.is_valid():
            print(f"Erros no DisciplinaForm: {form.errors}")
        self.assertTrue(form.is_valid())


class IntegrationTestCase(TestCase):
    """Testes de integração do sistema completo"""

    def setUp(self):
        self.client = Client()

        # Criar admin
        self.admin_user = User.objects.create_user(
            username="admin123456", email="admin@exemplo.com", password="senha123"
        )
        assign_role(self.admin_user, "admin")

        # Criar professor
        self.professor_user = User.objects.create_user(
            username="prof123456", email="prof@exemplo.com", password="senha123"
        )
        assign_role(self.professor_user, "professor")
        gerenciar_perfil_usuario(self.professor_user, "professor")

    def test_complete_workflow_curso_disciplina_turma(self):
        """Testa workflow completo: criar curso -> disciplina -> turma"""
        self.client.login(username="admin123456", password="senha123")

        # 1. Criar período letivo - usar get_or_create para evitar duplicatas
        periodo, created = PeriodoLetivo.objects.get_or_create(
            ano=2024, semestre=1, defaults={"nome": "Período 2024.1"}
        )

        # 2. Criar curso
        curso_response = self.client.post(
            reverse("gerenciar_cursos"),
            {
                "curso_nome": "Sistemas de Informação",
                "curso_sigla": "SI",
                "coordenador_curso": self.professor_user.perfil_professor.id,
            },
        )
        self.assertEqual(curso_response.status_code, 302)
        curso = Curso.objects.get(curso_sigla="SI")

        # 3. Criar disciplina
        disciplina_response = self.client.post(
            reverse("gerenciar_disciplinas"),
            {
                "disciplina_nome": "Desenvolvimento Web",
                "disciplina_sigla": "WEB",
                "disciplina_tipo": "Obrigatória",
                "curso": curso.id,
                "professor": self.professor_user.perfil_professor.id,
                "periodo_letivo": periodo.id,
            },
        )
        self.assertEqual(disciplina_response.status_code, 302)
        disciplina = Disciplina.objects.get(disciplina_sigla="WEB")

        # 4. Criar turma
        turma_response = self.client.post(
            reverse("gerenciar_turmas"),
            {
                "disciplina": disciplina.id,
                "professor": self.professor_user.perfil_professor.id,
                "periodo_letivo": periodo.id,
                "turno": "noturno",
            },
        )
        self.assertEqual(turma_response.status_code, 302)
        turma = Turma.objects.get(disciplina=disciplina, turno="noturno")

        # Verificar código gerado automaticamente
        self.assertEqual(turma.codigo_turma, "WEB-2024.1-NOT")

        # Verificar que tudo foi criado corretamente
        self.assertEqual(Curso.objects.count(), 1)
        self.assertEqual(Disciplina.objects.count(), 1)
        self.assertEqual(Turma.objects.count(), 1)
        self.assertEqual(PeriodoLetivo.objects.count(), 1)


class AvaliacaoDocenteTestCase(TestCase):
    """Testes para os modelos do sistema de avaliação docente"""

    def setUp(self):
        # Criar usuários
        self.user_admin = User.objects.create_user(
            username="admin123456",
            email="admin@exemplo.com",
            first_name="Admin",
            last_name="Sistema",
            password="senha123",
        )
        assign_role(self.user_admin, "admin")

        self.user_professor = User.objects.create_user(
            username="prof123456",
            email="prof@exemplo.com",
            first_name="Professor",
            last_name="Teste",
            password="senha123",
        )
        assign_role(self.user_professor, "professor")

        self.user_aluno = User.objects.create_user(
            username="aluno123456",
            email="aluno@exemplo.com",
            first_name="Aluno",
            last_name="Teste",
            password="senha123",
        )
        assign_role(self.user_aluno, "aluno")

        # Criar perfis
        self.perfil_professor = PerfilProfessor.objects.create(
            user=self.user_professor, registro_academico="PROF001"
        )

        self.perfil_aluno = PerfilAluno.objects.create(
            user=self.user_aluno, situacao="Ativo"
        )

        # Criar estrutura acadêmica
        self.periodo, created = PeriodoLetivo.objects.get_or_create(
            ano=2024, semestre=1, defaults={"nome": "Período 2024.1"}
        )

        self.curso = Curso.objects.create(
            curso_nome="Informática",
            curso_sigla="INFO",
            coordenador_curso=self.perfil_professor,
        )

        self.disciplina = Disciplina.objects.create(
            disciplina_nome="Programação",
            disciplina_sigla="PROG",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
        )

        self.turma = Turma.objects.create(
            disciplina=self.disciplina,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo,
            turno="matutino",
        )

        # Matricular aluno
        self.matricula = MatriculaTurma.objects.create(
            aluno=self.perfil_aluno, turma=self.turma
        )

    def test_questionario_avaliacao_creation(self):
        """Testa criação de questionário de avaliação"""
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Avaliação Docente 2024.1",
            descricao="Questionário para avaliar o desempenho dos docentes",
            criado_por=self.user_admin,
        )

        self.assertEqual(questionario.titulo, "Avaliação Docente 2024.1")
        self.assertTrue(questionario.ativo)
        self.assertEqual(questionario.criado_por, self.user_admin)
        self.assertEqual(str(questionario), "Avaliação Docente 2024.1")

    def test_categoria_pergunta_creation(self):
        """Testa criação de categoria de pergunta"""
        categoria = CategoriaPergunta.objects.create(
            nome="Didática",
            descricao="Perguntas relacionadas à metodologia de ensino",
            ordem=1,
        )

        self.assertEqual(categoria.nome, "Didática")
        self.assertEqual(categoria.ordem, 1)
        self.assertTrue(categoria.ativa)
        self.assertEqual(str(categoria), "Didática")

    def test_pergunta_avaliacao_creation(self):
        """Testa criação de pergunta de avaliação"""
        categoria = CategoriaPergunta.objects.create(
            nome="Didática", descricao="Metodologia de ensino"
        )

        pergunta = PerguntaAvaliacao.objects.create(
            enunciado="O professor explica o conteúdo de forma clara?",
            tipo="likert",
            categoria=categoria,
            ordem=1,
        )

        self.assertEqual(pergunta.tipo, "likert")
        self.assertTrue(pergunta.obrigatoria)
        self.assertTrue(pergunta.ativa)
        self.assertEqual(pergunta.categoria, categoria)
        self.assertIn("O professor explica", str(pergunta))

    def test_questionario_pergunta_relationship(self):
        """Testa relacionamento entre questionário e pergunta"""
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Teste Questionário", criado_por=self.user_admin
        )

        categoria = CategoriaPergunta.objects.create(nome="Didática")

        pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste", tipo="likert", categoria=categoria
        )

        rel = QuestionarioPergunta.objects.create(
            questionario=questionario, pergunta=pergunta, ordem_no_questionario=1
        )

        self.assertEqual(rel.questionario, questionario)
        self.assertEqual(rel.pergunta, pergunta)
        self.assertEqual(rel.ordem_no_questionario, 1)

    def test_ciclo_avaliacao_creation(self):
        """Testa criação de ciclo de avaliação"""
        from django.utils import timezone
        from datetime import timedelta

        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste 2024.1",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        self.assertEqual(ciclo.nome, "Ciclo Teste 2024.1")
        self.assertEqual(ciclo.questionario, questionario)
        self.assertTrue(ciclo.ativo)
        self.assertTrue(ciclo.permite_avaliacao_anonima)
        self.assertEqual(str(ciclo), f"Ciclo Teste 2024.1 ({self.periodo})")

    def test_ciclo_avaliacao_status_property(self):
        """Testa propriedade status do ciclo de avaliação"""
        from django.utils import timezone
        from datetime import timedelta

        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        now = timezone.now()

        # Ciclo futuro
        ciclo_futuro = CicloAvaliacao.objects.create(
            nome="Ciclo Futuro",
            periodo_letivo=self.periodo,
            data_inicio=now + timedelta(days=1),
            data_fim=now + timedelta(days=30),
            questionario=questionario,
            criado_por=self.user_admin,
        )

        # Ciclo passado
        ciclo_passado = CicloAvaliacao.objects.create(
            nome="Ciclo Passado",
            periodo_letivo=self.periodo,
            data_inicio=now - timedelta(days=30),
            data_fim=now - timedelta(days=1),
            questionario=questionario,
            criado_por=self.user_admin,
        )

        # Ciclo atual
        ciclo_atual = CicloAvaliacao.objects.create(
            nome="Ciclo Atual",
            periodo_letivo=self.periodo,
            data_inicio=now - timedelta(days=1),
            data_fim=now + timedelta(days=1),
            questionario=questionario,
            criado_por=self.user_admin,
        )

        self.assertEqual(ciclo_futuro.status, "agendado")
        self.assertEqual(ciclo_passado.status, "finalizado")
        self.assertEqual(ciclo_atual.status, "em_andamento")

    def test_avaliacao_docente_creation(self):
        """Testa criação de avaliação docente"""
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        from django.utils import timezone
        from datetime import timedelta

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.perfil_professor,
            disciplina=self.disciplina,
        )

        self.assertEqual(avaliacao.ciclo, ciclo)
        self.assertEqual(avaliacao.turma, self.turma)
        self.assertEqual(avaliacao.professor, self.perfil_professor)
        self.assertEqual(avaliacao.status, "pendente")

    def test_resposta_avaliacao_creation(self):
        """Testa criação de resposta de avaliação"""
        # Criar estrutura completa
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        categoria = CategoriaPergunta.objects.create(nome="Didática")

        pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste", tipo="likert", categoria=categoria
        )

        from django.utils import timezone
        from datetime import timedelta

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.perfil_professor,
            disciplina=self.disciplina,
        )

        resposta = RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            pergunta=pergunta,
            valor_numerico=5,
        )

        self.assertEqual(resposta.avaliacao, avaliacao)
        self.assertEqual(resposta.aluno, self.perfil_aluno)
        self.assertEqual(resposta.pergunta, pergunta)
        self.assertEqual(resposta.valor_numerico, 5)
        self.assertFalse(resposta.anonima)

    def test_resposta_valor_display(self):
        """Testa método valor_display das respostas"""
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        categoria = CategoriaPergunta.objects.create(nome="Didática")

        # Pergunta Likert
        pergunta_likert = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta Likert", tipo="likert", categoria=categoria
        )

        # Pergunta NPS
        pergunta_nps = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta NPS", tipo="nps", categoria=categoria
        )

        # Pergunta Sim/Não
        pergunta_sim_nao = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta Sim/Não", tipo="sim_nao", categoria=categoria
        )

        from django.utils import timezone
        from datetime import timedelta

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.perfil_professor,
            disciplina=self.disciplina,
        )

        # Testar resposta Likert
        resposta_likert = RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            pergunta=pergunta_likert,
            valor_numerico=5,
        )
        self.assertIn("Concordo totalmente", resposta_likert.valor_display())

        # Testar resposta NPS
        resposta_nps = RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            pergunta=pergunta_nps,
            valor_numerico=9,
        )
        self.assertEqual(resposta_nps.valor_display(), "9/10")

        # Testar resposta Sim/Não
        resposta_sim_nao = RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            pergunta=pergunta_sim_nao,
            valor_boolean=True,
        )
        self.assertEqual(resposta_sim_nao.valor_display(), "Sim")

    def test_comentario_avaliacao_creation(self):
        """Testa criação de comentário de avaliação"""
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        from django.utils import timezone
        from datetime import timedelta

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.perfil_professor,
            disciplina=self.disciplina,
        )

        comentario = ComentarioAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            elogios="Excelente professor!",
            sugestoes="Poderia usar mais exemplos práticos",
        )

        self.assertEqual(comentario.avaliacao, avaliacao)
        self.assertEqual(comentario.aluno, self.perfil_aluno)
        self.assertEqual(comentario.elogios, "Excelente professor!")
        self.assertFalse(comentario.anonimo)

    def test_avaliacao_docente_calculos(self):
        """Testa métodos de cálculo da avaliação docente"""
        # Criar estrutura completa
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.user_admin
        )

        categoria = CategoriaPergunta.objects.create(nome="Didática")

        pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste", tipo="likert", categoria=categoria
        )

        from django.utils import timezone
        from datetime import timedelta

        data_inicio = timezone.now()
        data_fim = data_inicio + timedelta(days=30)

        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            questionario=questionario,
            criado_por=self.user_admin,
        )

        avaliacao = AvaliacaoDocente.objects.create(
            ciclo=ciclo,
            turma=self.turma,
            professor=self.perfil_professor,
            disciplina=self.disciplina,
        )

        # Adicionar resposta
        RespostaAvaliacao.objects.create(
            avaliacao=avaliacao,
            aluno=self.perfil_aluno,
            pergunta=pergunta,
            valor_numerico=4,
        )

        # Testar métodos
        self.assertEqual(avaliacao.total_respostas(), 1)
        self.assertEqual(len(avaliacao.alunos_aptos()), 1)
        self.assertEqual(avaliacao.percentual_participacao(), 100.0)
        self.assertEqual(avaliacao.media_geral(), 4.0)
