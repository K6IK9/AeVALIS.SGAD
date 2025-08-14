#!/usr/bin/env python3
"""
Script de build específico para Vercel
Executa migrações e coleta arquivos estáticos
"""

import os
import django
import subprocess
import sys


def run_command(command):
    """Executa comando e captura output"""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        print(f"Stderr: {e.stderr}")
        return False


def main():
    print("🚀 Iniciando build para Vercel...")

    # Configurar Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

    print("🗄️ Executando migrações...")
    if not run_command("python manage.py migrate --noinput"):
        sys.exit(1)

    print("📁 Coletando arquivos estáticos...")
    if not run_command("python manage.py collectstatic --noinput --clear"):
        sys.exit(1)

    print("🔍 Verificando arquivos coletados...")
    run_command("ls -la staticfiles/")
    run_command("ls -la staticfiles/assets/ || echo 'Assets não encontrados'")

    print("✅ Build concluído com sucesso!")


if __name__ == "__main__":
    main()
