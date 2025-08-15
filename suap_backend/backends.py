# coding: utf-8

from social_core.backends.oauth import BaseOAuth2
import logging
from django.conf import settings


class SuapOAuth2(BaseOAuth2):
    name = "suap"
    AUTHORIZATION_URL = "https://suap.ifmt.edu.br/o/authorize/"
    ACCESS_TOKEN_METHOD = "POST"
    ACCESS_TOKEN_URL = "https://suap.ifmt.edu.br/o/token/"
    ID_KEY = "identificacao"
    RESPONSE_TYPE = "code"
    REDIRECT_STATE = True
    STATE_PARAMETER = True
    USER_DATA_URL = "https://suap.ifmt.edu.br/api/eu/"

    # Garanta que apenas os campos aprovados sejam persistidos em extra_data
    EXTRA_DATA = [
        ("identificacao", "identificacao"),
        ("nome_usual", "nome_usual"),
        ("nome_registro", "nome_registro"),
        ("nome", "nome"),
        ("primeiro_nome", "primeiro_nome"),
        ("ultimo_nome", "ultimo_nome"),
        ("email", "email"),
        ("email_academico", "email_academico"),
        ("campus", "campus"),
        ("foto", "foto"),
        ("tipo_usuario", "tipo_usuario"),
        ("data_de_nascimento", "data_de_nascimento"),
        ("sexo", "sexo"),
    ]

    def user_data(self, access_token, *args, **kwargs):
        """Busca dados do usuário no SUAP e filtra apenas os campos permitidos."""
        # LOG TEMPORÁRIO: imprimir o token para fins de teste/debug.
        # ATENÇÃO: Não deixe isto ativo em produção. O token é sensível.
        if getattr(settings, "DEBUG", False):
            # Usa logger de namespace principal para herdar config e nível INFO
            logger = logging.getLogger("suap_backend")
            logger.info("[TESTE][SUAP OAuth] Access Token obtido: %s", access_token)
            # Print explícito para garantir visualização mesmo se logging estiver filtrando
            print(f"[TESTE][SUAP OAuth] Access Token obtido: {access_token}")
            
        raw = self.request(
            url=self.USER_DATA_URL,
            data={
                "scope": (
                    kwargs.get("response", {}).get("scope")
                    if kwargs.get("response")
                    else None
                )
            },
            method="GET",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        allowed_keys = {
            "identificacao",
            "nome_usual",
            "nome_registro",
            "nome",
            "primeiro_nome",
            "ultimo_nome",
            "email",
            "email_academico",
            "campus",
            "foto",
            "tipo_usuario",
            "data_de_nascimento",
            "sexo",
        }

        # Retorna apenas o subconjunto desejado
        return {k: raw.get(k) for k in allowed_keys if k in raw}

    def get_user_details(self, response):
        """Mapeia detalhes do usuário priorizando os campos aprovados.

        - username: identificacao
        - first_name/last_name: prioriza primeiro_nome/ultimo_nome; fallback: separa "nome"
        - email: prioriza email_academico; fallback: email
        """
        first_name = (response.get("primeiro_nome") or "").strip()
        last_name = (response.get("ultimo_nome") or "").strip()

        if not first_name and not last_name:
            splitted = (response.get("nome") or "").split()
            if splitted:
                first_name = splitted[0].strip()
                if len(splitted) > 1:
                    last_name = splitted[-1].strip()

        email = response.get("email_academico") or response.get("email") or ""

        return {
            "username": response.get(self.ID_KEY) or response.get("username"),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
