"""
Serviços de agregação e cálculo de métricas de avaliações.

Este módulo centraliza lógicas de negócio reutilizáveis para relatórios
e dashboards, mantendo as views limpas e focadas em apresentação.
"""

from django.db.models import Q, Prefetch, Count
from .models import (
    PerfilProfessor,
    AvaliacaoDocente,
    RespostaAvaliacao,
    Curso,
)


def calcular_metricas_professor(professor, ciclo=None):
    """
    Calcula métricas consolidadas de um professor (OTIMIZADO).

    Args:
        professor: Instância de PerfilProfessor
        ciclo: Instância de CicloAvaliacao (opcional, filtra por ciclo específico)

    Returns:
        dict com:
            - avaliacoes_respondidas: int (total de avaliações com respostas)
            - total_respondentes: int (alunos únicos que responderam)
            - total_alunos_aptos: int (alunos que poderiam responder)
            - taxa_resposta: float (percentual)
            - media_ciclo: float ou None (média ponderada do ciclo/geral)
            - classificacao_ciclo: str (Excelente, Bom, Regular, etc)
            - total_avaliacoes: int (avaliações criadas, com ou sem resposta)
    """
    # Filtrar avaliações do professor
    avaliacoes_qs = AvaliacaoDocente.objects.filter(professor=professor)

    if ciclo:
        avaliacoes_qs = avaliacoes_qs.filter(ciclo=ciclo)

    # Usar aggregação para contar avaliações
    total_avaliacoes = avaliacoes_qs.count()

    if total_avaliacoes == 0:
        return {
            "avaliacoes_respondidas": 0,
            "total_respondentes": 0,
            "total_alunos_aptos": 0,
            "taxa_resposta": 0.0,
            "media_ciclo": None,
            "classificacao_ciclo": "Sem dados",
            "total_avaliacoes": 0,
        }

    # Pré-carregar apenas o necessário
    avaliacoes = avaliacoes_qs.select_related("turma", "ciclo").prefetch_related(
        Prefetch(
            "respostas",
            queryset=RespostaAvaliacao.objects.select_related("pergunta"),
        ),
        "turma__matriculas",
    )

    avaliacoes_respondidas = 0
    respondentes_ids = set()
    total_alunos_aptos = 0
    medias_avaliacoes = []

    # Loop único para calcular tudo
    for avaliacao in avaliacoes:
        respostas = list(avaliacao.respostas.all())

        if respostas:
            avaliacoes_respondidas += 1

            # Contar respondentes únicos
            for resposta in respostas:
                if resposta.aluno_id:
                    respondentes_ids.add(resposta.aluno_id)

            # Calcular média desta avaliação
            resultado = avaliacao.calcular_media_geral_questionario_padrao()
            if resultado:
                medias_avaliacoes.append(resultado["media_geral"])

        # Contar alunos aptos (cache na turma se possível)
        alunos_aptos = avaliacao.alunos_aptos()
        total_alunos_aptos += len(alunos_aptos)

    total_respondentes = len(respondentes_ids)
    taxa_resposta = (
        round((total_respondentes / total_alunos_aptos) * 100, 2)
        if total_alunos_aptos > 0
        else 0.0
    )

    # Calcular média final
    media_ciclo = None
    classificacao_ciclo = "Sem dados"

    if medias_avaliacoes:
        media_ciclo = round(sum(medias_avaliacoes) / len(medias_avaliacoes), 4)
        # Usar método estático para classificar
        classificacao_ciclo = AvaliacaoDocente.get_classificacao_media(
            None, media_ciclo
        )

    return {
        "avaliacoes_respondidas": avaliacoes_respondidas,
        "total_respondentes": total_respondentes,
        "total_alunos_aptos": total_alunos_aptos,
        "taxa_resposta": taxa_resposta,
        "media_ciclo": media_ciclo,
        "classificacao_ciclo": classificacao_ciclo,
        "total_avaliacoes": total_avaliacoes,
    }


