from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from avaliacao_docente.models import MatriculaTurma


class Command(BaseCommand):
    help = "Remove admins das matrículas de turmas (admins não devem estar matriculados como alunos)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula as mudanças sem aplicá-las no banco",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("=== Verificando matrículas de admins ===")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODO SIMULAÇÃO - Nenhuma mudança será aplicada")
            )

        # Buscar todas as matrículas ativas
        matriculas = MatriculaTurma.objects.filter(status="ativa").select_related(
            "aluno__user", "turma"
        )

        removed_count = 0

        for matricula in matriculas:
            user = matricula.aluno.user

            # Verificar se o usuário é admin
            if has_role(user, "admin"):
                removed_count += 1

                status = "SIMULAÇÃO" if dry_run else "REMOVIDO"
                self.stdout.write(
                    f"[{status}] Admin {user.username} ({user.get_full_name()}) "
                    f"removido da turma {matricula.turma.codigo_turma}"
                )

                if not dry_run:
                    matricula.delete()

        # Resumo
        self.stdout.write(self.style.SUCCESS(f"\n=== Resumo ==="))
        self.stdout.write(f"Matrículas de admins encontradas: {removed_count}")

        if removed_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "Nenhuma matrícula de admin encontrada - sistema está correto!"
                )
            )
        elif dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Execute novamente sem --dry-run para aplicar as mudanças"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Matrículas de admins removidas com sucesso!")
            )
