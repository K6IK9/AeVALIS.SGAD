from django import template
from rolepermissions.checkers import has_role as check_role, has_permission

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
    elif check_role(user, "servidor"):
        return "Servidor (Técnico-Administrativo)"
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
    elif check_role(user, "servidor"):
        return "role-servidor"
    else:
        return "role-sem-role"


@register.filter
def get_user_profile_type(user):
    """
    Template filter para obter o tipo de perfil do usuário baseado nos perfis cadastrados
    """
    # Verificar perfis específicos primeiro
    if hasattr(user, "perfil_professor"):
        return "Professor"
    elif hasattr(user, "perfil_aluno"):
        return "Aluno"
    # Para usuários sem perfil específico, verificar roles administrativas
    elif check_role(user, "admin"):
        return "Administrador do Sistema"
    elif check_role(user, "coordenador"):
        return "Coordenador Acadêmico"
    elif check_role(user, "servidor"):
        return "Servidor (Técnico-Administrativo)"
    else:
        return "Usuário do Sistema"


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


@register.filter
def has_permission(user, permission):
    """
    Template filter para verificar se o usuário tem uma permissão específica
    """
    from rolepermissions.checkers import has_permission as check_permission

    return check_permission(user, permission)


@register.filter
def can_access_admin(user):
    """
    Template filter para verificar se o usuário pode acessar funcionalidades administrativas
    """
    return check_role(user, "admin") or check_role(user, "coordenador")


@register.filter
def is_admin(user):
    """
    Template filter para verificar se o usuário é admin
    """
    return check_role(user, "admin")


@register.filter
def is_coordenador(user):
    """
    Template filter para verificar se o usuário é coordenador
    """
    return check_role(user, "coordenador")


@register.filter
def is_professor(user):
    """
    Template filter para verificar se o usuário é professor
    """
    return check_role(user, "professor")


@register.filter
def is_aluno(user):
    """
    Template filter para verificar se o usuário é aluno
    """
    return check_role(user, "aluno")


@register.filter
def is_servidor(user):
    """
    Template filter para verificar se o usuário é servidor
    """
    return check_role(user, "servidor")
