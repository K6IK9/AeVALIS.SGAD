"""
Script para validar cálculos de média das avaliações.

Uso:
    python manage.py shell
    from scripts.validar_calculos_media import validar_media_avaliacao
    validar_media_avaliacao(1)  # ID da avaliação
"""

from avaliacao_docente.models import AvaliacaoDocente


def validar_media_avaliacao(avaliacao_id):
    """
    Valida se a média está sendo calculada corretamente para uma avaliação.

    Args:
        avaliacao_id: ID da avaliação a ser validada
    """
    try:
        avaliacao = AvaliacaoDocente.objects.get(id=avaliacao_id)
    except AvaliacaoDocente.DoesNotExist:
        print(f"❌ Avaliação com ID {avaliacao_id} não encontrada")
        return

    resultado = avaliacao.calcular_media_geral_questionario_padrao()

    print(f"\n{'=' * 80}")
    print(f"🎯 VALIDAÇÃO DE CÁLCULO DE MÉDIA")
    print(f"{'=' * 80}")
    print(f"Avaliação: {avaliacao}")
    print(f"Professor: {avaliacao.professor.user.get_full_name()}")
    print(f"Disciplina: {avaliacao.disciplina.disciplina_nome}")
    print(f"Turma: {avaliacao.turma.codigo}")
    print(f"Ciclo: {avaliacao.ciclo.nome}")
    print(f"{'=' * 80}")

    if not resultado:
        print("\n❌ Sem dados para cálculo de média")
        print("   Motivo: Nenhuma pergunta de múltipla escolha respondida")
        return

    print(f"\n📊 RESULTADO GERAL:")
    print(f"   Média Geral: {resultado['media_geral']:.4f}")
    print(f"   Total de Perguntas: {resultado['total_perguntas']}")

    # Determinar classificação
    classificacao = avaliacao.get_classificacao_media(resultado["media_geral"])
    print(f"   Classificação: {classificacao}")

    print(f"\n{'─' * 80}")
    print(f"📋 DETALHES POR PERGUNTA:")
    print(f"{'─' * 80}")

    todas_validas = True

    for pergunta_id, dados in resultado["detalhes_por_pergunta"].items():
        print(f"\n   Pergunta {pergunta_id}:")
        print(f"   {dados['enunciado'][:70]}...")
        print(f"   ├─ Média: {dados['media']:.4f}")
        print(f"   ├─ Respondentes: {dados['total_respondentes']}")
        print(f"   ├─ Moda: {dados['moda']}")
        print(f"   └─ Contagens:")

        # Mostrar contagens
        for opcao, count in dados["contagens"].items():
            peso = avaliacao.OPCOES_PESOS[opcao]
            print(f"      • {opcao}: {count} (peso {peso})")

        # Validar cálculo manual
        soma_ponderada = sum(
            dados["contagens"][k] * v for k, v in avaliacao.OPCOES_PESOS.items()
        )
        total = dados["total_respondentes"]
        media_manual = soma_ponderada / total if total > 0 else 0

        diferenca = abs(media_manual - dados["media"])

        if diferenca > 0.0001:
            print(f"\n   ⚠️  ALERTA: Divergência detectada!")
            print(f"      Média esperada: {media_manual:.4f}")
            print(f"      Média obtida:   {dados['media']:.4f}")
            print(f"      Diferença:      {diferenca:.4f}")
            todas_validas = False
        else:
            print(f"   ✅ Cálculo validado (diferença < 0.0001)")

    # Validar média geral
    print(f"\n{'─' * 80}")
    print(f"🎯 VALIDAÇÃO DA MÉDIA GERAL:")
    print(f"{'─' * 80}")

    medias = [d["media"] for d in resultado["detalhes_por_pergunta"].values()]
    media_manual_geral = sum(medias) / len(medias) if medias else 0

    print(f"   Média Calculada: {resultado['media_geral']:.4f}")
    print(f"   Média Manual:    {media_manual_geral:.4f}")
    print(
        f"   Diferença:       {abs(media_manual_geral - resultado['media_geral']):.4f}"
    )

    if abs(media_manual_geral - resultado["media_geral"]) > 0.0001:
        print(f"\n   ❌ DIVERGÊNCIA NA MÉDIA GERAL!")
        todas_validas = False
    else:
        print(f"   ✅ Média geral validada")

    # Estatísticas adicionais
    print(f"\n{'─' * 80}")
    print(f"📈 ESTATÍSTICAS ADICIONAIS:")
    print(f"{'─' * 80}")

    total_respostas = avaliacao.respostas.count()
    total_respondentes = avaliacao.respostas.values("aluno").distinct().count()
    alunos_aptos = avaliacao.alunos_aptos()
    total_alunos_aptos = len(alunos_aptos)

    print(f"   Total de Respostas (registros): {total_respostas}")
    print(f"   Total de Respondentes (alunos únicos): {total_respondentes}")
    print(f"   Total de Alunos Aptos: {total_alunos_aptos}")

    if total_alunos_aptos > 0:
        taxa_resposta = (total_respondentes / total_alunos_aptos) * 100
        print(f"   Taxa de Resposta: {taxa_resposta:.2f}%")

    # Resumo final
    print(f"\n{'=' * 80}")
    if todas_validas:
        print(f"✅ TODOS OS CÁLCULOS ESTÃO CORRETOS!")
    else:
        print(f"⚠️  DIVERGÊNCIAS ENCONTRADAS - REQUER INVESTIGAÇÃO")
    print(f"{'=' * 80}\n")

    return todas_validas


