"""
Management command para enviar lembretes automáticos de avaliação.

Este comando deve ser executado periodicamente (via cron/celery) para:
1. Identificar turmas que não atingiram o limiar mínimo de respostas (10%)
2. Selecionar alunos elegíveis que ainda não responderam
3. Enviar e-mails de lembrete em lote
4. Atualizar contadores e status dos jobs
5. Parar automaticamente quando limiar for atingido

Uso:
    python manage.py enviar_lembretes_ciclos [--dry-run] [--force-job-id ID]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
import logging

from avaliacao_docente.models import (
    JobLembreteCicloTurma,
    NotificacaoLembrete,
    ConfiguracaoSite,
)
from avaliacao_docente.services import (
    calcular_taxa_resposta_turma,
    obter_alunos_pendentes_lembrete,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Envia lembretes automáticos de avaliação para alunos de turmas que não atingiram o limiar mínimo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula o envio sem realmente enviar e-mails",
        )
        parser.add_argument(
            "--force-job-id",
            type=int,
            help="Força o processamento de um job específico (ignora próximo_envio_em)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Tamanho do lote de e-mails por iteração (padrão: 200)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force_job_id = options["force_job_id"]
        batch_size = options["batch_size"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "🔍 Modo DRY RUN ativado - nenhum e-mail será enviado"
                )
            )

        config = ConfiguracaoSite.obter_config()

        self.stdout.write(f"\n📧 Iniciando processamento de lembretes...")
        self.stdout.write(f"⚙️  Configurações:")
        self.stdout.write(f"   - Limiar mínimo: {config.limiar_minimo_percentual}%")
        self.stdout.write(f"   - Frequência: {config.frequencia_lembrete_horas}h")
        self.stdout.write(f"   - Max lembretes/aluno: {config.max_lembretes_por_aluno}")
        self.stdout.write(f"   - Tamanho do lote: {batch_size}\n")

        # Buscar jobs pendentes
        if force_job_id:
            jobs = JobLembreteCicloTurma.objects.filter(id=force_job_id)
            self.stdout.write(
                self.style.WARNING(
                    f"⚡ Modo FORCE: processando apenas job ID {force_job_id}"
                )
            )
        else:
            jobs = JobLembreteCicloTurma.objects.filter(
                status__in=["pendente", "em_execucao"],
                proximo_envio_em__lte=timezone.now(),
            ).select_related("ciclo", "turma", "turma__disciplina", "turma__curso")

        if not jobs.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ Nenhum job pendente para processar no momento")
            )
            return

        self.stdout.write(f"📋 Encontrados {jobs.count()} job(s) para processar\n")

        total_emails_enviados = 0
        total_jobs_concluidos = 0
        total_jobs_com_erro = 0

        for job in jobs:
            self.stdout.write(f'\n{"="*80}')
            self.stdout.write(
                f"🔄 Processando: {job.ciclo.nome} - {job.turma.codigo_turma}"
            )
            self.stdout.write(f"   Status atual: {job.status}")

            try:
                # Atualizar status para "em_execucao"
                job.status = "em_execucao"
                job.ultima_execucao = timezone.now()
                if not dry_run:
                    job.save(update_fields=["status", "ultima_execucao"])

                # Verificar se ciclo ainda está ativo
                if job.ciclo.data_fim < timezone.now().date():
                    self.stdout.write(
                        self.style.WARNING(
                            f"⏰ Ciclo expirado ({job.ciclo.data_fim}). Marcando job como completo."
                        )
                    )
                    job.status = "completo"
                    if not dry_run:
                        job.save(update_fields=["status"])
                    continue

                # Calcular taxa de resposta atual
                taxa_info = calcular_taxa_resposta_turma(job.ciclo, job.turma)
                job.total_alunos_aptos = taxa_info["alunos_aptos"]
                job.total_respondentes = taxa_info["respondentes"]
                job.taxa_resposta_atual = taxa_info["taxa_percentual"]

                self.stdout.write(
                    f'   📊 Taxa atual: {taxa_info["taxa_percentual"]}% '
                    f'({taxa_info["respondentes"]}/{taxa_info["alunos_aptos"]} alunos)'
                )

                # Verificar se atingiu o limiar
                if taxa_info["taxa_percentual"] >= config.limiar_minimo_percentual:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ✅ Limiar atingido ({config.limiar_minimo_percentual}%)! "
                            f"Marcando job como completo."
                        )
                    )
                    job.status = "completo"
                    if not dry_run:
                        job.save()
                    total_jobs_concluidos += 1
                    continue

                # Obter alunos elegíveis para receber lembrete
                alunos_elegiveis = obter_alunos_pendentes_lembrete(job)

                if not alunos_elegiveis.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            "   ⚠️  Nenhum aluno elegível para receber lembrete. "
                            "Possíveis razões: todos responderam ou atingiram limite de lembretes."
                        )
                    )
                    job.status = "completo"
                    if not dry_run:
                        job.save(update_fields=["status"])
                    total_jobs_concluidos += 1
                    continue

                self.stdout.write(f"   👥 Alunos elegíveis: {alunos_elegiveis.count()}")

                # Processar em lotes
                emails_enviados_job = 0
                emails_falhados_job = 0

                for i in range(0, alunos_elegiveis.count(), batch_size):
                    lote = alunos_elegiveis[i : i + batch_size]
                    self.stdout.write(f"   📤 Processando lote {i//batch_size + 1}...")

                    for aluno in lote:
                        resultado = self._enviar_lembrete(
                            job=job, aluno=aluno, config=config, dry_run=dry_run
                        )

                        if resultado["sucesso"]:
                            emails_enviados_job += 1
                        else:
                            emails_falhados_job += 1

                # Atualizar contadores do job
                job.total_emails_enviados += emails_enviados_job
                job.total_falhas += emails_falhados_job
                job.rodadas_executadas += 1

                # Agendar próximo envio
                job.proximo_envio_em = timezone.now() + timedelta(
                    hours=config.frequencia_lembrete_horas
                )
                job.status = "pendente"

                if not dry_run:
                    job.save()

                total_emails_enviados += emails_enviados_job

                self.stdout.write(
                    self.style.SUCCESS(
                        f"   ✅ Job processado: {emails_enviados_job} enviados, "
                        f"{emails_falhados_job} falhas"
                    )
                )
                self.stdout.write(f"   ⏰ Próximo envio: {job.proximo_envio_em}")

            except Exception as e:
                logger.exception(f"Erro ao processar job {job.id}")
                self.stdout.write(self.style.ERROR(f"   ❌ ERRO: {str(e)}"))

                job.status = "erro"
                job.mensagem_erro = str(e)[:500]
                if not dry_run:
                    job.save(update_fields=["status", "mensagem_erro"])

                total_jobs_com_erro += 1

        # Resumo final
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.SUCCESS("\n📊 RESUMO DA EXECUÇÃO:"))
        self.stdout.write(f"   📧 Total de e-mails enviados: {total_emails_enviados}")
        self.stdout.write(f"   ✅ Jobs concluídos: {total_jobs_concluidos}")
        self.stdout.write(f"   ❌ Jobs com erro: {total_jobs_com_erro}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n⚠️  DRY RUN: Nenhuma alteração foi salva no banco")
            )

    def _enviar_lembrete(self, job, aluno, config, dry_run=False):
        """
        Envia um e-mail de lembrete para um aluno específico.

        Returns:
            dict: {'sucesso': bool, 'mensagem': str}
        """
        try:
            # Calcular número da rodada para este aluno
            rodada = (
                NotificacaoLembrete.objects.filter(job=job, aluno=aluno).count() + 1
            )

            # Preparar contexto para o template
            contexto = {
                "nome_aluno": aluno.user.get_full_name() or aluno.user.username,
                "nome_curso": job.turma.curso.nome if job.turma.curso else "N/A",
                "codigo_turma": job.turma.codigo_turma,
                "nome_ciclo": job.ciclo.nome,
                "data_fim": job.ciclo.data_fim,
                "link_avaliacao": f"{settings.SITE_URL}/avaliacoes/",
                "rodada": rodada,
            }

            # Renderizar templates
            assunto = f"Lembrete: Avalie a disciplina - {job.turma.disciplina.nome}"
            mensagem_html = render_to_string("emails/lembrete_avaliacao.html", contexto)
            mensagem_texto = render_to_string("emails/lembrete_avaliacao.txt", contexto)

            if not dry_run:
                # Criar registro de notificação
                notificacao = NotificacaoLembrete.objects.create(
                    job=job,
                    aluno=aluno,
                    status="pendente",
                    rodada=rodada,
                )

                try:
                    # Enviar e-mail
                    send_mail(
                        subject=assunto,
                        message=mensagem_texto,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[aluno.user.email],
                        html_message=mensagem_html,
                        fail_silently=False,
                    )

                    # Atualizar notificação como enviada
                    notificacao.status = "enviado"
                    notificacao.enviado_em = timezone.now()
                    notificacao.save()

                    return {"sucesso": True, "mensagem": "E-mail enviado com sucesso"}

                except Exception as e:
                    # Registrar falha
                    notificacao.status = "falhou"
                    notificacao.tentativas += 1
                    notificacao.motivo_falha = str(e)[:500]
                    notificacao.save()

                    logger.error(f"Erro ao enviar e-mail para {aluno.user.email}: {e}")
                    return {"sucesso": False, "mensagem": str(e)}
            else:
                self.stdout.write(
                    f"      [DRY RUN] Enviaria e-mail para: {aluno.user.email} "
                    f"(Rodada {rodada})"
                )
                return {"sucesso": True, "mensagem": "DRY RUN"}

        except Exception as e:
            logger.exception(
                f"Erro inesperado ao processar lembrete para aluno {aluno.id}"
            )
            return {"sucesso": False, "mensagem": str(e)}
