from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import csv
from datetime import datetime
from .models import (
    PerfilAluno,
    PerfilProfessor,
    Disciplina,
    Curso,
    PeriodoLetivo,
    Turma,
    MatriculaTurma,
    PerguntaAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
    CicloAvaliacao,
    ConfiguracaoSite,
)
from .models import (
    QuestionarioAvaliacao,
    CategoriaPergunta,
    QuestionarioPergunta,
)
from django.contrib.auth.models import User
from rolepermissions.roles import assign_role, remove_role
from rolepermissions.checkers import has_role
from .utils import (
    check_user_permission,
    get_user_role_name,
    mark_role_manually_changed,
    reset_role_manual_flag,
    is_role_manually_changed,
    processar_mudanca_role,
    gerenciar_perfil_usuario,
    display_form_errors,
    calcular_estatisticas_respostas,
    sanitize_csv_value,
    preparar_response_csv,
)
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import (
    GerenciarRoleForm,
    CursoForm,
    DisciplinaForm,
    PeriodoLetivoForm,
    TurmaForm,
    CicloAvaliacaoForm,
    PerguntaAvaliacaoForm,
    QuestionarioAvaliacaoForm,
    CategoriaPerguntaForm,
    RegistroForm,
    ConfiguracaoSiteForm,
)


@login_required
def gerenciar_configuracao_site(request):
    config = ConfiguracaoSite.obter_config()
    if request.method == "POST":
        form = ConfiguracaoSiteForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configurações do site atualizadas com sucesso!")
            return redirect("gerenciar_configuracao_site")
    else:
        form = ConfiguracaoSiteForm(instance=config)

    return render(request, "admin/gerenciar_configuracao.html", {"form": form})


@login_required
def gerenciar_roles(request):
    """
    View para gerenciar roles de usuários
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = GerenciarRoleForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data["usuario"]
            nova_role = form.cleaned_data["role"]

            # Processar mudança de role (função consolidada)
            mensagens_perfil = processar_mudanca_role(usuario, nova_role)

            # Adicionar mensagens informativas sobre mudanças de perfil
            for msg in mensagens_perfil:
                messages.info(request, msg)

            messages.success(
                request,
                f"Role de {usuario.username} alterada para {nova_role} com sucesso!",
            )
            return redirect("gerenciar_roles")
    else:
        form = GerenciarRoleForm()

    # Obter todos os usuários ativos e suas roles
    usuarios_queryset = User.objects.filter(is_active=True).order_by("username")

    # Lista todos os usuários com suas roles
    usuarios_com_roles = []
    for user in usuarios_queryset:
        role_atual = get_user_role_name(user)
        role_manual = is_role_manually_changed(user)

        usuarios_com_roles.append(
            {"usuario": user, "role": role_atual, "role_manual": role_manual}
        )

    context = {
        "form": form,
        "usuarios_com_roles": usuarios_com_roles,
    }

    return render(request, "gerenciar_roles.html", context)


@login_required
def resetar_role_automatica(request, usuario_id):
    """
    View para resetar a flag de role manual, permitindo que o SUAP
    volte a gerenciar automaticamente a role do usuário
    """
    if not check_user_permission(request.user, ["admin"]):
        messages.error(
            request, "Apenas administradores podem resetar roles automáticas."
        )
        return redirect("gerenciar_usuarios")

    try:
        usuario = User.objects.get(id=usuario_id)
        if reset_role_manual_flag(usuario):
            messages.success(
                request,
                f"Flag manual removida para {usuario.username}. O SUAP voltará a gerenciar automaticamente a role deste usuário.",
            )
        else:
            messages.warning(
                request,
                f"Usuário {usuario.username} não possui integração com SUAP ou não tem flag manual definida.",
            )
    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado.")
    except Exception as e:
        messages.error(request, f"Erro ao resetar flag manual: {str(e)}")

    return redirect("gerenciar_usuarios")


@login_required
def gerenciar_usuarios(request):
    """
    View para gerenciar usuários
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "POST":
        form = GerenciarRoleForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data["usuario"]
            nova_role = form.cleaned_data["role"]

            # Processar mudança de role (função consolidada)
            mensagens_perfil = processar_mudanca_role(usuario, nova_role)

            # Adicionar mensagens informativas sobre mudanças de perfil
            for msg in mensagens_perfil:
                messages.info(request, msg)

            messages.success(
                request,
                f"Role de {usuario.username} alterada para {nova_role} com sucesso!",
            )
            return redirect("gerenciar_usuarios")
    else:
        form = GerenciarRoleForm()

    # Capturar parâmetros de filtro
    filtro_busca = request.GET.get("busca", "").strip()
    filtro_role = request.GET.get("role", "").strip()
    filtro_status = request.GET.get("status", "").strip()

    # Obter todos os usuários ordenados - Força avaliação do queryset a cada request
    usuarios_queryset = User.objects.all().order_by(
        "username", "first_name", "last_name"
    )

    # Aplicar filtros no QuerySet
    if filtro_busca:
        from django.db.models import Q

        usuarios_queryset = usuarios_queryset.filter(
            Q(username__icontains=filtro_busca)
            | Q(first_name__icontains=filtro_busca)
            | Q(last_name__icontains=filtro_busca)
            | Q(email__icontains=filtro_busca)
        )

    if filtro_status:
        if filtro_status == "ativo":
            usuarios_queryset = usuarios_queryset.filter(is_active=True)
        elif filtro_status == "inativo":
            usuarios_queryset = usuarios_queryset.filter(is_active=False)

    # Lista todos os usuários com suas roles
    usuarios_list = []
    for user in usuarios_queryset:
        role_atual = get_user_role_name(user)
        role_manual = is_role_manually_changed(user)

        # Filtrar por role (após obter a role do usuário)
        if filtro_role:
            # Normalizar roles para comparação
            role_filtro_normalizada = filtro_role.lower().replace("-", " ")
            role_usuario_normalizada = role_atual.lower()

            if role_filtro_normalizada != role_usuario_normalizada:
                continue

        usuarios_list.append(
            {
                "usuario": user,
                "role": role_atual,
                "role_manual": role_manual,
                "nome_completo": f"{user.first_name} {user.last_name}".strip(),
                "status": "Ativo" if user.is_active else "Inativo",
            }
        )

    # Paginação - 15 usuários por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(usuarios_list, 15)  # 15 usuários por página
    page_number = request.GET.get("page", 1)

    try:
        usuarios = paginator.page(page_number)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)

    # Estatísticas para o template
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    professores_count = User.objects.filter(groups__name="professor").count()
    alunos_count = User.objects.filter(groups__name="aluno").count()

    context = {
        "form": form,
        "usuarios": usuarios,  # Objeto Page com paginação
        "total_usuarios": total_usuarios,
        "usuarios_ativos": usuarios_ativos,
        "professores_count": professores_count,
        "alunos_count": alunos_count,
        "available_roles": [],  # Para o modal de criação
        "roles_disponiveis": [
            {"value": "admin", "label": "Admin"},
            {"value": "coordenador", "label": "Coordenador"},
            {"value": "professor", "label": "Professor"},
            {"value": "aluno", "label": "Aluno"},
        ],
        # Valores dos filtros para manter no formulário
        "filtro_busca": filtro_busca,
        "filtro_role": filtro_role,
        "filtro_status": filtro_status,
    }

    return render(request, "gerenciar_usuarios.html", context)


@login_required
def editar_usuario(request, usuario_id):
    """
    View para editar um usuário específico
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar usuários.")
        return redirect("inicio")

    usuario = get_object_or_404(User, id=usuario_id)

    if request.method == "POST":
        try:
            # Validar matrícula (username) - deve conter apenas números
            novo_username = request.POST.get("username", "").strip()
            if not novo_username:
                messages.error(request, "A matrícula é obrigatória.")
                raise ValueError("Matrícula obrigatória")

            if not novo_username.isdigit():
                messages.error(request, "A matrícula deve conter apenas números.")
                raise ValueError("Matrícula inválida")

            # Verificar duplicação de username (matrícula)
            if novo_username != usuario.username:
                if User.objects.filter(username=novo_username).exists():
                    messages.error(
                        request,
                        f"A matrícula '{novo_username}' já está em uso por outro usuário.",
                    )
                    raise ValueError("Matrícula duplicada")

            # Atualizar campos básicos
            usuario.username = novo_username
            usuario.email = request.POST.get("email", usuario.email)
            usuario.first_name = request.POST.get("first_name", usuario.first_name)
            usuario.last_name = request.POST.get("last_name", usuario.last_name)
            usuario.is_active = request.POST.get("is_active") == "on"

            # Atualizar senha se fornecida com validação
            password = request.POST.get("password")
            if password:
                # Importar validadores de senha do Django
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError

                try:
                    # Validar a senha usando os validadores do Django
                    validate_password(password, usuario)
                    usuario.set_password(password)
                except ValidationError as e:
                    # Se a validação falhar, mostrar erros ao usuário
                    for error in e.messages:
                        messages.error(request, error)
                    # Retornar ao formulário de edição mantendo os dados
                    context = {
                        "usuario": usuario,
                        "editing": True,
                    }
                    return render(request, "gerenciar_usuarios.html", context)

            usuario.save()

            messages.success(
                request, f"Usuário '{usuario.username}' atualizado com sucesso!"
            )
            return redirect("gerenciar_usuarios")

        except ValueError:
            # Erros de validação já foram tratados com messages.error
            pass
        except Exception as e:
            messages.error(request, f"Erro ao atualizar usuário: {str(e)}")

    context = {"usuario": usuario, "editing": True}
    return render(request, "gerenciar_usuarios.html", context)


@login_required
def resetar_senha_usuario(request, usuario_id):
    """
    View para resetar senha de um usuário
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Permissão negada"}, status=403)

    if request.method == "POST":
        try:
            usuario = get_object_or_404(User, id=usuario_id)

            # Não permite resetar a própria senha por esta via
            if usuario == request.user:
                return JsonResponse(
                    {"error": "Use a opção de alteração de senha no perfil"}, status=400
                )

            # Não permite resetar senha de admin se não for admin
            if has_role(usuario, "admin") and not has_role(request.user, "admin"):
                return JsonResponse(
                    {
                        "error": "Apenas administradores podem resetar senha de outros administradores"
                    },
                    status=403,
                )

            nova_senha = "123456"
            usuario.set_password(nova_senha)
            usuario.save()

            return JsonResponse(
                {
                    "success": f"Senha do usuário '{usuario.username}' resetada para: {nova_senha}"
                }
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Erro ao resetar senha: {str(e)}"}, status=500
            )

    return JsonResponse({"error": "Método não permitido"}, status=405)


@login_required
def gerenciar_cursos(request):
    """
    View para gerenciar cursos
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Capturar filtros da requisição
    filtro_busca = request.GET.get("busca", "")
    filtro_coordenador = request.GET.get("coordenador", "")

    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            messages.success(
                request,
                f"Curso '{curso.curso_nome}' criado com sucesso!",
            )
            return redirect("gerenciar_cursos")
    else:
        form = CursoForm()

    # Lista todos os cursos com filtros
    cursos_list = Curso.objects.all()

    # Aplicar filtros
    if filtro_busca:
        from django.db.models import Q

        cursos_list = cursos_list.filter(
            Q(curso_nome__icontains=filtro_busca)
            | Q(curso_sigla__icontains=filtro_busca)
        )

    if filtro_coordenador:
        if filtro_coordenador == "sem_coordenador":
            cursos_list = cursos_list.filter(coordenador_curso__isnull=True)
        else:
            cursos_list = cursos_list.filter(coordenador_curso_id=filtro_coordenador)

    cursos_list = cursos_list.order_by("curso_nome")

    # Paginação - 15 cursos por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(cursos_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        cursos = paginator.page(page_number)
    except PageNotAnInteger:
        cursos = paginator.page(1)
    except EmptyPage:
        cursos = paginator.page(paginator.num_pages)

    # Lista todos os coordenadores para o filtro
    coordenadores = (
        PerfilProfessor.objects.all()
        .select_related("user")
        .order_by("user__first_name", "user__last_name")
    )

    context = {
        "form": form,
        "cursos": cursos,
        "coordenadores": coordenadores,
        "filtro_busca": filtro_busca,
        "filtro_coordenador": filtro_coordenador,
    }

    return render(request, "gerenciar_cursos.html", context)


@login_required
def editar_curso(request, curso_id):
    """
    View para editar um curso existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar cursos.")
        return redirect("inicio")

    curso = get_object_or_404(Curso, id=curso_id)

    if request.method == "POST":
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Curso '{curso.curso_nome}' atualizado com sucesso!"
            )
            return redirect("gerenciar_cursos")
        else:
            display_form_errors(request, form)
    else:
        form = CursoForm(instance=curso)

    context = {"form": form, "curso": curso, "editing": True}
    return render(request, "gerenciar_cursos.html", context)


@login_required
def excluir_curso(request, curso_id):
    """
    View para excluir um curso
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"error": "Sem permissão"}, status=403)
        messages.error(request, "Sem permissão para realizar esta ação.")
        return redirect("gerenciar_cursos")

    if request.method == "POST":
        try:
            curso = get_object_or_404(Curso, id=curso_id)

            # Verificar se há disciplinas relacionadas
            if curso.disciplinas.exists():
                error_msg = f"Não é possível excluir o curso '{curso.curso_nome}' pois existem disciplinas vinculadas a ele."
                if request.headers.get("Content-Type") == "application/json":
                    return JsonResponse({"error": error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect("gerenciar_cursos")

            nome_curso = curso.curso_nome
            curso.delete()

            success_msg = f"Curso '{nome_curso}' excluído com sucesso!"
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"success": True, "message": success_msg})

            messages.success(request, success_msg)
            return redirect("gerenciar_cursos")

        except Exception as e:
            error_msg = str(e)
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"error": error_msg}, status=500)
            messages.error(request, f"Erro ao excluir curso: {error_msg}")
            return redirect("gerenciar_cursos")

    if request.headers.get("Content-Type") == "application/json":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    return redirect("gerenciar_cursos")


@login_required
def gerenciar_disciplinas(request):
    """
    View para gerenciar disciplinas
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Capturar filtros da requisição
    filtro_busca = request.GET.get("busca", "")
    filtro_curso = request.GET.get("curso", "")
    filtro_tipo = request.GET.get("tipo", "")
    filtro_periodo = request.GET.get("periodo", "")

    if request.method == "POST":
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(
                request,
                f"Disciplina '{disciplina.disciplina_nome}' criada com sucesso!",
            )
            return redirect("gerenciar_disciplinas")
        else:
            display_form_errors(request, form)
    else:
        form = DisciplinaForm()

    # Lista todas as disciplinas com filtros
    disciplinas_list = Disciplina.objects.all()

    # Aplicar filtros
    if filtro_busca:
        from django.db.models import Q

        disciplinas_list = disciplinas_list.filter(
            Q(disciplina_nome__icontains=filtro_busca)
            | Q(disciplina_sigla__icontains=filtro_busca)
        )

    if filtro_curso:
        disciplinas_list = disciplinas_list.filter(curso_id=filtro_curso)

    if filtro_tipo:
        disciplinas_list = disciplinas_list.filter(disciplina_tipo=filtro_tipo)

    if filtro_periodo:
        disciplinas_list = disciplinas_list.filter(periodo_letivo_id=filtro_periodo)

    disciplinas_list = disciplinas_list.order_by("disciplina_nome")

    # Paginação - 15 disciplinas por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(disciplinas_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        disciplinas = paginator.page(page_number)
    except PageNotAnInteger:
        disciplinas = paginator.page(1)
    except EmptyPage:
        disciplinas = paginator.page(paginator.num_pages)

    # Buscar dados para os filtros
    cursos = Curso.objects.all().order_by("curso_nome")
    periodos = PeriodoLetivo.objects.all().order_by("nome")

    context = {
        "form": form,
        "disciplinas": disciplinas,
        "cursos": cursos,
        "periodos": periodos,
        "filtro_busca": filtro_busca,
        "filtro_curso": filtro_curso,
        "filtro_tipo": filtro_tipo,
        "filtro_periodo": filtro_periodo,
    }

    return render(request, "gerenciar_disciplinas.html", context)


