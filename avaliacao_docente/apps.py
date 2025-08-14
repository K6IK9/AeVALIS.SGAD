from django.apps import AppConfig


class AvaliacaoDocenteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "avaliacao_docente"

    def ready(self):
        import avaliacao_docente.signals
