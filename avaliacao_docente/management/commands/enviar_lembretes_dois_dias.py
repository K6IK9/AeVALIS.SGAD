"""
Comando de gerenciamento Django para enviar lembretes 2 dias antes do encerramento.

Execução:
    python manage.py enviar_lembretes_dois_dias

Configuração Cron (todo dia às 9h):
    0 9 * * * cd /path/to/project && python manage.py enviar_lembretes_dois_dias
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from avaliacao_docente.models import (
    CicloAvaliacao,
    LembreteAvaliacao,
    MatriculaTurma,
    RespostaAvaliacao,
)


class Command(BaseCommand):
    help = "Envia lembretes para alunos 2 dias antes do encerramento do ciclo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula execução sem enviar e-mails",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 MODO DRY-RUN: Nenhum e-mail será enviado")
            )

        hoje = timezone.now().date()
        data_alvo = hoje + timedelta(days=2)

        self.stdout.write(
            f"\n📅 Verificando ciclos que encerram em: {data_alvo.strftime('%d/%m/%Y')}"
        )

        # Buscar ciclos que encerram exatamente em 2 dias
        ciclos = CicloAvaliacao.objects.filter(
            ativo=True, encerrado=False, data_fim__date=data_alvo
        )

        total_ciclos = ciclos.count()
        self.stdout.write(f"📊 Encontrados {total_ciclos} ciclo(s)\n")

        if total_ciclos == 0:
            self.stdout.write(self.style.SUCCESS("✓ Nenhum ciclo encerrando em 2 dias"))
            return

        total_emails_enviados = 0

        for ciclo in ciclos:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🔄 Processando: {ciclo.nome}")
            self.stdout.write(f"{'='*60}")

            # Verificar se já foi enviado
            if LembreteAvaliacao.objects.filter(ciclo=ciclo, tipo="dois_dias").exists():
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Lembrete já enviado anteriormente")
                )
                continue

            # Buscar alunos que NÃO responderam
            try:
                turmas = ciclo.turmas.all()
                if not turmas.exists():
                    self.stdout.write(
                        self.style.WARNING("⚠️  Ciclo sem turmas vinculadas")
                    )
                    continue

                matriculas = MatriculaTurma.objects.filter(
                    turma__in=turmas, ativo=True
                ).select_related("aluno__user")

                alunos_matriculados = [m.aluno for m in matriculas]
                total_matriculados = len(alunos_matriculados)

                self.stdout.write(
                    f"👥 Total de alunos matriculados: {total_matriculados}"
                )

                # Filtrar alunos que já responderam
                alunos_responderam = (
                    RespostaAvaliacao.objects.filter(avaliacao__ciclo=ciclo)
                    .values_list("aluno_id", flat=True)
                    .distinct()
                )

                total_responderam = alunos_responderam.count()
                self.stdout.write(f"✅ Alunos que já responderam: {total_responderam}")

                alunos_sem_resposta = [
                    aluno
                    for aluno in alunos_matriculados
                    if aluno.id not in alunos_responderam
                ]

                total_sem_resposta = len(alunos_sem_resposta)
                self.stdout.write(f"⏳ Alunos sem resposta: {total_sem_resposta}")

                if not alunos_sem_resposta:
                    self.stdout.write(
                        self.style.SUCCESS("🎉 Todos os alunos já responderam!")
                    )
                    continue

                # Preparar e-mails
                mensagens = []
                for aluno in alunos_sem_resposta:
                    if not aluno.user.email:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Aluno {aluno.user.username} sem e-mail cadastrado"
                            )
                        )
                        continue

                    assunto = (
                        f"LEMBRETE: Avaliação Docente encerra em 2 dias - {ciclo.nome}"
                    )
                    mensagem = f"""Olá {aluno.user.get_full_name() or aluno.user.username},

Este é um lembrete de que a avaliação docente está próxima do encerramento.

Ciclo: {ciclo.nome}
Encerra em: {ciclo.data_fim.strftime('%d/%m/%Y às %H:%M')} (faltam 2 dias)

Você ainda NÃO respondeu a esta avaliação.
Sua participação é fundamental para a qualidade do ensino.

Por favor, acesse o sistema e preencha a avaliação o quanto antes.

Atenciosamente,
Equipe de Avaliação Docente
"""

                    mensagens.append(
                        (
                            assunto,
                            mensagem,
                            settings.DEFAULT_FROM_EMAIL,
                            [aluno.user.email],
                        )
                    )

                # Enviar e-mails
                if mensagens:
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f"🔍 [DRY-RUN] {len(mensagens)} e-mails seriam enviados"
                            )
                        )
                    else:
                        try:
                            send_mass_mail(mensagens, fail_silently=False)

                            # Registrar envio
                            LembreteAvaliacao.objects.create(
                                ciclo=ciclo,
                                tipo="dois_dias",
                                total_enviados=len(mensagens),
                            )

                            total_emails_enviados += len(mensagens)

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"✅ {len(mensagens)} lembretes enviados com sucesso!"
                                )
                            )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"❌ Erro ao enviar e-mails: {str(e)}")
                            )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Erro ao processar ciclo {ciclo.nome}: {str(e)}"
                    )
                )

        # Resumo final
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("📊 RESUMO")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(f"Ciclos verificados: {total_ciclos}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"🔍 [DRY-RUN] E-mails que seriam enviados: {total_emails_enviados}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Total de e-mails enviados: {total_emails_enviados}"
                )
            )

        self.stdout.write(f"{'='*60}\n")
        self.stdout.write(self.style.SUCCESS("✓ Processo concluído!"))