def validar_todas_avaliacoes_ciclo(ciclo_id):
    """
    Valida todas as avaliações de um ciclo.

    Args:
        ciclo_id: ID do ciclo
    """
    from avaliacao_docente.models import CicloAvaliacao

    try:
        ciclo = CicloAvaliacao.objects.get(id=ciclo_id)
    except CicloAvaliacao.DoesNotExist:
        print(f"❌ Ciclo com ID {ciclo_id} não encontrado")
        return

    avaliacoes = AvaliacaoDocente.objects.filter(ciclo=ciclo)

    print(f"\n{'=' * 80}")
    print(f"🎯 VALIDAÇÃO DE TODAS AS AVALIAÇÕES DO CICLO")
    print(f"{'=' * 80}")
    print(f"Ciclo: {ciclo.nome}")
    print(f"Total de Avaliações: {avaliacoes.count()}")
    print(f"{'=' * 80}\n")

    resultados = []

    for avaliacao in avaliacoes:
        print(f"\n{'─' * 80}")
        print(f"Avaliação ID {avaliacao.id}:")
        valida = validar_media_avaliacao(avaliacao.id)
        resultados.append((avaliacao.id, valida))

    # Resumo final
    print(f"\n{'=' * 80}")
    print(f"📊 RESUMO GERAL DO CICLO")
    print(f"{'=' * 80}")

    total = len(resultados)
    validas = sum(1 for _, v in resultados if v)
    invalidas = total - validas

    print(f"   Total de Avaliações: {total}")
    print(f"   ✅ Válidas: {validas}")
    print(f"   ❌ Com Divergências: {invalidas}")

    if invalidas > 0:
        print(f"\n   Avaliações com problemas:")
        for av_id, valida in resultados:
            if not valida:
                print(f"      • Avaliação ID {av_id}")

    print(f"{'=' * 80}\n")


def exemplo_calculo_manual():
    """
    Mostra um exemplo de como o cálculo é feito manualmente.
    """
    print(f"\n{'=' * 80}")
    print(f"📐 EXEMPLO DE CÁLCULO MANUAL")
    print(f"{'=' * 80}\n")

    print("Suponha uma pergunta com as seguintes respostas:")
    print("   • Não atende: 2 respostas")
    print("   • Insuficiente: 6 respostas")
    print("   • Regular: 12 respostas")
    print("   • Bom: 15 respostas")
    print("   • Excelente: 5 respostas")
    print("   TOTAL: 40 respondentes\n")

    print("Pesos padrão:")
    print("   • Não atende = 0.00")
    print("   • Insuficiente = 0.25")
    print("   • Regular = 0.50")
    print("   • Bom = 0.75")
    print("   • Excelente = 1.00\n")

    print("Cálculo:")
    print("   Soma ponderada = (2×0.00) + (6×0.25) + (12×0.50) + (15×0.75) + (5×1.00)")
    print("   Soma ponderada = 0.00 + 1.50 + 6.00 + 11.25 + 5.00")
    print("   Soma ponderada = 23.75\n")

    print("   Média = Soma ponderada / Total respondentes")
    print("   Média = 23.75 / 40")
    print("   Média = 0.5938\n")

    print("Classificação:")
    print("   0.50 ≤ 0.5938 < 0.75 → Regular\n")

    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    print("Este script deve ser executado via Django shell:")
    print("   python manage.py shell")
    print("   from scripts.validar_calculos_media import validar_media_avaliacao")
    print("   validar_media_avaliacao(1)")
    print("\nOu para validar todas as avaliações de um ciclo:")
    print(
        "   from scripts.validar_calculos_media import validar_todas_avaliacoes_ciclo"
    )
    print("   validar_todas_avaliacoes_ciclo(1)")
    print("\nOu ver exemplo de cálculo:")
    print("   from scripts.validar_calculos_media import exemplo_calculo_manual")
    print("   exemplo_calculo_manual()")
