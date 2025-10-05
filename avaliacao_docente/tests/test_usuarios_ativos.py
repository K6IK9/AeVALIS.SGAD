"""
Testes para garantir que usuários desativados não apareçam em seleções
"""

from django.test import TestCase
from django.contrib.auth.models import User
from ..models import PerfilProfessor, PerfilAluno
from ..forms import CursoForm, GerenciarRoleForm


class UsuariosAtivosTestCase(TestCase):
    """Testes para verificar filtro de usuários ativos em forms e managers"""

    def setUp(self):
        """Criar usuários de teste"""
        # Usuário ativo
        self.user_ativo = User.objects.create_user(
            username="ativo",
            email="ativo@test.com",
            password="senha123",
            is_active=True,
            first_name="Usuario",
            last_name="Ativo",
        )

        # Usuário inativo
        self.user_inativo = User.objects.create_user(
            username="inativo",
            email="inativo@test.com",
            password="senha123",
            is_active=False,
            first_name="Usuario",
            last_name="Inativo",
        )

        # Criar perfis de professor
        self.professor_ativo = PerfilProfessor.objects.create(
            user=self.user_ativo, registro_academico="PROF001"
        )
        self.professor_inativo = PerfilProfessor.objects.create(
            user=self.user_inativo, registro_academico="PROF002"
        )

        # Criar perfis de aluno
        self.aluno_ativo = PerfilAluno.objects.create(user=self.user_ativo)
        self.aluno_inativo = PerfilAluno.objects.create(user=self.user_inativo)

    def test_perfil_professor_manager_filtra_inativos(self):
        """Testa que PerfilProfessor.non_admin retorna apenas professores ativos"""
        professores = PerfilProfessor.non_admin.all()

        # Deve incluir apenas o professor ativo
        self.assertIn(self.professor_ativo, professores)
        self.assertNotIn(self.professor_inativo, professores)

    def test_perfil_aluno_manager_filtra_inativos(self):
        """Testa que PerfilAluno.non_admin retorna apenas alunos ativos"""
        alunos = PerfilAluno.non_admin.all()

        # Deve incluir apenas o aluno ativo
        self.assertIn(self.aluno_ativo, alunos)
        self.assertNotIn(self.aluno_inativo, alunos)

    def test_curso_form_nao_exibe_professor_inativo(self):
        """Testa que CursoForm não exibe professores inativos no campo coordenador"""
        form = CursoForm()
        queryset_professores = form.fields["coordenador_curso"].queryset

        # Deve incluir apenas o professor ativo
        self.assertIn(self.professor_ativo, queryset_professores)
        self.assertNotIn(self.professor_inativo, queryset_professores)

    def test_gerenciar_role_form_nao_exibe_usuario_inativo(self):
        """Testa que GerenciarRoleForm não exibe usuários inativos"""
        form = GerenciarRoleForm()
        queryset_usuarios = form.fields["usuario"].queryset

        # Deve incluir apenas o usuário ativo
        self.assertIn(self.user_ativo, queryset_usuarios)
        self.assertNotIn(self.user_inativo, queryset_usuarios)

    def test_usuario_desativado_nao_aparece_em_queryset_padrao(self):
        """Testa que usuários inativos não aparecem em querysets padrão de seleção"""
        # Simula queryset usado em forms
        usuarios_ativos = User.objects.filter(is_active=True)

        self.assertIn(self.user_ativo, usuarios_ativos)
        self.assertNotIn(self.user_inativo, usuarios_ativos)

    def test_perfil_professor_get_queryset_exclui_inativos(self):
        """Testa que o manager non_admin de PerfilProfessor exclui inativos"""
        # Usando o manager non_admin (usado pelos forms)
        professores = PerfilProfessor.non_admin.all()

        # Deve retornar apenas professores ativos
        self.assertIn(self.professor_ativo, professores)
        self.assertNotIn(self.professor_inativo, professores)

        # Verificar que todos são ativos
        for prof in professores:
            self.assertTrue(prof.user.is_active)

    def test_perfil_aluno_get_queryset_exclui_inativos(self):
        """Testa que o manager non_admin de PerfilAluno exclui inativos"""
        # Usando o manager non_admin (usado pelos forms)
        alunos = PerfilAluno.non_admin.all()

        # Deve retornar apenas alunos ativos
        self.assertIn(self.aluno_ativo, alunos)
        self.assertNotIn(self.aluno_inativo, alunos)

        # Verificar que todos são ativos
        for aluno in alunos:
            self.assertTrue(aluno.user.is_active)

    def test_reativar_usuario_volta_a_aparecer(self):
        """Testa que ao reativar um usuário ele volta a aparecer nas seleções"""
        # Reativar o usuário inativo
        self.user_inativo.is_active = True
        self.user_inativo.save()

        # Verificar que agora aparece
        form = GerenciarRoleForm()
        queryset_usuarios = form.fields["usuario"].queryset

        self.assertIn(self.user_inativo, queryset_usuarios)

    def test_usuario_ativo_aparece_em_todas_selecoes(self):
        """Testa que usuário ativo aparece em todos os forms de seleção"""
        # CursoForm
        curso_form = CursoForm()
        self.assertIn(
            self.professor_ativo, curso_form.fields["coordenador_curso"].queryset
        )

        # GerenciarRoleForm
        role_form = GerenciarRoleForm()
        self.assertIn(self.user_ativo, role_form.fields["usuario"].queryset)
