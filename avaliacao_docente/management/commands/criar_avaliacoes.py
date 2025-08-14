from django.core.management.base import BaseCommand
from django.db import transaction
from avaliacao_docente.models import CicloAvaliacao, AvaliacaoDocente


class Command(BaseCommand):
    help = "Cria avaliações para ciclos existentes que não possuem avaliações"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ciclo-id", type=int, help="ID específico do ciclo para criar avaliações"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Força a criação mesmo se já existirem avaliações",
        )

    def handle(self, *args, **options):
        ciclo_id = options.get("ciclo_id")
        force = options.get("force", False)

        if ciclo_id:
            # Processar apenas um ciclo específico
            try:
                ciclo = CicloAvaliacao.objects.get(id=ciclo_id)
                ciclos = [ciclo]
            except CicloAvaliacao.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Ciclo com ID {ciclo_id} não encontrado")
                )
                return
        else:
            # Processar todos os ciclos
            ciclos = CicloAvaliacao.objects.all()

        total_avaliacoes_criadas = 0
        total_ciclos_processados = 0

        for ciclo in ciclos:
            avaliacoes_criadas = 0

            self.stdout.write(self.style.SUCCESS(f"\nProcessando ciclo: {ciclo.nome}"))

            # Verificar se o ciclo tem turmas
            if not ciclo.turmas.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"  Ciclo {ciclo.nome} não tem turmas associadas"
                    )
                )
                continue

            with transaction.atomic():
                for turma in ciclo.turmas.all():
                    # Verificar se já existe uma avaliação
                    existe_avaliacao = AvaliacaoDocente.objects.filter(
                        ciclo=ciclo,
                        turma=turma,
                        professor=turma.professor,
                        disciplina=turma.disciplina,
                    ).exists()

                    if existe_avaliacao and not force:
                        self.stdout.write(
                            f"  Avaliação já existe para turma {turma.codigo_turma} - pulando"
                        )
                        continue

                    if existe_avaliacao and force:
                        # Remover avaliação existente
                        AvaliacaoDocente.objects.filter(
                            ciclo=ciclo,
                            turma=turma,
                            professor=turma.professor,
                            disciplina=turma.disciplina,
                        ).delete()
                        self.stdout.write(
                            f"  Avaliação existente removida para turma {turma.codigo_turma}"
                        )

                    # Criar nova avaliação
                    try:
                        avaliacao = AvaliacaoDocente.objects.create(
                            ciclo=ciclo,
                            turma=turma,
                            professor=turma.professor,
                            disciplina=turma.disciplina,
                            status="pendente",
                        )
                        avaliacoes_criadas += 1
                        self.stdout.write(
                            f"  ✓ Avaliação criada: {avaliacao.professor.user.get_full_name()} - {avaliacao.disciplina.disciplina_nome} ({avaliacao.turma.codigo_turma})"
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"  Erro ao criar avaliação para turma {turma.codigo_turma}: {e}"
                            )
                        )
                        continue

            total_avaliacoes_criadas += avaliacoes_criadas
            total_ciclos_processados += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  Total de avaliações criadas para este ciclo: {avaliacoes_criadas}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n=== RESUMO ===\n"
                f"Ciclos processados: {total_ciclos_processados}\n"
                f"Total de avaliações criadas: {total_avaliacoes_criadas}"
            )
        )
