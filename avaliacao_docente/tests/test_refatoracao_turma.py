"""
Testes de regressão para validar a refatoração do modelo Turma.
"""

from django.test import TestCase
from django.db import connection
from django.contrib.auth.models import User

from avaliacao_docente.models import (
    PerfilProfessor,
    PerfilAluno,
    Curso,
    PeriodoLetivo,
    Disciplina,
    Turma,
)


class TurmaRefatoracaoTests(TestCase):
    """
    Testes para validar a refatoração de Turma
    (remoção de campos redundantes professor e periodo_letivo)
    """

    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuários
        self.user_prof = User.objects.create_user(
            username="prof.teste",
            password="senha123",
            first_name="Professor",
            last_name="Teste",
        )
        self.user_prof2 = User.objects.create_user(
            username="prof.teste2",
            password="senha123",
            first_name="Professor",
            last_name="Teste 2",
        )

        # Criar perfis de professor
        self.perfil_professor = PerfilProfessor.objects.create(
            user=self.user_prof,
            registro_academico="PROF001",
        )

        self.perfil_professor2 = PerfilProfessor.objects.create(
            user=self.user_prof2,
            registro_academico="PROF002",
        )

        # Criar curso
        self.curso = Curso.objects.create(
            curso_nome="Ciência da Computação",
            curso_sigla="CC",
            coordenador_curso=self.perfil_professor,
        )

        # Criar períodos letivos
        self.periodo_2024_1 = PeriodoLetivo.objects.create(
            nome="2024.1", ano=2024, semestre=1
        )
        self.periodo_2024_2 = PeriodoLetivo.objects.create(
            nome="2024.2", ano=2024, semestre=2
        )

        # Criar disciplinas
        self.disciplina1 = Disciplina.objects.create(
            disciplina_nome="Algoritmos",
            disciplina_sigla="ALG",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor,
            periodo_letivo=self.periodo_2024_1,
        )

        self.disciplina2 = Disciplina.objects.create(
            disciplina_nome="Estrutura de Dados",
            disciplina_sigla="ED",
            disciplina_tipo="Obrigatória",
            curso=self.curso,
            professor=self.perfil_professor2,
            periodo_letivo=self.periodo_2024_2,
        )

        # Criar turmas
        self.turma1 = Turma.objects.create(
            disciplina=self.disciplina1,
            turno="matutino",
        )

        self.turma2 = Turma.objects.create(
            disciplina=self.disciplina2,
            turno="vespertino",
        )

    def test_schema_nao_possui_campos_redundantes(self):
        """
        Teste 1: Valida que os campos 'professor' e 'periodo_letivo'
        NÃO existem mais na tabela Turma do banco de dados
        """
        # Obter descrição da tabela Turma (PostgreSQL)
        with connection.cursor() as cursor:
            table_name = Turma._meta.db_table
            cursor.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
                """,
                [table_name],
            )
            columns = [row[0] for row in cursor.fetchall()]

        # Validar que campos redundantes foram removidos
        self.assertNotIn(
            "professor_id",
            columns,
            "Campo 'professor_id' ainda existe em Turma (deveria ter sido removido)",
        )
        self.assertNotIn(
            "periodo_letivo_id",
            columns,
            "Campo 'periodo_letivo_id' ainda existe em Turma (deveria ter sido removido)",
        )

        # Validar que campos essenciais existem
        self.assertIn("disciplina_id", columns)
        self.assertIn("turno", columns)
        self.assertIn("codigo_turma", columns)

    def test_property_professor_funciona(self):
        """
        Teste 2: Valida que a property turma.professor
        retorna corretamente o professor da disciplina
        """
        self.assertEqual(self.turma1.professor, self.perfil_professor)
        self.assertEqual(self.turma2.professor, self.perfil_professor2)

        # Validar que retorna o mesmo que disciplina.professor
        self.assertEqual(self.turma1.professor, self.turma1.disciplina.professor)
        self.assertEqual(self.turma2.professor, self.turma2.disciplina.professor)

    def test_property_periodo_letivo_funciona(self):
        """
        Teste 3: Valida que a property turma.periodo_letivo
        retorna corretamente o período da disciplina
        """
        self.assertEqual(self.turma1.periodo_letivo, self.periodo_2024_1)
        self.assertEqual(self.turma2.periodo_letivo, self.periodo_2024_2)

        # Validar que retorna o mesmo que disciplina.periodo_letivo
        self.assertEqual(
            self.turma1.periodo_letivo, self.turma1.disciplina.periodo_letivo
        )
        self.assertEqual(
            self.turma2.periodo_letivo, self.turma2.disciplina.periodo_letivo
        )

    def test_filtro_por_professor_via_disciplina(self):
        """
        Teste 4: Valida que é possível filtrar turmas
        por professor usando disciplina__professor
        """
        # Filtrar turmas do professor 1
        turmas_prof1 = Turma.objects.filter(disciplina__professor=self.perfil_professor)
        self.assertEqual(turmas_prof1.count(), 1)
        self.assertIn(self.turma1, turmas_prof1)

        # Filtrar turmas do professor 2
        turmas_prof2 = Turma.objects.filter(
            disciplina__professor=self.perfil_professor2
        )
        self.assertEqual(turmas_prof2.count(), 1)
        self.assertIn(self.turma2, turmas_prof2)

    def test_filtro_por_periodo_letivo_via_disciplina(self):
        """
        Teste 5: Valida que é possível filtrar turmas
        por período letivo usando disciplina__periodo_letivo
        """
        # Filtrar turmas do período 2024.1
        turmas_2024_1 = Turma.objects.filter(
            disciplina__periodo_letivo=self.periodo_2024_1
        )
        self.assertEqual(turmas_2024_1.count(), 1)
        self.assertIn(self.turma1, turmas_2024_1)

        # Filtrar turmas do período 2024.2
        turmas_2024_2 = Turma.objects.filter(
            disciplina__periodo_letivo=self.periodo_2024_2
        )
        self.assertEqual(turmas_2024_2.count(), 1)
        self.assertIn(self.turma2, turmas_2024_2)

    def test_filtro_combinado_periodo_e_professor(self):
        """
        Teste 6: Valida filtros combinados por período e professor
        """
        turmas = Turma.objects.filter(
            disciplina__periodo_letivo=self.periodo_2024_1,
            disciplina__professor=self.perfil_professor,
        )
        self.assertEqual(turmas.count(), 1)
        self.assertEqual(turmas.first(), self.turma1)

        # Filtro que não deve retornar resultados
        turmas_vazio = Turma.objects.filter(
            disciplina__periodo_letivo=self.periodo_2024_1,
            disciplina__professor=self.perfil_professor2,
        )
        self.assertEqual(turmas_vazio.count(), 0)

    def test_ordering_por_periodo_via_disciplina(self):
        """
        Teste 7: Valida que o ordering padrão de Turma
        funciona corretamente via disciplina__periodo_letivo
        """
        # O Meta.ordering de Turma usa 'disciplina__periodo_letivo'
        turmas = Turma.objects.all()

        # Verificar que está ordenado por período (mais recente primeiro)
        self.assertEqual(turmas[0], self.turma2)  # 2024.2
        self.assertEqual(turmas[1], self.turma1)  # 2024.1

    def test_select_related_otimiza_queries(self):
        """
        Teste 8: Valida que select_related funciona corretamente
        para evitar N+1 queries ao acessar properties
        """
        # Sem select_related (múltiplas queries)
        with self.assertNumQueries(5):  # 1 turmas + 2 disciplinas + 2 professores
            turmas = Turma.objects.all()
            for turma in turmas:
                _ = turma.professor  # Acesso via property

        # Com select_related (query única)
        with self.assertNumQueries(1):
            turmas = Turma.objects.select_related(
                "disciplina__professor", "disciplina__periodo_letivo"
            ).all()
            for turma in turmas:
                _ = turma.professor  # Acesso via property otimizado
                _ = turma.periodo_letivo

    def test_property_nao_permite_atribuicao(self):
        """
        Teste 9: Valida que não é possível atribuir valores
        diretamente às properties (são read-only)
        """
        with self.assertRaises(AttributeError):
            self.turma1.professor = self.perfil_professor2

        with self.assertRaises(AttributeError):
            self.turma1.periodo_letivo = self.periodo_2024_2

    def test_consistencia_automatica(self):
        """
        Teste 10: Valida que professor e período são sempre
        consistentes com a disciplina (não há como divergir)
        """
        # Mudar a disciplina da turma
        self.turma1.disciplina = self.disciplina2
        self.turma1.save()

        # Properties devem refletir automaticamente os dados da nova disciplina
        self.assertEqual(self.turma1.professor, self.perfil_professor2)
        self.assertEqual(self.turma1.periodo_letivo, self.periodo_2024_2)

    def test_codigo_turma_usa_periodo_da_disciplina(self):
        """
        Teste 11: Valida que o código da turma é gerado
        corretamente usando o período da disciplina
        """
        # Criar nova turma (código será gerado automaticamente)
        turma = Turma.objects.create(
            disciplina=self.disciplina1,
            turno="noturno",
        )

        # Código deve incluir ano e semestre do período
        self.assertIn("2024", turma.codigo_turma)
        self.assertIn("1", turma.codigo_turma)
        self.assertIn("ALG", turma.codigo_turma)
        self.assertIn("NOT", turma.codigo_turma)  # Noturno


class TurmaBackwardsCompatibilityTests(TestCase):
    """
    Testes para validar retrocompatibilidade com código legado
    que pode estar usando turma.professor e turma.periodo_letivo
    """

    def setUp(self):
        """Configuração inicial"""
        user = User.objects.create_user(
            username="prof",
            password="senha123",
            first_name="Professor",
            last_name="Teste",
        )
        perfil = PerfilProfessor.objects.create(user=user, registro_academico="P001")
        curso = Curso.objects.create(
            curso_nome="Curso Teste", curso_sigla="CT", coordenador_curso=perfil
        )
        periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)
        disciplina = Disciplina.objects.create(
            disciplina_nome="Disciplina",
            disciplina_sigla="DIS",
            disciplina_tipo="Obrigatória",
            curso=curso,
            professor=perfil,
            periodo_letivo=periodo,
        )
        self.turma = Turma.objects.create(disciplina=disciplina, turno="matutino")
        self.periodo = periodo
        self.perfil = perfil

    def test_acesso_direto_property_funciona(self):
        """Código legado: turma.periodo_letivo"""
        self.assertEqual(self.turma.periodo_letivo, self.periodo)

    def test_acesso_via_get_funciona(self):
        """Código legado: getattr(turma, 'periodo_letivo')"""
        periodo = getattr(self.turma, "periodo_letivo")
        self.assertEqual(periodo, self.periodo)

    def test_comparacao_direta_funciona(self):
        """Código legado: if turma.periodo_letivo == periodo"""
        self.assertTrue(self.turma.periodo_letivo == self.periodo)

    def test_str_repr_funcionam(self):
        """Validar que __str__ e __repr__ funcionam"""
        str_result = str(self.turma)
        self.assertIsInstance(str_result, str)
        self.assertIn("DIS", str_result)