@login_required
def editar_disciplina(request, disciplina_id):
    """
    View para editar uma disciplina existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar disciplinas.")
        return redirect("inicio")

    disciplina = get_object_or_404(Disciplina, id=disciplina_id)

    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Disciplina '{disciplina.disciplina_nome}' atualizada com sucesso!",
            )
            return redirect("gerenciar_disciplinas")
        else:
            display_form_errors(request, form)
    else:
        form = DisciplinaForm(instance=disciplina)

    # Buscar dados para os filtros
    cursos = Curso.objects.all().order_by("curso_nome")
    periodos = PeriodoLetivo.objects.all().order_by("nome")
    disciplinas = Disciplina.objects.all().order_by("disciplina_nome")

    context = {
        "form": form,
        "disciplina": disciplina,
        "disciplinas": disciplinas,
        "cursos": cursos,
        "periodos": periodos,
        "editing": True,
    }
    return render(request, "gerenciar_disciplinas.html", context)


@login_required
def excluir_disciplina(request, disciplina_id):
    """
    View para excluir uma disciplina
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"error": "Sem permissão"}, status=403)
        messages.error(request, "Sem permissão para realizar esta ação.")
        return redirect("gerenciar_disciplinas")

    if request.method == "POST":
        try:
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)

            # Verificar se há turmas relacionadas
            if disciplina.turmas.exists():
                error_msg = f"Não é possível excluir a disciplina '{disciplina.disciplina_nome}' pois existem turmas vinculadas a ela."
                if request.headers.get("Content-Type") == "application/json":
                    return JsonResponse({"error": error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect("gerenciar_disciplinas")

            nome_disciplina = disciplina.disciplina_nome
            disciplina.delete()

            success_msg = f"Disciplina '{nome_disciplina}' excluída com sucesso!"
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"success": True, "message": success_msg})

            messages.success(request, success_msg)
            return redirect("gerenciar_disciplinas")

        except Exception as e:
            error_msg = str(e)
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"error": error_msg}, status=500)
            messages.error(request, f"Erro ao excluir disciplina: {error_msg}")
            return redirect("gerenciar_disciplinas")

    if request.headers.get("Content-Type") == "application/json":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    return redirect("gerenciar_disciplinas")


@login_required
def gerenciar_periodos(request):
    """
    View para gerenciar períodos letivos
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Capturar filtros da requisição
    filtro_busca = request.GET.get("busca", "")
    filtro_ano = request.GET.get("ano", "")
    filtro_semestre = request.GET.get("semestre", "")

    if request.method == "POST":
        form = PeriodoLetivoForm(request.POST)
        if form.is_valid():
            periodo = form.save()
            messages.success(
                request,
                f"Período '{periodo.nome}' criado com sucesso!",
            )
            return redirect("gerenciar_periodos")
    else:
        form = PeriodoLetivoForm()

    # Lista todos os períodos com filtros
    periodos_list = PeriodoLetivo.objects.all()

    # Aplicar filtros
    if filtro_busca:
        periodos_list = periodos_list.filter(nome__icontains=filtro_busca)

    if filtro_ano:
        periodos_list = periodos_list.filter(ano=filtro_ano)

    if filtro_semestre:
        periodos_list = periodos_list.filter(semestre=filtro_semestre)

    periodos_list = periodos_list.order_by("-ano", "-semestre")

    # Paginação - 15 períodos por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(periodos_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        periodos = paginator.page(page_number)
    except PageNotAnInteger:
        periodos = paginator.page(1)
    except EmptyPage:
        periodos = paginator.page(paginator.num_pages)

    # Anos disponíveis para o filtro (valores únicos)
    anos_disponiveis = (
        PeriodoLetivo.objects.values_list("ano", flat=True).distinct().order_by("-ano")
    )

    context = {
        "form": form,
        "periodos": periodos,
        "anos_disponiveis": anos_disponiveis,
        "filtro_busca": filtro_busca,
        "filtro_ano": filtro_ano,
        "filtro_semestre": filtro_semestre,
    }

    return render(request, "gerenciar_periodos.html", context)


@login_required
def editar_periodo(request, periodo_id):
    """
    View para editar um período letivo existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar períodos.")
        return redirect("inicio")

    periodo = get_object_or_404(PeriodoLetivo, id=periodo_id)

    if request.method == "POST":
        form = PeriodoLetivoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Período '{periodo.nome}' atualizado com sucesso!"
            )
            return redirect("gerenciar_periodos")
        else:
            display_form_errors(request, form)
    else:
        form = PeriodoLetivoForm(instance=periodo)

    context = {
        "form": form,
        "periodo": periodo,
        "periodos": PeriodoLetivo.objects.all().order_by("-ano", "-semestre"),
        "editing": True,
    }
    return render(request, "gerenciar_periodos.html", context)


@login_required
def editar_periodo_simples(request, periodo_id):
    """
    View para editar um período letivo - versão simples sem JavaScript
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar períodos.")
        return redirect("inicio")

    periodo = get_object_or_404(PeriodoLetivo, id=periodo_id)

    if request.method == "POST":
        form = PeriodoLetivoForm(request.POST, instance=periodo)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request, f"Período '{periodo.nome}' atualizado com sucesso!"
                )
                return redirect("gerenciar_periodos")
            except Exception as e:
                messages.error(
                    request, f"Não foi possível atualizar o período: {str(e)}"
                )
        else:
            display_form_errors(request, form)
    else:
        form = PeriodoLetivoForm(instance=periodo)

    # Lista todos os períodos
    periodos = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    context = {
        "form": form,
        "periodo": periodo,
        "periodos": periodos,
        "editing": True,
    }
    return render(request, "gerenciar_periodos.html", context)


@login_required
def excluir_periodo(request, periodo_id):
    """
    View para excluir um período letivo
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"error": "Sem permissão"}, status=403)
        messages.error(request, "Sem permissão para realizar esta ação.")
        return redirect("gerenciar_periodos")

    if request.method == "POST":
        try:
            periodo = get_object_or_404(PeriodoLetivo, id=periodo_id)

            # Verificar se há disciplinas relacionadas
            if periodo.disciplinas.exists():
                # Conta quantas disciplinas estão ativas
                disciplinas_ativas = periodo.disciplinas.filter(ativo=True).count()

                if disciplinas_ativas > 0:
                    error_msg = (
                        f"⚠️ Não é possível excluir o período '{periodo.nome}'.\n\n"
                        f"Existem {disciplinas_ativas} disciplina(s) vinculada(s) a este período.\n"
                        f"Remova ou desative as disciplinas antes de excluir o período."
                    )
                else:
                    # Todas as disciplinas estão inativas, pode excluir
                    error_msg = None

                if error_msg:
                    if request.headers.get("Content-Type") == "application/json":
                        return JsonResponse({"error": error_msg}, status=400)
                    messages.error(request, error_msg)
                    return redirect("gerenciar_periodos")

            nome_periodo = periodo.nome
            periodo.delete()

            success_msg = f"✅ Período '{nome_periodo}' excluído com sucesso!"
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"success": True, "message": success_msg})

            messages.success(request, success_msg)
            return redirect("gerenciar_periodos")

        except Exception as e:
            error_msg = str(e)

            # Mensagens de erro mais amigáveis
            if "object has no attribute" in error_msg:
                error_msg = "⚠️ Erro técnico ao excluir o período. Verifique se não há dependências relacionadas."
            elif "ProtectedError" in error_msg or "FOREIGN KEY" in error_msg:
                error_msg = (
                    f"⚠️ Não é possível excluir o período '{periodo.nome if 'periodo' in locals() else 'selecionado'}'.\n\n"
                    "Existem registros vinculados a este período que impedem sua exclusão."
                )
            else:
                error_msg = f"❌ Erro ao excluir período: {error_msg}"

            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"error": error_msg}, status=500)
            messages.error(request, error_msg)
            return redirect("gerenciar_periodos")

    if request.headers.get("Content-Type") == "application/json":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    return redirect("gerenciar_periodos")


@login_required
def gerenciar_alunos_turma(request, turma_id):
    """
    View para gerenciar alunos de uma turma específica sem JavaScript
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    turma = get_object_or_404(Turma, id=turma_id)
    busca_aluno = request.GET.get("busca_aluno", "")

    # Processar ações POST
    if request.method == "POST":
        acao = request.POST.get("acao")
        alunos_selecionados = request.POST.getlist("alunos_selecionados")

        if acao and alunos_selecionados:
            try:
                usuarios = User.objects.filter(id__in=alunos_selecionados)
                alunos = PerfilAluno.objects.filter(user__in=usuarios)

                sucesso_count = 0
                for aluno in alunos:
                    if acao == "matricular":
                        matricula, created = MatriculaTurma.objects.get_or_create(
                            aluno=aluno, turma=turma, defaults={"status": "ativa"}
                        )
                        if created:
                            sucesso_count += 1
                    elif acao == "desmatricular":
                        MatriculaTurma.objects.filter(aluno=aluno, turma=turma).delete()
                        sucesso_count += 1

                if acao == "matricular":
                    messages.success(
                        request, f"{sucesso_count} aluno(s) matriculado(s) com sucesso!"
                    )
                else:
                    messages.success(
                        request,
                        f"{sucesso_count} aluno(s) desmatriculado(s) com sucesso!",
                    )

            except Exception as e:
                messages.error(request, f"Erro ao processar ação: {str(e)}")

        return redirect("gerenciar_alunos_turma", turma_id=turma_id)

    # Buscar todos os alunos ativos
    alunos_query = PerfilAluno.non_admin.select_related("user").all()

    # Aplicar filtro de busca
    if busca_aluno:
        alunos_query = alunos_query.filter(
            Q(user__first_name__icontains=busca_aluno)
            | Q(user__last_name__icontains=busca_aluno)
            | Q(user__username__icontains=busca_aluno)
            | Q(user__email__icontains=busca_aluno)
        )

    # Verificar quais alunos estão matriculados na turma
    matriculas_ativas = MatriculaTurma.objects.filter(
        turma=turma, status="ativa"
    ).values_list("aluno_id", flat=True)

    # Preparar dados dos alunos
    alunos_data = []
    for aluno in alunos_query.order_by("user__first_name", "user__last_name"):
        alunos_data.append(
            {
                "id": aluno.user.id,
                "perfil_id": aluno.id,
                "nome": aluno.user.get_full_name() or aluno.user.username,
                "username": aluno.user.username,
                "email": aluno.user.email or "Não informado",
                "matriculado": aluno.id in matriculas_ativas,
            }
        )

    context = {
        "turma": turma,
        "alunos": alunos_data,
        "busca_aluno": busca_aluno,
        "total_alunos": len(alunos_data),
        "alunos_matriculados": len([a for a in alunos_data if a["matriculado"]]),
        "alunos_disponiveis": len([a for a in alunos_data if not a["matriculado"]]),
    }

    return render(request, "gerenciar_alunos_turma.html", context)


@login_required
def gerenciar_turmas(request):
    """
    View para gerenciar turmas com filtros
    Apenas coordenadores e admins podem acessar
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Filtros da requisição
    filtro_turno = request.GET.get("turno", "")
    filtro_periodo = request.GET.get("periodo", "")

    if request.method == "POST":
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(
                request,
                f"Turma '{turma.codigo_turma}' criada com sucesso!",
            )
            return redirect("gerenciar_turmas")
        else:
            display_form_errors(request, form)
    else:
        form = TurmaForm()

    # Base queryset
    turmas_list = (
        Turma.objects.select_related(
            "disciplina",
            "disciplina__professor__user",
            "disciplina__periodo_letivo",
        )
        .prefetch_related("matriculas")
        .order_by(
            "-disciplina__periodo_letivo__ano",
            "-disciplina__periodo_letivo__semestre",
            "disciplina__disciplina_nome",
        )
    )

    # Aplicar filtros
    if filtro_turno:
        turmas_list = turmas_list.filter(turno=filtro_turno)
    if filtro_periodo:
        turmas_list = turmas_list.filter(disciplina__periodo_letivo_id=filtro_periodo)

    # Paginação - 15 turmas por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(turmas_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        turmas = paginator.page(page_number)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)

    # Períodos disponíveis para o filtro
    periodos_disponiveis = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    # Disciplinas e professores para os filtros
    disciplinas = Disciplina.objects.all().order_by("disciplina_nome")
    professores = PerfilProfessor.non_admin.select_related("user").order_by(
        "user__first_name", "user__last_name"
    )

    context = {
        "form": form,
        "turmas": turmas,
        "periodos_disponiveis": periodos_disponiveis,
        "disciplinas": disciplinas,
        "professores": professores,
        "filtro_turno": filtro_turno,
        "filtro_periodo": filtro_periodo,
    }

    return render(request, "gerenciar_turmas.html", context)


@login_required
def editar_turma(request, turma_id):
    """
    View para editar uma turma existente
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para editar turmas.")
        return redirect("inicio")

    turma = get_object_or_404(Turma, id=turma_id)

    if request.method == "POST":
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Turma '{turma.codigo_turma}' atualizada com sucesso!"
            )
            return redirect("gerenciar_turmas")
        else:
            display_form_errors(request, form)
    else:
        form = TurmaForm(instance=turma)

    # Períodos disponíveis para o filtro
    periodos_disponiveis = PeriodoLetivo.objects.all().order_by("-ano", "-semestre")

    context = {
        "form": form,
        "turma": turma,
        "turmas": Turma.objects.select_related(
            "disciplina",
            "disciplina__professor__user",
            "disciplina__periodo_letivo",
        ).order_by(
            "-disciplina__periodo_letivo__ano",
            "-disciplina__periodo_letivo__semestre",
            "disciplina__disciplina_nome",
        ),
        "periodos_disponiveis": periodos_disponiveis,
        "editing": True,
    }
    return render(request, "gerenciar_turmas.html", context)


@login_required
def excluir_turma(request, turma_id):
    """
    View para excluir uma turma
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"error": "Sem permissão"}, status=403)
        messages.error(request, "Sem permissão para realizar esta ação.")
        return redirect("gerenciar_turmas")

    if request.method == "POST":
        try:
            turma = get_object_or_404(Turma, id=turma_id)

            # Verificar se há matrículas ativas
            matriculas_ativas = turma.matriculas.filter(status="ativa").count()
            if matriculas_ativas > 0:
                error_msg = f"Não é possível excluir a turma '{turma.codigo_turma}' pois existem {matriculas_ativas} aluno(s) matriculado(s)."
                if request.headers.get("Content-Type") == "application/json":
                    return JsonResponse({"error": error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect("gerenciar_turmas")

            codigo_turma = turma.codigo_turma
            turma.delete()

            success_msg = f"Turma '{codigo_turma}' excluída com sucesso!"
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"success": True, "message": success_msg})

            messages.success(request, success_msg)
            return redirect("gerenciar_turmas")

        except Exception as e:
            error_msg = str(e)
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"error": error_msg}, status=500)
            messages.error(request, f"Erro ao excluir turma: {error_msg}")
            return redirect("gerenciar_turmas")

    if request.headers.get("Content-Type") == "application/json":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    return redirect("gerenciar_turmas")


