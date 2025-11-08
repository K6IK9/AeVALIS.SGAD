from rolepermissions.checkers import has_role


def check_user_permission(user, roles):
    """
    Verifica se o usuário tem uma das roles especificadas
    """
    if not user.is_authenticated:
        return False

    for role in roles:
        if has_role(user, role):
            return True
    return False


def get_user_role_name(user):
    """
    Retorna o nome da role do usuário
    """
    if has_role(user, "admin"):
        return "Administrador"
    elif has_role(user, "coordenador"):
        return "Coordenador"
    elif has_role(user, "professor"):
        return "Professor"
    elif has_role(user, "aluno"):
        return "Aluno"
    else:
        return "Sem role"


def mark_role_manually_changed(user):
    """
    Marca que a role do usuário foi alterada manualmente,
    evitando que seja sobrescrita no próximo login via SUAP
    """
    try:
        social_auth = user.social_auth.filter(provider="suap").first()
        if social_auth:
            if not isinstance(social_auth.extra_data, dict):
                social_auth.extra_data = {}
            social_auth.extra_data["role_manually_changed"] = True
            social_auth.save()
            return True
    except Exception:
        pass
    return False


def reset_role_manual_flag(user):
    """
    Remove a flag de alteração manual, permitindo que a role
    seja novamente gerenciada automaticamente pelo SUAP
    """
    try:
        social_auth = user.social_auth.filter(provider="suap").first()
        if social_auth and isinstance(social_auth.extra_data, dict):
            social_auth.extra_data.pop("role_manually_changed", None)
            social_auth.save()
            return True
    except Exception:
        pass
    return False


def is_role_manually_changed(user):
    """
    Verifica se a role do usuário foi alterada manualmente
    """
    try:
        social_auth = user.social_auth.filter(provider="suap").first()
        if social_auth and isinstance(social_auth.extra_data, dict):
            return social_auth.extra_data.get("role_manually_changed", False)
    except Exception:
        pass
    return False


def gerenciar_perfil_usuario(usuario, nova_role):
    """
    Função utilitária para gerenciar perfis de usuário baseado na role
    Remove perfis incompatíveis e cria os necessários

    Args:
        usuario: Instância do User
        nova_role: String com a nova role ('admin', 'coordenador', 'professor', 'aluno')

    Returns:
        Lista de mensagens sobre as mudanças realizadas
    """
    from .models import PerfilAluno, PerfilProfessor

    mensagens = []

    if nova_role == "aluno":
        # Se tinha perfil de professor, remover
        if hasattr(usuario, "perfil_professor"):
            usuario.perfil_professor.delete()
            mensagens.append(f"Perfil de professor removido de {usuario.username}")

        # Criar ou manter perfil de aluno
        perfil_aluno, created = PerfilAluno.objects.get_or_create(user=usuario)
        if created:
            mensagens.append(f"Perfil de aluno criado para {usuario.username}")

    elif nova_role in ["professor", "coordenador"]:
        # Se tinha perfil de aluno, remover
        if hasattr(usuario, "perfil_aluno"):
            usuario.perfil_aluno.delete()
            mensagens.append(f"Perfil de aluno removido de {usuario.username}")

        # Criar ou manter perfil de professor
        perfil_professor, created = PerfilProfessor.objects.get_or_create(
            user=usuario, defaults={"registro_academico": usuario.username}
        )
        if created:
            mensagens.append(f"Perfil de professor criado para {usuario.username}")

    elif nova_role == "admin":
        # Admin não deve ter nenhum perfil específico
        # Remover qualquer perfil existente
        if hasattr(usuario, "perfil_professor"):
            usuario.perfil_professor.delete()
            mensagens.append(
                f"Perfil de professor removido de admin {usuario.username}"
            )

        if hasattr(usuario, "perfil_aluno"):
            usuario.perfil_aluno.delete()
            mensagens.append(f"Perfil de aluno removido de admin {usuario.username}")

    return mensagens


