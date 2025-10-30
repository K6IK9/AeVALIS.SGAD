"""
Comando para limpar usuários com username/matrícula inválidos.
Remove usuários cujo username contém letras, pois matrícula deve ser apenas numérica.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = "Remove usuários com username/matrícula inválidos (contendo letras)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Apenas lista os usuários que seriam excluídos, sem excluir",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirma a exclusão dos usuários inválidos",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        confirm = options["confirm"]

        # Buscar usuários com letras no username (matrícula inválida)
        usuarios_invalidos = User.objects.filter(username__regex=r"[a-zA-Z]").exclude(
            is_superuser=True  # Não excluir superusuários
        )

        total = usuarios_invalidos.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Nenhum usuário com username/matrícula inválido encontrado."
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"\n⚠ Encontrados {total} usuário(s) com username/matrícula inválido(s):\n"
            )
        )

        # Listar usuários que serão afetados
        for user in usuarios_invalidos:
            roles = []
            if hasattr(user, "perfil_aluno"):
                roles.append("Aluno")
            if hasattr(user, "perfil_professor"):
                roles.append("Professor")

            role_str = ", ".join(roles) if roles else "Sem perfil"

            self.stdout.write(
                f'  • ID: {user.id} | Username: "{user.username}" | '
                f'Nome: {user.get_full_name() or "N/A"} | '
                f'Email: {user.email or "N/A"} | '
                f"Roles: {role_str}"
            )

        # Se for dry-run, apenas mostrar o que seria feito
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n🔍 DRY RUN: {total} usuário(s) seriam excluídos.\n"
                    "Execute novamente com --confirm para confirmar a exclusão."
                )
            )
            return

        # Se não houver confirmação, pedir
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ Para excluir estes {total} usuário(s), execute:\n"
                    "python manage.py limpar_usuarios_invalidos --confirm\n"
                )
            )
            return

        # Confirmar exclusão
        self.stdout.write(
            self.style.WARNING(
                f"\n⚠ ATENÇÃO: Você está prestes a excluir {total} usuário(s)!"
            )
        )

        confirmacao = input('Digite "SIM" para confirmar a exclusão: ')

        if confirmacao != "SIM":
            self.stdout.write(self.style.ERROR("\n✗ Exclusão cancelada."))
            return

        # Executar exclusão com transação
        try:
            with transaction.atomic():
                # Contar perfis relacionados
                perfis_aluno = sum(
                    1 for u in usuarios_invalidos if hasattr(u, "perfil_aluno")
                )
                perfis_professor = sum(
                    1 for u in usuarios_invalidos if hasattr(u, "perfil_professor")
                )

                # Excluir usuários (cascade exclui perfis automaticamente)
                usuarios_excluidos, detalhes = usuarios_invalidos.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✓ Exclusão concluída com sucesso!\n"
                        f"  • Usuários excluídos: {total}\n"
                        f"  • Perfis de aluno excluídos: {perfis_aluno}\n"
                        f"  • Perfis de professor excluídos: {perfis_professor}\n"
                    )
                )

                # Mostrar detalhes da exclusão
                if detalhes:
                    self.stdout.write("\n📊 Detalhes da exclusão:")
                    for modelo, qtd in detalhes.items():
                        if qtd > 0:
                            self.stdout.write(f"  • {modelo}: {qtd}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n✗ Erro ao excluir usuários: {str(e)}")
            )
            raise

        self.stdout.write(self.style.SUCCESS("\n✓ Limpeza concluída!\n"))