class AdminHubView(LoginRequiredMixin, TemplateView):
    template_name = "admin/admin_hub.html"

    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário tem permissão para acessar o admin hub"""
        if not check_user_permission(request.user, ["coordenador", "admin"]):
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect("inicio")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estatísticas do sistema
        context["total_usuarios"] = User.objects.count()
        context["total_cursos"] = Curso.objects.count()
        context["total_disciplinas"] = Disciplina.objects.count()
        context["total_turmas"] = Turma.objects.count()
        context["total_professores"] = PerfilProfessor.objects.count()
        context["total_alunos"] = PerfilAluno.objects.count()
        context["total_periodos"] = PeriodoLetivo.objects.count()

        # Avaliaições realizadas - contar respostas únicas

        context["total_avaliacoes"] = (
            RespostaAvaliacao.objects.values("avaliacao").distinct().count()
        )

        return context


# Painel principal
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "inicial.html"
    context_object_name = "avaliacao_docente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Tela de Perfil separada
@login_required
def perfil_usuario(request):
    """
    View para a tela de perfil do usuário
    Página separada com informações completas do perfil
    """
    context = {"usuario": request.user, "titulo": "Meu Perfil"}
    return render(request, "perfil.html", context)


# Tela para registros de usuarios - Redirecionada para login SUAP
class RegistrarUsuarioView(FormView):
    template_name = "registration/register.html"
    form_class = RegistroForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["suap_message"] = True
        return context

    def form_valid(self, form):
        # Salva o usuário
        user = form.save()

        # Mensagem de sucesso
        messages.success(self.request, f"Usuário '{user.username}' criado com sucesso!")

        # Se há um parâmetro 'next' na URL, redireciona para lá
        next_url = self.request.GET.get("next")
        if next_url:
            return redirect(next_url)

        # Caso contrário, redireciona para a página inicial
        return redirect("inicio")

    def form_invalid(self, form):
        # Adiciona mensagens de erro
        display_form_errors(self.request, form)
        return super().form_invalid(form)


# Tela para avaliações, mas será apresentado por diario
class Avaliacoes(LoginRequiredMixin, TemplateView):
    template_name = "avaliacoes.html"
    context_object_name = "avaliacao_docente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def get_perfil_aluno_from_user(user):
    """
    Função simplificada - agora usa o relacionamento OneToOne
    """
    try:
        return user.perfil_aluno
    except PerfilAluno.DoesNotExist:
        return None


@login_required
def buscar_alunos_ajax(request):
    """
    View para buscar alunos via AJAX
    """
    if request.is_ajax and request.method == "GET":
        termo = request.GET.get("termo", "")
        alunos = (
            PerfilAluno.objects.filter(
                Q(user__first_name__icontains=termo)
                | Q(user__last_name__icontains=termo)
                | Q(user__username__icontains=termo)
            )
            .select_related("user")
            .distinct()
        )

        resultados = [
            {"id": aluno.user.id, "nome": aluno.user.get_full_name()}
            for aluno in alunos
        ]

        return JsonResponse({"resultados": resultados})

    return JsonResponse({"resultados": []})


@login_required
def buscar_alunos_turma(request):
    """
    View para buscar alunos para gerenciamento de turmas via AJAX
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    turma_id = request.GET.get("turma_id")
    busca = request.GET.get("busca", "")

    try:
        turma = get_object_or_404(Turma, id=turma_id)

        # Buscar todos os alunos ativos
        alunos_query = PerfilAluno.non_admin.select_related("user").all()

        if busca:
            alunos_query = alunos_query.filter(
                Q(user__first_name__icontains=busca)
                | Q(user__last_name__icontains=busca)
                | Q(user__username__icontains=busca)
                | Q(user__email__icontains=busca)
            )

        # Verificar quais alunos estão matriculados na turma
        matriculas_ativas = MatriculaTurma.objects.filter(
            turma=turma, status="ativa"
        ).values_list("aluno_id", flat=True)

        alunos_data = []
        for aluno in alunos_query.order_by("user__first_name", "user__last_name"):
            alunos_data.append(
                {
                    "id": aluno.user.id,
                    "nome": aluno.user.get_full_name() or aluno.user.username,
                    "username": aluno.user.username,
                    "email": aluno.user.email or "Não informado",
                    "matriculado": aluno.id in matriculas_ativas,
                }
            )

        turma_data = {
            "codigo": turma.codigo_turma,
            "disciplina": turma.disciplina.disciplina_nome,
            "professor": turma.disciplina.professor.user.get_full_name(),
        }

        return JsonResponse(
            {
                "success": True,
                "alunos": alunos_data,
                "turma": turma_data,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def matricular_alunos_massa(request):
    """
    View para matricular/desmatricular alunos em massa via AJAX
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Sem permissão"}, status=403)

    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        turma_id = request.POST.get("turma_id")
        acao = request.POST.get("acao")  # 'matricular' ou 'desmatricular'
        alunos_ids = request.POST.getlist("alunos_ids[]")

        if not turma_id or not acao or not alunos_ids:
            return JsonResponse({"error": "Dados incompletos"}, status=400)

        turma = get_object_or_404(Turma, id=turma_id)

        # Buscar os perfis de aluno pelos IDs dos usuários
        usuarios = User.objects.filter(id__in=alunos_ids)
        alunos = PerfilAluno.objects.filter(user__in=usuarios)

        sucesso_count = 0
        erro_count = 0

        for aluno in alunos:
            try:
                if acao == "matricular":
                    matricula, created = MatriculaTurma.objects.get_or_create(
                        aluno=aluno, turma=turma, defaults={"status": "ativa"}
                    )
                    if created:
                        sucesso_count += 1
                    else:
                        # Se já existe, ativar se estiver inativa
                        if matricula.status != "ativa":
                            matricula.status = "ativa"
                            matricula.save()
                            sucesso_count += 1

                elif acao == "desmatricular":
                    matriculas = MatriculaTurma.objects.filter(
                        aluno=aluno, turma=turma, status="ativa"
                    )
                    if matriculas.exists():
                        matriculas.update(status="cancelada")
                        sucesso_count += 1

            except Exception as e:
                erro_count += 1
                print(f"Erro ao processar aluno {aluno.user.username}: {e}")

        if acao == "matricular":
            message = f"{sucesso_count} aluno(s) matriculado(s) com sucesso"
        else:
            message = f"{sucesso_count} aluno(s) desmatriculado(s) com sucesso"

        if erro_count > 0:
            message += f" ({erro_count} erro(s))"

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "sucesso_count": sucesso_count,
                "erro_count": erro_count,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============= VIEWS PARA AVALIAÇÃO DOCENTE =============


@login_required
def listar_avaliacoes(request):
    """
    View para listar avaliações disponíveis
    Para alunos: mostra apenas avaliações das turmas em que estão matriculados
    Para outros usuários: mostra todas as avaliações ativas
    """
    # Bloquear acesso para professores (exceto se também forem coordenadores/admin)
    if check_user_permission(request.user, ["professor"]) and not check_user_permission(
        request.user, ["coordenador", "admin"]
    ):
        messages.error(
            request,
            "Professores não têm acesso direto à listagem geral de avaliações.",
        )
        return redirect("inicio")
    if hasattr(request.user, "perfil_aluno"):
        # Para alunos: mostrar apenas avaliações das turmas em que estão matriculados
        turmas_aluno = request.user.perfil_aluno.matriculas.filter(
            status="ativa"
        ).values_list("turma_id", flat=True)

        now = timezone.now()
        # Filtrar avaliações de ciclos ativos e em andamento
        # Usa data_inicio e data_fim para garantir que apenas ciclos no período correto apareçam
        avaliacoes_disponiveis = (
            AvaliacaoDocente.objects.filter(
                ciclo__ativo=True,
                ciclo__encerrado=False,
                ciclo__data_inicio__lte=now,
                ciclo__data_fim__gte=now,  # Garante que o ciclo ainda não passou da data fim
                turma_id__in=turmas_aluno,
                status__in=["pendente", "em_andamento"],
            )
            .exclude(respostas__aluno=request.user.perfil_aluno)
            .distinct()
            .order_by("-data_criacao")
        )

        avaliacoes = avaliacoes_disponiveis
        titulo = "Avaliações Disponíveis para Responder"
        ciclos = []
    else:
        # Para administradores e coordenadores: NÃO mostrar avaliações individuais
        # Eles veem apenas os ciclos de avaliação
        avaliacoes = []  # Lista vazia - não mostrar seção de avaliações
        titulo = "Gerenciamento de Ciclos de Avaliação"
        # Ciclos separados por status para facilitar exibição
        now = timezone.now()
        ciclos_queryset = CicloAvaliacao.objects.all().order_by("-data_inicio")
        ciclos_em_andamento = []
        ciclos_finalizados = []
        for c in ciclos_queryset:
            # Ciclo está finalizado se foi encerrado manualmente OU passou da data_fim
            if c.encerrado or c.data_fim < now:
                ciclos_finalizados.append(c)
            else:
                ciclos_em_andamento.append(c)
        ciclos = {
            "em_andamento": ciclos_em_andamento,
            "finalizados": ciclos_finalizados,
        }

    # Remover a linha duplicada de ciclos que estava fora do if/else
    # Paginação - apenas para alunos que têm avaliações
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    if hasattr(request.user, "perfil_aluno") and avaliacoes:
        paginator = Paginator(avaliacoes, 10)
        page_number = request.GET.get("page", 1)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    else:
        # Para coordenadores/admins ou quando não há avaliações
        page_obj = []

    context = {
        "avaliacoes": page_obj,
        "ciclos": ciclos,
        "titulo": titulo,
        "ciclos_em_andamento": (
            ciclos.get("em_andamento")
            if not hasattr(request.user, "perfil_aluno")
            else []
        ),
        "ciclos_finalizados": (
            ciclos.get("finalizados")
            if not hasattr(request.user, "perfil_aluno")
            else []
        ),
    }
    return render(request, "avaliacoes/listar_avaliacoes.html", context)


@login_required
def dashboard_gestao_ciclos(request):
    """
    Dashboard de gestão centralizada de múltiplos ciclos.
    Exibe KPIs, filtros, status de lembretes e permite ações em massa.
    Apenas para admin/coordenador.
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(
            request, "Você não tem permissão para acessar o dashboard de gestão."
        )
        return redirect("listar_avaliacoes")

    from .services import calcular_kpis_multiplos_ciclos, obter_ciclos_em_alerta

    # Filtros da requisição
    filtro_status = request.GET.get(
        "status", "todos"
    )  # 'todos', 'ativos', 'finalizados'
    filtro_periodo_inicio = request.GET.get("periodo_inicio", "")
    filtro_periodo_fim = request.GET.get("periodo_fim", "")
    filtro_curso = request.GET.get("curso", "")
    filtro_limiar = request.GET.get("limiar", "")  # 'abaixo', 'atingido', 'todos'
    ordenar_por = request.GET.get("ordenar", "-data_inicio")  # campo de ordenação

    # Base query
    ciclos_qs = CicloAvaliacao.objects.all()

    # Aplicar filtros
    now = timezone.now()

    if filtro_status == "ativos":
        # Ativos = Não encerrados E dentro do prazo
        ciclos_qs = ciclos_qs.filter(encerrado=False, data_fim__gte=now)
    elif filtro_status == "finalizados":
        # Finalizados = Encerrados manualmente OU Prazo expirado
        ciclos_qs = ciclos_qs.filter(Q(encerrado=True) | Q(data_fim__lt=now))

    if filtro_periodo_inicio:
        ciclos_qs = ciclos_qs.filter(data_inicio__gte=filtro_periodo_inicio)

    if filtro_periodo_fim:
        # Add one day to make the filter inclusive (include cycles ending on this date)
        from datetime import datetime, timedelta
        data_fim_inclusiva = datetime.fromisoformat(filtro_periodo_fim) + timedelta(days=1)
        ciclos_qs = ciclos_qs.filter(data_fim__lt=data_fim_inclusiva)

    if filtro_curso:
        ciclos_qs = ciclos_qs.filter(
            turmas__disciplina__curso_id=filtro_curso
        ).distinct()

    # Ordenação
    ciclos_qs = ciclos_qs.order_by(ordenar_por)

    # Calcular KPIs para todos os ciclos filtrados
    ciclos_com_kpis = []
    kpis_dict = calcular_kpis_multiplos_ciclos(ciclos_qs)

    for ciclo in ciclos_qs:
        kpis = kpis_dict.get(ciclo.id, {})

        # Aplicar filtro de limiar (pós-processamento)
        if filtro_limiar == "abaixo":
            if kpis.get("taxa_media_resposta", 0) >= kpis.get("limiar_configurado", 10):
                continue
        elif filtro_limiar == "atingido":
            if kpis.get("taxa_media_resposta", 0) < kpis.get("limiar_configurado", 10):
                continue

        ciclos_com_kpis.append({"ciclo": ciclo, "kpis": kpis})

    # Paginação
    paginator = Paginator(ciclos_com_kpis, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Estatísticas gerais (cards do topo)
    total_ativos = CicloAvaliacao.objects.filter(encerrado=False).count()
    total_finalizados = CicloAvaliacao.objects.filter(encerrado=True).count()
    ciclos_alerta = obter_ciclos_em_alerta()
    total_em_alerta = ciclos_alerta.count()

    # Jobs com erro em ciclos ativos
    from .models import JobLembreteCicloTurma

    jobs_erro = JobLembreteCicloTurma.objects.filter(
        ciclo__ativo=True, status="erro"
    ).count()

    # Lista de cursos para filtro
    cursos = Curso.objects.all().order_by("curso_nome")

    context = {
        "page_obj": page_obj,
        "total_ativos": total_ativos,
        "total_finalizados": total_finalizados,
        "total_em_alerta": total_em_alerta,
        "jobs_erro": jobs_erro,
        "ciclos_alerta": ciclos_alerta[:5],  # Top 5 mais urgentes
        "cursos": cursos,
        "filtros": {
            "status": filtro_status,
            "periodo_inicio": filtro_periodo_inicio,
            "periodo_fim": filtro_periodo_fim,
            "curso": filtro_curso,
            "limiar": filtro_limiar,
            "ordenar": ordenar_por,
        },
    }

    return render(request, "admin/dashboard_gestao_ciclos.html", context)


@login_required
def gerenciar_questionarios(request):
    """
    View para gerenciar questionários de avaliação
    Permite criar, editar e listar questionários
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para gerenciar questionários.")
        return redirect("listar_avaliacoes")

    editing_id = request.GET.get("edit")
    questionario_editando = None

    if editing_id:
        try:
            questionario_editando = QuestionarioAvaliacao.objects.get(id=editing_id)
        except QuestionarioAvaliacao.DoesNotExist:
            messages.error(request, "Questionário não encontrado.")
            return redirect("gerenciar_questionarios")

    if request.method == "POST":
        if editing_id:
            # Editando questionário existente
            form = QuestionarioAvaliacaoForm(
                request.POST, instance=questionario_editando
            )
            if form.is_valid():
                questionario = form.save()
                messages.success(
                    request,
                    f"Questionário '{questionario.titulo}' atualizado com sucesso!",
                )
                return redirect("gerenciar_questionarios")
        else:
            # Criando novo questionário
            form = QuestionarioAvaliacaoForm(request.POST)
            if form.is_valid():
                questionario = form.save(commit=False)
                questionario.criado_por = request.user
                questionario.save()
                messages.success(
                    request, f"Questionário '{questionario.titulo}' criado com sucesso!"
                )
                return redirect("gerenciar_questionarios")
    else:
        if questionario_editando:
            form = QuestionarioAvaliacaoForm(instance=questionario_editando)
        else:
            form = QuestionarioAvaliacaoForm()

    # Listar todos os questionários
    questionarios_list = QuestionarioAvaliacao.objects.all().order_by("-data_criacao")

    # Paginação - 15 questionários por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(questionarios_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        questionarios = paginator.page(page_number)
    except PageNotAnInteger:
        questionarios = paginator.page(1)
    except EmptyPage:
        questionarios = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "questionarios": questionarios,
        "editing": bool(editing_id),
        "questionario_editando": questionario_editando,
        "titulo": "Editar Questionário" if editing_id else "Novo Questionário",
    }

    return render(request, "gerenciar_questionarios.html", context)


@login_required
def editar_questionario_simples(request, questionario_id):
    """
    Redireciona para o gerenciamento com o questionário selecionado para edição
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para editar questionários.")
        return redirect("listar_avaliacoes")

    return redirect(f"{reverse('gerenciar_questionarios')}?edit={questionario_id}")


@login_required
def excluir_questionario(request, questionario_id):
    """
    View para excluir um questionário
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para excluir questionários.")
        return redirect("listar_avaliacoes")

    try:
        questionario = QuestionarioAvaliacao.objects.get(id=questionario_id)
        nome_questionario = questionario.titulo

        # Verificar se o questionário está sendo usado em algum ciclo
        if CicloAvaliacao.objects.filter(questionario=questionario).exists():
            messages.error(
                request,
                f"Não é possível excluir o questionário '{nome_questionario}' pois está sendo usado em ciclos de avaliação.",
            )
            return redirect("gerenciar_questionarios")

        questionario.delete()
        messages.success(
            request, f"Questionário '{nome_questionario}' excluído com sucesso!"
        )

    except QuestionarioAvaliacao.DoesNotExist:
        messages.error(request, "Questionário não encontrado.")

    return redirect("gerenciar_questionarios")


@login_required
def editar_questionario_perguntas(request, questionario_id):
    """
    View para editar as perguntas de um questionário
    """
    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para editar questionários.")
        return redirect("listar_avaliacoes")

    questionario = get_object_or_404(QuestionarioAvaliacao, id=questionario_id)
    categorias = CategoriaPergunta.objects.all()

    # ========== PROCESSAR POST PRIMEIRO (ANTES DA LIMPEZA) ==========
    if request.method == "POST":
        print(f"DEBUG: POST data: {request.POST}")
        if "adicionar_pergunta" in request.POST:
            print("DEBUG: Tentando adicionar pergunta")
            form = PerguntaAvaliacaoForm(request.POST)
            print(f"DEBUG: Form data: {form.data}")
            if form.is_valid():
                print("DEBUG: Form é válido, salvando pergunta")
                pergunta = form.save()
                print(f"DEBUG: Pergunta salva: {pergunta}")
                # Adicionar ao questionário - contar apenas perguntas ativas
                ordem = (
                    QuestionarioPergunta.objects.filter(
                        questionario=questionario, pergunta__ativo=True
                    ).count()
                    + 1
                )
                qp = QuestionarioPergunta.objects.create(
                    questionario=questionario,
                    pergunta=pergunta,
                    ordem_no_questionario=ordem,
                )
                print(f"DEBUG: QuestionarioPergunta criado: {qp}")
                messages.success(request, "Pergunta adicionada com sucesso!")
                return redirect(
                    "editar_questionario_perguntas", questionario_id=questionario.id
                )
            else:
                print(f"DEBUG: Form inválido - erros: {form.errors}")
                # Extrair mensagens de erro de forma limpa
                erros_list = []
                for field, errors in form.errors.items():
                    field_label = (
                        form.fields.get(field).label if field in form.fields else field
                    )
                    for error in errors:
                        erros_list.append(f"{field_label}: {error}")

                erro_msg = (
                    " | ".join(erros_list)
                    if erros_list
                    else "Verifique os campos do formulário."
                )
                messages.error(request, f"Erro ao adicionar pergunta: {erro_msg}")

        elif "salvar_edicao" in request.POST:
            print("DEBUG: Tentando editar pergunta via POST")
            pergunta_id = request.POST.get("pergunta_id")
            print(f"DEBUG: pergunta_id recebido do POST: {pergunta_id}")
            print(f"DEBUG: Todos os dados POST: {request.POST}")

            if not pergunta_id:
                messages.error(request, "❌ ID da pergunta não foi fornecido.")
                return redirect(
                    "editar_questionario_perguntas", questionario_id=questionario.id
                )

            try:
                # Buscar a pergunta e verificar se pertence a este questionário
                pergunta_para_editar = PerguntaAvaliacao.objects.get(id=pergunta_id)
                print(f"DEBUG: Pergunta encontrada para editar: {pergunta_para_editar}")

                # Verificar se a pergunta está associada a este questionário
                if not QuestionarioPergunta.objects.filter(
                    questionario=questionario, pergunta=pergunta_para_editar
                ).exists():
                    messages.error(
                        request, "❌ Pergunta não pertence a este questionário."
                    )
                    return redirect(
                        "editar_questionario_perguntas", questionario_id=questionario.id
                    )

                form = PerguntaAvaliacaoForm(
                    request.POST, instance=pergunta_para_editar
                )
                if form.is_valid():
                    pergunta = form.save()
                    messages.success(request, "Pergunta atualizada com sucesso!")
                    return redirect(
                        "editar_questionario_perguntas", questionario_id=questionario.id
                    )
                else:
                    # Extrair mensagens de erro de forma limpa
                    erros_list = []
                    for field, errors in form.errors.items():
                        field_label = (
                            form.fields.get(field).label
                            if field in form.fields
                            else field
                        )
                        for error in errors:
                            erros_list.append(f"{field_label}: {error}")

                    erro_msg = (
                        " | ".join(erros_list)
                        if erros_list
                        else "Verifique os campos do formulário."
                    )
                    messages.error(request, f"❌ Erro ao editar pergunta: {erro_msg}")
                    pergunta_editando = pergunta_para_editar  # Manter no modo de edição
            except PerguntaAvaliacao.DoesNotExist:
                messages.error(request, "❌ Pergunta não encontrada.")
                return redirect(
                    "editar_questionario_perguntas", questionario_id=questionario.id
                )

        elif "remover_pergunta" in request.POST:
            pergunta_id = request.POST.get("pergunta_id")
            QuestionarioPergunta.objects.filter(
                questionario=questionario, pergunta_id=pergunta_id
            ).delete()
            # Reordenar perguntas - apenas ativas
            perguntas_restantes = QuestionarioPergunta.objects.filter(
                questionario=questionario, pergunta__ativo=True
            ).order_by("ordem_no_questionario")
            for i, qp in enumerate(perguntas_restantes, 1):
                qp.ordem_no_questionario = i
                qp.save()
            messages.success(request, "Pergunta removida com sucesso!")
            return redirect(
                "editar_questionario_perguntas", questionario_id=questionario.id
            )

    # ========== LIMPEZA SÓ RODA APÓS O POST OU EM GET ==========
    # Limpar QuestionarioPergunta que apontam para perguntas inativas (soft-deleted)
    qps_com_perguntas_inativas = QuestionarioPergunta.objects.filter(
        questionario=questionario, pergunta__ativo=False
    )

    if qps_com_perguntas_inativas.exists():
        count_orfas = qps_com_perguntas_inativas.count()
        print(f"DEBUG: Encontradas {count_orfas} referência(s) a perguntas inativas")
        for qp in qps_com_perguntas_inativas:
            print(
                f"DEBUG: Removendo QuestionarioPergunta {qp.id} (pergunta #{qp.pergunta_id} está inativa)"
            )
        qps_com_perguntas_inativas.delete()
        messages.info(
            request,
            f"✓ {count_orfas} referência(s) a perguntas removidas foram limpas.",
        )

    # Buscar apenas perguntas ativas
    perguntas_existentes = QuestionarioPergunta.objects.filter(
        questionario=questionario, pergunta__ativo=True
    ).order_by("ordem_no_questionario")

    # Verificar se está editando uma pergunta existente
    editando_pergunta_id = request.GET.get("editar_pergunta")
    pergunta_editando = None

    if editando_pergunta_id:
        print(f"DEBUG: Tentando editar pergunta com ID: {editando_pergunta_id}")
        try:
            pergunta_editando = PerguntaAvaliacao.objects.get(id=editando_pergunta_id)
            print(f"DEBUG: Pergunta encontrada: {pergunta_editando}")

            # Verificar se a pergunta pertence a este questionário
            qp_exists = QuestionarioPergunta.objects.filter(
                questionario=questionario, pergunta=pergunta_editando
            ).exists()
            print(f"DEBUG: Pergunta pertence ao questionário? {qp_exists}")

            if not qp_exists:
                messages.error(
                    request, "❌ Pergunta não encontrada neste questionário."
                )
                return redirect(
                    "editar_questionario_perguntas", questionario_id=questionario.id
                )
        except PerguntaAvaliacao.DoesNotExist:
            print(f"DEBUG: Pergunta com ID {editando_pergunta_id} não existe no banco")
            messages.error(
                request,
                f"❌ Pergunta #{editando_pergunta_id} não encontrada. "
                "Esta pergunta pode ter sido removida. Por favor, atualize a página.",
            )
            return redirect(
                "editar_questionario_perguntas", questionario_id=questionario.id
            )
        except Exception as e:
            print(f"DEBUG: Erro inesperado ao buscar pergunta: {e}")
            messages.error(request, f"❌ Erro ao buscar pergunta: {str(e)}")
            return redirect(
                "editar_questionario_perguntas", questionario_id=questionario.id
            )

    # Inicializar formulário para adicionar ou editar
    if pergunta_editando:
        form = PerguntaAvaliacaoForm(instance=pergunta_editando)
    else:
        form = PerguntaAvaliacaoForm()

    context = {
        "questionario": questionario,
        "perguntas_existentes": perguntas_existentes,
        "form": form,
        "categorias": categorias,
        "titulo": f"Editar Perguntas - {questionario.titulo}",
        "pergunta_editando": pergunta_editando,
        "editando": bool(pergunta_editando),
    }
    return render(request, "avaliacoes/editar_questionario_perguntas.html", context)


@login_required
def detalhe_ciclo_avaliacao(request, ciclo_id):
    """
    View para visualizar detalhes de um ciclo de avaliação
    """
    # Pode visualizar ciclos encerrados ou deletados para consulta histórica
    ciclo = get_object_or_404(CicloAvaliacao.all_objects, id=ciclo_id)
    avaliacoes_docentes = AvaliacaoDocente.objects.filter(ciclo=ciclo)

    # Estatísticas do ciclo
    total_avaliacoes = avaliacoes_docentes.count()

    # Contar avaliações que têm pelo menos uma resposta
    avaliacoes_com_respostas = (
        avaliacoes_docentes.filter(respostas__isnull=False).distinct().count()
    )

    context = {
        "ciclo": ciclo,
        "avaliacoes_docentes": avaliacoes_docentes,
        "total_avaliacoes": total_avaliacoes,
        "avaliacoes_respondidas": avaliacoes_com_respostas,
        "percentual_respondidas": (
            (avaliacoes_com_respostas / total_avaliacoes * 100)
            if total_avaliacoes > 0
            else 0
        ),
        "titulo": f"Ciclo: {ciclo.nome}",
    }
    return render(request, "avaliacoes/detalhe_ciclo.html", context)


@login_required
def responder_avaliacao(request, avaliacao_id):
    """
    View para um aluno responder uma avaliação docente
    """
    avaliacao = get_object_or_404(AvaliacaoDocente, id=avaliacao_id)

    # Verificar se o usuário pode responder esta avaliação
    if not hasattr(request.user, "perfil_aluno"):
        messages.error(request, "Apenas alunos podem responder avaliações.")
        return redirect("listar_avaliacoes")

    # Verificar se o aluno está matriculado na turma da avaliação
    if not request.user.perfil_aluno.matriculas.filter(
        turma=avaliacao.turma, status="ativa"
    ).exists():
        messages.error(request, "Você não está matriculado na turma desta avaliação.")
        return redirect("listar_avaliacoes")

    # Verificar se a avaliação já foi respondida
    respostas_existentes = RespostaAvaliacao.objects.filter(
        avaliacao=avaliacao, aluno=request.user.perfil_aluno
    ).exists()

    if respostas_existentes:
        messages.warning(request, "Esta avaliação já foi respondida.")
        return redirect("visualizar_avaliacao", avaliacao_id=avaliacao.id)

    now = timezone.now()
    # Verificar se o ciclo está ativo e dentro do período
    if (
        avaliacao.ciclo.encerrado
        or avaliacao.ciclo.data_fim < now
        or avaliacao.status not in ["pendente", "em_andamento"]
    ):
        messages.error(
            request, "Esta avaliação está encerrada e não aceita novas respostas."
        )
        return redirect("listar_avaliacoes")

    # Pegar perguntas do questionário
    perguntas_questionario = QuestionarioPergunta.objects.filter(
        questionario=avaliacao.ciclo.questionario
    ).order_by("ordem_no_questionario")

    if request.method == "POST":
        # Processar respostas
        respostas_validas = True

        for qp in perguntas_questionario:
            campo_resposta = f"pergunta_{qp.pergunta.id}"
            valor_resposta = request.POST.get(campo_resposta)

            if not valor_resposta and qp.pergunta.obrigatoria:
                messages.error(
                    request, f'A pergunta "{qp.pergunta.enunciado}" é obrigatória.'
                )
                respostas_validas = False
                continue

            if valor_resposta:
                # Criar resposta baseada no tipo
                resposta_data = {
                    "avaliacao": avaliacao,
                    "aluno": request.user.perfil_aluno,
                    "pergunta": qp.pergunta,
                    # Agora sempre anônima conforme nova regra
                    "anonima": True,
                }

                if qp.pergunta.tipo in ["likert", "nps"]:
                    resposta_data["valor_numerico"] = int(valor_resposta)
                elif qp.pergunta.tipo == "sim_nao":
                    resposta_data["valor_boolean"] = valor_resposta.lower() == "sim"
                else:
                    resposta_data["valor_texto"] = valor_resposta

                RespostaAvaliacao.objects.create(**resposta_data)

        if respostas_validas:
            messages.success(request, "Avaliação respondida com sucesso!")
            return redirect("visualizar_avaliacao", avaliacao_id=avaliacao.id)

    context = {
        "avaliacao": avaliacao,
        "perguntas_questionario": perguntas_questionario,
        "titulo": f"Responder Avaliação - {avaliacao.professor.user.get_full_name()}",
    }
    return render(request, "avaliacoes/responder_avaliacao.html", context)


@login_required
def visualizar_avaliacao(request, avaliacao_id):
    """
    View para visualizar uma avaliação respondida
    """
    avaliacao = get_object_or_404(AvaliacaoDocente, id=avaliacao_id)

    # Verificar permissões
    pode_visualizar = False
    if hasattr(request.user, "perfil_aluno"):
        # Verificar se o aluno está matriculado na turma e se há respostas do aluno para esta avaliação
        respostas_aluno = RespostaAvaliacao.objects.filter(
            avaliacao=avaliacao, aluno=request.user.perfil_aluno
        ).exists()

        matricula_ativa = request.user.perfil_aluno.matriculas.filter(
            turma=avaliacao.turma, status="ativa"
        ).exists()

        if respostas_aluno and matricula_ativa:
            pode_visualizar = True
    elif (
        hasattr(request.user, "perfil_professor")
        and avaliacao.professor == request.user.perfil_professor
    ):
        pode_visualizar = True
    elif check_user_permission(request.user, ["coordenador", "admin"]):
        pode_visualizar = True

    if not pode_visualizar:
        messages.error(
            request, "Você não tem permissão para visualizar esta avaliação."
        )
        return redirect("listar_avaliacoes")

    # Pegar respostas
    # Ajuste: alunos só podem visualizar as PRÓPRIAS respostas; demais perfis (professor da avaliação,
    # coordenador, admin) continuam podendo ver o conjunto completo.
    if hasattr(request.user, "perfil_aluno"):
        respostas = (
            RespostaAvaliacao.objects.filter(
                avaliacao=avaliacao, aluno=request.user.perfil_aluno
            )
            .select_related("pergunta")
            .filter(pergunta__questionarios__questionario=avaliacao.ciclo.questionario)
            .order_by("pergunta__questionarios__ordem_no_questionario")
            .distinct()
        )
    else:
        respostas = (
            RespostaAvaliacao.objects.filter(avaliacao=avaliacao)
            .select_related("pergunta")
            .filter(pergunta__questionarios__questionario=avaliacao.ciclo.questionario)
            .order_by("pergunta__questionarios__ordem_no_questionario")
            .distinct()
        )
    context = {
        "avaliacao": avaliacao,
        "respostas": respostas,
        "titulo": f"Avaliação - {avaliacao.professor.user.get_full_name()}",
    }
    return render(request, "avaliacoes/visualizar_avaliacao.html", context)


@login_required
def relatorio_avaliacoes(request):
    """
    View para gerar relatórios de avaliações
    Apenas coordenadores e admins podem acessar
    """
    from django.db.models import Avg, Count
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    import json

    if not (check_user_permission(request.user, ["coordenador", "admin"])):
        messages.error(request, "Você não tem permissão para acessar relatórios.")
        return redirect("listar_avaliacoes")

    # Verificar se é solicitação de exportação CSV
    formato = request.GET.get("formato")

    ciclos = CicloAvaliacao.objects.all().order_by("-data_inicio")
    professores = PerfilProfessor.non_admin.all().order_by("user__first_name")

    # Filtros
    ciclo_selecionado = request.GET.get("ciclo")
    professor_selecionado = request.GET.get("professor")
    search_query = request.GET.get("search", "").strip()

    # Buscar avaliações que têm respostas com otimização de queries
    avaliacoes = (
        AvaliacaoDocente.objects.filter(respostas__isnull=False)
        .select_related(
            "turma__disciplina__periodo_letivo",
            "turma__disciplina__professor__user",
            "professor__user",
            "ciclo__questionario",
        )
        .prefetch_related(
            "respostas",
            "turma__matriculas",
            "ciclo__questionario__perguntas__pergunta",
        )
        .distinct()
    )

    if ciclo_selecionado:
        avaliacoes = avaliacoes.filter(ciclo_id=ciclo_selecionado)

    if professor_selecionado:
        avaliacoes = avaliacoes.filter(professor_id=professor_selecionado)

    # Busca por texto (professor, disciplina, turma)
    if search_query:
        from django.db.models import Q

        avaliacoes = avaliacoes.filter(
            Q(professor__user__first_name__icontains=search_query)
            | Q(professor__user__last_name__icontains=search_query)
            | Q(turma__disciplina__disciplina_nome__icontains=search_query)
            | Q(turma__codigo_turma__icontains=search_query)
        )

    # Se for solicitação de exportação CSV, gerar e retornar o arquivo (sem paginação)
    if formato == "csv":
        return gerar_csv_avaliacoes(
            avaliacoes, ciclo_selecionado, professor_selecionado
        )

    # Estatísticas
    total_avaliacoes = avaliacoes.count()

    # Configurar paginação
    per_page = request.GET.get("per_page", "6")
    try:
        per_page = int(per_page)
        if per_page not in [6, 12, 24, 50]:
            per_page = 6
    except (ValueError, TypeError):
        per_page = 6

    paginator = Paginator(avaliacoes, per_page)
    page = request.GET.get("page", 1)

    try:
        avaliacoes_paginadas = paginator.page(page)
    except PageNotAnInteger:
        avaliacoes_paginadas = paginator.page(1)
    except EmptyPage:
        avaliacoes_paginadas = paginator.page(paginator.num_pages)

    # Calcular dados adicionais para cada avaliação (apenas da página atual)
    avaliacoes_com_stats = []
    for avaliacao in avaliacoes_paginadas:
        # Contar respondentes únicos
        respondentes = (
            RespostaAvaliacao.objects.filter(avaliacao=avaliacao)
            .values("aluno")
            .distinct()
            .count()
        )

        # Calcular taxa de resposta
        total_alunos = avaliacao.turma.matriculas.filter(status="ativa").count()
        taxa_resposta = (respondentes / total_alunos * 100) if total_alunos > 0 else 0

        # Calcular estatísticas por pergunta
        pergunta_stats = []
        perguntas_questionario = avaliacao.ciclo.questionario.perguntas.all()

        for pergunta_questionario in perguntas_questionario:
            pergunta = pergunta_questionario.pergunta

            # Tratamento para perguntas de múltipla escolha (questionário padrão)
            if pergunta.tipo == "multipla_escolha":
                resultado = avaliacao.calcular_media_pergunta(pergunta)
                if resultado:
                    pergunta_stats.append(
                        {
                            "pergunta": pergunta,
                            "tipo": "multipla_escolha",
                            "media": resultado["media"],
                            "moda": resultado.get("moda", "N/A"),
                            "contagens": resultado["contagens"],
                            "respostas_count": resultado["total_respondentes"],
                            "classificacao": avaliacao.get_classificacao_media(
                                resultado["media"]
                            ),
                        }
                    )
            else:
                # Tratamento para perguntas numéricas (likert, nps)
                respostas_pergunta = RespostaAvaliacao.objects.filter(
                    avaliacao__ciclo=avaliacao.ciclo,
                    avaliacao__professor=avaliacao.professor,
                    avaliacao__turma=avaliacao.turma,
                    pergunta=pergunta,
                    valor_numerico__isnull=False,
                )

                stats = calcular_estatisticas_respostas(respostas_pergunta)
                if stats:
                    pergunta_stats.append(
                        {
                            "pergunta": pergunta,
                            "tipo": "numerico",
                            "media": round(stats["media"], 2),
                            "moda": stats["moda"],
                            "respostas_count": stats["count"],
                        }
                    )

        # Buscar comentários da avaliação (anônimos)
        # Filtrar apenas perguntas do tipo "texto_livre" para evitar incluir
        # respostas de múltipla escolha ou sim/não que também têm valor_texto
        comentarios = (
            RespostaAvaliacao.objects.filter(
                avaliacao=avaliacao,
                pergunta__tipo="texto_livre",
                valor_texto__isnull=False,
                valor_texto__gt="",
            )
            .exclude(valor_texto="")
            .only("valor_texto", "data_resposta")
        )

        # Calcular média geral do questionário padrão (se aplicável)
        media_geral_padrao = avaliacao.calcular_media_geral_questionario_padrao()

        # Adicionar dados calculados à avaliação
        avaliacao.respondentes = respondentes
        avaliacao.total_alunos = total_alunos
        avaliacao.taxa_resposta = round(taxa_resposta, 2)
        avaliacao.pergunta_stats = pergunta_stats
        avaliacao.comentarios = comentarios
        avaliacao.media_geral_padrao = media_geral_padrao
        if media_geral_padrao:
            avaliacao.classificacao_geral = avaliacao.get_classificacao_media(
                media_geral_padrao["media_geral"]
            )
        else:
            avaliacao.classificacao_geral = None

        avaliacoes_com_stats.append(avaliacao)

    # Calcular média simples das respostas numéricas
    media_geral = 0
    if total_avaliacoes > 0:
        respostas_numericas = RespostaAvaliacao.objects.filter(
            avaliacao__in=avaliacoes, valor_numerico__isnull=False
        )
        if respostas_numericas.exists():
            media_geral = (
                respostas_numericas.aggregate(media=Avg("valor_numerico"))["media"] or 0
            )

    # ================= Geração de dados para gráficos por ciclo =================

    ciclos_para_graficos = []

    # Ciclos considerados conforme filtros aplicados
    if ciclo_selecionado:
        ciclos_iter = ciclos.filter(id=ciclo_selecionado)
    else:
        # Apenas ciclos que aparecem nas avaliacoes filtradas
        ciclos_iter = ciclos.filter(
            id__in=avaliacoes.values_list("ciclo_id", flat=True).distinct()
        )

    for ciclo in ciclos_iter:
        # Base de todas as respostas dentro do ciclo e filtros de professor se houver
        respostas_base = RespostaAvaliacao.objects.filter(
            avaliacao__ciclo=ciclo,
        )
        if professor_selecionado:
            respostas_base = respostas_base.filter(
                avaliacao__professor_id=professor_selecionado
            )

        if not respostas_base.exists():
            continue

        # Separar respostas por tipo para processamento específico
        respostas_numericas = respostas_base.filter(
            pergunta__tipo__in=["likert", "nps"],
            valor_numerico__isnull=False,
        )

        respostas_multipla_escolha = respostas_base.filter(
            pergunta__tipo="multipla_escolha",
            valor_texto__isnull=False,
        ).exclude(valor_texto="")

        respostas_sim_nao = respostas_base.filter(
            pergunta__tipo="sim_nao",
            valor_boolean__isnull=False,
        )

        respostas_texto_livre = respostas_base.filter(
            pergunta__tipo="texto_livre",
            valor_texto__isnull=False,
        ).exclude(valor_texto="")

        # Processar perguntas numéricas (Likert e NPS)
        contagens_numericas = respostas_numericas.values(
            "pergunta_id",
            "pergunta__enunciado",
            "pergunta__tipo",
            "valor_numerico",
        ).annotate(qtd=Count("id"))

        # Processar perguntas de múltipla escolha
        contagens_multipla = respostas_multipla_escolha.values(
            "pergunta_id",
            "pergunta__enunciado",
            "pergunta__tipo",
            "valor_texto",
        ).annotate(qtd=Count("id"))

        # Processar perguntas sim/não
        contagens_sim_nao = respostas_sim_nao.values(
            "pergunta_id",
            "pergunta__enunciado",
            "pergunta__tipo",
            "valor_boolean",
        ).annotate(qtd=Count("id"))

        # Processar perguntas de texto livre (apenas contagem)
        contagens_texto = respostas_texto_livre.values(
            "pergunta_id",
            "pergunta__enunciado",
            "pergunta__tipo",
        ).annotate(qtd=Count("id"))

        # Médias para perguntas numéricas
        medias_numericas = respostas_numericas.values("pergunta_id").annotate(
            media=Avg("valor_numerico")
        )
        medias_map = {m["pergunta_id"]: m["media"] for m in medias_numericas}

        perguntas_data = {}

        # Processar perguntas numéricas (Likert e NPS)
        for item in contagens_numericas:
            pid = item["pergunta_id"]
            if pid not in perguntas_data:
                # Inicializa estrutura conforme o tipo
                if item["pergunta__tipo"] == "likert":
                    escala_default = {str(i): 0 for i in range(1, 6)}
                else:  # nps
                    escala_default = {str(i): 0 for i in range(0, 11)}
                perguntas_data[pid] = {
                    "id": pid,
                    "enunciado": item["pergunta__enunciado"],
                    "tipo": item["pergunta__tipo"],
                    "contagens": escala_default,
                    "media": round(medias_map.get(pid) or 0, 2),
                }
            perguntas_data[pid]["contagens"][str(item["valor_numerico"])] = item["qtd"]

        # Processar perguntas de múltipla escolha
        for item in contagens_multipla:
            pid = item["pergunta_id"]
            if pid not in perguntas_data:
                perguntas_data[pid] = {
                    "id": pid,
                    "enunciado": item["pergunta__enunciado"],
                    "tipo": item["pergunta__tipo"],
                    "contagens": {},
                    "media": "N/A",
                }
            valor = (
                item["valor_texto"][:30] + "..."
                if len(item["valor_texto"]) > 30
                else item["valor_texto"]
            )
            perguntas_data[pid]["contagens"][valor] = item["qtd"]

        # Processar perguntas sim/não
        for item in contagens_sim_nao:
            pid = item["pergunta_id"]
            if pid not in perguntas_data:
                perguntas_data[pid] = {
                    "id": pid,
                    "enunciado": item["pergunta__enunciado"],
                    "tipo": item["pergunta__tipo"],
                    "contagens": {"Sim": 0, "Não": 0},
                    "media": "N/A",
                }
            valor = "Sim" if item["valor_boolean"] else "Não"
            perguntas_data[pid]["contagens"][valor] = item["qtd"]

        # Processar perguntas de texto livre
        for item in contagens_texto:
            pid = item["pergunta_id"]
            if pid not in perguntas_data:
                perguntas_data[pid] = {
                    "id": pid,
                    "enunciado": item["pergunta__enunciado"],
                    "tipo": item["pergunta__tipo"],
                    "contagens": {"Total de respostas": item["qtd"]},
                    "media": "N/A",
                }

        ciclos_para_graficos.append(
            {
                "id": ciclo.id,
                "nome": ciclo.nome,
                "perguntas": list(perguntas_data.values()),
            }
        )

    context = {
        "ciclos": ciclos,
        "professores": professores,
        "avaliacoes": avaliacoes_com_stats,
        "page_obj": avaliacoes_paginadas,
        "paginator": paginator,
        "total_avaliacoes": total_avaliacoes,
        "media_geral": round(media_geral, 2),
        "ciclo_selecionado": ciclo_selecionado,
        "professor_selecionado": professor_selecionado,
        "search_query": search_query,
        "per_page": per_page,
        "titulo": "Relatórios de Avaliação",
        "ciclos_graficos_json": json.dumps(ciclos_para_graficos),
    }
    return render(request, "avaliacoes/relatorio_avaliacoes.html", context)


def gerar_csv_avaliacoes(
    avaliacoes, ciclo_selecionado=None, professor_selecionado=None
):
    """
    Função para gerar arquivo CSV com dados das avaliações
    """
    from django.db.models import Avg, Count

    # Preparar resposta HTTP para CSV
    response = HttpResponse(content_type="text/csv; charset=utf-8")

    # Nome do arquivo com filtros aplicados
    nome_arquivo = "relatorio_avaliacoes"
    if ciclo_selecionado:
        ciclo = CicloAvaliacao.objects.get(id=ciclo_selecionado)
        nome_arquivo += f"_ciclo_{ciclo.nome.replace(' ', '_')}"
    if professor_selecionado:
        professor = PerfilProfessor.objects.get(id=professor_selecionado)
        nome_professor = (
            f"{professor.user.first_name}_{professor.user.last_name}".replace(" ", "_")
        )
        nome_arquivo += f"_prof_{nome_professor}"

    nome_arquivo += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'

    # Criar writer CSV
    writer = csv.writer(response)

    # Escrever BOM para UTF-8 (compatibilidade com Excel)
    response.write("\ufeff")

    # Cabeçalhos principais
    writer.writerow(
        [
            "Disciplina",
            "Professor",
            "Turma",
            "Período Letivo",
            "Ciclo",
            "Total Alunos",
            "Respondentes",
            "Taxa de Resposta (%)",
            "Média Geral",
            "Classificação Geral",
            "Pergunta",
            "Tipo Pergunta",
            "Média Pergunta",
            "Moda",
            "Classificação",
            "Não atende",
            "Insuficiente",
            "Regular",
            "Bom",
            "Excelente",
            "Total Respostas",
            "Comentários",
        ]
    )

    # Processar cada avaliação
    for avaliacao in avaliacoes:
        # Dados básicos da avaliação
        disciplina = avaliacao.turma.disciplina.disciplina_nome
        professor = avaliacao.professor.user.get_full_name()
        turma = avaliacao.turma.codigo_turma
        periodo = avaliacao.turma.disciplina.periodo_letivo.nome
        ciclo = avaliacao.ciclo.nome

        # Contar respondentes únicos (seguindo a mesma lógica do relatório)
        respostas_com_aluno = (
            avaliacao.respostas.filter(aluno__isnull=False).values("aluno").distinct()
        )
        respostas_sem_aluno = (
            avaliacao.respostas.filter(aluno__isnull=True)
            .exclude(session_key="")
            .values("session_key")
            .distinct()
        )
        respondentes = respostas_com_aluno.count() + respostas_sem_aluno.count()

        # Calcular taxa de resposta
        total_alunos = avaliacao.turma.matriculas.filter(status="ativa").count()
        taxa_resposta = (
            round((respondentes / total_alunos * 100), 2) if total_alunos > 0 else 0
        )

        # Buscar comentários da avaliação
        # Filtrar apenas perguntas do tipo "texto_livre" para evitar incluir
        # respostas de múltipla escolha ou sim/não que também têm valor_texto
        comentarios = RespostaAvaliacao.objects.filter(
            avaliacao=avaliacao,
            pergunta__tipo="texto_livre",
            valor_texto__isnull=False,
            valor_texto__gt="",
        ).exclude(valor_texto="")

        comentarios_texto = " | ".join(
            [sanitize_csv_value(c.valor_texto) for c in comentarios[:5]]
        )  # Máximo 5 comentários
        if comentarios.count() > 5:
            comentarios_texto += f" | ... (+{comentarios.count() - 5} comentários)"

        # Calcular média geral do questionário padrão
        media_geral_padrao = avaliacao.calcular_media_geral_questionario_padrao()
        if media_geral_padrao:
            media_geral = media_geral_padrao["media_geral"]
            classificacao_geral = avaliacao.get_classificacao_media(media_geral)
        else:
            media_geral = "N/A"
            classificacao_geral = "N/A"

        # Processar estatísticas por pergunta
        perguntas_questionario = avaliacao.ciclo.questionario.perguntas.all()

        if not perguntas_questionario.exists():
            # Se não há perguntas, escrever linha básica
            writer.writerow(
                [
                    sanitize_csv_value(disciplina),
                    sanitize_csv_value(professor),
                    sanitize_csv_value(turma),
                    sanitize_csv_value(periodo),
                    sanitize_csv_value(ciclo),
                    total_alunos,
                    respondentes,
                    taxa_resposta,
                    media_geral,
                    classificacao_geral,
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    "N/A",
                    comentarios_texto,
                ]
            )
        else:
            # Para cada pergunta do questionário
            for pergunta_questionario in perguntas_questionario:
                pergunta = pergunta_questionario.pergunta

                # Tratamento para perguntas de múltipla escolha (questionário padrão)
                if pergunta.tipo == "multipla_escolha":
                    resultado = avaliacao.calcular_media_pergunta(pergunta)
                    if resultado:
                        contagens = resultado["contagens"]
                        writer.writerow(
                            [
                                sanitize_csv_value(disciplina),
                                sanitize_csv_value(professor),
                                sanitize_csv_value(turma),
                                sanitize_csv_value(periodo),
                                sanitize_csv_value(ciclo),
                                total_alunos,
                                respondentes,
                                taxa_resposta,
                                media_geral,
                                classificacao_geral,
                                sanitize_csv_value(pergunta.enunciado),
                                "Múltipla Escolha",
                                resultado["media"],
                                sanitize_csv_value(resultado.get("moda", "N/A")),
                                avaliacao.get_classificacao_media(resultado["media"]),
                                contagens.get("Não atende", 0),
                                contagens.get("Insuficiente", 0),
                                contagens.get("Regular", 0),
                                contagens.get("Bom", 0),
                                contagens.get("Excelente", 0),
                                resultado["total_respondentes"],
                                (
                                    comentarios_texto
                                    if pergunta_questionario.ordem_no_questionario == 1
                                    else ""
                                ),
                            ]
                        )
                else:
                    # Tratamento para perguntas numéricas
                    respostas_pergunta = RespostaAvaliacao.objects.filter(
                        avaliacao=avaliacao,
                        pergunta=pergunta,
                        valor_numerico__isnull=False,
                    )

                    stats = calcular_estatisticas_respostas(respostas_pergunta)
                    if stats:
                        writer.writerow(
                            [
                                sanitize_csv_value(disciplina),
                                sanitize_csv_value(professor),
                                sanitize_csv_value(turma),
                                sanitize_csv_value(periodo),
                                sanitize_csv_value(ciclo),
                                total_alunos,
                                respondentes,
                                taxa_resposta,
                                media_geral,
                                classificacao_geral,
                                sanitize_csv_value(pergunta.enunciado),
                                pergunta.get_tipo_display(),
                                round(stats["media"], 2),
                                stats.get("moda", "N/A"),
                                "N/A",
                                "N/A",
                                "N/A",
                                "N/A",
                                "N/A",
                                "N/A",
                                stats["count"],
                                (
                                    comentarios_texto
                                    if pergunta_questionario.ordem_no_questionario == 1
                                    else ""
                                ),
                            ]
                        )

    return response


@login_required
def relatorio_professores(request):
    """
    View para relatório consolidado de professores com métricas de avaliação.
    Apenas coordenadores e admins podem acessar.
    """
    from .services import listar_professores_com_metricas

    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar relatórios.")
        return redirect("listar_avaliacoes")

    # Verificar se é solicitação de exportação CSV
    formato = request.GET.get("formato")

    # Buscar dados para filtros
    ciclos = CicloAvaliacao.objects.all().order_by("-data_inicio")
    cursos = Curso.objects.all().order_by("curso_nome")

    # Capturar filtros
    ciclo_id = request.GET.get("ciclo")
    curso_id = request.GET.get("curso")
    busca = request.GET.get("busca", "").strip()

    ciclo_selecionado = None
    curso_selecionado = None

    if ciclo_id:
        try:
            ciclo_selecionado = CicloAvaliacao.objects.get(id=ciclo_id)
        except CicloAvaliacao.DoesNotExist:
            pass

    if curso_id:
        try:
            curso_selecionado = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            pass

    # Buscar professores com métricas aplicando filtros
    professores_metricas = listar_professores_com_metricas(
        ciclo=ciclo_selecionado, curso=curso_selecionado, busca=busca
    )

    # Se for exportação CSV, gerar e retornar
    if formato == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        nome_arquivo = "relatorio_professores"
        if ciclo_selecionado:
            nome_arquivo += f"_ciclo_{ciclo_selecionado.nome.replace(' ', '_')}"
        if curso_selecionado:
            nome_arquivo += f"_curso_{curso_selecionado.curso_nome.replace(' ', '_')}"
        nome_arquivo += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'

        writer = csv.writer(response)
        response.write("\ufeff")  # BOM para UTF-8

        # Cabeçalhos
        writer.writerow(
            [
                "Professor",
                "Matrícula",
                "Curso(s)",
                "Avaliações Respondidas",
                "Total Respondentes",
                "Total Alunos Aptos",
                "Taxa de Resposta (%)",
                "Média no Ciclo",
                "Classificação no Ciclo",
                "Média Histórica",
                "Classificação Histórica",
                "Total Ciclos Históricos",
                "Total Avaliações Históricas",
            ]
        )

        # Dados
        for item in professores_metricas:
            professor = item["professor"]
            writer.writerow(
                [
                    sanitize_csv_value(professor.user.get_full_name()),
                    sanitize_csv_value(professor.matricula),
                    sanitize_csv_value(item["cursos"]),
                    item["avaliacoes_respondidas"],
                    item["total_respondentes"],
                    item["total_alunos_aptos"],
                    item["taxa_resposta"],
                    item["media_ciclo"] if item["media_ciclo"] else "N/A",
                    item["classificacao_ciclo"],
                    item["media_historica"] if item["media_historica"] else "N/A",
                    item["classificacao_historica"],
                    item["total_ciclos"],
                    item["total_avaliacoes_historicas"],
                ]
            )

        return response

    # Paginação
    paginator = Paginator(professores_metricas, 20)  # 20 por página
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "ciclos": ciclos,
        "cursos": cursos,
        "ciclo_selecionado": ciclo_selecionado,
        "curso_selecionado": curso_selecionado,
        "busca": busca,
        "total_professores": len(professores_metricas),
    }

    return render(request, "avaliacoes/relatorio_professores.html", context)


@login_required
def detalhe_professor_relatorio(request, professor_id):
    """
    View para detalhes de um professor específico com histórico por ciclo.
    Inclui paginação de ciclos (5 por página) e cache para melhor performance.
    Apenas coordenadores e admins podem acessar.
    """
    from .services import obter_historico_professor_por_ciclo_cached
    from .models import CicloAvaliacao, AvaliacaoDocente
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar este relatório.")
        return redirect("listar_avaliacoes")

    # Buscar professor
    professor = get_object_or_404(
        PerfilProfessor.objects.select_related("user"), id=professor_id
    )

    # Buscar ciclos do professor (ordenados do mais recente)
    ciclos_queryset = (
        CicloAvaliacao.objects.filter(avaliacoes__professor=professor, ativo=True)
        .distinct()
        .order_by("-data_inicio")
    )

    # Paginar: 5 ciclos por vez
    paginator = Paginator(ciclos_queryset, 5)
    page_number = request.GET.get("page", 1)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    # Processar apenas os ciclos da página atual (com cache)
    ciclos = []
    for ciclo in page_obj:
        historico = obter_historico_professor_por_ciclo_cached(professor, ciclo)
        if historico and historico.get("avaliacoes"):
            ciclos.append(historico)

    # Calcular estatísticas gerais (todos os ciclos)
    todas_avaliacoes = AvaliacaoDocente.objects.filter(
        professor=professor, ativo=True
    ).select_related("disciplina", "turma", "ciclo")

    total_avaliacoes = todas_avaliacoes.count()
    avaliacoes_com_resposta = (
        todas_avaliacoes.filter(respostas__isnull=False).distinct().count()
    )

    # Calcular média geral
    medias = []
    for avaliacao in todas_avaliacoes:
        resultado = avaliacao.calcular_media_geral_questionario_padrao()
        if resultado and resultado.get("media_geral") is not None:
            medias.append(resultado["media_geral"])

    media_geral = None
    classificacao_geral = "Sem dados"
    if medias:
        media_geral = sum(medias) / len(medias)
        classificacao_geral = AvaliacaoDocente.get_classificacao_media(
            None, media_geral
        )

    estatisticas_gerais = {
        "total_ciclos": ciclos_queryset.count(),
        "total_avaliacoes": total_avaliacoes,
        "avaliacoes_respondidas": avaliacoes_com_resposta,
        "media_geral": media_geral,
        "classificacao_geral": classificacao_geral,
    }

    context = {
        "professor": professor,
        "ciclos": ciclos,
        "estatisticas_gerais": estatisticas_gerais,
        "page_obj": page_obj,
    }

    return render(request, "avaliacoes/detalhe_professor_relatorio.html", context)


@login_required
def detalhe_calculo_avaliacao(request, avaliacao_id):
    """
    View para mostrar detalhes completos do cálculo de uma avaliação específica.
    Mostra passo a passo como a média é calculada, respondentes, taxa de resposta, etc.
    Ideal para auditoria e transparência dos cálculos.
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(
            request, "Você não tem permissão para acessar esta funcionalidade."
        )
        return redirect("listar_avaliacoes")

    # Buscar avaliação
    avaliacao = get_object_or_404(
        AvaliacaoDocente.objects.select_related(
            "professor__user", "disciplina", "turma", "ciclo"
        ).prefetch_related("respostas__aluno__user", "respostas__pergunta"),
        id=avaliacao_id,
    )

    # Calcular respondentes
    respostas_com_aluno = (
        avaliacao.respostas.filter(aluno__isnull=False).values("aluno").distinct()
    )

    respostas_sem_aluno = (
        avaliacao.respostas.filter(aluno__isnull=True)
        .exclude(session_key="")
        .values("session_key")
        .distinct()
    )

    total_respondentes = respostas_com_aluno.count() + respostas_sem_aluno.count()

    # Alunos aptos
    alunos_aptos = avaliacao.alunos_aptos()
    total_alunos_aptos = len(alunos_aptos)

    # Taxa de resposta
    taxa_resposta = (
        (total_respondentes / total_alunos_aptos * 100) if total_alunos_aptos > 0 else 0
    )

    # Calcular média geral
    resultado = avaliacao.calcular_media_geral_questionario_padrao()

    if not resultado:
        messages.warning(
            request,
            "Esta avaliação não possui respostas de múltipla escolha para calcular a média.",
        )
        return redirect("relatorio_avaliacoes")

    # Processar detalhes das perguntas
    detalhes_perguntas = []
    for pergunta_id, dados in resultado["detalhes_por_pergunta"].items():
        # Calcular soma ponderada para mostrar no exemplo
        soma_ponderada = sum(
            dados["contagens"][k] * v for k, v in avaliacao.OPCOES_PESOS.items()
        )

        detalhes_perguntas.append(
            {
                "id": pergunta_id,
                "enunciado": dados["enunciado"],
                "media": dados["media"],
                "total_respondentes": dados["total_respondentes"],
                "moda": dados["moda"],
                "contagens": {
                    "nao_atende": dados["contagens"]["Não atende"],
                    "insuficiente": dados["contagens"]["Insuficiente"],
                    "regular": dados["contagens"]["Regular"],
                    "bom": dados["contagens"]["Bom"],
                    "excelente": dados["contagens"]["Excelente"],
                },
                "soma_ponderada": soma_ponderada,
            }
        )

    # Classificação
    classificacao = avaliacao.get_classificacao_media(resultado["media_geral"])

    # Preparar dados para o template
    dados = {
        "total_respondentes": total_respondentes,
        "total_alunos_aptos": total_alunos_aptos,
        "taxa_resposta": taxa_resposta,
        "media_geral": resultado["media_geral"],
        "classificacao": classificacao,
        "total_perguntas": resultado["total_perguntas"],
        "detalhes_perguntas": detalhes_perguntas,
        "total_respostas": avaliacao.respostas.count(),
        "soma_medias": sum(p["media"] for p in detalhes_perguntas),
    }

    context = {
        "avaliacao": avaliacao,
        "dados": dados,
    }

    return render(request, "avaliacoes/detalhe_calculo_avaliacao.html", context)


# ============ CRUD CATEGORIAS DE PERGUNTA ============


@login_required
def gerenciar_categorias(request):
    """
    View para gerenciar categorias de pergunta
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    if request.method == "GET":
        # Verificar se é uma requisição AJAX (para compatibilidade com código existente)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Listar todas as categorias para AJAX
            categorias = CategoriaPergunta.objects.all().order_by("ordem", "nome")
            categorias_data = []

            for categoria in categorias:
                categorias_data.append(
                    {
                        "id": categoria.id,
                        "nome": categoria.nome,
                        "descricao": categoria.descricao,
                        "ordem": categoria.ordem,
                        "ativo": categoria.ativo,
                        "total_perguntas": categoria.perguntas.count(),
                    }
                )

            return JsonResponse({"categorias": categorias_data})
        else:
            # Renderizar template normal
            categorias = CategoriaPergunta.objects.all().order_by("ordem", "nome")
            form = CategoriaPerguntaForm()

            context = {
                "categorias": categorias,
                "form": form,
            }

            return render(request, "gerenciar_categorias.html", context)

    elif request.method == "POST":
        # Verificar se é uma requisição AJAX
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Criar nova categoria via AJAX
            form = CategoriaPerguntaForm(request.POST)
            if form.is_valid():
                nome = form.cleaned_data.get("nome")

                # Verificar se existe categoria inativa com este nome
                categoria_inativa = CategoriaPergunta.all_objects.filter(
                    nome__iexact=nome, ativo=False
                ).first()

                if categoria_inativa:
                    # Reativar categoria existente ao invés de criar nova
                    categoria_inativa.restore()
                    # Atualizar outros campos
                    categoria_inativa.descricao = form.cleaned_data.get("descricao", "")
                    categoria_inativa.ordem = form.cleaned_data.get(
                        "ordem", categoria_inativa.ordem
                    )
                    categoria_inativa.save()

                    messages.success(
                        request,
                        f"Categoria '{categoria_inativa.nome}' foi reativada com sucesso!",
                    )
                    return JsonResponse(
                        {
                            "success": True,
                            "reactivated": True,
                            "categoria": {
                                "id": categoria_inativa.id,
                                "nome": categoria_inativa.nome,
                                "descricao": categoria_inativa.descricao,
                                "ordem": categoria_inativa.ordem,
                                "ativo": categoria_inativa.ativo,
                                "total_perguntas": categoria_inativa.perguntas.count(),
                            },
                        }
                    )
                else:
                    # Criar nova categoria
                    categoria = form.save()
                    messages.success(
                        request, f"Categoria '{categoria.nome}' criada com sucesso!"
                    )
                    return JsonResponse(
                        {
                            "success": True,
                            "reactivated": False,
                            "categoria": {
                                "id": categoria.id,
                                "nome": categoria.nome,
                                "descricao": categoria.descricao,
                                "ordem": categoria.ordem,
                                "ativo": categoria.ativo,
                                "total_perguntas": 0,
                            },
                        }
                    )
            else:
                return JsonResponse(
                    {"error": "Dados inválidos", "errors": form.errors}, status=400
                )
        else:
            # Criar nova categoria via formulário normal
            form = CategoriaPerguntaForm(request.POST)
            if form.is_valid():
                try:
                    nome = form.cleaned_data.get("nome")

                    # Verificar se existe categoria inativa com este nome
                    categoria_inativa = CategoriaPergunta.all_objects.filter(
                        nome__iexact=nome, ativo=False
                    ).first()

                    if categoria_inativa:
                        # Reativar categoria existente ao invés de criar nova
                        categoria_inativa.restore()
                        # Atualizar outros campos
                        categoria_inativa.descricao = form.cleaned_data.get(
                            "descricao", ""
                        )
                        categoria_inativa.ordem = form.cleaned_data.get(
                            "ordem", categoria_inativa.ordem
                        )
                        categoria_inativa.save()

                        messages.success(
                            request,
                            f"Categoria '{categoria_inativa.nome}' foi reativada com sucesso!",
                        )
                        return redirect("gerenciar_categorias")
                    else:
                        # Criar nova categoria
                        categoria = form.save()
                        messages.success(
                            request, f"Categoria '{categoria.nome}' criada com sucesso!"
                        )
                        return redirect("gerenciar_categorias")
                except Exception as e:
                    messages.error(request, f"Erro ao criar categoria: {str(e)}")
                    # Se houve erro, renderizar novamente o template com os erros
                    categorias = CategoriaPergunta.objects.all().order_by(
                        "ordem", "nome"
                    )
                    context = {
                        "categorias": categorias,
                        "form": form,
                    }
                    return render(request, "gerenciar_categorias.html", context)
            else:
                # Se houve erro, renderizar novamente o template com os erros
                categorias = CategoriaPergunta.objects.all().order_by("ordem", "nome")
                context = {
                    "categorias": categorias,
                    "form": form,
                }
                return render(request, "gerenciar_categorias.html", context)


@login_required
def categoria_detail(request, categoria_id):
    """
    View para detalhes, edição e exclusão de categoria específica
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        return JsonResponse({"error": "Permissão negada"}, status=403)

    categoria = get_object_or_404(CategoriaPergunta, id=categoria_id)

    if request.method == "GET":
        # Retornar detalhes da categoria
        return JsonResponse(
            {
                "id": categoria.id,
                "nome": categoria.nome,
                "descricao": categoria.descricao,
                "ordem": categoria.ordem,
                "ativo": categoria.ativo,
                "total_perguntas": categoria.perguntas.count(),
            }
        )

    elif request.method == "PUT":
        # Editar categoria
        import json

        data = json.loads(request.body)
        form = CategoriaPerguntaForm(data, instance=categoria)

        if form.is_valid():
            categoria = form.save()
            messages.success(
                request, f"Categoria '{categoria.nome}' atualizada com sucesso!"
            )
            return JsonResponse(
                {
                    "success": True,
                    "categoria": {
                        "id": categoria.id,
                        "nome": categoria.nome,
                        "descricao": categoria.descricao,
                        "ordem": categoria.ordem,
                        "ativo": categoria.ativo,
                        "total_perguntas": categoria.perguntas.count(),
                    },
                }
            )
        else:
            return JsonResponse(
                {"error": "Dados inválidos", "errors": form.errors}, status=400
            )

    elif request.method == "DELETE":
        # Excluir categoria
        total_perguntas = categoria.perguntas.count()

        if total_perguntas > 0:
            return JsonResponse(
                {
                    "error": f"Não é possível excluir a categoria '{categoria.nome}' pois ela possui {total_perguntas} pergunta(s) associada(s)."
                },
                status=400,
            )

        nome_categoria = categoria.nome
        categoria.delete()
        messages.success(request, f"Categoria '{nome_categoria}' excluída com sucesso!")
        return JsonResponse(
            {
                "success": True,
                "message": f"Categoria '{nome_categoria}' excluída com sucesso!",
            }
        )


@login_required
def editar_categoria(request, categoria_id):
    """
    View para editar uma categoria específica
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    categoria = get_object_or_404(CategoriaPergunta, id=categoria_id)

    if request.method == "POST":
        form = CategoriaPerguntaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(
                request, f"Categoria '{categoria.nome}' atualizada com sucesso!"
            )
            return redirect("gerenciar_categorias")
        else:
            messages.error(request, "Erro ao atualizar categoria. Verifique os dados.")

    return redirect("gerenciar_categorias")


@login_required
def editar_categoria_simples(request, categoria_id):
    """
    View para editar uma categoria específica - versão simples sem JavaScript
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    categoria = get_object_or_404(CategoriaPergunta, id=categoria_id)

    if request.method == "POST":
        form = CategoriaPerguntaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(
                request, f"Categoria '{categoria.nome}' atualizada com sucesso!"
            )
            return redirect("gerenciar_categorias")
        else:
            # Se houve erro, renderizar novamente o template com os erros
            categorias = CategoriaPergunta.objects.all().order_by("ordem", "nome")
            context = {
                "categorias": categorias,
                "form": form,
                "editing": True,
                "categoria": categoria,
            }
            return render(request, "gerenciar_categorias.html", context)
    else:
        form = CategoriaPerguntaForm(instance=categoria)

    # Buscar todas as categorias para exibir na listagem
    categorias = CategoriaPergunta.objects.all().order_by("ordem", "nome")

    context = {
        "form": form,
        "categorias": categorias,
        "editing": True,
        "categoria": categoria,
    }

    return render(request, "gerenciar_categorias.html", context)


@login_required
def excluir_categoria(request, categoria_id):
    """
    View para excluir uma categoria específica
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"error": "Permissão negada"}, status=403)
        else:
            messages.error(request, "Você não tem permissão para acessar esta página.")
            return redirect("inicio")

    categoria = get_object_or_404(CategoriaPergunta, id=categoria_id)

    if request.method == "POST":
        # Verificar se a categoria tem perguntas associadas
        total_perguntas = categoria.perguntas.count()

        if total_perguntas > 0:
            error_msg = f"Não é possível excluir a categoria '{categoria.nome}' pois ela possui {total_perguntas} pergunta(s) associada(s)."

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "error": error_msg},
                    status=400,
                )
            else:
                messages.error(request, error_msg)
                return redirect("gerenciar_categorias")

        nome_categoria = categoria.nome
        categoria.delete()

        success_msg = f"Categoria '{nome_categoria}' excluída com sucesso!"

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": True,
                    "message": success_msg,
                }
            )
        else:
            messages.success(request, success_msg)
            return redirect("gerenciar_categorias")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"error": "Método não permitido"}, status=405)
    else:
        return redirect("gerenciar_categorias")


@login_required
def minhas_avaliacoes(request):
    """
    View para listar as avaliações anteriores do aluno
    Apenas alunos podem acessar suas próprias avaliações das turmas em que estão matriculados
    """
    if not hasattr(request.user, "perfil_aluno"):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Buscar turmas em que o aluno está ou esteve matriculado
    turmas_aluno = request.user.perfil_aluno.matriculas.values_list(
        "turma_id", flat=True
    )

    # Buscar avaliações que o aluno já respondeu das suas turmas
    avaliacoes_respondidas = (
        AvaliacaoDocente.objects.filter(
            respostas__aluno=request.user.perfil_aluno,
            turma_id__in=turmas_aluno,  # Apenas das turmas em que o aluno está/esteve matriculado
        )
        .distinct()
        .order_by("-data_criacao")
    )

    context = {
        "avaliacoes": avaliacoes_respondidas,
        "titulo": "Minhas Avaliações",
    }
    return render(request, "avaliacoes/minhas_avaliacoes.html", context)


# ============ CRUD CICLOS DE AVALIAÇÃO ============


@login_required
def gerenciar_ciclos(request):
    """
    View para gerenciar ciclos de avaliação
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Capturar filtros da requisição
    filtro_busca = request.GET.get("busca", "")
    filtro_periodo = request.GET.get("periodo", "")
    filtro_status = request.GET.get("status", "")

    if request.method == "POST":
        form = CicloAvaliacaoForm(request.POST)
        if form.is_valid():
            ciclo = form.save(commit=False)
            ciclo.criado_por = request.user
            try:
                ciclo.save()
                # Salvar as turmas (ManyToManyField)
                form.save_m2m()
                messages.success(request, f"Ciclo '{ciclo.nome}' criado com sucesso!")
                return redirect("gerenciar_ciclos")
            except Exception as e:
                messages.error(
                    request,
                    f"Não foi possível criar o ciclo: {str(e)}",
                )
        else:
            # Se houve erro, renderizar novamente o template com os erros
            ciclos = CicloAvaliacao.objects.all().order_by("-data_inicio")
            context = {
                "ciclos": ciclos,
                "form": form,
            }
            return render(request, "gerenciar_ciclos.html", context)
    else:
        form = CicloAvaliacaoForm()

    # Lista todos os ciclos ativos (não deletados) com filtros
    ciclos_list = CicloAvaliacao.objects.all()

    # Aplicar filtros
    if filtro_busca:
        ciclos_list = ciclos_list.filter(nome__icontains=filtro_busca)

    if filtro_periodo:
        ciclos_list = ciclos_list.filter(periodo_letivo_id=filtro_periodo)

    # Filtrar por status (aplicado após a query, pois 'status' é uma propriedade calculada)
    if filtro_status:
        from django.utils import timezone

        now = timezone.now()

        if filtro_status == "agendado":
            ciclos_list = ciclos_list.filter(data_inicio__gt=now, encerrado=False)
        elif filtro_status == "em_andamento":
            ciclos_list = ciclos_list.filter(
                data_inicio__lte=now, data_fim__gte=now, encerrado=False
            )
        elif filtro_status == "finalizado":
            ciclos_list = ciclos_list.filter(data_fim__lt=now, encerrado=False)
        elif filtro_status == "encerrado":
            ciclos_list = ciclos_list.filter(encerrado=True)

    ciclos_list = ciclos_list.order_by("-data_inicio")

    # Paginação - 15 ciclos por página
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(ciclos_list, 15)
    page_number = request.GET.get("page", 1)

    try:
        ciclos = paginator.page(page_number)
    except PageNotAnInteger:
        ciclos = paginator.page(1)
    except EmptyPage:
        ciclos = paginator.page(paginator.num_pages)

    # Buscar periodos para o filtro
    periodos = PeriodoLetivo.objects.all().order_by("nome")

    context = {
        "form": form,
        "ciclos": ciclos,
        "periodos": periodos,
        "filtro_busca": filtro_busca,
        "filtro_periodo": filtro_periodo,
        "filtro_status": filtro_status,
    }

    return render(request, "gerenciar_ciclos.html", context)


@login_required
def editar_ciclo_simples(request, ciclo_id):
    """
    View para editar um ciclo de avaliação - versão simples sem JavaScript
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(
            request, "Você não tem permissão para editar ciclos de avaliação."
        )
        return redirect("inicio")

    # Permite editar ciclos mesmo que encerrados ou deletados (para recuperação)
    ciclo = get_object_or_404(CicloAvaliacao.all_objects, id=ciclo_id)

    if request.method == "POST":
        form = CicloAvaliacaoForm(request.POST, instance=ciclo)
        if form.is_valid():
            try:
                # Salvar o ciclo
                ciclo_atualizado = form.save(commit=False)

                # Se o ciclo estava encerrado e as datas foram alteradas,
                # verificar se deve reativar automaticamente
                from django.utils import timezone

                now = timezone.now()

                if ciclo.encerrado:
                    # Verifica se as novas datas indicam que o ciclo deveria estar ativo
                    data_inicio = ciclo_atualizado.data_inicio
                    data_fim = ciclo_atualizado.data_fim

                    # Se a nova data de fim é no futuro, reativar o ciclo
                    if data_fim > now:
                        ciclo_atualizado.encerrado = False
                        ciclo_atualizado.data_encerramento = None
                        messages.info(
                            request,
                            f"Ciclo '{ciclo.nome}' foi reativado automaticamente pois a data de fim foi alterada para o futuro.",
                        )

                ciclo_atualizado.save()
                form.save_m2m()  # Salvar relações ManyToMany (turmas)

                messages.success(
                    request, f"Ciclo '{ciclo.nome}' atualizado com sucesso!"
                )
                return redirect("gerenciar_ciclos")
            except Exception as e:
                messages.error(request, f"Não foi possível atualizar o ciclo: {str(e)}")
        else:
            display_form_errors(request, form)
    else:
        form = CicloAvaliacaoForm(instance=ciclo)

    context = {"form": form, "ciclo": ciclo, "editing": True}
    return render(request, "gerenciar_ciclos.html", context)


@login_required
def excluir_ciclo(request, ciclo_id):
    """
    View para excluir um ciclo de avaliação (soft delete)
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(
            request, "Você não tem permissão para excluir ciclos de avaliação."
        )
        return redirect("inicio")

    # Buscar apenas ciclos ativos (não deletados)
    ciclo = get_object_or_404(CicloAvaliacao.objects, id=ciclo_id)

    if request.method == "POST":
        nome_ciclo = ciclo.nome

        # Usar soft delete (marca ativo=False)
        # O signal ignorará ciclos inativos, evitando duplicações
        ciclo.soft_delete()

        messages.success(
            request,
            f"Ciclo '{nome_ciclo}' movido para a lixeira. "
            f"Os dados permanecem no sistema e podem ser recuperados se necessário.",
        )
        # Limpa a sessão de confirmação (se houver)
        request.session.pop("confirm_delete_ciclo_id", None)
        return redirect("gerenciar_ciclos")

    return redirect("gerenciar_ciclos")


@login_required
def encerrar_ciclo(request, ciclo_id):
    """Encerra manualmente um ciclo impedindo novas respostas."""
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para encerrar ciclos.")
        return redirect("inicio")

    # Buscar ciclo (apenas ativos, não deletados)
    ciclo = get_object_or_404(CicloAvaliacao.objects, id=ciclo_id)

    if request.method == "POST":
        if ciclo.encerrado:
            messages.info(request, f"Ciclo '{ciclo.nome}' já está encerrado.")
        else:
            from django.utils import timezone

            ciclo.encerrado = True
            ciclo.data_encerramento = timezone.now()
            ciclo.save(update_fields=["encerrado", "data_encerramento"])
            messages.success(request, f"Ciclo '{ciclo.nome}' encerrado com sucesso.")
        return redirect("detalhe_ciclo_avaliacao", ciclo_id=ciclo.id)

    messages.error(request, "Método inválido.")
    return redirect("detalhe_ciclo_avaliacao", ciclo_id=ciclo.id)


@login_required
def reativar_ciclo(request, ciclo_id):
    """Reativa um ciclo que foi encerrado manualmente."""
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para reativar ciclos.")
        return redirect("inicio")

    # Buscar ciclo (apenas ativos, não deletados)
    ciclo = get_object_or_404(CicloAvaliacao.objects, id=ciclo_id)

    if request.method == "POST":
        if not ciclo.encerrado:
            messages.info(request, f"Ciclo '{ciclo.nome}' já está ativo.")
        else:
            from django.utils import timezone

            now = timezone.now()

            # Verificar se as datas permitem reativação
            if ciclo.data_fim < now:
                messages.warning(
                    request,
                    f"Atenção: A data de fim do ciclo '{ciclo.nome}' ({ciclo.data_fim.strftime('%d/%m/%Y %H:%M')}) "
                    f"já passou. O ciclo será marcado como 'finalizado'. "
                    f"Edite as datas se desejar torná-lo 'em andamento'.",
                )

            ciclo.encerrado = False
            ciclo.data_encerramento = None
            ciclo.save(update_fields=["encerrado", "data_encerramento"])
            messages.success(
                request,
                f"Ciclo '{ciclo.nome}' reativado com sucesso! Status atual: {ciclo.status}.",
            )
        return redirect("detalhe_ciclo_avaliacao", ciclo_id=ciclo.id)

    messages.error(request, "Método inválido.")
    return redirect("detalhe_ciclo_avaliacao", ciclo_id=ciclo.id)


@login_required
def encerrar_avaliacao(request, avaliacao_id):
    """Encerra manualmente uma avaliação (marca como finalizada)."""
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para encerrar avaliações.")
        return redirect("inicio")
    avaliacao = get_object_or_404(AvaliacaoDocente, id=avaliacao_id)
    if request.method == "POST":
        if avaliacao.status == "finalizada":
            messages.info(
                request,
                f"Avaliação já finalizada: {avaliacao.disciplina.disciplina_nome}.",
            )
        else:
            avaliacao.status = "finalizada"
            avaliacao.save(update_fields=["status", "data_atualizacao"])
            messages.success(
                request,
                f"Avaliação de {avaliacao.professor.user.get_full_name()} / {avaliacao.disciplina.disciplina_nome} finalizada.",
            )
        return redirect("listar_avaliacoes")
    messages.error(request, "Método inválido.")
    return redirect("listar_avaliacoes")


# ============ FUNÇÕES DE EXPORTAÇÃO CSV PARA ADMIN HUB ============


@login_required
def exportar_usuarios_csv(request):
    """
    Exporta lista de usuários em formato CSV
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Preparar resposta CSV (função consolidada)
    response, writer = preparar_response_csv("usuarios")

    # Cabeçalhos
    writer.writerow(
        [
            "ID",
            "Nome Completo",
            "Email",
            "Username",
            "Role Principal",
            "É Professor",
            "É Aluno",
            "Data de Cadastro",
            "Último Login",
            "Ativo",
        ]
    )

    # Buscar usuários com prefetch das roles
    usuarios = (
        User.objects.select_related()
        .prefetch_related("perfil_professor", "perfil_aluno")
        .order_by("date_joined")
    )

    for usuario in usuarios:
        # Determinar role principal
        role_principal = "N/A"
        if hasattr(usuario, "perfil_professor") and usuario.perfil_professor:
            role_principal = "Professor"
        elif hasattr(usuario, "perfil_aluno") and usuario.perfil_aluno:
            role_principal = "Aluno"

        # Verificar se é admin ou coordenador usando has_role (já importado no topo)
        if has_role(usuario, "admin"):
            role_principal = "Admin"
        elif has_role(usuario, "coordenador"):
            role_principal = "Coordenador"

        writer.writerow(
            [
                usuario.id,
                sanitize_csv_value(
                    usuario.get_full_name()
                    or f"{usuario.first_name} {usuario.last_name}".strip()
                ),
                sanitize_csv_value(usuario.email),
                sanitize_csv_value(usuario.username),
                role_principal,
                (
                    "Sim"
                    if hasattr(usuario, "perfil_professor") and usuario.perfil_professor
                    else "Não"
                ),
                (
                    "Sim"
                    if hasattr(usuario, "perfil_aluno") and usuario.perfil_aluno
                    else "Não"
                ),
                (
                    usuario.date_joined.strftime("%d/%m/%Y %H:%M")
                    if usuario.date_joined
                    else ""
                ),
                (
                    usuario.last_login.strftime("%d/%m/%Y %H:%M")
                    if usuario.last_login
                    else "Nunca"
                ),
                "Sim" if usuario.is_active else "Não",
            ]
        )

    return response


@login_required
def exportar_cursos_csv(request):
    """
    Exporta lista de cursos em formato CSV
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Preparar resposta CSV (função consolidada)
    response, writer = preparar_response_csv("cursos")

    # Cabeçalhos
    writer.writerow(
        [
            "ID",
            "Nome do Curso",
            "Sigla",
            "Coordenador",
            "Email Coordenador",
            "Total de Disciplinas",
            "Total de Turmas",
            "Ativo",
            "Data de Criação",
        ]
    )

    # Buscar cursos com related data
    cursos = (
        Curso.objects.select_related("coordenador_curso__user")
        .prefetch_related("disciplinas", "disciplinas__turmas")
        .order_by("curso_nome")
    )

    for curso in cursos:
        # Contar disciplinas e turmas
        total_disciplinas = curso.disciplinas.count()
        total_turmas = sum(
            disciplina.turmas.count() for disciplina in curso.disciplinas.all()
        )

        writer.writerow(
            [
                curso.id,
                sanitize_csv_value(curso.curso_nome),
                sanitize_csv_value(curso.curso_sigla),
                sanitize_csv_value(
                    curso.coordenador_curso.user.get_full_name()
                    if curso.coordenador_curso
                    else "Não definido"
                ),
                sanitize_csv_value(
                    curso.coordenador_curso.user.email
                    if curso.coordenador_curso
                    else ""
                ),
                total_disciplinas,
                total_turmas,
                "Sim" if curso.ativo else "Não",
                (
                    curso.data_criacao.strftime("%d/%m/%Y %H:%M")
                    if curso.data_criacao
                    else ""
                ),
            ]
        )

    return response


@login_required
def exportar_disciplinas_csv(request):
    """
    Exporta lista de disciplinas em formato CSV
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Preparar resposta CSV (função consolidada)
    response, writer = preparar_response_csv("disciplinas")

    # Cabeçalhos
    writer.writerow(
        [
            "ID",
            "Nome da Disciplina",
            "Sigla",
            "Curso",
            "Tipo",
            "Período Letivo",
            "Professor Responsável",
            "Total de Turmas",
            "Ativo",
            "Data de Criação",
        ]
    )

    # Buscar disciplinas com related data
    disciplinas = (
        Disciplina.objects.select_related("curso", "professor__user", "periodo_letivo")
        .prefetch_related("turmas")
        .order_by("curso__curso_nome", "disciplina_nome")
    )

    for disciplina in disciplinas:
        # Contar turmas
        total_turmas = disciplina.turmas.count()

        writer.writerow(
            [
                disciplina.id,
                sanitize_csv_value(disciplina.disciplina_nome),
                sanitize_csv_value(disciplina.disciplina_sigla),
                sanitize_csv_value(disciplina.curso.curso_nome),
                disciplina.disciplina_tipo,
                sanitize_csv_value(disciplina.periodo_letivo.nome),
                sanitize_csv_value(
                    disciplina.professor.user.get_full_name()
                    if disciplina.professor
                    else "Não definido"
                ),
                total_turmas,
                "Sim" if disciplina.ativo else "Não",
                (
                    disciplina.data_criacao.strftime("%d/%m/%Y %H:%M")
                    if disciplina.data_criacao
                    else ""
                ),
            ]
        )

    return response


@login_required
def exportar_turmas_csv(request):
    """
    Exporta lista de turmas em formato CSV
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Preparar resposta CSV (função consolidada)
    response, writer = preparar_response_csv("turmas")

    # Cabeçalhos
    writer.writerow(
        [
            "ID",
            "Código da Turma",
            "Disciplina",
            "Curso",
            "Professor",
            "Email Professor",
            "Período Letivo",
            "Total de Alunos",
            "Alunos Ativos",
            "Ativa",
        ]
    )

    # Buscar turmas com related data
    turmas = (
        Turma.objects.select_related(
            "disciplina__curso",
            "disciplina__professor__user",
            "disciplina__periodo_letivo",
        )
        .prefetch_related("matriculas")
        .order_by(
            "disciplina__periodo_letivo__nome",
            "disciplina__curso__curso_nome",
            "codigo_turma",
        )
    )

    for turma in turmas:
        # Contar alunos
        total_alunos = turma.matriculas.count()
        alunos_ativos = turma.matriculas.filter(status="ativa").count()

        writer.writerow(
            [
                turma.id,
                sanitize_csv_value(turma.codigo_turma),
                sanitize_csv_value(turma.disciplina.disciplina_nome),
                sanitize_csv_value(turma.disciplina.curso.curso_nome),
                sanitize_csv_value(
                    turma.disciplina.professor.user.get_full_name()
                    if turma.disciplina.professor
                    else "Não definido"
                ),
                sanitize_csv_value(
                    turma.disciplina.professor.user.email
                    if turma.disciplina.professor
                    else ""
                ),
                sanitize_csv_value(turma.disciplina.periodo_letivo.nome),
                total_alunos,
                alunos_ativos,
                (
                    "Ativa" if turma.status == "ativa" else "Finalizada"
                ),  # Corrigido: era turma.ativa
            ]
        )

    return response


@login_required
def exportar_periodos_csv(request):
    """
    Exporta lista de períodos letivos em formato CSV
    """
    if not check_user_permission(request.user, ["coordenador", "admin"]):
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("inicio")

    # Preparar resposta CSV (função consolidada)
    response, writer = preparar_response_csv("periodos_letivos")

    # Cabeçalhos
    writer.writerow(
        [
            "ID",
            "Nome do Período",
            "Ano",
            "Semestre",
            "Total de Disciplinas",
            "Total de Turmas",
            "Total de Ciclos",
            "Total de Avaliações",
        ]
    )

    # Buscar períodos com related data
    periodos = PeriodoLetivo.objects.prefetch_related(
        "disciplinas", "disciplinas__turmas", "ciclos_avaliacao"
    ).order_by("-ano", "-semestre")

    for periodo in periodos:
        # Contar disciplinas, turmas, ciclos e avaliações
        total_disciplinas = periodo.disciplinas.count()
        total_turmas = sum(
            disciplina.turmas.count() for disciplina in periodo.disciplinas.all()
        )
        total_ciclos = periodo.ciclos_avaliacao.count()
        total_avaliacoes = sum(
            ciclo.avaliacoes.count() for ciclo in periodo.ciclos_avaliacao.all()
        )

        writer.writerow(
            [
                periodo.id,
                sanitize_csv_value(periodo.nome),
                periodo.ano,
                periodo.semestre,
                total_disciplinas,
                total_turmas,
                total_ciclos,
                total_avaliacoes,
            ]
        )

    return response
