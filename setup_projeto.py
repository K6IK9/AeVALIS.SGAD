#!/usr/bin/env python3
"""
Script de setup automático para o Sistema de Avaliação Docente
Execute este script após baixar o projeto para configurar tudo automaticamente
"""

import os
import sys
import subprocess
from pathlib import Path


def print_step(step_number, description):
    """Imprime passo formatado"""
    print(f"\n🔄 Passo {step_number}: {description}")
    print("-" * 50)


def run_command(command, description):
    """Executa comando e trata erros"""
    try:
        print(f"Executando: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            if result.stdout:
                print(f"   📋 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Erro")
            if result.stderr:
                print(f"   🚨 Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False


def check_python():
    """Verifica se o Python está instalado"""
    print_step(1, "Verificando Python")

    try:
        result = subprocess.run(
            [sys.executable, "--version"], capture_output=True, text=True
        )
        print(f"✅ Python encontrado: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python não encontrado: {e}")
        return False


def install_requirements():
    """Instala dependências do requirements.txt"""
    print_step(2, "Instalando dependências")

    if not Path("requirements.txt").exists():
        print("❌ Arquivo requirements.txt não encontrado")
        return False

    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Instalação de dependências",
    )


def setup_database():
    """Configura o banco de dados"""
    print_step(3, "Configurando banco de dados")

    # Fazer migrações
    if not run_command(f"{sys.executable} manage.py migrate", "Aplicação de migrações"):
        return False

    return True


def setup_static_files():
    """Configura arquivos estáticos"""
    print_step(4, "Configurando arquivos estáticos")

    # Verificar se o diretório static existe
    static_dir = Path("static")
    if not static_dir.exists():
        print("⚠️  Diretório 'static' não encontrado, criando...")
        static_dir.mkdir(exist_ok=True)

        # Criar assets
        assets_dir = static_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        print("✅ Diretórios criados")

    # Coletar arquivos estáticos
    return run_command(
        f"{sys.executable} manage.py collectstatic --noinput --clear",
        "Coleta de arquivos estáticos",
    )


def verify_static_files():
    """Verifica se os arquivos estáticos estão corretos"""
    print_step(5, "Verificando arquivos estáticos")

    critical_files = [
        "static/assets/saad_logo.svg",
        "static/assets/perfil.svg",
        "static/assets/email.svg",
        "static/image.png",
    ]

    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print("⚠️  Arquivos estáticos ausentes:")
        for file_path in missing_files:
            print(f"   - {file_path}")

        # Tentar copiar do staticfiles
        print("🔄 Tentando copiar do staticfiles...")
        staticfiles_dir = Path("staticfiles")
        if staticfiles_dir.exists():
            try:
                # Copiar assets
                source_assets = staticfiles_dir / "assets"
                dest_assets = Path("static") / "assets"

                if source_assets.exists():
                    import shutil

                    shutil.copytree(source_assets, dest_assets, dirs_exist_ok=True)
                    print("✅ Assets copiados do staticfiles")

                # Copiar image.png
                source_image = staticfiles_dir / "image.png"
                dest_image = Path("static") / "image.png"
                if source_image.exists():
                    shutil.copy2(source_image, dest_image)
                    print("✅ image.png copiado")

            except Exception as e:
                print(f"❌ Erro ao copiar arquivos: {e}")
    else:
        print("✅ Todos os arquivos estáticos encontrados")

    return True


def create_superuser():
    """Pergunta se deve criar superusuário"""
    print_step(6, "Criação de superusuário")

    response = input("Deseja criar um superusuário? (s/n): ").lower().strip()
    if response in ["s", "sim", "y", "yes"]:
        return run_command(
            f"{sys.executable} manage.py createsuperuser", "Criação de superusuário"
        )
    else:
        print("⏭️  Pulando criação de superusuário")
        return True


def test_server():
    """Testa se o servidor pode ser iniciado"""
    print_step(7, "Teste do servidor")

    print("🔄 Testando se o servidor pode ser iniciado...")
    print("   (Pressione Ctrl+C para interromper o teste)")

    try:
        # Iniciar servidor em modo de teste
        process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", "--noreload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Aguardar alguns segundos
        import time

        time.sleep(3)

        # Verificar se o processo ainda está rodando
        if process.poll() is None:
            print("✅ Servidor iniciado com sucesso")
            print("   🌐 Teste manual: http://127.0.0.1:8000/")

            # Terminar processo
            process.terminate()
            process.wait()
            return True
        else:
            # Processo terminou com erro
            stdout, stderr = process.communicate()
            print("❌ Erro ao iniciar servidor")
            if stderr:
                print(f"   🚨 Erro: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Erro no teste do servidor: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 SETUP AUTOMÁTICO - Sistema de Avaliação Docente")
    print("=" * 60)
    print("Este script vai configurar automaticamente o projeto.")
    print("Certifique-se de estar no diretório raiz do projeto.")
    print()

    input("Pressione Enter para continuar...")

    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Erro: manage.py não encontrado")
        print("   Certifique-se de estar no diretório raiz do projeto")
        sys.exit(1)

    # Executar passos
    steps = [
        check_python,
        install_requirements,
        setup_database,
        setup_static_files,
        verify_static_files,
        create_superuser,
        test_server,
    ]

    success_count = 0

    for step in steps:
        try:
            if step():
                success_count += 1
            else:
                print(f"⚠️  Passo falhou, mas continuando...")
        except KeyboardInterrupt:
            print("\n🛑 Setup interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    # Resultado final
    print("\n" + "=" * 60)
    print(f"🎯 SETUP CONCLUÍDO: {success_count}/{len(steps)} passos executados")
    print("=" * 60)

    if success_count >= len(steps) - 1:  # Permitir falha em 1 passo
        print("✅ Projeto configurado com sucesso!")
        print("\n🚀 Para iniciar o servidor:")
        print("   python manage.py runserver")
        print("\n🌐 Acesse: http://127.0.0.1:8000/")
    else:
        print("⚠️  Alguns passos falharam. Verifique os erros acima.")
        print("\n🔧 Para diagnóstico detalhado:")
        print("   python diagnose_static.py")

    print("\n📚 Documentação adicional:")
    print("   - STATIC_FILES_README.md")
    print("   - README.md")


if __name__ == "__main__":
    main()
