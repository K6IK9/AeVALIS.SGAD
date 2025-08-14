#!/usr/bin/env python3
"""
Script para configurar arquivos estáticos do projeto Django
Este script deve ser executado após baixar o projeto em um novo ambiente
"""

import os
import sys
import django
from django.core.management import execute_from_command_line


def setup_static_files():
    """Configura os arquivos estáticos do projeto"""

    # Configurar o Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
    django.setup()

    print("🔧 Configurando arquivos estáticos...")

    # Coletar arquivos estáticos
    print("\n📁 Coletando arquivos estáticos...")
    try:
        execute_from_command_line(["manage.py", "collectstatic", "--noinput"])
        print("✅ Arquivos estáticos coletados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao coletar arquivos estáticos: {e}")
        return False

    # Verificar se os arquivos estão no lugar correto
    print("\n🔍 Verificando arquivos estáticos...")

    from django.conf import settings

    # Verificar diretório static
    static_dir = settings.STATICFILES_DIRS[0]
    if os.path.exists(static_dir):
        print(f"✅ Diretório static encontrado: {static_dir}")

        # Verificar assets
        assets_dir = os.path.join(static_dir, "assets")
        if os.path.exists(assets_dir):
            assets_files = os.listdir(assets_dir)
            print(f"✅ Assets encontrados: {len(assets_files)} arquivos")
            for file in assets_files:
                print(f"   - {file}")
        else:
            print("❌ Diretório assets não encontrado!")
            return False
    else:
        print(f"❌ Diretório static não encontrado: {static_dir}")
        return False

    # Verificar diretório staticfiles
    staticfiles_dir = settings.STATIC_ROOT
    if os.path.exists(staticfiles_dir):
        print(f"✅ Diretório staticfiles encontrado: {staticfiles_dir}")
    else:
        print(f"❌ Diretório staticfiles não encontrado: {staticfiles_dir}")

    print("\n🎉 Configuração de arquivos estáticos concluída!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python manage.py runserver")
    print("2. Acesse: http://127.0.0.1:8000")
    print("3. Verifique se as imagens estão carregando corretamente")

    return True


if __name__ == "__main__":
    success = setup_static_files()
    if not success:
        sys.exit(1)