def calcular_media_historica_professor(professor, excluir_ciclo=None):
    """
    Calcula a média histórica geral do professor em todos os ciclos anteriores.

    Args:
        professor: Instância de PerfilProfessor
        excluir_ciclo: CicloAvaliacao para excluir do cálculo (útil para comparação)

    Returns:
        dict com:
            - media_historica: float ou None
            - classificacao_historica: str
            - total_ciclos: int (quantidade de ciclos considerados)
            - total_avaliacoes_historicas: int
    """
    avaliacoes = AvaliacaoDocente.objects.filter(
        professor=professor, respostas__isnull=False
    ).distinct()

    if excluir_ciclo:
        avaliacoes = avaliacoes.exclude(ciclo=excluir_ciclo)

    avaliacoes = avaliacoes.select_related(
        "turma", "disciplina", "ciclo"
    ).prefetch_related(
        Prefetch(
            "respostas",
            queryset=RespostaAvaliacao.objects.select_related("pergunta"),
        )
    )

    if not avaliacoes.exists():
        return {
            "media_historica": None,
            "classificacao_historica": "Sem dados",
            "total_ciclos": 0,
            "total_avaliacoes_historicas": 0,
        }

    medias_avaliacoes = []
    ciclos_unicos = set()

    for avaliacao in avaliacoes:
        resultado = avaliacao.calcular_media_geral_questionario_padrao()
        if resultado:
            medias_avaliacoes.append(resultado["media_geral"])
            ciclos_unicos.add(avaliacao.ciclo.id)

    if not medias_avaliacoes:
        return {
            "media_historica": None,
            "classificacao_historica": "Sem dados",
            "total_ciclos": len(ciclos_unicos),
            "total_avaliacoes_historicas": avaliacoes.count(),
        }

    media_historica = round(sum(medias_avaliacoes) / len(medias_avaliacoes), 4)
    classificacao_historica = avaliacoes.first().get_classificacao_media(
        media_historica
    )

    return {
        "media_historica": media_historica,
        "classificacao_historica": classificacao_historica,
        "total_ciclos": len(ciclos_unicos),
        "total_avaliacoes_historicas": avaliacoes.count(),
    }


def listar_professores_com_metricas(ciclo=None, curso=None, busca=None):
    """
    Lista professores com suas métricas agregadas, aplicando filtros (OTIMIZADO).

    Args:
        ciclo: CicloAvaliacao para filtrar (opcional)
        curso: Curso para filtrar (opcional)
        busca: String para buscar no nome do professor (opcional)

    Returns:
        QuerySet de PerfilProfessor com métricas já calculadas (lista de dicts)
    """
    # Pré-carregar avaliações de todos os professores de uma vez
    avaliacoes_prefetch = Prefetch(
        "avaliacoes_recebidas",
        queryset=AvaliacaoDocente.objects.select_related(
            "turma", "ciclo"
        ).prefetch_related(
            Prefetch(
                "respostas",
                queryset=RespostaAvaliacao.objects.select_related("pergunta"),
            ),
            "turma__matriculas",
        ),
    )

    professores = (
        PerfilProfessor.non_admin.all()
        .select_related("user")
        .prefetch_related(avaliacoes_prefetch)
        .order_by("user__first_name", "user__last_name")
    )

    # Aplicar filtros
    if busca:
        professores = professores.filter(
            Q(user__first_name__icontains=busca)
            | Q(user__last_name__icontains=busca)
            | Q(matricula__icontains=busca)
        )

    # Filtrar por curso (professores que lecionam disciplinas desse curso)
    if curso:
        professores = professores.filter(
            avaliacoes_recebidas__turma__disciplina__curso=curso
        ).distinct()

    # Filtrar por ciclo (professores avaliados nesse ciclo)
    if ciclo:
        professores = professores.filter(avaliacoes_recebidas__ciclo=ciclo).distinct()

    # Pré-carregar cursos de todos os professores em uma única query
    cursos_por_professor = {}
    if professores.exists():
        cursos_data = (
            Curso.objects.filter(
                disciplinas__turmas__avaliacoes_docente__professor__in=professores
            )
            .values("disciplinas__turmas__avaliacoes_docente__professor", "curso_nome")
            .distinct()
        )

        for item in cursos_data:
            prof_id = item["disciplinas__turmas__avaliacoes_docente__professor"]
            curso_nome = item["curso_nome"]
            if prof_id not in cursos_por_professor:
                cursos_por_professor[prof_id] = []
            if curso_nome not in cursos_por_professor[prof_id]:
                cursos_por_professor[prof_id].append(curso_nome)

    # Calcular métricas para cada professor
    professores_com_metricas = []

    for professor in professores:
        metricas_ciclo = calcular_metricas_professor(professor, ciclo)
        metricas_historico = calcular_media_historica_professor(
            professor, excluir_ciclo=ciclo
        )

        # Obter cursos do cache
        cursos_lista = cursos_por_professor.get(professor.id, [])
        cursos_str = ", ".join(cursos_lista) if cursos_lista else "N/A"

        professores_com_metricas.append(
            {
                "professor": professor,
                "cursos": cursos_str,
                **metricas_ciclo,
                **metricas_historico,
            }
        )

    return professores_com_metricas