def processar_mudanca_role(usuario, nova_role):
    """
    Processa a mudança de role de um usuário.

    Remove todas as roles existentes, atribui a nova role,
    marca como alteração manual e gerencia perfis.

    Args:
        usuario: Instância do User
        nova_role: String com a nova role ('admin', 'coordenador', 'professor', 'aluno')

    Returns:
        Lista de mensagens informativas sobre mudanças de perfil
    """
    from rolepermissions.roles import assign_role, remove_role
    from rolepermissions.checkers import has_role

    # Remove todas as roles existentes
    for role in ["admin", "coordenador", "professor", "aluno"]:
        if has_role(usuario, role):
            remove_role(usuario, role)

    # Atribui a nova role
    assign_role(usuario, nova_role)

    # Marcar que a role foi alterada manualmente
    mark_role_manually_changed(usuario)

    # Gerenciar perfis usando função utilitária
    mensagens_perfil = gerenciar_perfil_usuario(usuario, nova_role)

    return mensagens_perfil


from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from decouple import config


def _send_email_smtp(subject, html_message, recipient_list):
    """Função interna para enviar e-mail via SMTP."""
    plain_message = "Este e-mail contém conteúdo HTML. Por favor, use um cliente de e-mail compatível."
    from_email = config("DEFAULT_FROM_EMAIL", default="")
    django_send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def _send_email_sendgrid_api(subject, html_message, recipient_list):
    """Função interna para enviar e-mail via API do SendGrid."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=config("DEFAULT_FROM_EMAIL", default=""),
        to_emails=recipient_list,
        subject=subject,
        html_content=html_message,
    )
    try:
        api_key = config("SENDGRID_API_KEY", default=None)
        if not api_key:
            raise Exception(
                "SENDGRID_API_KEY não configurada nas variáveis de ambiente."
            )
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        if response.status_code >= 300:
            raise Exception(
                f"Erro da API SendGrid: {response.status_code} {response.body}"
            )
    except Exception as e:
        raise e


def send_generic_email(subject, html_message, recipient_list):
    """Verifica a configuração e envia o e-mail pelo método escolhido."""
    from .models import ConfiguracaoSite

    config_model = ConfiguracaoSite.obter_config()

    if config_model.metodo_envio_email == "api":
        _send_email_sendgrid_api(subject, html_message, recipient_list)
    else:
        _send_email_smtp(subject, html_message, recipient_list)


def enviar_email_notificacao_avaliacao(aluno, avaliacao, request=None):
    """
    Prepara e envia um e-mail de notificação de avaliação usando o método genérico.
    """
    if not aluno.email:
        print(
            f"AVISO: Aluno {aluno.username} não possui e-mail cadastrado. Notificação pulada."
        )
        return

    subject = "Nova Avaliação Docente Disponível"

    if request:
        link_avaliacao = request.build_absolute_uri(
            reverse("responder_avaliacao", args=[avaliacao.id])
        )
    else:
        domain = config("SITE_DOMAIN", default="localhost:8000")
        link_avaliacao = (
            f"http://{domain}{reverse('responder_avaliacao', args=[avaliacao.id])}"
        )

    context = {
        "nome_aluno": aluno.first_name or aluno.username,
        "disciplina": avaliacao.turma.disciplina.disciplina_nome,
        "professor": avaliacao.professor.user.get_full_name(),
        "link_avaliacao": link_avaliacao,
    }

    html_message = render_to_string("emails/notificacao_avaliacao.html", context)
    send_generic_email(subject, html_message, [aluno.email])


from django.utils.log import AdminEmailHandler


class DynamicAdminEmailHandler(AdminEmailHandler):
    """
    Um handler de e-mail que envia erros usando o método configurado (API ou SMTP).
    """

    def send_mail(self, subject, message, *args, **kwargs):
        if settings.DEBUG:
            return
        try:
            from .models import ConfiguracaoSite

            config = ConfiguracaoSite.obter_config()
            email_destino = config.email_notificacao_erros

            if email_destino:
                # Para o handler de erro, a mensagem é o corpo do e-mail
                send_generic_email(subject, message, [email_destino])
        except Exception as e:
            print(f"Erro no DynamicAdminEmailHandler: {e}")


def display_form_errors(request, form):
    """
    Exibe os erros de um formulário Django de forma amigável usando messages.

    Args:
        request: HttpRequest object
        form: Django Form com erros

    Uso:
        if form.is_valid():
            # processar
        else:
            display_form_errors(request, form)
    """
    from django.contrib import messages

    for field, errors in form.errors.items():
        for error in errors:
            if field == "__all__":
                messages.error(request, str(error))
            else:
                field_name = form.fields[field].label if field in form.fields else field
                messages.error(request, f"{field_name}: {error}")


def calcular_estatisticas_respostas(respostas_pergunta):
    """
    Calcula estatísticas (média, moda, contagem) para respostas de avaliação.

    Args:
        respostas_pergunta: QuerySet de RespostaAvaliacao filtrado

    Returns:
        dict com 'media', 'moda' e 'count', ou None se não houver respostas
    """
    from django.db.models import Avg, Count

    if not respostas_pergunta.exists():
        return None

    # Calcular média
    media = respostas_pergunta.aggregate(media=Avg("valor_numerico"))["media"] or 0

    # Calcular moda (valor mais frequente)
    valores = (
        respostas_pergunta.values("valor_numerico")
        .annotate(count=Count("valor_numerico"))
        .order_by("-count")
    )
    moda = valores[0]["valor_numerico"] if valores else 0

    # Contar respostas
    count = respostas_pergunta.count()

    return {"media": media, "moda": moda, "count": count}


def sanitize_csv_value(value):
    """
    Sanitiza valores para prevenir CSV Injection.

    Remove caracteres perigosos que poderiam ser interpretados como fórmulas
    em programas de planilha (Excel, LibreOffice, etc.).

    Args:
        value: Valor a ser sanitizado (string, número ou None)

    Returns:
        Valor sanitizado seguro para CSV

    Referência: https://owasp.org/www-community/attacks/CSV_Injection
    """
    if value is None:
        return ""

    # Converter para string
    value_str = str(value)

    # Caracteres perigosos que iniciam fórmulas
    dangerous_chars = ["=", "+", "-", "@", "\t", "\r"]

    # Se começa com caractere perigoso, adiciona aspas simples no início
    if value_str and value_str[0] in dangerous_chars:
        return "'" + value_str

    return value_str


def preparar_response_csv(nome_base, filtros_aplicados=None):
    """
    Prepara um HttpResponse configurado para exportação CSV.

    Args:
        nome_base: Nome base do arquivo (ex: 'usuarios', 'cursos')
        filtros_aplicados: Dict opcional com filtros aplicados para incluir no nome
                          Ex: {'ciclo': 'Ciclo 2024.1', 'curso': 'Informatica'}

    Returns:
        Tupla (response, writer) onde:
        - response: HttpResponse configurado para CSV
        - writer: csv.writer pronto para uso
    """
    from django.http import HttpResponse
    from datetime import datetime
    import csv

    # Preparar resposta HTTP para CSV
    response = HttpResponse(content_type="text/csv; charset=utf-8")

    # Construir nome do arquivo
    nome_arquivo = nome_base

    if filtros_aplicados:
        for chave, valor in filtros_aplicados.items():
            if valor:
                # Substituir espaços por underscores
                valor_limpo = str(valor).replace(" ", "_")
                nome_arquivo += f"_{chave}_{valor_limpo}"

    # Adicionar timestamp
    nome_arquivo += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Configurar headers
    response["Content-Disposition"] = f'attachment; filename="{nome_arquivo}"'

    # Escrever BOM para UTF-8 (compatibilidade com Excel)
    response.write("\ufeff")

    # Criar e retornar writer
    writer = csv.writer(response)

    return response, writer
