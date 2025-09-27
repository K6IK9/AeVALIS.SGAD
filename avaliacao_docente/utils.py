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

from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from decouple import config

def _send_email_smtp(subject, html_message, recipient_list):
    """Função interna para enviar e-mail via SMTP."""
    plain_message = "Este e-mail contém conteúdo HTML. Por favor, use um cliente de e-mail compatível."
    from_email = config('DEFAULT_FROM_EMAIL', default='')
    django_send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message, fail_silently=False)

def _send_email_sendgrid_api(subject, html_message, recipient_list):
    """Função interna para enviar e-mail via API do SendGrid."""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    message = Mail(
        from_email=config('DEFAULT_FROM_EMAIL', default=''),
        to_emails=recipient_list,
        subject=subject,
        html_content=html_message
    )
    try:
        api_key = config('SENDGRID_API_KEY', default=None)
        if not api_key:
            raise Exception("SENDGRID_API_KEY não configurada nas variáveis de ambiente.")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        if response.status_code >= 300:
            raise Exception(f"Erro da API SendGrid: {response.status_code} {response.body}")
    except Exception as e:
        raise e

def send_generic_email(subject, html_message, recipient_list):
    """Verifica a configuração e envia o e-mail pelo método escolhido."""
    from .models import ConfiguracaoSite
    config_model = ConfiguracaoSite.obter_config()

    if config_model.metodo_envio_email == 'api':
        _send_email_sendgrid_api(subject, html_message, recipient_list)
    else:
        _send_email_smtp(subject, html_message, recipient_list)

def enviar_email_notificacao_avaliacao(aluno, avaliacao, request=None):
    """
    Prepara e envia um e-mail de notificação de avaliação usando o método genérico.
    """
    if not aluno.email:
        print(f"AVISO: Aluno {aluno.username} não possui e-mail cadastrado. Notificação pulada.")
        return

    subject = "Nova Avaliação Docente Disponível"
    
    if request:
        link_avaliacao = request.build_absolute_uri(reverse('responder_avaliacao', args=[avaliacao.id]))
    else:
        domain = config('SITE_DOMAIN', default='localhost:8000')
        link_avaliacao = f"http://{domain}{reverse('responder_avaliacao', args=[avaliacao.id])}"

    context = {
        'nome_aluno': aluno.first_name or aluno.username,
        'disciplina': avaliacao.turma.disciplina.disciplina_nome,
        'professor': avaliacao.professor.user.get_full_name(),
        'link_avaliacao': link_avaliacao,
    }

    html_message = render_to_string('emails/notificacao_avaliacao.html', context)
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


