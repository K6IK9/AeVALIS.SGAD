"""
Script de teste simples para verificar a funcionalidade de gerenciar usuários
"""

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from avaliacao_docente.forms import GerenciarUsuarioForm
from rolepermissions.roles import assign_role


def test_gerenciar_usuarios():
    print("=== TESTE DA FUNCIONALIDADE GERENCIAR USUÁRIOS ===\n")

    # Teste 1: Verificar se as URLs estão configuradas
    print("1. Testando URLs...")
    try:
        url = reverse("gerenciar_usuarios")
        print(f"✓ URL 'gerenciar_usuarios' resolvida: {url}")
    except Exception as e:
        print(f"✗ Erro ao resolver URL 'gerenciar_usuarios': {e}")
        return

    # Teste 2: Verificar se o formulário funciona
    print("\n2. Testando formulário...")
    dados_validos = {
        "username": "teste_usuario",
        "first_name": "Teste",
        "last_name": "Usuário",
        "email": "teste@exemplo.com",
        "is_active": True,
    }

    form = GerenciarUsuarioForm(data=dados_validos)
    if form.is_valid():
        print("✓ Formulário válido com dados corretos")
    else:
        print("✗ Formulário inválido:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")

    # Teste 3: Verificar se conseguimos criar um usuário admin
    print("\n3. Testando criação de usuário admin...")
    try:
        # Deletar se já existe
        User.objects.filter(username="admin_teste").delete()

        admin_user = User.objects.create_user(
            username="admin_teste",
            email="admin@teste.com",
            password="123456",
            first_name="Admin",
            last_name="Teste",
        )
        assign_role(admin_user, "admin")
        print(f"✓ Usuário admin criado: {admin_user.username}")
    except Exception as e:
        print(f"✗ Erro ao criar usuário admin: {e}")
        return

    # Teste 4: Verificar acesso à view
    print("\n4. Testando acesso à view...")
    client = Client()

    # Testar sem login
    response = client.get(reverse("gerenciar_usuarios"))
    if response.status_code == 302:
        print("✓ Acesso negado sem login (redirecionamento)")
    else:
        print(f"✗ Deveria redirecionar sem login, mas retornou: {response.status_code}")

    # Testar com login
    login_success = client.login(username="admin_teste", password="123456")
    if login_success:
        print("✓ Login realizado com sucesso")

        response = client.get(reverse("gerenciar_usuarios"))
        if response.status_code == 200:
            print("✓ GET na view funcionou")
            print(
                f"  - Context keys: {list(response.context.keys()) if response.context else 'Não encontrado'}"
            )
        else:
            print(f"✗ GET na view falhou: {response.status_code}")
    else:
        print("✗ Falha no login")

    # Teste 5: Verificar se o template existe
    print("\n5. Testando template...")
    import os
    from django.conf import settings

    template_path = os.path.join(
        settings.BASE_DIR, "templates", "gerenciar_usuarios.html"
    )

    if os.path.exists(template_path):
        print("✓ Template gerenciar_usuarios.html existe")

        # Verificar conteúdo básico
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "form" in content:
            print("✓ Template contém referência ao formulário")
        else:
            print("✗ Template não contém referência ao formulário")

        if "usuarios_detalhados" in content:
            print("✓ Template contém referência aos usuários")
        else:
            print("✗ Template não contém referência aos usuários")
    else:
        print("✗ Template gerenciar_usuarios.html não existe")

    # Limpeza
    print("\n6. Limpando dados de teste...")
    User.objects.filter(username__in=["admin_teste", "teste_usuario"]).delete()
    print("✓ Dados de teste removidos")

    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    test_gerenciar_usuarios()
