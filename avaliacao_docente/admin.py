from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from rolepermissions.checkers import has_role
from .models import (
    PerfilAluno,
    PerfilProfessor,
    Curso,
    Disciplina,
    PeriodoLetivo,
    Turma,
    MatriculaTurma,
    HorarioTurma,
    # Novos modelos de avaliação
    QuestionarioAvaliacao,
    CategoriaPergunta,
    PerguntaAvaliacao,
    QuestionarioPergunta,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    # Modelos deprecated (manter compatibilidade)
    ConfiguracaoSite,
    # Sistema de lembretes
    JobLembreteCicloTurma,
    NotificacaoLembrete,
)


# ============ CONFIGURAÇÕES DO SITE =============

admin.site.register(ConfiguracaoSite)


class PerfilAlunoInline(admin.StackedInline):
    model = PerfilAluno
    can_delete = False
    verbose_name_plural = "Perfil de Aluno"


class PerfilProfessorInline(admin.StackedInline):
    model = PerfilProfessor
    can_delete = False
    verbose_name_plural = "Perfil de Professor"


class CustomUserAdmin(DefaultUserAdmin):
    """
    Admin customizado que mostra as roles dos usuários
    """

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "get_user_role",
        "get_user_profile",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")

    def get_user_role(self, obj):
        """Retorna a role do usuário"""
        if has_role(obj, "admin"):
            return "Administrador"
        elif has_role(obj, "coordenador"):
            return "Coordenador"
        elif has_role(obj, "professor"):
            return "Professor"
        elif has_role(obj, "aluno"):
            return "Aluno"
        return "Sem role"

    get_user_role.short_description = "Role"

    def get_user_profile(self, obj):
        """Retorna o tipo de perfil do usuário"""
        # Admins não devem ter perfis específicos
        if has_role(obj, "admin"):
            return "Admin (sem perfil)"

        profiles = []
        if hasattr(obj, "perfil_aluno"):
            profiles.append("Aluno")
        if hasattr(obj, "perfil_professor"):
            profiles.append("Professor")

        if profiles:
            return " + ".join(profiles)
        return "Sem perfil"

    get_user_profile.short_description = "Perfil"

    def get_inlines(self, request, obj):
        """
        Mostra o inline apropriado baseado na role do usuário
        Admins não devem ter perfis específicos
        """
        if obj and has_role(obj, "admin"):
            return []  # Admins não têm perfis
        elif obj and has_role(obj, "aluno"):
            return [PerfilAlunoInline]
        elif obj and (has_role(obj, "professor") or has_role(obj, "coordenador")):
            return [PerfilProfessorInline]
        return []


# Re-registra o User com o admin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============ CONFIGURAÇÕES ADMIN PARA NOVOS MODELOS ============


@admin.register(CategoriaPergunta)
class CategoriaPerguntaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem", "ativo")
    list_filter = ("ativo",)
    list_editable = ("ordem", "ativo")
    search_fields = ("nome",)
    ordering = ("ordem", "nome")


@admin.register(PerguntaAvaliacao)
class PerguntaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "enunciado_resumido",
        "tipo",
        "categoria",
        "obrigatoria",
        "ativo",
    )
    list_filter = ("tipo", "categoria", "obrigatoria", "ativo")
    list_editable = ("obrigatoria", "ativo")
    search_fields = ("enunciado",)
    ordering = ("categoria__ordem",)

    def enunciado_resumido(self, obj):
        return obj.enunciado[:80] + "..." if len(obj.enunciado) > 80 else obj.enunciado

    enunciado_resumido.short_description = "Enunciado"


class QuestionarioPerguntaInline(admin.TabularInline):
    model = QuestionarioPergunta
    extra = 1
    ordering = ("ordem_no_questionario",)


