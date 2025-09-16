from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_docente.utils import (
    is_role_manually_changed,
    reset_role_manual_flag,
    mark_role_manually_changed,
)


class Command(BaseCommand):
    help = "Gerencia flags de roles manuais dos usuários"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="Lista usuários com flags manuais ativas",
        )
        parser.add_argument(
            "--reset-all",
            action="store_true",
            help="Remove todas as flags manuais (permitindo gerenciamento automático)",
        )
        parser.add_argument(
            "--reset-user",
            type=str,
            help="Remove flag manual de um usuário específico (username)",
        )
        parser.add_argument(
            "--set-user",
            type=str,
            help="Define flag manual para um usuário específico (username)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula as ações sem aplicar mudanças",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODO SIMULAÇÃO - Nenhuma mudança será aplicada")
            )

        if options["list"]:
            self.list_manual_flags()
        elif options["reset_all"]:
            self.reset_all_flags(dry_run)
        elif options["reset_user"]:
            self.reset_user_flag(options["reset_user"], dry_run)
        elif options["set_user"]:
            self.set_user_flag(options["set_user"], dry_run)
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Nenhuma ação especificada. Use --help para ver as opções."
                )
            )

    def list_manual_flags(self):
        self.stdout.write(
            self.style.SUCCESS("=== Usuários com Flags Manuais Ativas ===")
        )

        users_with_manual_flags = []
        for user in User.objects.all():
            if is_role_manually_changed(user):
                users_with_manual_flags.append(user)

        if users_with_manual_flags:
            for user in users_with_manual_flags:
                from avaliacao_docente.utils import get_user_role_name

                role = get_user_role_name(user)
                self.stdout.write(
                    f"📌 {user.username} ({user.get_full_name()}) - Role: {role}"
                )
            self.stdout.write(f"\nTotal: {len(users_with_manual_flags)} usuários")
        else:
            self.stdout.write("✅ Nenhum usuário com flag manual encontrado")

    def reset_all_flags(self, dry_run):
        self.stdout.write(
            self.style.SUCCESS("=== Removendo Todas as Flags Manuais ===")
        )

        reset_count = 0
        for user in User.objects.all():
            if is_role_manually_changed(user):
                reset_count += 1
                status = "SIMULAÇÃO" if dry_run else "REMOVIDO"
                self.stdout.write(
                    f"[{status}] Flag manual removida de {user.username} ({user.get_full_name()})"
                )

                if not dry_run:
                    reset_role_manual_flag(user)

        if reset_count == 0:
            self.stdout.write("✅ Nenhuma flag manual encontrada")
        else:
            status_msg = "seriam removidas" if dry_run else "removidas"
            self.stdout.write(
                self.style.SUCCESS(f"\n{reset_count} flags manuais {status_msg}")
            )

    def reset_user_flag(self, username, dry_run):
        try:
            user = User.objects.get(username=username)

            if is_role_manually_changed(user):
                status = "SIMULAÇÃO" if dry_run else "REMOVIDO"
                self.stdout.write(
                    f"[{status}] Flag manual removida de {user.username} ({user.get_full_name()})"
                )

                if not dry_run:
                    reset_role_manual_flag(user)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Usuário {username} não possui flag manual ativa"
                    )
                )

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Usuário {username} não encontrado"))

    def set_user_flag(self, username, dry_run):
        try:
            user = User.objects.get(username=username)

            if not is_role_manually_changed(user):
                status = "SIMULAÇÃO" if dry_run else "DEFINIDO"
                self.stdout.write(
                    f"[{status}] Flag manual definida para {user.username} ({user.get_full_name()})"
                )

                if not dry_run:
                    mark_role_manually_changed(user)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Usuário {username} já possui flag manual ativa"
                    )
                )

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Usuário {username} não encontrado"))
