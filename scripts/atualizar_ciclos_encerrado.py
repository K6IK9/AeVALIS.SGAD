#!/usr/bin/env python
"""
Script para atualizar os ciclos existentes com o novo campo 'encerrado'.

Este script analisa os ciclos que estavam com ativo=False e os marca
adequadamente com encerrado=True.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.utils import timezone
from avaliacao_docente.models import CicloAvaliacao


def atualizar_ciclos():
    """
    Atualiza os ciclos existentes:
    1. Ciclos com ativo=False que foram "encerrados" -> marca encerrado=True e restaura ativo=True
    2. Mantém os ciclos deletados (soft delete) com ativo=False
    """

    print("=" * 80)
    print("ATUALIZANDO CICLOS EXISTENTES")
    print("=" * 80)

    # Buscar TODOS os ciclos (incluindo inativos)
    todos_ciclos = CicloAvaliacao.all_objects.all()
    total = todos_ciclos.count()

    print(f"\n📊 Total de ciclos no banco: {total}")

    if total == 0:
        print("⚠️  Nenhum ciclo encontrado no banco de dados.")
        return

    # Separar por status atual
    ativos = todos_ciclos.filter(ativo=True)
    inativos = todos_ciclos.filter(ativo=False)

    print(f"  - Ciclos ativos (ativo=True): {ativos.count()}")
    print(f"  - Ciclos inativos (ativo=False): {inativos.count()}")

    print("\n" + "=" * 80)
    print("ESTRATÉGIA DE ATUALIZAÇÃO")
    print("=" * 80)

    # Analisar ciclos inativos
    if inativos.exists():
        print(f"\n🔍 Analisando {inativos.count()} ciclo(s) inativo(s)...")
        print("\nEsses ciclos estavam usando ativo=False para dois propósitos:")
        print("  1. Encerramento manual (não aceita respostas)")
        print("  2. Soft delete (exclusão lógica)")
        print("\n⚠️  DECISÃO NECESSÁRIA:")
        print("  Vamos assumir que ciclos com ativo=False foram ENCERRADOS manualmente")
        print("  e vamos restaurá-los como visíveis (ativo=True, encerrado=True)")

        for ciclo in inativos:
            print(f"\n  📋 Ciclo: {ciclo.nome}")
            print(f"     - ID: {ciclo.id}")
            print(
                f"     - Período: {ciclo.data_inicio.strftime('%d/%m/%Y')} - {ciclo.data_fim.strftime('%d/%m/%Y')}"
            )
            print(
                f"     - Status atual: ativo={ciclo.ativo}, encerrado={ciclo.encerrado}"
            )

    # Perguntar confirmação
    print("\n" + "=" * 80)
    print("AÇÃO A SER EXECUTADA:")
    print("=" * 80)
    print("\n1️⃣  Ciclos com ativo=False serão:")
    print("   - Marcados como encerrado=True")
    print("   - Restaurados para ativo=True (ficarão visíveis)")
    print("   - data_encerramento será definida como data_exclusao (se existir)")
    print("\n2️⃣  Ciclos com ativo=True permanecem:")
    print("   - ativo=True")
    print("   - encerrado=False (valor padrão já definido na migration)")

    resposta = (
        input("\n❓ Deseja continuar com a atualização? (sim/não): ").strip().lower()
    )

    if resposta not in ["sim", "s", "yes", "y"]:
        print("\n❌ Atualização cancelada pelo usuário.")
        return

    print("\n" + "=" * 80)
    print("EXECUTANDO ATUALIZAÇÃO...")
    print("=" * 80)

    # Atualizar ciclos inativos
    ciclos_atualizados = 0

    for ciclo in inativos:
        print(f"\n🔄 Atualizando: {ciclo.nome}")

        # Marcar como encerrado
        ciclo.encerrado = True

        # Usar data_exclusao como data_encerramento se existir
        if ciclo.data_exclusao:
            ciclo.data_encerramento = ciclo.data_exclusao
            print(
                f"   ✓ data_encerramento definida: {ciclo.data_encerramento.strftime('%d/%m/%Y %H:%M')}"
            )
        else:
            # Se não tem data_exclusao, usar a data_fim como referência
            ciclo.data_encerramento = ciclo.data_fim
            print(
                f"   ✓ data_encerramento definida como data_fim: {ciclo.data_encerramento.strftime('%d/%m/%Y %H:%M')}"
            )

        # Restaurar para ativo (visível)
        ciclo.ativo = True
        ciclo.data_exclusao = None  # Limpar data_exclusao

        # Salvar
        # IMPORTANTE: Usar skip_validation=True para evitar triggering de signals
        # que podem causar problemas de duplicação
        from django.db.models import signals
        from avaliacao_docente.signals import criar_avaliacoes_pos_save

        # Desconectar signal temporariamente
        signals.post_save.disconnect(criar_avaliacoes_pos_save, sender=CicloAvaliacao)

        ciclo.save(
            update_fields=["ativo", "encerrado", "data_encerramento", "data_exclusao"]
        )

        # Reconectar signal
        signals.post_save.connect(criar_avaliacoes_pos_save, sender=CicloAvaliacao)

        print(f"   ✓ Ciclo restaurado e marcado como encerrado")
        ciclos_atualizados += 1

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DA ATUALIZAÇÃO")
    print("=" * 80)
    print(f"\n✅ Total de ciclos atualizados: {ciclos_atualizados}")
    print(f"✅ Ciclos agora visíveis e marcados como encerrados: {ciclos_atualizados}")

    # Verificar resultado final
    print("\n" + "=" * 80)
    print("ESTADO FINAL DOS CICLOS")
    print("=" * 80)

    ativos_finais = CicloAvaliacao.objects.filter(ativo=True)
    encerrados_finais = CicloAvaliacao.objects.filter(encerrado=True)

    print(f"\n📊 Ciclos ativos (ativo=True): {ativos_finais.count()}")
    print(f"📊 Ciclos encerrados (encerrado=True): {encerrados_finais.count()}")

    for ciclo in CicloAvaliacao.objects.all():
        status = "🟢 Ativo" if not ciclo.encerrado else "🔒 Encerrado"
        print(f"\n  {status} - {ciclo.nome}")
        print(f"     ativo={ciclo.ativo}, encerrado={ciclo.encerrado}")

    print("\n✅ Atualização concluída com sucesso!")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Teste o sistema acessando a lista de ciclos")
    print("   2. Verifique se ciclos encerrados aparecem corretamente")
    print("   3. Se tudo estiver OK, faça commit das mudanças")


if __name__ == "__main__":
    try:
        atualizar_ciclos()
    except KeyboardInterrupt:
        print("\n\n❌ Atualização interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
