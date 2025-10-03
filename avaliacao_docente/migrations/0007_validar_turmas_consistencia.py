# Generated manually

from django.db import migrations


def validar_consistencia_turmas(apps, schema_editor):
    """
    Valida se todos os registros de Turma têm:
    - professor == disciplina.professor
    - periodo_letivo == disciplina.periodo_letivo
    """
    Turma = apps.get_model("avaliacao_docente", "Turma")

    inconsistencias_professor = []
    inconsistencias_periodo = []

    for turma in Turma.objects.select_related("disciplina").all():
        if turma.professor_id != turma.disciplina.professor_id:
            inconsistencias_professor.append(turma.id)

        if turma.periodo_letivo_id != turma.disciplina.periodo_letivo_id:
            inconsistencias_periodo.append(turma.id)

    if inconsistencias_professor or inconsistencias_periodo:
        erro_msg = "Inconsistências encontradas nas turmas:\\n"
        if inconsistencias_professor:
            erro_msg += (
                f"- Professor inconsistente nas turmas: {inconsistencias_professor}\\n"
            )
        if inconsistencias_periodo:
            erro_msg += f"- Período letivo inconsistente nas turmas: {inconsistencias_periodo}\\n"
        erro_msg += "Execute o script docs/validar_turma_consistencia.py para corrigir antes de prosseguir."
        raise RuntimeError(erro_msg)


class Migration(migrations.Migration):

    dependencies = [
        ("avaliacao_docente", "0006_configuracaosite_metodo_envio_email"),
    ]

    operations = [
        migrations.RunPython(validar_consistencia_turmas, migrations.RunPython.noop),
    ]
