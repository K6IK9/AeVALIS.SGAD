from django import template
from rolepermissions.checkers import has_role as check_role

register = template.Library()


@register.filter
def get_user_role(user):
    """
    Template filter para obter a role do usuário
    """
    if check_role(user, "admin"):
        return "Administrador"
    elif check_role(user, "coordenador"):
        return "Coordenador"
    elif check_role(user, "professor"):
        return "Professor"
    elif check_role(user, "aluno"):
        return "Aluno"
    else:
        return "Sem role definida"


@register.filter
def get_user_role_class(user):
    """
    Template filter para obter a classe CSS baseada na role do usuário
    """
    if check_role(user, "admin"):
        return "role-admin"
    elif check_role(user, "coordenador"):
        return "role-coordenador"
    elif check_role(user, "professor"):
        return "role-professor"
    elif check_role(user, "aluno"):
        return "role-aluno"
    else:
        return "role-sem-role"


@register.filter
def get_user_profile_type(user):
    """
    Template filter para obter o tipo de perfil do usuário
    """
    if hasattr(user, "perfil_professor"):
        return "Professor"
    elif hasattr(user, "perfil_aluno"):
        return "Aluno"
    else:
        return "Administrativo"


@register.filter
def has_user_role(user, role):
    """
    Template filter para verificar se o usuário tem uma role específica
    """
    return check_role(user, role)


@register.filter
def has_role(user, role):
    """
    Template filter para verificar se o usuário tem uma role específica
    """
    return check_role(user, role)


@register.simple_tag
def nps_scale():
    """Retorna a escala NPS de 0 a 10 (inclusive).

    Uso no template:
        {% nps_scale as escala %}
        {% for i in escala %}
            ... {{ i }} ...
        {% endfor %}
    """
    return list(range(0, 11))
