# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao_docente", "0007_validar_turmas_consistencia"),
    ]

    operations = [
        # Remove unique_together antigo
        migrations.AlterUniqueTogether(
            name="turma",
            unique_together=set(),
        ),
        # Remove campos redundantes
        migrations.RemoveField(
            model_name="turma",
            name="professor",
        ),
        migrations.RemoveField(
            model_name="turma",
            name="periodo_letivo",
        ),
        # Adiciona nova unique_together
        migrations.AlterUniqueTogether(
            name="turma",
            unique_together={("disciplina", "turno")},
        ),
        # Atualiza ordering do Meta
        migrations.AlterModelOptions(
            name="turma",
            options={
                "ordering": [
                    "disciplina__periodo_letivo",
                    "disciplina__disciplina_nome",
                ]
            },
        ),
    ]