def obter_historico_professor_por_ciclo(professor):
    """
    Obtém o histórico completo de um professor agrupado por ciclo.

    Args:
        professor: Instância de PerfilProfessor

    Returns:
        dict com:
            - ciclos: lista de dicts com métricas por ciclo
            - avaliacoes_detalhadas: lista de todas avaliações com detalhes
            - estatisticas_gerais: dict com totais e médias gerais
    """
    from .models import CicloAvaliacao

    # Buscar todos os ciclos onde o professor foi avaliado
    ciclos_ids = (
        AvaliacaoDocente.objects.filter(professor=professor)
        .values_list("ciclo_id", flat=True)
        .distinct()
    )

    ciclos = CicloAvaliacao.objects.filter(id__in=ciclos_ids).order_by("-data_inicio")

    historico_ciclos = []
    todas_avaliacoes = []

    for ciclo in ciclos:
        # Calcular métricas deste ciclo
        metricas_ciclo = calcular_metricas_professor(professor, ciclo)

        # Buscar avaliações deste ciclo
        avaliacoes = (
            AvaliacaoDocente.objects.filter(professor=professor, ciclo=ciclo)
            .select_related("turma", "disciplina", "turma__disciplina__curso")
            .prefetch_related(
                Prefetch(
                    "respostas",
                    queryset=RespostaAvaliacao.objects.select_related("pergunta"),
                )
            )
        )

        avaliacoes_info = []
        for avaliacao in avaliacoes:
            resultado = avaliacao.calcular_media_geral_questionario_padrao()
            total_respostas = avaliacao.respostas.count()
            alunos_aptos = avaliacao.alunos_aptos()

            avaliacoes_info.append(
                {
                    "avaliacao": avaliacao,
                    "turma": avaliacao.turma,
                    "disciplina": avaliacao.disciplina,
                    "curso": (
                        avaliacao.turma.disciplina.curso
                        if avaliacao.turma.disciplina
                        else None
                    ),
                    "total_respostas": total_respostas,
                    "total_alunos": len(alunos_aptos),
                    "media": resultado["media_geral"] if resultado else None,
                    "classificacao": (
                        AvaliacaoDocente.get_classificacao_media(
                            None, resultado["media_geral"]
                        )
                        if resultado
                        else "Sem dados"
                    ),
                }
            )

        historico_ciclos.append(
            {
                "ciclo": ciclo,
                "metricas": metricas_ciclo,
                "avaliacoes": avaliacoes_info,
            }
        )

        todas_avaliacoes.extend(avaliacoes_info)

    # Calcular estatísticas gerais
    total_avaliacoes = len(todas_avaliacoes)
    avaliacoes_com_media = [av for av in todas_avaliacoes if av["media"] is not None]
    media_geral = (
        round(
            sum(av["media"] for av in avaliacoes_com_media) / len(avaliacoes_com_media),
            4,
        )
        if avaliacoes_com_media
        else None
    )
    classificacao_geral = (
        AvaliacaoDocente.get_classificacao_media(None, media_geral)
        if media_geral
        else "Sem dados"
    )

    return {
        "ciclos": historico_ciclos,
        "avaliacoes_detalhadas": todas_avaliacoes,
        "estatisticas_gerais": {
            "total_ciclos": len(historico_ciclos),
            "total_avaliacoes": total_avaliacoes,
            "avaliacoes_respondidas": len(avaliacoes_com_media),
            "media_geral": media_geral,
            "classificacao_geral": classificacao_geral,
        },
    }


