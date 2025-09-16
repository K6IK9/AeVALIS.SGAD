from typing import Optional


def apply_suap_user_type(
    strategy, backend, details, response, user=None, *args, **kwargs
):
    """
    Pipeline: aplica role e perfis (PerfilAluno/PerfilProfessor) com base em response['tipo_usuario'] do SUAP.

    - Executa apenas quando o backend é 'suap'.
    - Remove roles existentes entre {admin, coordenador, professor, aluno} e aplica a nova role.
    - Cria/ajusta PerfilAluno ou PerfilProfessor conforme a role (coordenador usa PerfilProfessor).
    - Mantém admin intocado se o usuário já tiver admin (não rebaixa admin automaticamente).
    - Respeita roles definidas manualmente (não sobrescreve se foram alteradas por admin).
    """
    if backend.name != "suap" or not user:
        return

    # Admin prevalece: não altera roles/perfis de administradores automaticamente
    try:
        from rolepermissions.checkers import has_role

        if has_role(user, "admin"):
            return
    except Exception:
        pass

    # Verificar se a role foi definida manualmente (flag para evitar sobrescrita)
    # Se o usuário já tem uma role diferente da que seria aplicada pelo SUAP,
    # e não é seu primeiro login (user.last_login não é None), não sobrescrever
    if user.last_login is not None:
        # Verificar se já tem alguma role definida (que não seja a padrão do SUAP)
        current_roles = []
        for role_name in ["coordenador", "professor", "aluno"]:
            if has_role(user, role_name):
                current_roles.append(role_name)

        # Se já tem role definida, verificar se deve manter
        if current_roles:
            # Usar função utilitária para verificar se foi alterada manualmente
            try:
                from .utils import is_role_manually_changed

                if is_role_manually_changed(user):
                    return
            except Exception:
                # Fallback: verificar diretamente
                try:
                    social_auth = user.social_auth.filter(provider="suap").first()
                    if social_auth and isinstance(social_auth.extra_data, dict):
                        # Se tem flag de alteração manual, não sobrescrever
                        if social_auth.extra_data.get("role_manually_changed", False):
                            return
                except Exception:
                    pass

    # Tenta obter o tipo do response; se ausente, tenta via extra_data
    tipo: Optional[str] = None
    try:
        tipo = (response or {}).get("tipo_usuario")
        if not tipo and hasattr(user, "social_auth"):
            social = user.social_auth.filter(provider="suap").first()
            if social and isinstance(social.extra_data, dict):
                tipo = social.extra_data.get("tipo_usuario")
    except Exception:
        tipo = None

    if not tipo:
        return

    tipo_norm = str(tipo).strip().lower()

    # Mapeamentos com verificação por substring para cobrir variações
    if any(x in tipo_norm for x in ["aluno", "discente", "estudante"]):
        role_target = "aluno"
    elif any(x in tipo_norm for x in ["coorden", "coordenaç", "coordenac"]):
        role_target = "coordenador"
    elif any(x in tipo_norm for x in ["prof", "docent"]):
        role_target = "professor"
    else:
        # Tipo desconhecido – não altera
        return

    from rolepermissions.roles import assign_role, remove_role

    # Limpa roles anteriores relevantes
    for r in ["coordenador", "professor", "aluno"]:
        try:
            remove_role(user, r)
        except Exception:
            pass

    # Aplica a nova role
    assign_role(user, role_target)

    # Gerencia perfis
    try:
        from avaliacao_docente.models import PerfilAluno, PerfilProfessor

        if role_target == "aluno":
            # Remove perfil de professor, mantém/cria aluno
            if hasattr(user, "perfil_professor"):
                user.perfil_professor.delete()
            PerfilAluno.objects.get_or_create(user=user)

        elif role_target in {"professor", "coordenador"}:
            # Remove perfil de aluno, mantém/cria professor
            if hasattr(user, "perfil_aluno"):
                user.perfil_aluno.delete()
            PerfilProfessor.objects.get_or_create(
                user=user, defaults={"registro_academico": user.username}
            )
    except Exception:
        # Não falha o login caso algo dê errado no ajuste de perfil
        pass

    # Nada a retornar – esse passo é side-effect only
    return
