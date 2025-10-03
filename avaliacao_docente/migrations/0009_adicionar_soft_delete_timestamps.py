# Generated migration for adding soft delete and timestamp fields
from django.db import migrations, models
import django.utils.timezone


def inicializar_ativo(apps, schema_editor):
    """Inicializa campo ativo=True em todos os registros existentes"""
    MODELOS = [
        "Turma",
        "Disciplina",
        "Curso",
        "CategoriaPergunta",
        "PerguntaAvaliacao",
        "QuestionarioAvaliacao",
        "QuestionarioPergunta",
        "CicloAvaliacao",
        "AvaliacaoDocente",
        "RespostaAvaliacao",
        "MatriculaTurma",
    ]

    for nome in MODELOS:
        try:
            Model = apps.get_model("avaliacao_docente", nome)
            Model.objects.filter(ativo__isnull=True).update(ativo=True)
        except Exception as e:
            print(f"Aviso: Não foi possível inicializar {nome}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao_docente", "0008_remover_campos_redundantes_turma"),
    ]

    operations = [
        # Adicionar campos de soft delete em todos os modelos
        # Turma
        migrations.AddField(
            model_name="turma",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="turma",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="turma",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # Disciplina
        migrations.AddField(
            model_name="disciplina",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="disciplina",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="disciplina",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="disciplina",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # Curso
        migrations.AddField(
            model_name="curso",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="curso",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="curso",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="curso",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # CategoriaPergunta
        migrations.AddField(
            model_name="categoriapergunta",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="categoriapergunta",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="categoriapergunta",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # CategoriaPergunta já tem campo 'ativa' (boolean), vamos renomear para 'ativo'
        migrations.RenameField(
            model_name="categoriapergunta",
            old_name="ativa",
            new_name="ativo",
        ),
        # PerguntaAvaliacao
        migrations.AddField(
            model_name="perguntaavaliacao",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="perguntaavaliacao",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # PerguntaAvaliacao já tem campo 'ativa' (boolean), vamos renomear para 'ativo'
        migrations.RenameField(
            model_name="perguntaavaliacao",
            old_name="ativa",
            new_name="ativo",
        ),
        # QuestionarioAvaliacao
        migrations.AddField(
            model_name="questionarioavaliacao",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="questionarioavaliacao",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # QuestionarioAvaliacao já tem campo 'ativo' (boolean), não precisa adicionar
        # QuestionarioPergunta
        migrations.AddField(
            model_name="questionariopergunta",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="questionariopergunta",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="questionariopergunta",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="questionariopergunta",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # CicloAvaliacao
        migrations.AddField(
            model_name="cicloavaliacao",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="cicloavaliacao",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # CicloAvaliacao já tem campo 'ativo' (boolean), não precisa adicionar
        # AvaliacaoDocente
        migrations.AddField(
            model_name="avaliacaodocente",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="avaliacaodocente",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="avaliacaodocente",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # RespostaAvaliacao
        migrations.AddField(
            model_name="respostaavaliacao",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="respostaavaliacao",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="respostaavaliacao",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="respostaavaliacao",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # MatriculaTurma
        migrations.AddField(
            model_name="matriculaturma",
            name="ativo",
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name="matriculaturma",
            name="data_exclusao",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="matriculaturma",
            name="data_criacao",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="matriculaturma",
            name="data_atualizacao",
            field=models.DateTimeField(auto_now=True),
        ),
        # Inicializar ativo=True em todos os registros existentes
        migrations.RunPython(inicializar_ativo, migrations.RunPython.noop),
    ]
