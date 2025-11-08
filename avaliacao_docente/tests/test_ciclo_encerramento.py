"""
Testes unitários para funcionalidades de encerramento e soft delete de ciclos.

Testa as modificações implementadas:
1. Campo 'encerrado' e 'data_encerramento' no CicloAvaliacao
2. Separação entre soft delete (ativo) e encerramento operacional (encerrado)
3. Propriedade status do CicloAvaliacao
4. SoftDeleteMixin.soft_delete() com update_fields
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from avaliacao_docente.models import (
    CicloAvaliacao,
    PeriodoLetivo,
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
)


class CicloAvaliacaoEncerramentoModelTest(TestCase):
    """Testes do modelo CicloAvaliacao - campo encerrado e status"""

    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário para o questionário
        self.usuario = User.objects.create_user(
            username="testuser", password="testpass_not_real_123"
        )

        # Criar período letivo
        self.periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)

        # Criar categoria de pergunta
        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Teste", descricao="Teste"
        )

        # Criar questionário
        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Teste", criado_por=self.usuario
        )

        # Criar pergunta
        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste?", tipo="likert", categoria=self.categoria
        )

        # Vincular pergunta ao questionário
        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        # Data base para testes
        self.now = timezone.now()

    def test_campo_encerrado_default_false(self):
        """Testa que campo encerrado é False por padrão"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now + timedelta(days=1),
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        self.assertFalse(ciclo.encerrado)
        self.assertIsNone(ciclo.data_encerramento)

    def test_status_encerrado_tem_prioridade(self):
        """Testa que status 'encerrado' tem prioridade sobre datas"""
        # Criar ciclo em andamento
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Em Andamento",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        # Verificar que está em andamento
        self.assertEqual(ciclo.status, "em_andamento")

        # Encerrar manualmente
        ciclo.encerrado = True
        ciclo.data_encerramento = timezone.now()
        ciclo.save(update_fields=["encerrado", "data_encerramento"])

        # Verificar que status mudou para encerrado
        ciclo.refresh_from_db()
        self.assertEqual(ciclo.status, "encerrado")

    def test_status_agendado(self):
        """Testa status 'agendado' quando data_inicio é futura"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Futuro",
            periodo_letivo=self.periodo,
            data_inicio=self.now + timedelta(days=10),
            data_fim=self.now + timedelta(days=40),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        self.assertEqual(ciclo.status, "agendado")
        self.assertFalse(ciclo.encerrado)

    def test_status_em_andamento(self):
        """Testa status 'em_andamento' quando within data_inicio e data_fim"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Ativo",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        self.assertEqual(ciclo.status, "em_andamento")
        self.assertFalse(ciclo.encerrado)

    def test_status_finalizado(self):
        """Testa status 'finalizado' quando data_fim passou"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Finalizado",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=35),
            data_fim=self.now - timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        self.assertEqual(ciclo.status, "finalizado")
        self.assertFalse(ciclo.encerrado)

    def test_separacao_ativo_e_encerrado(self):
        """Testa que ativo (soft delete) e encerrado são independentes"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.usuario,
        )

        # Inicialmente ativo e não encerrado
        self.assertTrue(ciclo.ativo)
        self.assertFalse(ciclo.encerrado)

        # Encerrar (operacional)
        ciclo.encerrado = True
        ciclo.save()
        ciclo.refresh_from_db()
        self.assertTrue(ciclo.ativo)  # Ainda ativo
        self.assertTrue(ciclo.encerrado)

        # Soft delete
        ciclo.soft_delete()
        ciclo.refresh_from_db()
        self.assertFalse(ciclo.ativo)  # Agora inativo
        self.assertTrue(ciclo.encerrado)  # Mas ainda encerrado


