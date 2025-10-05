# Migração para adicionar data_criacao a RespostaAvaliacao
# NOTA: Este campo já foi adicionado na migração 0009_adicionar_soft_delete_timestamps
# Esta migração foi mantida vazia para preservar a ordem das migrações
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao_docente", "0009_adicionar_soft_delete_timestamps"),
    ]

    operations = [
        # Campo data_criacao já adicionado na migração 0009
    ]
