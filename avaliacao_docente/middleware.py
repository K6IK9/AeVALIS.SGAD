from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class ClearMessageMiddleware:
    """
    Middleware que consome e limpa todas as mensagens pendentes
    no início de cada requisição para evitar que mensagens
    apareçam em páginas onde não deveriam.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Consome e limpa mensagens pendentes
        list(messages.get_messages(request))

        response = self.get_response(request)
        return response


class SocialAuthExceptionMiddleware:
    """
    Middleware para capturar exceções do social auth e fornecer
    mensagens amigáveis aos usuários.

    NOTA: Este middleware é um fallback. A função auto_login_existing_user
    no pipeline deve prevenir a maioria dos casos de AuthAlreadyAssociated.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Trata exceções específicas do social auth"""
        import logging

        logger = logging.getLogger(__name__)

        try:
            from social_core.exceptions import AuthAlreadyAssociated
            from social_django.models import UserSocialAuth
            from django.contrib.auth import login

            if isinstance(exception, AuthAlreadyAssociated):
                logger.warning(
                    f"AuthAlreadyAssociated no middleware (fallback) - "
                    f"User: {request.user.username if request.user.is_authenticated else 'Anônimo'}"
                )

                # Tentar recuperar informações da sessão
                partial_pipeline = request.session.get("partial_pipeline", {})
                uid = partial_pipeline.get("kwargs", {}).get("uid")

                if uid:
                    try:
                        # Buscar a conta SUAP vinculada
                        social_user = UserSocialAuth.objects.select_related("user").get(
                            provider="suap", uid=uid
                        )

                        # Se não está autenticado, fazer login automático
                        if not request.user.is_authenticated:
                            logger.info(
                                f"Fazendo login automático para {social_user.user.username}"
                            )
                            login(request, social_user.user, backend="suap")

                            # Limpar pipeline parcial
                            if "partial_pipeline" in request.session:
                                del request.session["partial_pipeline"]

                            messages.success(
                                request,
                                f"✅ Bem-vindo de volta, {social_user.user.first_name}!",
                            )
                            return redirect(reverse("inicio"))

                        # Se já está autenticado com o mesmo usuário
                        elif request.user.id == social_user.user.id:
                            logger.info(
                                f"Usuário {request.user.username} já autenticado, redirecionando"
                            )

                            # Limpar pipeline parcial
                            if "partial_pipeline" in request.session:
                                del request.session["partial_pipeline"]

                            messages.info(
                                request,
                                f"✅ Você já está autenticado, {request.user.first_name}!",
                            )
                            return redirect(reverse("inicio"))

                        # Conflito real: tentando vincular a outro usuário
                        else:
                            logger.error(
                                f"Conflito de contas - Autenticado: {request.user.username}, "
                                f"SUAP pertence a: {social_user.user.username}"
                            )

                            # Limpar pipeline parcial
                            if "partial_pipeline" in request.session:
                                del request.session["partial_pipeline"]

                            messages.error(
                                request,
                                f"❌ Esta conta SUAP está vinculada a outro usuário. "
                                f"Você está autenticado como '{request.user.username}', "
                                f"mas esta conta SUAP pertence a '{social_user.user.username}'. "
                                "Faça logout primeiro se quiser trocar de conta.",
                            )
                            return redirect(reverse("login"))

                    except UserSocialAuth.DoesNotExist:
                        logger.error(
                            f"Conta SUAP com UID {uid} não encontrada (inconsistência)"
                        )

                # Limpar pipeline parcial em caso de fallback
                if "partial_pipeline" in request.session:
                    del request.session["partial_pipeline"]

                # Mensagem genérica se nada funcionou
                messages.error(
                    request,
                    "❌ Erro ao autenticar com SUAP. "
                    "Tente fazer logout e login novamente. "
                    "Se o problema persistir, entre em contato com o suporte.",
                )
                return redirect(reverse("login"))

        except ImportError:
            pass

        return None