@admin.register(QuestionarioAvaliacao)
class QuestionarioAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ativo", "criado_por", "data_criacao", "total_perguntas")
    list_filter = ("ativo", "data_criacao")
    search_fields = ("titulo", "descricao")
    ordering = ("-data_criacao",)
    inlines = [QuestionarioPerguntaInline]

    def total_perguntas(self, obj):
        return obj.perguntas.count()

    total_perguntas.short_description = "Total de Perguntas"

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(CicloAvaliacao)
class CicloAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "periodo_letivo",
        "status_display",
        "data_inicio",
        "data_fim",
        "ativo",
        "total_avaliacoes",
    )
    list_filter = ("ativo", "periodo_letivo", "data_inicio")
    search_fields = ("nome",)
    ordering = ("-data_inicio",)
    date_hierarchy = "data_inicio"

    def status_display(self, obj):
        status_colors = {
            "agendado": "blue",
            "em_andamento": "green",
            "finalizado": "gray",
        }
        color = status_colors.get(obj.status, "black")
        return f'<span style="color: {color};">{obj.status.replace("_", " ").title()}</span>'

    status_display.allow_tags = True
    status_display.short_description = "Status"

    def total_avaliacoes(self, obj):
        return obj.avaliacoes.count()

    total_avaliacoes.short_description = "Total de Avaliações"

    def save_model(self, request, obj, form, change):
        if not change:  # Novo objeto
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


class RespostaAvaliacaoInline(admin.TabularInline):
    model = RespostaAvaliacao
    extra = 0
    readonly_fields = ("data_resposta", "valor_display")
    fields = ("pergunta", "aluno", "valor_display", "data_resposta")


@admin.register(AvaliacaoDocente)
class AvaliacaoDocenteAdmin(admin.ModelAdmin):
    list_display = (
        "professor",
        "disciplina",
        "turma",
        "ciclo",
        "status",
        "total_respostas",
        "percentual_participacao_display",
    )
    list_filter = (
        "status",
        "ciclo",
        "disciplina__curso",
        "turma__disciplina__periodo_letivo",
    )
    search_fields = (
        "professor__user__first_name",
        "professor__user__last_name",
        "disciplina__disciplina_nome",
        "turma__codigo_turma",
    )
    ordering = ("-data_criacao",)
    readonly_fields = (
        "data_criacao",
        "data_atualizacao",
        "total_respostas",
        "percentual_participacao_display",
        "media_geral_display",
    )
    inlines = [RespostaAvaliacaoInline]

    def percentual_participacao_display(self, obj):
        percentual = obj.percentual_participacao()
        color = "green" if percentual >= 70 else "orange" if percentual >= 50 else "red"
        return f'<span style="color: {color};">{percentual}%</span>'

    percentual_participacao_display.allow_tags = True
    percentual_participacao_display.short_description = "Participação"

    def media_geral_display(self, obj):
        media = obj.media_geral()
        if media is None:
            return "N/A"
        color = "green" if media >= 4 else "orange" if media >= 3 else "red"
        return f'<span style="color: {color};">{media}</span>'

    media_geral_display.allow_tags = True
    media_geral_display.short_description = "Média Geral"


@admin.register(RespostaAvaliacao)
class RespostaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "avaliacao",
        "aluno_display",
        "pergunta_resumida",
        "valor_display",
        "data_resposta",
    )
    list_filter = ("anonima", "pergunta__tipo", "data_resposta", "avaliacao__ciclo")
    search_fields = (
        "aluno__user__first_name",
        "aluno__user__last_name",
        "pergunta__enunciado",
    )
    ordering = ("-data_resposta",)
    readonly_fields = ("data_resposta",)

    def aluno_display(self, obj):
        if obj.anonima:
            return f"Anônimo ({obj.session_key[:8]})"
        return obj.aluno

    aluno_display.short_description = "Aluno"

    def pergunta_resumida(self, obj):
        return (
            obj.pergunta.enunciado[:50] + "..."
            if len(obj.pergunta.enunciado) > 50
            else obj.pergunta.enunciado
        )

    pergunta_resumida.short_description = "Pergunta"


# ============ MODELOS BÁSICOS ============

# Registra os modelos básicos
admin.site.register(PerfilAluno)
admin.site.register(PerfilProfessor)
admin.site.register(Curso)
admin.site.register(Disciplina)
admin.site.register(PeriodoLetivo)
admin.site.register(Turma)
admin.site.register(MatriculaTurma)
admin.site.register(HorarioTurma)


# ============ MODELOS DEPRECATED ============

# Os modelos abaixo foram marcados como obsoletos e suas classes de admin foram removidas
# para evitar erros no sistema. O código foi mantido comentado para referência futura,
# caso seja necessário consultar a estrutura antiga.

