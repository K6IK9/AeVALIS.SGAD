from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from datetime import timedelta
from .models import (
    CicloAvaliacao,
    AvaliacaoDocente,
    JobLembreteCicloTurma,
    ConfiguracaoSite,
)
from .utils import enviar_email_notificacao_avaliacao


@receiver(m2m_changed, sender=CicloAvaliacao.turmas.through)
def criar_avaliacoes_automaticamente(sender, instance, action, pk_set, **kwargs):
    """
    Signal para criar automaticamente as avaliações e notificar alunos.
    """
    if action == "post_add":
        Turma = apps.get_model("avaliacao_docente", "Turma")

        for turma_id in pk_set:
            try:
                turma = Turma.objects.get(id=turma_id)

                avaliacao, created = AvaliacaoDocente.objects.get_or_create(
                    ciclo=instance,
                    turma=turma,
                    professor=turma.disciplina.professor,
                    disciplina=turma.disciplina,
                    defaults={"status": "pendente"},
                )

                if created:
                    print(f"Avaliação criada: {avaliacao}")

                    # Se a notificação estiver ativa no ciclo, enviar e-mails
                    if instance.enviar_lembrete_email:
                        # Buscar todos os alunos com matrícula ativa na turma
                        matriculas = turma.matriculas.filter(
                            status="ativa"
                        ).select_related("aluno__user")
                        print(
                            f"Notificando {matriculas.count()} alunos da turma {turma.codigo_turma}..."
                        )
                        for matricula in matriculas:
                            try:
                                enviar_email_notificacao_avaliacao(
                                    matricula.aluno.user, avaliacao
                                )
                            except Exception as e:
                                print(
                                    f"ERRO ao enviar e-mail para {matricula.aluno.user.email}: {e}"
                                )

            except Turma.DoesNotExist:
                print(f"Turma com ID {turma_id} não encontrada")
                continue
            except Exception as e:
                print(f"Erro ao criar avaliação para turma {turma_id}: {e}")
                continue
    elif action == "post_remove":
        # Quando turmas são removidas do ciclo, remover avaliações sem respostas associadas
        for turma_id in pk_set:
            try:
                avaliacoes = AvaliacaoDocente.objects.filter(
                    ciclo=instance, turma_id=turma_id
                )
                for avaliacao in avaliacoes:
                    if not avaliacao.respostas.exists():
                        avaliacao.delete()
            except Exception as e:
                print(
                    f"Erro ao remover avaliações da turma {turma_id} após remoção do ciclo: {e}"
                )


@receiver(post_save, sender=CicloAvaliacao)
def criar_avaliacoes_pos_save(sender, instance, created, **kwargs):
    """
    Signal para criar avaliações após salvar um ciclo (backup para casos onde o signal anterior não funciona)
    """
    if created:
        # Se o ciclo foi recém-criado, aguardar o save_m2m
        return

    # Verificar se existem turmas sem avaliações
    from django.db import transaction

    with transaction.atomic():
        for turma in instance.turmas.all():
            # Verificar se já existe uma avaliação para esta turma neste ciclo
            if not AvaliacaoDocente.objects.filter(
                ciclo=instance,
                turma=turma,
                professor=turma.disciplina.professor,
                disciplina=turma.disciplina,
            ).exists():
                # Criar a avaliação
                avaliacao = AvaliacaoDocente.objects.create(
                    ciclo=instance,
                    turma=turma,
                    professor=turma.disciplina.professor,
                    disciplina=turma.disciplina,
                    status="pendente",
                )
                print(f"Avaliação criada via post_save: {avaliacao}")


@receiver(m2m_changed, sender=CicloAvaliacao.turmas.through)
def criar_jobs_lembrete_para_turmas(sender, instance, action, pk_set, **kwargs):
    """
    Signal para criar JobLembreteCicloTurma quando turmas são adicionadas a um ciclo.
    Garante que cada turma tenha um job de controle de lembretes.
    """
    if action == "post_add":
        Turma = apps.get_model("avaliacao_docente", "Turma")
        config = ConfiguracaoSite.obter_config()

        # Calcular o próximo envio baseado na frequência configurada
        proximo_envio = timezone.now() + timedelta(
            hours=config.frequencia_lembrete_horas
        )

        for turma_id in pk_set:
            try:
                turma = Turma.objects.get(id=turma_id)

                # Criar ou atualizar job de lembrete para esta turma/ciclo
                job, created = JobLembreteCicloTurma.objects.get_or_create(
                    ciclo=instance,
                    turma=turma,
                    defaults={
                        "status": "pendente",
                        "proximo_envio_em": proximo_envio,
                    },
                )

                if created:
                    print(
                        f"✅ Job de lembrete criado: {instance.nome} - {turma.codigo_turma}"
                    )
                else:
                    print(
                        f"ℹ️ Job de lembrete já existe: {instance.nome} - {turma.codigo_turma}"
                    )

            except Turma.DoesNotExist:
                print(f"❌ Turma com ID {turma_id} não encontrada")
                continue
            except Exception as e:
                print(f"❌ Erro ao criar job de lembrete para turma {turma_id}: {e}")
                continue

    elif action == "post_remove":
        # Quando turmas são removidas do ciclo, pausar os jobs correspondentes
        for turma_id in pk_set:
            try:
                JobLembreteCicloTurma.objects.filter(
                    ciclo=instance, turma_id=turma_id
                ).update(status="pausado")
                print(f"⏸️ Job de lembrete pausado para turma ID {turma_id}")
            except Exception as e:
                print(f"❌ Erro ao pausar job de lembrete da turma {turma_id}: {e}")
