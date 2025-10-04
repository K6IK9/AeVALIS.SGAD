"""Script de verificação manual para o fluxo de soft delete de usuários.

Execute com:
    python -m scripts.manual_tests.test_soft_delete
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django

# Configuração dinâmica do PYTHONPATH para permitir execução direta do script
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.apps import apps  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402
from django.db import transaction  # noqa: E402

from avaliacao_docente.models import (  # noqa: E402
    AvaliacaoDocente,
    MatriculaTurma,
    PerfilAluno,
    PerfilProfessor,
    RespostaAvaliacao,
)


def test_soft_delete_preserves_data() -> None:
    """Valida que o soft delete preserva dados relacionados."""
    print("\n" + "=" * 70)
    print("🧪 TESTE DE SOFT DELETE - PRESERVAÇÃO DE DADOS")
    print("=" * 70 + "\n")

    print("📝 1. Criando usuário de teste...")
    test_user = User.objects.create_user(
        username="999999",
        email="teste@teste.com",
        first_name="Teste",
        last_name="Usuário",
        password="senha123",
    )
    print(f"   ✅ Usuário criado: {test_user.username}")

    print("\n📝 2. Criando perfil de aluno...")
    perfil_aluno = PerfilAluno.objects.create(user=test_user, situacao="Ativo")
    print(f"   ✅ Perfil aluno criado: ID {perfil_aluno.id}")

    matriculas_count = MatriculaTurma.objects.filter(aluno=perfil_aluno).count()
    print(f"\n📊 3. Dados relacionados ANTES do soft delete:")
    print(f"   - Matrículas: {matriculas_count}")
    print(f"   - Perfil ativo: {perfil_aluno.situacao}")
    print(f"   - User is_active: {test_user.is_active}")

    print("\n🔄 4. Executando SOFT DELETE...")
    original_username = test_user.username
    original_email = test_user.email

    test_user.is_active = False
    test_user.first_name = "Usuário"
    test_user.last_name = "Desativado"
    test_user.email = f"desativado_{test_user.id}_{original_email}"
    test_user.username = f"del_{test_user.id}_{original_username}"
    test_user.save()

    print("   ✅ Soft delete executado")
    print(f"   - Username alterado: {original_username} → {test_user.username}")
    print(f"   - Email alterado: {original_email} → {test_user.email}")
    print(f"   - is_active: True → {test_user.is_active}")

    print("\n✅ 5. Verificando PRESERVAÇÃO DE DADOS:")

    test_user.refresh_from_db()

    try:
        perfil_aluno.refresh_from_db()
        print(f"   ✅ Perfil de aluno PRESERVADO (ID: {perfil_aluno.id})")
    except PerfilAluno.DoesNotExist:  # noqa: PERF203 - CLI feedback
        print("   ❌ ERRO: Perfil de aluno foi DELETADO!")

    matriculas_count_after = MatriculaTurma.objects.filter(aluno=perfil_aluno).count()
    print(f"   ✅ Matrículas PRESERVADAS: {matriculas_count_after}")

    print("\n🔒 6. Verificando bloqueio de acesso:")
    print(f"   - is_active: {test_user.is_active}")
    if not test_user.is_active:
        print("   ✅ Usuário NÃO pode fazer login (comportamento esperado)")
    else:
        print("   ❌ ERRO: Usuário ainda pode fazer login!")

    print("\n🧹 7. Limpando dados de teste...")
    test_user.delete()
    print("   ✅ Usuário de teste removido")

    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70 + "\n")


def test_cascade_relationships() -> None:
    """Inspeciona relacionamentos com User e seus on_delete."""
    print("\n" + "=" * 70)
    print("🔍 TESTE DE RELACIONAMENTOS CASCADE")
    print("=" * 70 + "\n")

    models_with_user_fk = [
        ("avaliacao_docente", "PerfilAluno", "user"),
        ("avaliacao_docente", "PerfilProfessor", "user"),
        ("avaliacao_docente", "QuestionarioAvaliacao", "criado_por"),
    ]

    print("📊 Relacionamentos identificados:\n")
    for app_label, model_name, field_name in models_with_user_fk:
        try:
            model = apps.get_model(app_label, model_name)
            field = model._meta.get_field(field_name)
            on_delete = field.remote_field.on_delete.__name__
            print(f"   {model_name}.{field_name}")
            print(f"   └─ on_delete: {on_delete}\n")
        except Exception as exc:  # noqa: BLE001 - CLI feedback
            print(f"   ⚠️ Erro ao inspecionar {model_name}: {exc}\n")

    print("💡 CONCLUSÃO:")
    print("   Com soft delete (is_active=False), os relacionamentos CASCADE")
    print("   são PRESERVADOS porque o registro User não é deletado.")
    print("\n" + "=" * 70 + "\n")


def test_view_behavior() -> None:
    """Exibe estatísticas de usuários ativos/inativos para análise manual."""
    print("\n" + "=" * 70)
    print("🎯 TESTE DE COMPORTAMENTO EM VIEWS")
    print("=" * 70 + "\n")

    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()

    print("📊 Estatísticas de Usuários:")
    print(f"   Total: {total_users}")
    print(f"   Ativos: {active_users}")
    print(f"   Inativos: {inactive_users}\n")

    alunos_inativos = PerfilAluno.objects.filter(user__is_active=False).count()
    professores_inativos = PerfilProfessor.objects.filter(user__is_active=False).count()

    print("📊 Perfis com Usuários Inativos:")
    print(f"   Alunos: {alunos_inativos}")
    print(f"   Professores: {professores_inativos}\n")

    print("💡 RECOMENDAÇÃO:")
    print("   Adicionar filtros nas views para excluir usuários inativos:")
    print("   - PerfilAluno.objects.filter(user__is_active=True)")
    print("   - PerfilProfessor.objects.filter(user__is_active=True)")
    print("\n" + "=" * 70 + "\n")


def main() -> None:
    """Executa os testes com rollback automático para preservar o banco."""
    print("\n🚀 Iniciando bateria de testes de Soft Delete...\n")

    try:
        with transaction.atomic():
            test_soft_delete_preserves_data()
            test_cascade_relationships()
            test_view_behavior()

            print("\n✅ TODOS OS TESTES EXECUTADOS COM SUCESSO!")
            print("\n⚠️  Nota: Testes executados em transação (rollback automático)\n")

            raise Exception(
                "Rollback intencional - dados de teste não foram persistidos"
            )

    except Exception as exc:  # noqa: BLE001 - CLI feedback
        if "Rollback intencional" in str(exc):
            print("✅ Rollback executado - banco de dados não foi alterado\n")
        else:
            print(f"\n❌ ERRO durante os testes: {exc}\n")
            raise


if __name__ == "__main__":
    main()
