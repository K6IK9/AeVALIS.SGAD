from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.apps import apps
from .models import CicloAvaliacao, AvaliacaoDocente


@receiver(m2m_changed, sender=CicloAvaliacao.turmas.through)
def criar_avaliacoes_automaticamente(sender, instance, action, pk_set, **kwargs):
    """
    Signal para criar automaticamente as avaliações quando turmas são adicionadas a um ciclo
    """
    if action == "post_add":
        # Obter o modelo Turma
        Turma = apps.get_model("avaliacao_docente", "Turma")

        # Criar avaliações para as turmas adicionadas
        for turma_id in pk_set:
            try:
                turma = Turma.objects.get(id=turma_id)

                # Criar avaliação para a turma
                avaliacao, created = AvaliacaoDocente.objects.get_or_create(
                    ciclo=instance,
                    turma=turma,
                    professor=turma.professor,
                    disciplina=turma.disciplina,
                    defaults={"status": "pendente"},
                )

                if created:
                    print(f"Avaliação criada: {avaliacao}")

            except Turma.DoesNotExist:
                print(f"Turma com ID {turma_id} não encontrada")
                continue
            except Exception as e:
                print(f"Erro ao criar avaliação para turma {turma_id}: {e}")
                continue


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
                professor=turma.professor,
                disciplina=turma.disciplina,
            ).exists():
                # Criar a avaliação
                avaliacao = AvaliacaoDocente.objects.create(
                    ciclo=instance,
                    turma=turma,
                    professor=turma.professor,
                    disciplina=turma.disciplina,
                    status="pendente",
                )
                print(f"Avaliação criada via post_save: {avaliacao}")
