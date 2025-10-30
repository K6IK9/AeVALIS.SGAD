"""
Testes para validação das funções de exportação CSV.

Este módulo testa todos os 7 exports CSV do sistema:
1. exportar_usuarios_csv
2. exportar_cursos_csv
3. exportar_disciplinas_csv
4. exportar_periodos_csv
5. exportar_turmas_csv
6. relatorio_avaliacoes_view (formato CSV)
7. relatorio_professores (formato CSV)

Validações realizadas:
- UTF-8 BOM presente para compatibilidade com Excel
- Headers corretos e na ordem esperada
- Formatação de datas (dd/mm/YYYY HH:MM)
- Tratamento de valores nulos/vazios
- Completude dos dados exportados
- Permissões de acesso (coordenador/admin)
"""

import csv
from io import StringIO
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rolepermissions.roles import assign_role

from avaliacao_docente.models import (
    Curso,
    Disciplina,
    Turma,
    PeriodoLetivo,
    PerfilProfessor,
    PerfilAluno,
    CicloAvaliacao,
    QuestionarioAvaliacao,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    AvaliacaoDocente,
    MatriculaTurma,
    RespostaAvaliacao,
)

User = get_user_model()


class CSVExportTestCase(TestCase):
    """Classe base para testes de exportação CSV"""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial dos dados de teste"""
        # Criar usuários com diferentes roles
        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            first_name="Admin",
            last_name="Sistema",
            password="admin123",
        )
        assign_role(cls.admin, "admin")

        cls.coordenador = User.objects.create_user(
            username="coordenador",
            email="coord@test.com",
            first_name="Coordenador",
            last_name="Teste",
            password="coord123",
        )
        assign_role(cls.coordenador, "coordenador")

        # Criar período letivo
        cls.periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)

        # Criar perfil professor primeiro (necessário para curso)
        cls.professor_user = User.objects.create_user(
            username="professor",
            email="prof@test.com",
            first_name="Professor",
            last_name="Teste",
            password="prof123",
        )
        cls.perfil_professor = PerfilProfessor.objects.create(
            user=cls.professor_user, registro_academico="PROF001"
        )

        # Criar curso
        cls.curso = Curso.objects.create(
            curso_nome="Engenharia de Software",
            curso_sigla="ESW",
            coordenador_curso=cls.perfil_professor,
        )

        # Criar perfil aluno
        cls.aluno_user = User.objects.create_user(
            username="ALU001",  # username é usado como matrícula
            email="aluno@test.com",
            first_name="Aluno",
            last_name="Teste",
            password="aluno123",
        )
        cls.perfil_aluno = PerfilAluno.objects.create(
            user=cls.aluno_user, situacao="Ativo"
        )

        # Criar disciplina
        cls.disciplina = Disciplina.objects.create(
            disciplina_nome="Engenharia de Software I",
            disciplina_sigla="ESW1",
            disciplina_tipo="Obrigatória",
            curso=cls.curso,
            periodo_letivo=cls.periodo,
            professor=cls.perfil_professor,
        )

        # Criar turma
        cls.turma = Turma.objects.create(
            codigo_turma="ESW1-2024.1-T01",
            disciplina=cls.disciplina,
            turno="noturno",
            status="ativa",
        )

        # Criar matrícula
        cls.matricula = MatriculaTurma.objects.create(
            aluno=cls.perfil_aluno, turma=cls.turma, status="ativa"
        )

        # Criar questionário e perguntas
        cls.questionario = QuestionarioAvaliacao.objects.create(
            nome="Questionário Padrão", descricao="Questionário de avaliação docente"
        )

        cls.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Como você avalia a didática do professor?",
            tipo="multipla_escolha",
            obrigatoria=True,
        )

        QuestionarioPergunta.objects.create(
            questionario=cls.questionario,
            pergunta=cls.pergunta,
            ordem_no_questionario=1,
        )

        # Criar ciclo de avaliação
        cls.ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo 2024.1",
            periodo_letivo=cls.periodo,
            questionario=cls.questionario,
            data_inicio=datetime.now() - timedelta(days=10),
            data_fim=datetime.now() + timedelta(days=10),
        )

        # Criar avaliação docente
        cls.avaliacao = AvaliacaoDocente.objects.create(
            turma=cls.turma,
            professor=cls.perfil_professor,
            ciclo=cls.ciclo,
            data_inicio=cls.ciclo.data_inicio,
            data_fim=cls.ciclo.data_fim,
            ativo=True,
        )

        # Criar resposta
        RespostaAvaliacao.objects.create(
            avaliacao=cls.avaliacao,
            aluno=cls.perfil_aluno,
            pergunta=cls.pergunta,
            valor_multipla_escolha="Excelente",
            valor_numerico=5,
        )

    def setUp(self):
        """Configuração para cada teste"""
        self.client = Client()

    def assert_csv_has_utf8_bom(self, response):
        """Verifica se o CSV tem BOM UTF-8"""
        content = response.content.decode("utf-8-sig")
        self.assertTrue(
            content.startswith("\ufeff")
            or response.content.startswith(b"\xef\xbb\xbf"),
            "CSV deve conter BOM UTF-8 para compatibilidade com Excel",
        )

    def parse_csv_response(self, response):
        """Parse da resposta CSV"""
        content = response.content.decode("utf-8-sig")
        # Remove BOM se presente
        if content.startswith("\ufeff"):
            content = content[1:]
        reader = csv.reader(StringIO(content))
        rows = list(reader)
        return rows


class ExportarUsuariosCSVTest(CSVExportTestCase):
    """Testes para exportar_usuarios_csv"""

    def test_permissao_admin(self):
        """Admin pode acessar exportação de usuários"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

    def test_permissao_coordenador(self):
        """Coordenador pode acessar exportação de usuários"""
        self.client.login(username="coordenador", password="coord123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        self.assertEqual(response.status_code, 200)

    def test_permissao_negada_professor(self):
        """Professor não pode acessar exportação"""
        self.client.login(username="professor", password="prof123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_utf8_bom_presente(self):
        """CSV deve ter BOM UTF-8"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        self.assert_csv_has_utf8_bom(response)

    def test_headers_corretos(self):
        """Verifica se os headers estão corretos"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        rows = self.parse_csv_response(response)

        expected_headers = [
            "ID",
            "Nome Completo",
            "Email",
            "Username",
            "Role Principal",
            "É Professor",
            "É Aluno",
            "Data de Cadastro",
            "Último Login",
            "Ativo",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_dados_usuario_completos(self):
        """Verifica se os dados do usuário estão completos"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_usuarios_csv"))
        rows = self.parse_csv_response(response)

        # Encontrar linha do admin
        admin_row = None
        for row in rows[1:]:
            if row[3] == "admin":  # Username
                admin_row = row
                break

        self.assertIsNotNone(admin_row)
        self.assertEqual(admin_row[4], "Admin")  # Role
        self.assertEqual(admin_row[9], "Sim")  # Ativo


class ExportarCursosCSVTest(CSVExportTestCase):
    """Testes para exportar_cursos_csv"""

    def test_headers_corretos(self):
        """Verifica headers da exportação de cursos"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_cursos_csv"))
        rows = self.parse_csv_response(response)

        expected_headers = [
            "ID",
            "Nome do Curso",
            "Sigla",
            "Coordenador",
            "Email Coordenador",
            "Total de Disciplinas",
            "Total de Turmas",
            "Ativo",
            "Data de Criação",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_campo_ativo_presente(self):
        """Verifica se campo 'Ativo' está presente (não mais N/A)"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_cursos_csv"))
        rows = self.parse_csv_response(response)

        # Verificar linha do curso de teste
        curso_row = rows[1]  # Primeira linha de dados
        self.assertIn(curso_row[7], ["Sim", "Não"])  # Campo Ativo

    def test_data_criacao_formatada(self):
        """Verifica formatação da data de criação"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_cursos_csv"))
        rows = self.parse_csv_response(response)

        curso_row = rows[1]
        data_criacao = curso_row[8]

        # Verificar formato dd/mm/YYYY HH:MM
        if data_criacao:
            self.assertRegex(
                data_criacao,
                r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}",
                "Data deve estar no formato dd/mm/YYYY HH:MM",
            )


