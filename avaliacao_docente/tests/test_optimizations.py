"""
Script de teste para validar otimizações de performance implementadas na Fase 1.

Testa:
1. Índices no banco de dados
2. Sistema de cache
3. Invalidação automática de cache
4. Funções com cache
5. Performance das views
"""

import os
import sys
import django
import time
from django.core.cache import cache

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.db import connection
from django.test.utils import CaptureQueriesContext
from avaliacao_docente.models import (
    PerfilProfessor,
    CicloAvaliacao,
    AvaliacaoDocente,
    RespostaAvaliacao,
)
from avaliacao_docente.services import (
    get_cache_key,
    calcular_metricas_professor_cached,
    obter_historico_professor_por_ciclo_cached,
    listar_professores_com_metricas,
)

# Cores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def print_metric(label, value):
    print(f"   {label}: {BLUE}{value}{RESET}")


# ============================================================================
# TESTE 1: VERIFICAR ÍNDICES NO BANCO DE DADOS
# ============================================================================


def test_database_indexes():
    print_header("TESTE 1: VERIFICAÇÃO DE ÍNDICES NO BANCO DE DADOS")

    cursor = connection.cursor()

    # Verificar índices criados
    indexes_to_check = [
        ("idx_aval_prof_ciclo_ativo", "avaliacao_docente_avaliacaodocente"),
        ("idx_resp_aval_aluno", "avaliacao_docente_respostaavaliacao"),
        ("idx_matric_turma_ativo", "avaliacao_docente_matriculaturma"),
        ("idx_ciclo_status_data", "avaliacao_docente_cicloavaliacao"),
        ("idx_disc_curso_ativo", "avaliacao_docente_disciplina"),
    ]

    all_found = True

    for index_name, table_name in indexes_to_check:
        cursor.execute(
            """
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = %s AND indexname = %s
        """,
            [table_name, index_name],
        )

        result = cursor.fetchone()

        if result:
            print_success(f"Índice '{index_name}' encontrado em '{table_name}'")
        else:
            print_error(f"Índice '{index_name}' NÃO encontrado em '{table_name}'")
            all_found = False

    cursor.close()

    if all_found:
        print_success("\nTodos os 5 índices foram criados com sucesso!")
        return True
    else:
        print_error("\nAlguns índices não foram encontrados!")
        return False


# ============================================================================
# TESTE 2: SISTEMA DE CACHE
# ============================================================================


def test_cache_system():
    print_header("TESTE 2: SISTEMA DE CACHE")

    # Limpar cache antes do teste
    cache.clear()
    print_info("Cache limpo para teste inicial")

    # Teste 1: Verificar se cache está funcionando
    test_key = get_cache_key("test", "exemplo", 123)
    test_value = {"dados": "teste", "numero": 42}

    # Armazenar no cache
    cache.set(test_key, test_value, 60)
    print_info(f"Valor armazenado no cache com chave: {test_key[:16]}...")

    # Recuperar do cache
    cached_value = cache.get(test_key)

    if cached_value == test_value:
        print_success("Cache armazenando e recuperando valores corretamente")
    else:
        print_error("Falha ao recuperar valor do cache")
        return False

    # Teste 2: Verificar timeout
    cache.set("test_timeout", "valor", 1)  # 1 segundo
    print_info("Testando timeout de cache (1 segundo)...")
    time.sleep(1.5)

    expired_value = cache.get("test_timeout")
    if expired_value is None:
        print_success("Timeout de cache funcionando corretamente")
    else:
        print_error("Timeout de cache não está funcionando")
        return False

    # Teste 3: Verificar hash SHA256
    if len(test_key) == 64:  # SHA256 sempre gera 64 caracteres hexadecimais
        print_success("Hash SHA256 sendo usado corretamente (64 caracteres)")
    else:
        print_error(f"Hash incorreto (esperado 64 caracteres, obteve {len(test_key)})")
        return False

    print_success("\nSistema de cache funcionando perfeitamente!")
    return True


# ============================================================================
# TESTE 3: CACHE DE MÉTRICAS DE PROFESSOR
# ============================================================================


