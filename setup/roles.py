from rolepermissions.roles import AbstractUserRole


class Admin(AbstractUserRole):
    available_permissions = {
        'view_avaliacao': True,
        'edit_avaliacao': True,
        'delete_avaliacao': True,
        'add_avaliacao': True,
    }

class Coordenador(AbstractUserRole):
    available_permissions = {
        'view_avaliacao': True,
        'edit_avaliacao': True,
        'delete_avaliacao': True,
        'add_avaliacao': True,
    }
    
class Professor(AbstractUserRole):
    available_permissions = {
        'view_avaliacao': True,
        'edit_avaliacao': True,
        'delete_avaliacao': False,
        'add_avaliacao': True,
    }
    
class Aluno(AbstractUserRole):
    available_permissions = {
        'view_avaliacao': True,
        'edit_avaliacao': False,
        'delete_avaliacao': False,
        'add_avaliacao': True,
    }