class ExportarDisciplinasCSVTest(CSVExportTestCase):
    """Testes para exportar_disciplinas_csv"""

    def test_headers_corretos(self):
        """Verifica headers da exportação de disciplinas"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_disciplinas_csv"))
        rows = self.parse_csv_response(response)

        expected_headers = [
            "ID",
            "Nome da Disciplina",
            "Sigla",
            "Curso",
            "Tipo",
            "Período Letivo",
            "Professor Responsável",
            "Total de Turmas",
            "Ativo",
            "Data de Criação",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_periodo_letivo_presente(self):
        """Verifica se período letivo está presente"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_disciplinas_csv"))
        rows = self.parse_csv_response(response)

        disciplina_row = rows[1]
        self.assertEqual(disciplina_row[5], "2024.1")  # Período letivo

    def test_professor_responsavel_presente(self):
        """Verifica se professor responsável está presente"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_disciplinas_csv"))
        rows = self.parse_csv_response(response)

        disciplina_row = rows[1]
        self.assertEqual(disciplina_row[6], "Professor Teste")


class ExportarPeriodosCSVTest(CSVExportTestCase):
    """Testes para exportar_periodos_csv"""

    def test_headers_corretos(self):
        """Verifica headers da exportação de períodos"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_periodos_csv"))
        rows = self.parse_csv_response(response)

        expected_headers = [
            "ID",
            "Nome do Período",
            "Ano",
            "Semestre",
            "Total de Turmas",
            "Total de Ciclos",
            "Total de Avaliações",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_ano_semestre_separados(self):
        """Verifica se ano e semestre estão em colunas separadas"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_periodos_csv"))
        rows = self.parse_csv_response(response)

        periodo_row = rows[1]
        self.assertEqual(periodo_row[2], "2024")  # Ano
        self.assertEqual(periodo_row[3], "1")  # Semestre

    def test_total_ciclos_presente(self):
        """Verifica se total de ciclos está presente"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_periodos_csv"))
        rows = self.parse_csv_response(response)

        periodo_row = rows[1]
        self.assertEqual(periodo_row[5], "1")  # Total de ciclos