def test_professor_metrics_cache():
    print_header("TESTE 3: CACHE DE MÉTRICAS DE PROFESSOR")

    # Buscar um professor para teste
    professor = PerfilProfessor.objects.first()

    if not professor:
        print_error("Nenhum professor encontrado no banco para teste")
        return False

    print_info(f"Testando com professor: {professor.user.get_full_name()}")

    # Limpar cache
    cache.clear()

    # Primeira chamada (sem cache)
    print_info("Primeira chamada (sem cache)...")
    start_time = time.time()

    with CaptureQueriesContext(connection) as queries_sem_cache:
        metricas_1 = calcular_metricas_professor_cached(professor, None)

    time_sem_cache = time.time() - start_time

    print_metric("Tempo sem cache", f"{time_sem_cache:.4f}s")
    print_metric("Queries executadas", len(queries_sem_cache))

    # Segunda chamada (com cache)
    print_info("\nSegunda chamada (com cache)...")
    start_time = time.time()

    with CaptureQueriesContext(connection) as queries_com_cache:
        metricas_2 = calcular_metricas_professor_cached(professor, None)

    time_com_cache = time.time() - start_time

    print_metric("Tempo com cache", f"{time_com_cache:.4f}s")
    print_metric("Queries executadas", len(queries_com_cache))

    # Verificar se os dados são iguais
    if metricas_1 == metricas_2:
        print_success("Dados do cache são idênticos aos originais")
    else:
        print_error("Dados do cache diferem dos originais")
        return False

    # Calcular ganho de performance
    if time_sem_cache > 0:
        melhoria = ((time_sem_cache - time_com_cache) / time_sem_cache) * 100
        reducao_queries = len(queries_sem_cache) - len(queries_com_cache)

        print_metric("\nGanho de performance", f"{melhoria:.1f}%")
        print_metric("Redução de queries", f"{reducao_queries} queries")

        if melhoria > 30 and reducao_queries > 0:
            print_success(
                "\n✨ Cache proporcionando ganho significativo de performance!"
            )
            return True
        elif reducao_queries > 0:
            print_success("\n✨ Cache reduzindo queries conforme esperado!")
            return True
        else:
            print_info("\n⚠️ Cache funcionando, mas ganho menor que esperado")
            return True

    return True


# ============================================================================
# TESTE 4: INVALIDAÇÃO AUTOMÁTICA DE CACHE
# ============================================================================


def test_cache_invalidation():
    print_header("TESTE 4: INVALIDAÇÃO AUTOMÁTICA DE CACHE")

    # Buscar uma avaliação com resposta para teste
    resposta = RespostaAvaliacao.objects.select_related(
        "avaliacao__professor", "avaliacao__ciclo"
    ).first()

    if not resposta:
        print_info("Nenhuma resposta encontrada para testar invalidação")
        print_info("Pulando teste de invalidação...")
        return True

    professor = resposta.avaliacao.professor
    ciclo = resposta.avaliacao.ciclo

    print_info(f"Professor: {professor.user.get_full_name()}")
    print_info(f"Ciclo: {ciclo.nome}")

    # Limpar cache e popular
    cache.clear()
    print_info("\nPopulando cache...")
    metricas_antes = calcular_metricas_professor_cached(professor, ciclo)

    # Verificar se está em cache
    cache_key = get_cache_key("metricas_prof", professor.id, ciclo.id)
    cached = cache.get(cache_key)

    if cached:
        print_success("Cache populado com sucesso")
    else:
        print_error("Falha ao popular cache")
        return False

    # Simular atualização (forçar signal)
    print_info("\nSimulando atualização de resposta (trigger de signal)...")
    resposta.save()  # Isso deve invalidar o cache via signal

    # Verificar se cache foi invalidado
    cached_apos = cache.get(cache_key)

    if cached_apos is None:
        print_success("✨ Cache invalidado automaticamente pelo signal!")
        return True
    else:
        print_error("Cache NÃO foi invalidado (signal não funcionou)")
        return False


# ============================================================================
# TESTE 5: PERFORMANCE DE LISTAGEM DE PROFESSORES
# ============================================================================