# ============================================================================
# FUNÇÕES PARA SISTEMA DE LEMBRETES AUTOMÁTICOS
# ============================================================================


def calcular_taxa_resposta_turma(ciclo, turma):
    """
    Calcula a taxa de resposta de uma turma em um ciclo específico.

    Args:
        ciclo: Instância de CicloAvaliacao
        turma: Instância de Turma

    Returns:
        dict: {
            'respondentes': int,  # Alunos distintos que responderam
            'alunos_aptos': int,  # Total de alunos matriculados ativos
            'taxa_percentual': Decimal,  # Percentual de resposta (0-100)
        }
    """
    from decimal import Decimal

    # Contar alunos matriculados ativos na turma (aptos a responder)
    alunos_aptos = turma.matriculas.filter(status="ativa").count()

    if alunos_aptos == 0:
        return {
            "respondentes": 0,
            "alunos_aptos": 0,
            "taxa_percentual": Decimal("0.00"),
        }

    # Contar alunos distintos que responderam alguma avaliação da turma neste ciclo
    respondentes = (
        RespostaAvaliacao.objects.filter(avaliacao__turma=turma, avaliacao__ciclo=ciclo)
        .values("aluno_id")
        .distinct()
        .count()
    )

    # Calcular taxa percentual
    taxa_percentual = Decimal(str((respondentes / alunos_aptos) * 100.0))
    taxa_percentual = taxa_percentual.quantize(Decimal("0.01"))

    return {
        "respondentes": respondentes,
        "alunos_aptos": alunos_aptos,
        "taxa_percentual": taxa_percentual,
    }


def obter_alunos_pendentes_lembrete(job):
    """
    Retorna queryset de alunos que devem receber lembrete para um job específico.

    Critérios de elegibilidade:
    - Aluno tem matrícula ativa na turma
    - Aluno NÃO respondeu nenhuma avaliação da turma neste ciclo
    - Aluno NÃO atingiu o limite máximo de lembretes configurado

    Args:
        job: Instância de JobLembreteCicloTurma

    Returns:
        QuerySet de PerfilAluno elegíveis para receber lembrete
    """
    from .models import ConfiguracaoSite, PerfilAluno, NotificacaoLembrete

    config = ConfiguracaoSite.obter_config()

    # Alunos com matrícula ativa na turma
    matriculas_ativas = job.turma.matriculas.filter(status="ativa").values_list(
        "aluno_id", flat=True
    )

    # Alunos que já responderam (devem ser excluídos)
    alunos_que_responderam = (
        RespostaAvaliacao.objects.filter(
            avaliacao__turma=job.turma, avaliacao__ciclo=job.ciclo
        )
        .values_list("aluno_id", flat=True)
        .distinct()
    )

    # Alunos que já atingiram o limite de lembretes (devem ser excluídos)
    alunos_limite_atingido = (
        NotificacaoLembrete.objects.filter(job=job, status="enviado")
        .values("aluno_id")
        .annotate(total_lembretes=Count("id"))
        .filter(total_lembretes__gte=config.max_lembretes_por_aluno)
        .values_list("aluno_id", flat=True)
    )

    # Filtrar alunos elegíveis
    alunos_elegiveis = (
        PerfilAluno.objects.filter(id__in=matriculas_ativas)
        .exclude(id__in=alunos_que_responderam)
        .exclude(id__in=alunos_limite_atingido)
        .select_related("user")
    )

    return alunos_elegiveis