# @admin.register(Avaliacao)
# class AvaliacaoDeprecatedAdmin(admin.ModelAdmin):
#     list_display = ("aluno", "turma", "ciclo_avaliacao", "respondida", "data_respondida")
#     readonly_fields = ("aluno", "turma", "ciclo_avaliacao", "respondida", "data_respondida")
#
#     def has_add_permission(self, request):
#         return False  # Não permite adicionar novos
#
#     class Meta:
#         verbose_name = "Avaliação (DEPRECATED - Use AvaliacaoDocente)"
#
#
# @admin.register(Pergunta)
# class PerguntaDeprecatedAdmin(admin.ModelAdmin):
#     list_display = ("__str__", "tipo_pergunta")
#     readonly_fields = ("enunciado_pergunta", "tipo_pergunta")
#
#     def has_add_permission(self, request):
#         return False
#
#     class Meta:
#         verbose_name = "Pergunta (DEPRECATED - Use PerguntaAvaliacao)"
#
#
# @admin.register(AvaliacaoPergunta)
# class AvaliacaoPerguntaDeprecatedAdmin(admin.ModelAdmin):
#     list_display = ("__str__",)
#     readonly_fields = ("avaliacao", "pergunta")
#
#     def has_add_permission(self, request):
#         return False
#
#
# @admin.register(RespostaAluno)
# class RespostaAlunoDeprecatedAdmin(admin.ModelAdmin):
#     list_display = ("__str__",)
#     readonly_fields = ("resposta_pergunta", "aluno", "avaliacao_pergunta")
#
#     def has_add_permission(self, request):
#         return False


# ============ SISTEMA DE LEMBRETES AUTOMÁTICOS ============


class NotificacaoLembreteInline(admin.TabularInline):
    """Inline para mostrar notificações dentro do Job"""

    model = NotificacaoLembrete
    extra = 0
    can_delete = False
    readonly_fields = (
        "aluno",
        "status",
        "rodada",
        "tentativas",
        "enviado_em",
        "motivo_falha",
    )
    fields = ("aluno", "status", "rodada", "tentativas", "enviado_em")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(JobLembreteCicloTurma)
class JobLembreteCicloTurmaAdmin(admin.ModelAdmin):
    """
    Admin para monitorar e gerenciar jobs de envio de lembretes por turma/ciclo.
    """

    list_display = (
        "id",
        "ciclo_nome",
        "turma_codigo",
        "status_colored",
        "taxa_resposta_atual",
        "progresso",
        "proximo_envio_em",
        "rodadas_executadas",
        "ultima_execucao",
    )

    list_filter = (
        "status",
        ("ciclo", admin.RelatedOnlyFieldListFilter),
        ("turma__curso", admin.RelatedOnlyFieldListFilter),
        "data_criacao",
    )

    search_fields = (
        "ciclo__nome",
        "turma__codigo_turma",
        "turma__disciplina__nome",
    )

    readonly_fields = (
        "ciclo",
        "turma",
        "data_criacao",
        "data_atualizacao",
        "total_alunos_aptos",
        "total_respondentes",
        "taxa_resposta_atual",
        "total_emails_enviados",
        "total_falhas",
        "rodadas_executadas",
        "ultima_execucao",
        "mensagem_erro",
    )

    fields = (
        ("ciclo", "turma"),
        ("status", "proximo_envio_em"),
        ("total_alunos_aptos", "total_respondentes", "taxa_resposta_atual"),
        ("total_emails_enviados", "total_falhas", "rodadas_executadas"),
        "ultima_execucao",
        "mensagem_erro",
        ("data_criacao", "data_atualizacao"),
    )

    inlines = [NotificacaoLembreteInline]

    actions = ["pausar_jobs", "retomar_jobs", "forcar_execucao"]

    def ciclo_nome(self, obj):
        return obj.ciclo.nome

    ciclo_nome.short_description = "Ciclo"
    ciclo_nome.admin_order_field = "ciclo__nome"

    def turma_codigo(self, obj):
        return f"{obj.turma.codigo_turma} - {obj.turma.disciplina.nome}"

    turma_codigo.short_description = "Turma"
    turma_codigo.admin_order_field = "turma__codigo_turma"

    def status_colored(self, obj):
        """Exibe status com cores"""
        colors = {
            "pendente": "#ffc107",  # amarelo
            "em_execucao": "#17a2b8",  # azul
            "completo": "#28a745",  # verde
            "pausado": "#6c757d",  # cinza
            "erro": "#dc3545",  # vermelho
        }
        color = colors.get(obj.status, "#000")
        return f'<span style="color: {color}; font-weight: bold;">●</span> {obj.get_status_display()}'

    status_colored.short_description = "Status"
    status_colored.allow_tags = True

    def progresso(self, obj):
        """Exibe barra de progresso visual"""
        if obj.total_alunos_aptos == 0:
            return "N/A"

        percentual = float(obj.taxa_resposta_atual)
        cor = "#28a745" if percentual >= 10 else "#ffc107"

        return f"""
        <div style="width: 150px; background: #e9ecef; border-radius: 4px; overflow: hidden;">
            <div style="width: {min(percentual, 100)}%; background: {cor}; height: 20px; 
                        display: flex; align-items: center; justify-content: center; color: white; 
                        font-size: 11px; font-weight: bold;">
                {obj.total_respondentes}/{obj.total_alunos_aptos}
            </div>
        </div>
        """

    progresso.short_description = "Progresso"
    progresso.allow_tags = True

    def pausar_jobs(self, request, queryset):
        """Action para pausar jobs selecionados"""
        count = queryset.update(status="pausado")
        self.message_user(request, f"{count} job(s) pausado(s) com sucesso.")

    pausar_jobs.short_description = "⏸️ Pausar jobs selecionados"

    def retomar_jobs(self, request, queryset):
        """Action para retomar jobs pausados"""
        count = queryset.filter(status="pausado").update(status="pendente")
        self.message_user(request, f"{count} job(s) retomado(s) com sucesso.")

    retomar_jobs.short_description = "▶️ Retomar jobs pausados"

    def forcar_execucao(self, request, queryset):
        """Action para forçar execução imediata"""
        from django.utils import timezone

        count = queryset.update(proximo_envio_em=timezone.now(), status="pendente")
        self.message_user(
            request,
            f"{count} job(s) agendado(s) para execução imediata. "
            f"Execute o comando: python manage.py enviar_lembretes_ciclos",
        )

    forcar_execucao.short_description = "⚡ Forçar execução imediata"

    def has_add_permission(self, request):
        """Jobs são criados automaticamente via signals"""
        return False


