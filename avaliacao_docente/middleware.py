from django.contrib import messages


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
