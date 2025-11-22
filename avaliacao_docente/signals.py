from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mass_mail
from django.core.cache import cache
from datetime import timedelta
import hashlib

from .models import (
    CicloAvaliacao,
    AvaliacaoDocente,
    JobLembreteCicloTurma,
    ConfiguracaoSite,
    LembreteAvaliacao,
    RespostaAvaliacao,
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

                # Usa all_objects para evitar erro de integridade se já existir uma avaliação deletada
                avaliacao, created = AvaliacaoDocente.all_objects.get_or_create(
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

    # Não criar avaliações se o ciclo está sendo deletado (soft delete)
    if not instance.ativo:
        return

    # Não criar avaliações se o ciclo está encerrado
    if hasattr(instance, "encerrado") and instance.encerrado:
        return

    # Verificar se existem turmas sem avaliações
    from django.db import transaction

    with transaction.atomic():
        for turma in instance.turmas.all():
            # Verificar se já existe uma avaliação para esta turma neste ciclo (inclusive deletadas)
            if not AvaliacaoDocente.all_objects.filter(
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


@receiver(post_save, sender=CicloAvaliacao)
def enviar_email_criacao_ciclo(sender, instance, created, **kwargs):
    """
    Envia e-mail para todos os alunos quando um ciclo é criado.
    Dispara apenas na criação (created=True) e se o ciclo estiver ativo.
    """
    if not created:
        return

    if not instance.ativo or instance.encerrado:
        return

    # Verificar se já foi enviado (evitar duplicação)
    if LembreteAvaliacao.objects.filter(ciclo=instance, tipo="criacao").exists():
        print(f"ℹ️ E-mail de criação já foi enviado para o ciclo: {instance.nome}")
        return

    # Buscar todos os alunos das turmas do ciclo
    from .models import MatriculaTurma

    try:
        turmas = instance.turmas.all()
        if not turmas.exists():
            print(f"⚠️ Ciclo {instance.nome} não possui turmas vinculadas")
            return

        matriculas = MatriculaTurma.objects.filter(
            turma__in=turmas, ativo=True
        ).select_related("aluno__user")

        alunos = {m.aluno for m in matriculas}

        if not alunos:
            print(f"⚠️ Nenhum aluno ativo encontrado para o ciclo: {instance.nome}")
            return

        # Preparar e-mails em massa
        mensagens = []
        for aluno in alunos:
            if not aluno.user.email:
                continue

            assunto = f"Nova Avaliação Docente Disponível: {instance.nome}"
            mensagem = f"""Olá {aluno.user.get_full_name() or aluno.user.username},

Uma nova avaliação docente foi criada e está disponível para sua participação.

Ciclo: {instance.nome}
Período: {instance.data_inicio.strftime('%d/%m/%Y')} até {instance.data_fim.strftime('%d/%m/%Y')}
Prazo: {(instance.data_fim - instance.data_inicio).days} dias

Sua opinião é muito importante para a melhoria contínua do ensino.
Por favor, acesse o sistema e responda às avaliações disponíveis.

Atenciosamente,
Equipe de Avaliação Docente
"""

            mensagens.append(
                (assunto, mensagem, settings.DEFAULT_FROM_EMAIL, [aluno.user.email])
            )

        # Enviar e-mails em massa
        if mensagens:
            try:
                send_mass_mail(mensagens, fail_silently=True)

                # Registrar envio
                LembreteAvaliacao.objects.create(
                    ciclo=instance, tipo="criacao", total_enviados=len(mensagens)
                )

                print(
                    f"✅ {len(mensagens)} e-mails de criação enviados para o ciclo: {instance.nome}"
                )
            except Exception as e:
                print(
                    f"❌ Erro ao enviar e-mails de criação do ciclo {instance.nome}: {e}"
                )

    except Exception as e:
        print(f"❌ Erro no signal de envio de e-mail de criação: {e}")


# ============================================================================
# SIGNALS DE INVALIDAÇÃO DE CACHE
# ============================================================================


def get_cache_key_local(prefix, *args):
    """
    Gera chave de cache (replica função de services.py para evitar import circular).

    Args:
        prefix: Prefixo identificador do tipo de cache
        *args: Argumentos variáveis para compor a chave

    Returns:
        str: Hash SHA256 da chave (seguro e evita colisões)
    """
    key_parts = [str(arg) for arg in args if arg is not None]
    key_string = f"{prefix}:{'_'.join(key_parts)}"
    return hashlib.sha256(key_string.encode()).hexdigest()


@receiver(post_save, sender=RespostaAvaliacao)
def invalidar_cache_metricas_professor(sender, instance, **kwargs):
    """
    Invalida cache de métricas quando aluno responde avaliação.
    Garante que dados exibidos nos relatórios estejam sempre atualizados.

    Invalida:
    - Métricas do professor no ciclo específico
    - Métricas gerais do professor
    - Histórico do professor no ciclo
    """
    try:
        professor_id = instance.avaliacao.professor.id
        ciclo_id = instance.avaliacao.ciclo.id

        # Invalidar métricas do ciclo específico
        cache_key_ciclo = get_cache_key_local("metricas_prof", professor_id, ciclo_id)
        cache.delete(cache_key_ciclo)

        # Invalidar métricas gerais
        cache_key_all = get_cache_key_local("metricas_prof", professor_id, "all")
        cache.delete(cache_key_all)

        # Invalidar histórico do ciclo
        cache_key_historico = get_cache_key_local(
            "historico_prof_ciclo", professor_id, ciclo_id
        )
        cache.delete(cache_key_historico)

    except Exception as e:
        print(f"❌ Erro ao invalidar cache após resposta de avaliação: {e}")


@receiver(post_delete, sender=RespostaAvaliacao)
def invalidar_cache_ao_deletar_resposta(sender, instance, **kwargs):
    """
    Invalida cache quando resposta é deletada.
    Usa a mesma lógica de invalidação do post_save.
    """
    invalidar_cache_metricas_professor(sender, instance, **kwargs)
