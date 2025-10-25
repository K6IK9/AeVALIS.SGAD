#!/usr/bin/env python3
"""
Script para atualizar títulos de templates HTML com variáveis de branding.

Substitui títulos hard-coded "IF SADD" por variáveis dinâmicas que respeitam
a flag BRAND_ENABLE_NEW.
"""

import re
from pathlib import Path

# Diretório de templates
TEMPLATES_DIR = Path("/home/k6ik9/Documentos/GitHub/avaliacao_docente_suap/templates")

# Padrão de busca e substituição para títulos
TITLE_PATTERN = re.compile(
    r"<title>(.*?)IF SADD(.*?)</title>", re.IGNORECASE | re.DOTALL
)

TITLE_REPLACEMENT = r"<title>\1{% if brand.enabled %}{{ brand.name_short }}{% else %}{{ brand.name_old }}{% endif %}\2</title>"


def update_template_titles():
    """Atualiza todos os títulos HTML nos templates."""
    updated_files = []

    # Buscar todos os arquivos HTML
    for html_file in TEMPLATES_DIR.rglob("*.html"):
        try:
            content = html_file.read_text(encoding="utf-8")

            # Verificar se contém "IF SADD" no title
            if "<title>" in content and "IF SADD" in content:
                # Aplicar substituição
                new_content = TITLE_PATTERN.sub(TITLE_REPLACEMENT, content)

                if new_content != content:
                    # Salvar arquivo atualizado
                    html_file.write_text(new_content, encoding="utf-8")
                    updated_files.append(str(html_file.relative_to(TEMPLATES_DIR)))
                    print(f"✓ Atualizado: {html_file.relative_to(TEMPLATES_DIR)}")

        except Exception as e:
            print(f"✗ Erro em {html_file}: {e}")

    print(f"\n{'='*60}")
    print(f"Total de arquivos atualizados: {len(updated_files)}")
    print(f"{'='*60}")

    return updated_files


if __name__ == "__main__":
    print("Atualizando títulos de templates com variáveis de branding...\n")
    updated = update_template_titles()
