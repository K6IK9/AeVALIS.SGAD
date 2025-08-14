"""
Teste para verificar se a correção do erro AttributeError foi aplicada
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from avaliacao_docente.models import QuestionarioAvaliacao


def teste_atributo_questionario():
    """
    Testa se o QuestionarioAvaliacao possui o atributo 'titulo' corretamente
    """
    print("=== TESTANDO ATRIBUTO DO QUESTIONÁRIO ===")

    # Verificar se o modelo possui o atributo correto
    if hasattr(QuestionarioAvaliacao, "titulo"):
        print("✓ O modelo QuestionarioAvaliacao possui o atributo 'titulo'")
    else:
        print("✗ O modelo QuestionarioAvaliacao NÃO possui o atributo 'titulo'")

    # Verificar se o modelo NÃO possui o atributo incorreto
    if not hasattr(QuestionarioAvaliacao, "nome"):
        print("✓ O modelo QuestionarioAvaliacao NÃO possui o atributo 'nome' (correto)")
    else:
        print("✗ O modelo QuestionarioAvaliacao possui o atributo 'nome' (incorreto)")

    # Tentar criar um questionário de teste
    try:
        from django.contrib.auth.models import User

        # Verificar se existe um usuário para usar como criador
        user = User.objects.first()
        if not user:
            print("ℹ️  Não há usuários no sistema para criar um questionário de teste")
            return

        # Criar um questionário de teste
        questionario = QuestionarioAvaliacao.objects.create(
            titulo="Teste de Correção",
            descricao="Questionário para testar a correção do erro AttributeError",
            criado_por=user,
        )

        print(f"✓ Questionário criado com sucesso: {questionario.titulo}")
        print(f"✓ Método __str__ funcionando: {str(questionario)}")

        # Simular acesso ao atributo que estava causando erro
        nome_questionario = questionario.titulo  # Usado corretamente
        print(f"✓ Acesso ao atributo 'titulo' funcionando: {nome_questionario}")

        # Limpeza
        questionario.delete()
        print("✓ Questionário de teste removido")

    except Exception as e:
        print(f"✗ Erro ao testar criação do questionário: {e}")

    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    teste_atributo_questionario()
