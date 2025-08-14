from rolepermissions.checkers import has_role


def check_user_permission(user, roles):
    """
    Verifica se o usuário possui alguma das roles especificadas

    Args:
        user: Objeto User do Django
        roles: Lista de strings com os nomes das roles

    Returns:
        bool: True se o usuário possuir alguma das roles, False caso contrário
    """
    if not user or not user.is_authenticated:
        return False

    for role in roles:
        if has_role(user, role):
            return True

    return False


def get_user_role_name(user):
    """
    Retorna o nome da role do usuário em português

    Args:
        user: Objeto User do Django

    Returns:
        str: Nome da role em português
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
