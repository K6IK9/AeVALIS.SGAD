from django.urls import path

from . import views
from .views import AdminHubView, IndexView

urlpatterns = [
    path(
        "resetar-role-automatica/<int:usuario_id>/",
        views.resetar_role_automatica,
        name="resetar_role_automatica",
    ),
    path("gerenciar-usuarios/", views.gerenciar_usuarios, name="gerenciar_usuarios"),
    path(
        "editar-usuario/<int:usuario_id>/", views.editar_usuario, name="editar_usuario"
    ),
    path(
        "excluir-usuario/<int:usuario_id>/",
        views.excluir_usuario,
        name="excluir_usuario",
    ),
    path(
        "resetar-senha-usuario/<int:usuario_id>/",
        views.resetar_senha_usuario,
        name="resetar_senha_usuario",
    ),
    path("gerenciar-cursos/", views.gerenciar_cursos, name="gerenciar_cursos"),
    path("editar-curso/<int:curso_id>/", views.editar_curso, name="editar_curso"),
    path("excluir-curso/<int:curso_id>/", views.excluir_curso, name="excluir_curso"),
    path(
        "gerenciar-disciplinas/",
        views.gerenciar_disciplinas,
        name="gerenciar_disciplinas",
    ),
    path(
        "editar-disciplina/<int:disciplina_id>/",
        views.editar_disciplina,
        name="editar_disciplina",
    ),
    path(
        "excluir-disciplina/<int:disciplina_id>/",
        views.excluir_disciplina,
        name="excluir_disciplina",
    ),
    path("gerenciar-periodos/", views.gerenciar_periodos, name="gerenciar_periodos"),
    path(
        "editar-periodo/<int:periodo_id>/", views.editar_periodo, name="editar_periodo"
    ),
    path(
        "editar-periodo-simples/<int:periodo_id>/",
        views.editar_periodo_simples,
        name="editar_periodo_simples",
    ),
    path(
        "excluir-periodo/<int:periodo_id>/",
        views.excluir_periodo,
        name="excluir_periodo",
    ),
    path("gerenciar-turmas/", views.gerenciar_turmas, name="gerenciar_turmas"),
    path("editar-turma/<int:turma_id>/", views.editar_turma, name="editar_turma"),
    path("excluir-turma/<int:turma_id>/", views.excluir_turma, name="excluir_turma"),
    path(
        "gerenciar-alunos-turma/<int:turma_id>/",
        views.gerenciar_alunos_turma,
        name="gerenciar_alunos_turma",
    ),
    path("buscar-alunos-turma/", views.buscar_alunos_turma, name="buscar_alunos_turma"),
    path(
        "matricular-alunos-massa/",
        views.matricular_alunos_massa,
        name="matricular_alunos_massa",
    ),
    path("admin_hub/", views.AdminHubView.as_view(), name="admin_hub"),
    path(
        "admin_hub/configuracao/",
        views.gerenciar_configuracao_site,
        name="gerenciar_configuracao_site",
    ),
    # URLs para exportação CSV do admin hub
    path(
        "admin-hub/exportar-usuarios-csv/",
        views.exportar_usuarios_csv,
        name="exportar_usuarios_csv",
    ),
    path(
        "admin-hub/exportar-cursos-csv/",
        views.exportar_cursos_csv,
        name="exportar_cursos_csv",
    ),
    path(
        "admin-hub/exportar-disciplinas-csv/",
        views.exportar_disciplinas_csv,
        name="exportar_disciplinas_csv",
    ),
    path(
        "admin-hub/exportar-turmas-csv/",
        views.exportar_turmas_csv,
        name="exportar_turmas_csv",
    ),
    path(
        "admin-hub/exportar-periodos-csv/",
        views.exportar_periodos_csv,
        name="exportar_periodos_csv",
    ),
    # URLs para Avaliação Docente
    path("avaliacoes/", views.listar_avaliacoes, name="listar_avaliacoes"),
    path("minhas-avaliacoes/", views.minhas_avaliacoes, name="minhas_avaliacoes"),
    # path(
    #     "avaliacoes/criar-questionario/",
    #     views.criar_questionario_avaliacao,
    #     name="criar_questionario_avaliacao",
    # ),
    path(
        "avaliacoes/gerenciar-questionarios/",
        views.gerenciar_questionarios,
        name="gerenciar_questionarios",
    ),
    path(
        "avaliacoes/questionario/<int:questionario_id>/editar/",
        views.editar_questionario_simples,
        name="editar_questionario_simples",
    ),
    path(
        "avaliacoes/questionario/<int:questionario_id>/excluir/",
        views.excluir_questionario,
        name="excluir_questionario",
    ),
    path(
        "avaliacoes/questionario/<int:questionario_id>/perguntas/",
        views.editar_questionario_perguntas,
        name="editar_questionario_perguntas",
    ),
    path(
        "avaliacoes/ciclo/<int:ciclo_id>/",
        views.detalhe_ciclo_avaliacao,
        name="detalhe_ciclo_avaliacao",
    ),
    path(
        "avaliacoes/responder/<int:avaliacao_id>/",
        views.responder_avaliacao,
        name="responder_avaliacao",
    ),
    path(
        "avaliacoes/visualizar/<int:avaliacao_id>/",
        views.visualizar_avaliacao,
        name="visualizar_avaliacao",
    ),
    path(
        "avaliacoes/relatorios/",
        views.relatorio_avaliacoes,
        name="relatorio_avaliacoes",
    ),
    # URLs para CRUD de categorias
    path("categorias/", views.gerenciar_categorias, name="gerenciar_categorias"),
    path(
        "categorias/<int:categoria_id>/",
        views.categoria_detail,
        name="categoria_detail",
    ),
    # path("categorias/form/", views.categoria_form, name="categoria_form"),
    # path(
    #     "categorias/form/<int:categoria_id>/",
    #     views.categoria_form,
    #     name="categoria_form_edit",
    # ),
    path(
        "categorias/<int:categoria_id>/edit/",
        views.editar_categoria,
        name="editar_categoria",
    ),
    path(
        "editar-categoria/<int:categoria_id>/",
        views.editar_categoria_simples,
        name="editar_categoria_simples",
    ),
    path(
        "categorias/<int:categoria_id>/delete/",
        views.excluir_categoria,
        name="excluir_categoria",
    ),
    # URLs para CRUD de ciclos
    path("ciclos/", views.gerenciar_ciclos, name="gerenciar_ciclos"),
    path(
        "editar-ciclo/<int:ciclo_id>/",
        views.editar_ciclo_simples,
        name="editar_ciclo_simples",
    ),
    path(
        "excluir-ciclo/<int:ciclo_id>/",
        views.excluir_ciclo,
        name="excluir_ciclo",
    ),
    path(
        "encerrar-ciclo/<int:ciclo_id>/",
        views.encerrar_ciclo,
        name="encerrar_ciclo",
    ),
    path(
        "encerrar-avaliacao/<int:avaliacao_id>/",
        views.encerrar_avaliacao,
        name="encerrar_avaliacao",
    ),
    path("", IndexView.as_view(), name="inicio"),
    path("perfil/", views.perfil_usuario, name="perfil_usuario"),
]
