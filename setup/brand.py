"""
Context processor para injetar variáveis de branding em todos os templates.

Este módulo centraliza a identidade visual do sistema, permitindo alternar
entre a marca antiga e a nova através da flag BRAND_ENABLE_NEW.

Uso nos templates:
    {{ brand.name_short }} → "ÆVALIS" ou "IF SADD"
    {{ brand.name_full }} → "Sistema de Avaliação Docente"
    {{ brand.logo_curta }} → Path para logo compacta
    {{ brand.logo_extend }} → Path para logo estendida
    {{ brand.logo_glass }} → Path para logo glass/transparente
    {{ brand.alt.logo_curta }} → Texto alternativo para acessibilidade
"""

from django.conf import settings


def brand_context(request):
    """
    Retorna variáveis de branding disponíveis em todos os templates.

    Returns:
        dict: Dicionário com variáveis de marca:
            - name_short: Nome curto (ÆVALIS)
            - name_full: Nome completo (Sistema de Avaliação Docente)
            - name_old: Nome antigo (IF SADD) - para referência
            - logo_curta: Path da logo compacta
            - logo_extend: Path da logo estendida
            - logo_glass: Path da logo glass
            - alt: Dict com textos alt para cada logo
            - enabled: Boolean indicando se nova marca está ativa
    """
    return {
        "brand": {
            "name_short": settings.BRAND_NAME_SHORT,
            "name_full": settings.BRAND_NAME_FULL,
            "name_old": settings.BRAND_NAME_OLD,
            "logo_curta": settings.BRAND_ASSETS["logo_curta"],
            "logo_extend": settings.BRAND_ASSETS["logo_extend"],
            "logo_glass": settings.BRAND_ASSETS["logo_glass"],
            "favicon": settings.BRAND_ASSETS["favicon"],
            "alt": settings.BRAND_ALT_TEXT,
            "enabled": settings.BRAND_ENABLE_NEW,
        }
    }