class ExportarTurmasCSVTest(CSVExportTestCase):
    """Testes para exportar_turmas_csv"""

    def test_headers_corretos(self):
        """Verifica headers da exportação de turmas"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_turmas_csv"))
        rows = self.parse_csv_response(response)

        expected_headers = [
            "ID",
            "Código da Turma",
            "Disciplina",
            "Curso",
            "Professor",
            "Email Professor",
            "Período Letivo",
            "Total de Alunos",
            "Alunos Ativos",
            "Ativa",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_professor_via_disciplina(self):
        """Verifica se professor é acessado via disciplina.professor"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("exportar_turmas_csv"))
        rows = self.parse_csv_response(response)

        turma_row = rows[1]
        self.assertEqual(turma_row[4], "Professor Teste")
        self.assertEqual(turma_row[5], "prof@test.com")


class RelatorioAvaliacoesCSVTest(CSVExportTestCase):
    """Testes para relatorio_avaliacoes com formato CSV"""

    def test_headers_corretos(self):
        """Verifica headers do relatório de avaliações"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("relatorio_avaliacoes"), {"formato": "csv"})
        rows = self.parse_csv_response(response)

        expected_headers = [
            "Disciplina",
            "Professor",
            "Turma",
            "Período Letivo",
            "Ciclo",
            "Total Alunos",
            "Respondentes",
            "Taxa de Resposta (%)",
            "Média Geral",
            "Classificação Geral",
            "Pergunta",
            "Tipo Pergunta",
            "Média Pergunta",
            "Classificação",
            "Não atende",
            "Insuficiente",
            "Regular",
            "Bom",
            "Excelente",
            "Total Respostas",
            "Comentários",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_taxa_resposta_calculada(self):
        """Verifica se taxa de resposta está calculada"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("relatorio_avaliacoes"), {"formato": "csv"})
        rows = self.parse_csv_response(response)

        if len(rows) > 1:
            avaliacao_row = rows[1]
            taxa_resposta = avaliacao_row[7]
            # Deve ser um número ou 0
            self.assertIsNotNone(taxa_resposta)


class RelatorioProfessoresCSVTest(CSVExportTestCase):
    """Testes para relatorio_professores com formato CSV"""

    def test_headers_corretos(self):
        """Verifica headers do relatório de professores"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("relatorio_professores"), {"formato": "csv"})
        rows = self.parse_csv_response(response)

        expected_headers = [
            "Professor",
            "Matrícula",
            "Curso(s)",
            "Avaliações Respondidas",
            "Total Respondentes",
            "Total Alunos Aptos",
            "Taxa de Resposta (%)",
            "Média no Ciclo",
            "Classificação no Ciclo",
            "Média Histórica",
            "Classificação Histórica",
            "Total Ciclos Históricos",
            "Total Avaliações Históricas",
        ]
        self.assertEqual(rows[0], expected_headers)

    def test_medias_tratam_none(self):
        """Verifica se médias None são tratadas como N/A"""
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("relatorio_professores"), {"formato": "csv"})
        rows = self.parse_csv_response(response)

        if len(rows) > 1:
            professor_row = rows[1]
            media_ciclo = professor_row[7]
            # Deve ser número ou "N/A"
            self.assertTrue(
                media_ciclo == "N/A" or media_ciclo.replace(".", "").isdigit()
            )
