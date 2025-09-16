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