class CicloAvaliacaoSoftDeleteTest(TestCase):
    """Testes de soft delete do CicloAvaliacao"""

    def setUp(self):
        """Configuração inicial"""
        self.admin_user = User.objects.create_user(
            username="testadmin", password="testpass_not_real_456"
        )
        self.periodo = PeriodoLetivo.objects.create(nome="2024.1", ano=2024, semestre=1)

        # Criar categoria de pergunta
        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Teste", descricao="Teste"
        )

        # Criar questionário
        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário", criado_por=self.admin_user
        )

        # Criar pergunta
        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste?", tipo="likert", categoria=self.categoria
        )

        # Vincular pergunta ao questionário
        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        self.now = timezone.now()

    def test_soft_delete_marca_inativo(self):
        """Testa que soft_delete marca ativo=False"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now,
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        self.assertTrue(ciclo.ativo)
        self.assertIsNone(ciclo.data_exclusao)

        ciclo.soft_delete()
        ciclo.refresh_from_db()

        self.assertFalse(ciclo.ativo)
        self.assertIsNotNone(ciclo.data_exclusao)
        self.assertTrue(ciclo.is_deleted)

    def test_restore_reativa_registro(self):
        """Testa que restore reativa um registro deletado"""
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Teste",
            periodo_letivo=self.periodo,
            data_inicio=self.now,
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        ciclo.soft_delete()
        ciclo.refresh_from_db()
        self.assertFalse(ciclo.ativo)

        ciclo.restore()
        ciclo.refresh_from_db()
        self.assertTrue(ciclo.ativo)
        self.assertIsNone(ciclo.data_exclusao)
        self.assertFalse(ciclo.is_deleted)

    def test_manager_filtra_inativos(self):
        """Testa que manager padrão filtra registros inativos"""
        # Criar ciclo ativo
        ciclo_ativo = CicloAvaliacao.objects.create(
            nome="Ciclo Ativo",
            periodo_letivo=self.periodo,
            data_inicio=self.now,
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Criar ciclo inativo
        ciclo_inativo = CicloAvaliacao.objects.create(
            nome="Ciclo Inativo",
            periodo_letivo=self.periodo,
            data_inicio=self.now,
            data_fim=self.now + timedelta(days=30),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )
        ciclo_inativo.soft_delete()

        # Manager padrão não retorna inativos
        ciclos = CicloAvaliacao.objects.all()
        self.assertEqual(ciclos.count(), 1)
        self.assertEqual(ciclos.first().id, ciclo_ativo.id)

        # all_objects retorna todos
        todos_ciclos = CicloAvaliacao.all_objects.all()
        self.assertEqual(todos_ciclos.count(), 2)

    def test_fluxo_completo_ciclo_ativo_encerrado_deletado(self):
        """Testa fluxo completo: criar -> encerrar -> deletar"""
        # 1. Criar ciclo ativo
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Completo",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Verificar estado inicial
        self.assertTrue(ciclo.ativo)
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "em_andamento")

        # 2. Encerrar ciclo
        ciclo.encerrado = True
        ciclo.data_encerramento = timezone.now()
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        self.assertTrue(ciclo.ativo)  # Ainda visível
        self.assertTrue(ciclo.encerrado)  # Mas encerrado
        self.assertEqual(ciclo.status, "encerrado")

        # 3. Soft delete
        ciclo.soft_delete()
        ciclo.refresh_from_db()

        self.assertFalse(ciclo.ativo)  # Agora invisível
        self.assertTrue(ciclo.encerrado)  # Continua encerrado

        # Verificar que não aparece no manager padrão
        self.assertEqual(CicloAvaliacao.objects.filter(id=ciclo.id).count(), 0)

        # Mas existe no banco
        self.assertEqual(CicloAvaliacao.all_objects.filter(id=ciclo.id).count(), 1)


class CicloAvaliacaoReativacaoTest(TestCase):
    """Testes de reativação de ciclos encerrados"""

    def setUp(self):
        """Configuração inicial"""
        self.admin_user = User.objects.create_user(
            username="adminreativ", password="testpass_not_real_789", is_staff=True
        )
        self.periodo = PeriodoLetivo.objects.create(nome="2024.2", ano=2024, semestre=2)

        # Criar categoria de pergunta
        self.categoria = CategoriaPergunta.objects.create(
            nome="Categoria Reativação", descricao="Teste Reativação"
        )

        # Criar questionário
        self.questionario = QuestionarioAvaliacao.objects.create(
            titulo="Questionário Reativação", criado_por=self.admin_user
        )

        # Criar pergunta
        self.pergunta = PerguntaAvaliacao.objects.create(
            enunciado="Pergunta teste reativação?",
            tipo="likert",
            categoria=self.categoria,
        )

        # Vincular pergunta ao questionário
        QuestionarioPergunta.objects.create(
            questionario=self.questionario,
            pergunta=self.pergunta,
            ordem_no_questionario=1,
        )

        self.now = timezone.now()

    def test_reativar_ciclo_encerrado_com_data_futura(self):
        """Testa reativação de ciclo encerrado com data de fim no futuro"""
        # Criar ciclo em andamento
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Para Reativar",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Encerrar manualmente
        ciclo.encerrado = True
        ciclo.data_encerramento = timezone.now()
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar que está encerrado
        self.assertTrue(ciclo.encerrado)
        self.assertIsNotNone(ciclo.data_encerramento)
        self.assertEqual(ciclo.status, "encerrado")

        # Reativar
        ciclo.encerrado = False
        ciclo.data_encerramento = None
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar que foi reativado
        self.assertFalse(ciclo.encerrado)
        self.assertIsNone(ciclo.data_encerramento)
        self.assertEqual(ciclo.status, "em_andamento")

    def test_reativar_ciclo_com_data_passada_vira_finalizado(self):
        """Testa que ciclo reativado com data_fim passada fica 'finalizado'"""
        # Criar ciclo com data de fim no passado
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Passado",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=35),
            data_fim=self.now - timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Encerrar manualmente
        ciclo.encerrado = True
        ciclo.data_encerramento = self.now - timedelta(days=3)
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar status encerrado
        self.assertEqual(ciclo.status, "encerrado")

        # Reativar
        ciclo.encerrado = False
        ciclo.data_encerramento = None
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar que status é finalizado (não em_andamento)
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "finalizado")

    def test_edicao_data_fim_futura_reativa_automaticamente(self):
        """Testa que editar data_fim para futuro reativa ciclo encerrado"""
        # Criar ciclo encerrado
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Encerrado Edit",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=10),
            data_fim=self.now + timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=2),
        )

        # Verificar estado inicial
        self.assertTrue(ciclo.encerrado)
        self.assertEqual(ciclo.status, "encerrado")

        # Simular edição de data_fim para o futuro
        ciclo.data_fim = self.now + timedelta(days=30)

        # Lógica de reativação automática (como em editar_ciclo_simples)
        if ciclo.encerrado and ciclo.data_fim > self.now:
            ciclo.encerrado = False
            ciclo.data_encerramento = None

        ciclo.save()
        ciclo.refresh_from_db()

        # Verificar que foi reativado automaticamente
        self.assertFalse(ciclo.encerrado)
        self.assertIsNone(ciclo.data_encerramento)
        self.assertEqual(ciclo.status, "em_andamento")

    def test_edicao_data_fim_passada_nao_reativa(self):
        """Testa que editar data_fim para passado não reativa ciclo"""
        # Criar ciclo encerrado
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Encerrado Passado",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=20),
            data_fim=self.now - timedelta(days=5),
            questionario=self.questionario,
            criado_por=self.admin_user,
            encerrado=True,
            data_encerramento=self.now - timedelta(days=7),
        )

        # Verificar estado inicial
        self.assertTrue(ciclo.encerrado)

        # Simular edição de data_fim para outra data no passado
        ciclo.data_fim = self.now - timedelta(days=2)

        # Lógica de reativação automática (não deve reativar)
        if ciclo.encerrado and ciclo.data_fim > self.now:
            ciclo.encerrado = False
            ciclo.data_encerramento = None

        ciclo.save()
        ciclo.refresh_from_db()

        # Verificar que permanece encerrado
        self.assertTrue(ciclo.encerrado)
        self.assertIsNotNone(ciclo.data_encerramento)
        self.assertEqual(ciclo.status, "encerrado")

    def test_ciclo_ativo_nao_encerrado_permanece_ativo(self):
        """Testa que ciclo ativo (não encerrado) permanece com status correto"""
        # Criar ciclo em andamento (não encerrado)
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Ativo Normal",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Verificar status
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "em_andamento")

        # Editar nome (sem alterar datas nem encerramento)
        ciclo.nome = "Ciclo Ativo Editado"
        ciclo.save()
        ciclo.refresh_from_db()

        # Verificar que permanece ativo
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "em_andamento")

    def test_reativar_ciclo_agendado(self):
        """Testa reativação de ciclo agendado que foi encerrado"""
        # Criar ciclo agendado (futuro)
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Agendado",
            periodo_letivo=self.periodo,
            data_inicio=self.now + timedelta(days=10),
            data_fim=self.now + timedelta(days=40),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Verificar status inicial
        self.assertEqual(ciclo.status, "agendado")

        # Encerrar (cenário raro, mas possível)
        ciclo.encerrado = True
        ciclo.data_encerramento = timezone.now()
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar que está encerrado
        self.assertEqual(ciclo.status, "encerrado")

        # Reativar
        ciclo.encerrado = False
        ciclo.data_encerramento = None
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar que voltou a ser agendado
        self.assertFalse(ciclo.encerrado)
        self.assertEqual(ciclo.status, "agendado")

    def test_independencia_soft_delete_e_reativacao(self):
        """Testa que soft delete e reativação são independentes"""
        # Criar ciclo
        ciclo = CicloAvaliacao.objects.create(
            nome="Ciclo Independente",
            periodo_letivo=self.periodo,
            data_inicio=self.now - timedelta(days=5),
            data_fim=self.now + timedelta(days=25),
            questionario=self.questionario,
            criado_por=self.admin_user,
        )

        # Encerrar
        ciclo.encerrado = True
        ciclo.data_encerramento = timezone.now()
        ciclo.save(update_fields=["encerrado", "data_encerramento"])

        # Verificar estados
        self.assertTrue(ciclo.ativo)  # Visível
        self.assertTrue(ciclo.encerrado)  # Encerrado

        # Soft delete (mover para lixeira)
        ciclo.soft_delete()
        ciclo.refresh_from_db()

        # Verificar que soft delete não afeta encerramento
        self.assertFalse(ciclo.ativo)  # Invisível
        self.assertTrue(ciclo.encerrado)  # Ainda encerrado

        # Restaurar (remover da lixeira)
        ciclo.restore()
        ciclo.refresh_from_db()

        # Verificar que restauração não afeta encerramento
        self.assertTrue(ciclo.ativo)  # Visível novamente
        self.assertTrue(ciclo.encerrado)  # Ainda encerrado

        # Reativar (remover encerramento)
        ciclo.encerrado = False
        ciclo.data_encerramento = None
        ciclo.save(update_fields=["encerrado", "data_encerramento"])
        ciclo.refresh_from_db()

        # Verificar estado final
        self.assertTrue(ciclo.ativo)  # Visível
        self.assertFalse(ciclo.encerrado)  # Não encerrado
        self.assertEqual(ciclo.status, "em_andamento")
