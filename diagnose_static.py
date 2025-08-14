#!/usr/bin/env python3
"""
Script de verificação para diagnóstico de problemas com arquivos estáticos
Execute este script para identificar e resolver problemas automaticamente
"""

import os
import sys
import django
from pathlib import Path

# Configuração do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.conf import settings
from django.core.management import call_command


def print_header(title):
    """Imprime cabeçalho formatado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_static_directories():
    """Verifica se os diretórios estáticos existem"""
    print_header("VERIFICAÇÃO DE DIRETÓRIOS ESTÁTICOS")

    # Verificar STATICFILES_DIRS
    for i, static_dir in enumerate(settings.STATICFILES_DIRS):
        print(f"\n{i+1}. Verificando: {static_dir}")
        if os.path.exists(static_dir):
            print(f"   ✅ Diretório existe")

            # Verificar assets
            assets_dir = os.path.join(static_dir, "assets")
            if os.path.exists(assets_dir):
                print(f"   ✅ Pasta 'assets' encontrada")

                # Listar arquivos SVG
                svg_files = [f for f in os.listdir(assets_dir) if f.endswith(".svg")]
                print(f"   📁 {len(svg_files)} arquivos SVG encontrados:")
                for svg in svg_files:
                    print(f"      - {svg}")
            else:
                print(f"   ❌ Pasta 'assets' não encontrada")
        else:
            print(f"   ❌ Diretório não existe")

    # Verificar STATIC_ROOT
    print(f"\nVerificando STATIC_ROOT: {settings.STATIC_ROOT}")
    if os.path.exists(settings.STATIC_ROOT):
        print(f"   ✅ STATIC_ROOT existe")

        # Contar arquivos
        file_count = sum(len(files) for _, _, files in os.walk(settings.STATIC_ROOT))
        print(f"   📊 {file_count} arquivos coletados")
    else:
        print(f"   ❌ STATIC_ROOT não existe")


def check_static_files():
    """Verifica arquivos estáticos específicos"""
    print_header("VERIFICAÇÃO DE ARQUIVOS CRÍTICOS")

    critical_files = [
        "assets/saad_logo.svg",
        "assets/perfil.svg",
        "assets/email.svg",
        "assets/eye.svg",
        "assets/lock.svg",
        "assets/back_left.svg",
        "assets/back_right.svg",
        "assets/back_seta.svg",
        "assets/backg_left.svg",
        "assets/backg_right.svg",
        "image.png",
    ]

    for file_path in critical_files:
        found = False

        # Verificar em STATICFILES_DIRS
        for static_dir in settings.STATICFILES_DIRS:
            full_path = os.path.join(static_dir, file_path)
            if os.path.exists(full_path):
                print(f"✅ {file_path} - Encontrado em {static_dir}")
                found = True
                break

        if not found:
            # Verificar em STATIC_ROOT
            full_path = os.path.join(settings.STATIC_ROOT, file_path)
            if os.path.exists(full_path):
                print(f"⚠️  {file_path} - Apenas em STATIC_ROOT")
            else:
                print(f"❌ {file_path} - NÃO ENCONTRADO")


def check_settings():
    """Verifica configurações do Django"""
    print_header("VERIFICAÇÃO DE CONFIGURAÇÕES")

    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_FINDERS: {len(settings.STATICFILES_FINDERS)} finders")

    for finder in settings.STATICFILES_FINDERS:
        print(f"  - {finder}")


def check_templates():
    """Verifica referências estáticas em templates"""
    print_header("VERIFICAÇÃO DE TEMPLATES")

    templates_dir = Path(settings.BASE_DIR) / "templates"
    static_refs = []

    if templates_dir.exists():
        for template_file in templates_dir.rglob("*.html"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "{% static" in content:
                        # Contar referências
                        count = content.count("{% static")
                        static_refs.append((template_file.name, count))
            except Exception as e:
                print(f"❌ Erro ao ler {template_file}: {e}")

    print(f"📊 {len(static_refs)} templates com referências estáticas:")
    for template, count in static_refs:
        print(f"  - {template}: {count} referências")


def fix_static_files():
    """Tenta corrigir problemas automaticamente"""
    print_header("CORREÇÃO AUTOMÁTICA")

    try:
        # Coletar arquivos estáticos
        print("🔧 Coletando arquivos estáticos...")
        call_command("collectstatic", "--noinput", "--clear")
        print("✅ Arquivos coletados com sucesso")

        # Verificar se assets foram copiados
        assets_source = Path(settings.STATICFILES_DIRS[0]) / "assets"
        assets_dest = Path(settings.STATIC_ROOT) / "assets"

        if assets_source.exists() and assets_dest.exists():
            print("✅ Assets copiados corretamente")
        else:
            print("⚠️  Problemas na cópia dos assets")

    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")


def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO DE ARQUIVOS ESTÁTICOS")
    print("=" * 60)

    # Verificações
    check_static_directories()
    check_static_files()
    check_settings()
    check_templates()

    # Perguntar se deve tentar correção
    print_header("CORREÇÃO AUTOMÁTICA")
    response = input("Deseja tentar a correção automática? (s/n): ").lower().strip()

    if response in ["s", "sim", "y", "yes"]:
        fix_static_files()

        # Verificar novamente
        print_header("VERIFICAÇÃO PÓS-CORREÇÃO")
        check_static_files()

    print_header("DIAGNÓSTICO CONCLUÍDO")
    print("💡 Dicas:")
    print("1. Execute 'python manage.py runserver' para testar")
    print("2. Acesse http://127.0.0.1:8000/static/assets/saad_logo.svg")
    print("3. Se ainda houver problemas, verifique as permissões dos arquivos")


if __name__ == "__main__":
    main()