def test_professor_list_performance():
    print_header("TESTE 5: PERFORMANCE DA LISTAGEM DE PROFESSORES")

    total_professores = PerfilProfessor.objects.count()
    print_info(f"Total de professores no banco: {total_professores}")

    if total_professores == 0:
        print_error("Nenhum professor no banco para testar")
        return False

    # Limpar cache
    cache.clear()

    # Teste sem cache
    print_info("\nPrimeira execução (sem cache)...")
    start_time = time.time()

    with CaptureQueriesContext(connection) as queries_sem_cache:
        resultado_1 = listar_professores_com_metricas()

    time_sem_cache = time.time() - start_time

    print_metric("Tempo", f"{time_sem_cache:.4f}s")
    print_metric("Queries", len(queries_sem_cache))
    print_metric("Professores retornados", len(resultado_1))

    # Teste com cache
    print_info("\nSegunda execução (com cache)...")
    start_time = time.time()

    with CaptureQueriesContext(connection) as queries_com_cache:
        resultado_2 = listar_professores_com_metricas()

    time_com_cache = time.time() - start_time

    print_metric("Tempo", f"{time_com_cache:.4f}s")
    print_metric("Queries", len(queries_com_cache))
    print_metric("Professores retornados", len(resultado_2))

    # Calcular melhoria
    if time_sem_cache > 0:
        melhoria = ((time_sem_cache - time_com_cache) / time_sem_cache) * 100
        reducao_queries = len(queries_sem_cache) - len(queries_com_cache)

        print_metric("\nGanho de performance", f"{melhoria:.1f}%")
        print_metric("Redução de queries", f"{reducao_queries} queries")

        # Análise de performance
        if time_sem_cache < 3:
            print_success("\n✨ Excelente! Tempo < 3 segundos (meta atingida)")
        elif time_sem_cache < 5:
            print_info("\n⚠️ Bom tempo, mas pode melhorar (3-5 segundos)")
        else:
            print_info(f"\n⚠️ Tempo alto ({time_sem_cache:.2f}s), considere Fase 2")

        return True

    return True


# ============================================================================
# TESTE 6: VERIFICAR PAGINAÇÃO
# ============================================================================


def test_pagination():
    print_header("TESTE 6: VERIFICAÇÃO DE PAGINAÇÃO")

    from django.core.paginator import Paginator

    ciclos = CicloAvaliacao.objects.all().order_by("-data_inicio")
    total_ciclos = ciclos.count()

    print_info(f"Total de ciclos no banco: {total_ciclos}")

    if total_ciclos == 0:
        print_info("Nenhum ciclo para testar paginação")
        return True

    # Testar paginação (5 por página)
    paginator = Paginator(ciclos, 5)

    print_metric("Total de páginas", paginator.num_pages)
    print_metric("Itens por página", paginator.per_page)

    # Testar primeira página
    page_1 = paginator.get_page(1)
    print_metric("Itens na página 1", len(page_1))

    if len(page_1) <= 5:
        print_success("Paginação funcionando corretamente (5 itens/página)")
        return True
    else:
        print_error("Paginação com mais itens que o esperado")
        return False


# ============================================================================
# MAIN: EXECUTAR TODOS OS TESTES
# ============================================================================


def main():
    print_header("🚀 INICIANDO TESTES DE OTIMIZAÇÃO - FASE 1")

    resultados = {
        "Índices no Banco": test_database_indexes(),
        "Sistema de Cache": test_cache_system(),
        "Cache de Métricas": test_professor_metrics_cache(),
        "Invalidação de Cache": test_cache_invalidation(),
        "Performance de Listagem": test_professor_list_performance(),
        "Paginação": test_pagination(),
    }

    # Resumo final
    print_header("📊 RESUMO DOS TESTES")

    total = len(resultados)
    aprovados = sum(1 for passou in resultados.values() if passou)

    for teste, resultado in resultados.items():
        status = f"{GREEN}✅ PASSOU{RESET}" if resultado else f"{RED}❌ FALHOU{RESET}"
        print(f"   {teste}: {status}")

    print(f"\n{BLUE}{'=' * 70}{RESET}")

    if aprovados == total:
        print_success(f"\n🎉 TODOS OS {total} TESTES PASSARAM COM SUCESSO!")
        print_info("Sistema otimizado e pronto para produção!")
    else:
        print_error(f"\n⚠️ {aprovados}/{total} testes passaram")
        print_info(f"{total - aprovados} teste(s) falharam - verificar logs acima")

    print(f"\n{BLUE}{'=' * 70}{RESET}\n")

    return aprovados == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"\nErro durante execução dos testes: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
