#!/usr/bin/env python3
"""
Script de teste para a funcionalidade de gerenciar usuários
"""

import os
import sys

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

import django

django.setup()

# Importar depois do setup do Django
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from avaliacao_docente.models import *
from avaliacao_docente.forms import GerenciarUsuarioForm
from rolepermissions.roles import assign_role


def criar_usuario_teste():
    """Cria um usuário admin para teste"""
    try:
        # Criar usuário admin
        admin_user = User.objects.create_user(
            username="admin_teste",
            email="admin@teste.com",
            password="123456",
            first_name="Admin",
            last_name="Teste",
        )
        assign_role(admin_user, "admin")
        print(f"✓ Usuário admin criado: {admin_user.username}")
        return admin_user
    except Exception as e:
        print(f"✗ Erro ao criar usuário admin: {e}")
        return None


def testar_formulario_usuario():
    """Testa o formulário de gerenciar usuários"""
    print("\n=== Testando Formulário de Usuário ===")

    # Dados válidos
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
        usuario = form.save(commit=False)
        usuario.set_password("123456")
        usuario.save()
        print(f"✓ Usuário criado: {usuario.username}")
    else:
        print("✗ Formulário inválido:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")

    # Dados inválidos (sem username)
    dados_invalidos = {
        "first_name": "Teste",
        "last_name": "Usuário",
        "email": "teste2@exemplo.com",
    }

    form_invalido = GerenciarUsuarioForm(data=dados_invalidos)
    if not form_invalido.is_valid():
        print("✓ Formulário corretamente inválido com dados incorretos")
    else:
        print("✗ Formulário deveria ser inválido")


def testar_view_gerenciar_usuarios():
    """Testa a view de gerenciar usuários"""
    print("\n=== Testando View Gerenciar Usuários ===")

    # Criar usuário admin
    admin_user = criar_usuario_teste()
    if not admin_user:
        print("✗ Não foi possível criar usuário admin")
        return

    client = Client()

    # Testar acesso sem login
    response = client.get(reverse("gerenciar_usuarios"))
    if response.status_code == 302:  # Redirect para login
        print("✓ Acesso negado sem login (redirecionamento)")
    else:
        print(f"✗ Deveria redirecionar sem login, mas retornou: {response.status_code}")

    # Login com usuário admin
    login_success = client.login(username="admin_teste", password="123456")
    if login_success:
        print("✓ Login realizado com sucesso")
    else:
        print("✗ Falha no login")
        return

    # Testar GET na view
    response = client.get(reverse("gerenciar_usuarios"))
    if response.status_code == 200:
        print("✓ GET na view funcionou")
        print(
            f"  - Template usado: {response.templates[0].name if response.templates else 'Não encontrado'}"
        )
    else:
        print(f"✗ GET na view falhou: {response.status_code}")

    # Testar POST para criar usuário
    dados_post = {
        "username": "novo_usuario",
        "first_name": "Novo",
        "last_name": "Usuário",
        "email": "novo@exemplo.com",
        "is_active": True,
    }

    response = client.post(reverse("gerenciar_usuarios"), data=dados_post)
    if response.status_code == 302:  # Redirect após sucesso
        print("✓ POST para criar usuário funcionou")

        # Verificar se o usuário foi criado
        if User.objects.filter(username="novo_usuario").exists():
            print("✓ Usuário foi criado no banco de dados")
        else:
            print("✗ Usuário não foi criado no banco de dados")
    else:
        print(f"✗ POST para criar usuário falhou: {response.status_code}")


def testar_template_existe():
    """Verifica se o template existe"""
    print("\n=== Testando Template ===")

    template_path = os.path.join(
        settings.BASE_DIR, "templates", "gerenciar_usuarios.html"
    )

    if os.path.exists(template_path):
        print("✓ Template gerenciar_usuarios.html existe")

        # Ler o template e verificar alguns elementos básicos
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


def testar_urls():
    """Testa se as URLs estão configuradas corretamente"""
    print("\n=== Testando URLs ===")

    try:
        url = reverse("gerenciar_usuarios")
        print(f"✓ URL 'gerenciar_usuarios' resolvida: {url}")
    except Exception as e:
        print(f"✗ Erro ao resolver URL 'gerenciar_usuarios': {e}")

    try:
        url = reverse("editar_usuario", args=[1])
        print(f"✓ URL 'editar_usuario' resolvida: {url}")
    except Exception as e:
        print(f"✗ Erro ao resolver URL 'editar_usuario': {e}")


def limpar_dados_teste():
    """Remove os dados de teste criados"""
    print("\n=== Limpando Dados de Teste ===")

    # Remover usuários de teste
    usuarios_teste = User.objects.filter(
        username__in=["admin_teste", "teste_usuario", "novo_usuario"]
    )
    count = usuarios_teste.count()
    usuarios_teste.delete()
    print(f"✓ {count} usuários de teste removidos")


def main():
    """Função principal do teste"""
    print("=== TESTE DA FUNCIONALIDADE GERENCIAR USUÁRIOS ===")
    print(f"Django Version: {django.get_version()}")
    print(f"Python Version: {sys.version}")
    print("=" * 50)

    try:
        # Executar testes
        testar_urls()
        testar_template_existe()
        testar_formulario_usuario()
        testar_view_gerenciar_usuarios()

        print("\n" + "=" * 50)
        print("RESUMO DOS TESTES")
        print("=" * 50)
        print("✓ = Teste passou")
        print("✗ = Teste falhou")
        print(
            "\nSe todos os testes passaram, a funcionalidade está funcionando corretamente!"
        )

    except Exception as e:
        print(f"\n✗ Erro geral durante os testes: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Limpar dados de teste
        try:
            limpar_dados_teste()
        except Exception as e:
            print(f"Erro ao limpar dados de teste: {e}")


if __name__ == "__main__":
    main()
