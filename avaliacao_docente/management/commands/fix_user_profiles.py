from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from avaliacao_docente.models import PerfilAluno, PerfilProfessor


class Command(BaseCommand):
    help = "Corrige perfis de usuários inconsistentes baseado nas roles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula as mudanças sem aplicá-las no banco",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.SUCCESS("=== Verificando consistência de perfis ===")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("MODO SIMULAÇÃO - Nenhuma mudança será aplicada")
            )

        total_users = User.objects.count()
        processed = 0
        fixed = 0

        for user in User.objects.all():
            processed += 1
            changes = []

            # Determinar role atual
            current_role = None
            if has_role(user, "admin"):
                current_role = "admin"
            elif has_role(user, "coordenador"):
                current_role = "coordenador"
            elif has_role(user, "professor"):
                current_role = "professor"
            elif has_role(user, "aluno"):
                current_role = "aluno"

            # Verificar perfis existentes
            has_perfil_aluno = hasattr(user, "perfil_aluno")
            has_perfil_professor = hasattr(user, "perfil_professor")

            # Determinar ações necessárias
            if current_role == "aluno":
                if has_perfil_professor:
                    changes.append("Remover perfil de professor")
                    if not dry_run:
                        user.perfil_professor.delete()

                if not has_perfil_aluno:
                    changes.append("Criar perfil de aluno")
                    if not dry_run:
                        PerfilAluno.objects.create(user=user)

            elif current_role in ["professor", "coordenador"]:
                if has_perfil_aluno:
                    changes.append("Remover perfil de aluno")
                    if not dry_run:
                        user.perfil_aluno.delete()

                if not has_perfil_professor:
                    changes.append("Criar perfil de professor")
                    if not dry_run:
                        PerfilProfessor.objects.create(
                            user=user, registro_academico=user.username
                        )

            elif current_role == "admin":
                # Admin não deve ter nenhum perfil específico
                if has_perfil_aluno:
                    changes.append(
                        "Remover perfil de aluno (admin não deve ter perfil)"
                    )
                    if not dry_run:
                        user.perfil_aluno.delete()

                if has_perfil_professor:
                    changes.append(
                        "Remover perfil de professor (admin não deve ter perfil)"
                    )
                    if not dry_run:
                        user.perfil_professor.delete()

            else:
                # Usuário sem role
                if has_perfil_aluno or has_perfil_professor:
                    changes.append("Usuário sem role mas com perfil")

            # Reportar mudanças
            if changes:
                fixed += 1
                status = "SIMULAÇÃO" if dry_run else "APLICADO"
                self.stdout.write(
                    f"[{status}] {user.username} ({current_role or 'sem role'}):"
                )
                for change in changes:
                    self.stdout.write(f"  - {change}")

        # Resumo
        self.stdout.write(self.style.SUCCESS(f"\n=== Resumo ==="))
        self.stdout.write(f"Usuários processados: {processed}")
        self.stdout.write(f"Usuários que precisavam de correção: {fixed}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Execute novamente sem --dry-run para aplicar as mudanças"
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Correções aplicadas com sucesso!"))
