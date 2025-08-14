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
    ComentarioAvaliacao,
    # Modelos deprecated (manter compatibilidade)
    Avaliacao,
    Pergunta,
    AvaliacaoPergunta,
    RespostaAluno,
)


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
    list_display = ("nome", "ordem", "ativa")
    list_filter = ("ativa",)
    list_editable = ("ordem", "ativa")
    search_fields = ("nome",)
    ordering = ("ordem", "nome")


@admin.register(PerguntaAvaliacao)
class PerguntaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "enunciado_resumido",
        "tipo",
        "categoria",
        "ordem",
        "obrigatoria",
        "ativa",
    )
    list_filter = ("tipo", "categoria", "obrigatoria", "ativa")
    list_editable = ("ordem", "obrigatoria", "ativa")
    search_fields = ("enunciado",)
    ordering = ("categoria__ordem", "ordem")

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


class ComentarioAvaliacaoInline(admin.StackedInline):
    model = ComentarioAvaliacao
    extra = 0
    readonly_fields = ("data_comentario",)


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
    list_filter = ("status", "ciclo", "disciplina__curso", "turma__periodo_letivo")
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
    inlines = [RespostaAvaliacaoInline, ComentarioAvaliacaoInline]

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


@admin.register(ComentarioAvaliacao)
class ComentarioAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "avaliacao",
        "aluno_display",
        "tem_elogios",
        "tem_sugestoes",
        "tem_criticas",
        "data_comentario",
    )
    list_filter = ("anonimo", "data_comentario", "avaliacao__ciclo")
    search_fields = (
        "avaliacao__professor__user__first_name",
        "avaliacao__professor__user__last_name",
        "elogios",
        "sugestoes",
        "criticas_construtivas",
    )
    ordering = ("-data_comentario",)
    readonly_fields = ("data_comentario",)

    def aluno_display(self, obj):
        if obj.anonimo:
            return f"Anônimo ({obj.session_key[:8]})"
        return obj.aluno

    aluno_display.short_description = "Aluno"

    def tem_elogios(self, obj):
        return bool(obj.elogios.strip())

    tem_elogios.boolean = True
    tem_elogios.short_description = "Elogios"

    def tem_sugestoes(self, obj):
        return bool(obj.sugestoes.strip())

    tem_sugestoes.boolean = True
    tem_sugestoes.short_description = "Sugestões"

    def tem_criticas(self, obj):
        return bool(obj.criticas_construtivas.strip())

    tem_criticas.boolean = True
    tem_criticas.short_description = "Críticas"


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


# Registra os modelos deprecated com indicação
@admin.register(Avaliacao)
class AvaliacaoDeprecatedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "data_inicio", "data_fim", "status_avaliacao")
    readonly_fields = (
        "data_inicio",
        "data_fim",
        "status_avaliacao",
        "professor_disciplina",
    )

    def has_add_permission(self, request):
        return False  # Não permite adicionar novos

    class Meta:
        verbose_name = "Avaliação (DEPRECATED - Use AvaliacaoDocente)"


@admin.register(Pergunta)
class PerguntaDeprecatedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "tipo_pergunta")
    readonly_fields = ("enunciado_pergunta", "tipo_pergunta")

    def has_add_permission(self, request):
        return False

    class Meta:
        verbose_name = "Pergunta (DEPRECATED - Use PerguntaAvaliacao)"


@admin.register(AvaliacaoPergunta)
class AvaliacaoPerguntaDeprecatedAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    readonly_fields = ("avaliacao", "pergunta")

    def has_add_permission(self, request):
        return False


@admin.register(RespostaAluno)
class RespostaAlunoDeprecatedAdmin(admin.ModelAdmin):
    list_display = ("__str__",)
    readonly_fields = ("resposta_pergunta", "aluno", "avaliacao_pergunta")

    def has_add_permission(self, request):
        return False