@admin.register(NotificacaoLembrete)
class NotificacaoLembreteAdmin(admin.ModelAdmin):
    """
    Admin para visualizar o histórico de notificações enviadas.
    """

    list_display = (
        "id",
        "job_info",
        "aluno_nome",
        "status_colored",
        "rodada",
        "tentativas",
        "enviado_em",
        "data_criacao",
    )

    list_filter = (
        "status",
        "rodada",
        ("job__ciclo", admin.RelatedOnlyFieldListFilter),
        "enviado_em",
        "data_criacao",
    )

    search_fields = (
        "aluno__user__username",
        "aluno__user__email",
        "aluno__user__first_name",
        "aluno__user__last_name",
        "job__turma__codigo_turma",
    )

    readonly_fields = (
        "job",
        "aluno",
        "status",
        "rodada",
        "tentativas",
        "enviado_em",
        "mensagem_id",
        "motivo_falha",
        "data_criacao",
        "data_atualizacao",
    )

    fields = (
        ("job", "aluno"),
        ("status", "rodada", "tentativas"),
        "enviado_em",
        "mensagem_id",
        "motivo_falha",
        ("data_criacao", "data_atualizacao"),
    )

    def job_info(self, obj):
        return f"{obj.job.ciclo.nome} - {obj.job.turma.codigo_turma}"

    job_info.short_description = "Job (Ciclo - Turma)"

    def aluno_nome(self, obj):
        return obj.aluno.user.get_full_name() or obj.aluno.user.username

    aluno_nome.short_description = "Aluno"
    aluno_nome.admin_order_field = "aluno__user__first_name"

    def status_colored(self, obj):
        """Exibe status com cores e ícones"""
        icons = {
            "pendente": "⏳",
            "enviado": "✅",
            "falhou": "❌",
            "ignorado": "⊘",
        }
        colors = {
            "pendente": "#ffc107",
            "enviado": "#28a745",
            "falhou": "#dc3545",
            "ignorado": "#6c757d",
        }
        icon = icons.get(obj.status, "●")
        color = colors.get(obj.status, "#000")
        return f'<span style="color: {color}; font-weight: bold;">{icon}</span> {obj.get_status_display()}'

    status_colored.short_description = "Status"
    status_colored.allow_tags = True

    def has_add_permission(self, request):
        """Notificações são criadas automaticamente pelo comando"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Não permite deletar notificações (auditoria)"""
        return False
