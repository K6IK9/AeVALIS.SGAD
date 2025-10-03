# Migração para adicionar data_criacao a RespostaAvaliacao
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao_docente", "0009_adicionar_soft_delete_timestamps"),
    ]

    operations = [
        migrations.AddField(
            model_name="respostaavaliacao",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
