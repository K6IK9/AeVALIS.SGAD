"""
Testes para o formulário de Período Letivo
"""

from django.test import TestCase
from ..models import PeriodoLetivo
from ..forms import PeriodoLetivoForm


class PeriodoLetivoFormTestCase(TestCase):
    """Testes para PeriodoLetivoForm"""

    def setUp(self):
        """Criar período letivo de teste"""
        self.periodo_existente = PeriodoLetivo.objects.create(
            nome="Período Letivo 2026.2", ano=2026, semestre=2
        )

    def test_criar_periodo_novo(self):
        """Testa criação de um novo período"""
        form_data = {"nome": "Período Letivo 2025.1", "ano": 2025, "semestre": 1}
        form = PeriodoLetivoForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_criar_periodo_duplicado(self):
        """Testa que não permite criar período duplicado"""
        form_data = {"nome": "Outro Nome", "ano": 2026, "semestre": 2}
        form = PeriodoLetivoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Já existe um período cadastrado para 2026.2", str(form.errors))

    def test_editar_periodo_mesmo_ano_semestre(self):
        """Testa que permite editar um período sem mudar ano/semestre"""
        form_data = {
            "nome": "Novo Nome para Período 2026.2",
            "ano": 2026,
            "semestre": 2,
        }
        form = PeriodoLetivoForm(data=form_data, instance=self.periodo_existente)
        self.assertTrue(
            form.is_valid(),
            f"Formulário deveria ser válido ao editar período existente. Erros: {form.errors}",
        )

    def test_editar_periodo_mudando_ano_semestre_para_existente(self):
        """Testa que não permite mudar para ano/semestre já existente"""
        # Criar outro período
        outro_periodo = PeriodoLetivo.objects.create(
            nome="Período Letivo 2025.1", ano=2025, semestre=1
        )

        # Tentar mudar o período de 2026.2 para 2025.1 (que já existe)
        form_data = {"nome": "Período Alterado", "ano": 2025, "semestre": 1}
        form = PeriodoLetivoForm(data=form_data, instance=self.periodo_existente)
        self.assertFalse(form.is_valid())
        self.assertIn("Já existe um período cadastrado para 2025.1", str(form.errors))

    def test_editar_periodo_mudando_para_ano_semestre_livre(self):
        """Testa que permite mudar para ano/semestre que não existe"""
        form_data = {"nome": "Período Letivo 2027.1", "ano": 2027, "semestre": 1}
        form = PeriodoLetivoForm(data=form_data, instance=self.periodo_existente)
        self.assertTrue(form.is_valid())

        # Salvar e verificar que foi atualizado
        periodo_salvo = form.save()
        self.assertEqual(periodo_salvo.ano, 2027)
        self.assertEqual(periodo_salvo.semestre, 1)
        self.assertEqual(periodo_salvo.nome, "Período Letivo 2027.1")
        self.assertEqual(periodo_salvo.id, self.periodo_existente.id)  # Mesmo registro
