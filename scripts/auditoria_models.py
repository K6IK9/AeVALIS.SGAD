#!/usr/bin/env python
"""
Script de Auditoria de Duplicidades em Models Django
Detecta campos, métodos, choices, constraints e padrões repetidos
"""

import os
import sys
import django
import json
import hashlib
import inspect
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from django.apps import apps
from django.db import models


class ModelAuditor:
    """Classe principal para auditoria de duplicidades"""

    def __init__(self):
        self.models = []
        self.duplicidades = {
            "campos_repetidos": [],
            "metodos_similares": [],
            "choices_duplicados": [],
            "constraints_sobrepostos": [],
            "relacionamentos_redundantes": [],
            "padroes_transversais": [],
        }
        self.limiar_similaridade = 0.85

    def run(self):
        """Executa auditoria completa"""
        print("=" * 80)
        print("🔍 AUDITORIA DE DUPLICIDADES EM MODELS")
        print("=" * 80)

        print("\n📋 Etapa 1: Inventariando modelos...")
        self.inventariar_modelos()

        print(f"\n✅ {len(self.models)} modelos encontrados")

        print("\n📋 Etapa 2: Extraindo assinaturas de campos...")
        self.extrair_assinaturas_campos()

        print("\n📋 Etapa 3: Detectando campos repetidos...")
        self.detectar_campos_repetidos()

        print("\n📋 Etapa 4: Encontrando métodos duplicados...")
        self.encontrar_metodos_duplicados()

        print("\n📋 Etapa 5: Centralizando choices/enums...")
        self.centralizar_choices()

        print("\n📋 Etapa 6: Revisando constraints/índices...")
        self.revisar_constraints()

        print("\n📋 Etapa 7: Mapeando relacionamentos...")
        self.mapear_relacionamentos()

        print("\n📋 Etapa 8: Auditando padrões transversais...")
        self.auditar_padroes_transversais()

        print("\n📋 Etapa 9: Gerando relatórios...")
        self.gerar_relatorios()

        print("\n✅ AUDITORIA CONCLUÍDA!")
        print(f"\n📄 Relatórios gerados em:")
        print(f"   - docs/AUDITORIA_MODELS_DUPLICIDADES.md")
        print(f"   - docs/auditoria_models_resultado.json")

    def inventariar_modelos(self):
        """Etapa 1: Lista todos os models do app"""
        app_models = apps.get_app_config("avaliacao_docente").get_models()

        for model in app_models:
            model_info = {
                "nome": model.__name__,
                "app": model._meta.app_label,
                "tabela": model._meta.db_table,
                "abstrato": model._meta.abstract,
                "campos": {},
                "metodos": {},
                "meta": self._extrair_meta(model),
            }

            # Extrair campos
            for field in model._meta.get_fields():
                if hasattr(field, "name"):
                    model_info["campos"][field.name] = self._extrair_info_campo(field)

            # Extrair métodos customizados
            for name, method in inspect.getmembers(model, predicate=inspect.isfunction):
                if not name.startswith("_") and name not in ["save", "delete", "clean"]:
                    continue
                if name in ["save", "delete", "clean", "__str__", "__repr__"]:
                    try:
                        source = inspect.getsource(method)
                        model_info["metodos"][name] = source
                    except:
                        pass

            self.models.append(model_info)
            print(f"   ✓ {model_info['nome']}: {len(model_info['campos'])} campos")

    def _extrair_meta(self, model):
        """Extrai informações de Meta do modelo"""
        meta = model._meta
        return {
            "ordering": list(meta.ordering) if meta.ordering else [],
            "unique_together": (
                list(meta.unique_together) if meta.unique_together else []
            ),
            "indexes": (
                [str(idx) for idx in meta.indexes] if hasattr(meta, "indexes") else []
            ),
            "constraints": (
                [str(c) for c in meta.constraints]
                if hasattr(meta, "constraints")
                else []
            ),
        }

    def _extrair_info_campo(self, field):
        """Extrai informações detalhadas de um campo"""
        info = {
            "tipo": field.__class__.__name__,
            "null": getattr(field, "null", None),
            "blank": getattr(field, "blank", None),
            "default": str(getattr(field, "default", "NOT PROVIDED")),
            "unique": getattr(field, "unique", False),
            "choices": None,
            "relacionamento": None,
        }

        # Choices
        if hasattr(field, "choices") and field.choices:
            info["choices"] = sorted([str(c[0]) for c in field.choices])

        # Relacionamentos
        if isinstance(
            field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)
        ):
            info["relacionamento"] = (
                field.related_model.__name__
                if hasattr(field, "related_model")
                else None
            )

        return info

    def extrair_assinaturas_campos(self):
        """Etapa 2: Gera assinaturas hash para comparação"""
        for model_info in self.models:
            assinaturas = []
            for campo_nome, campo_info in model_info["campos"].items():
                # Criar assinatura: nome|tipo|null|blank|choices
                sig_parts = [
                    campo_nome,
                    campo_info["tipo"],
                    str(campo_info["null"]),
                    str(campo_info["blank"]),
                    "|".join(campo_info["choices"]) if campo_info["choices"] else "",
                ]
                assinatura = "|".join(sig_parts)
                hash_sig = hashlib.sha1(assinatura.encode()).hexdigest()[:12]
                assinaturas.append((campo_nome, hash_sig, campo_info))

            model_info["assinaturas_campos"] = assinaturas

    def detectar_campos_repetidos(self):
        """Etapa 3: Encontra grupos de campos idênticos em múltiplos models"""
        # Agrupar por nome de campo
        campos_por_nome = defaultdict(list)

        for model_info in self.models:
            for campo_nome, campo_info in model_info["campos"].items():
                campos_por_nome[campo_nome].append(
                    {
                        "modelo": model_info["nome"],
                        "info": campo_info,
                    }
                )

        # Detectar padrões recorrentes (ex: created_at + updated_at + ativo)
        padroes_conhecidos = {
            "timestamps": ["created_at", "updated_at"],
            "soft_delete": ["ativo", "deletado"],
            "auditoria": ["criado_por", "atualizado_por", "created_at", "updated_at"],
        }

        for padrao_nome, campos_padrao in padroes_conhecidos.items():
            modelos_com_padrao = []
            for model_info in self.models:
                campos_modelo = set(model_info["campos"].keys())
                if all(c in campos_modelo for c in campos_padrao):
                    modelos_com_padrao.append(model_info["nome"])

            if len(modelos_com_padrao) >= 2:
                self.duplicidades["padroes_transversais"].append(
                    {
                        "tipo": f"Padrão {padrao_nome}",
                        "campos": campos_padrao,
                        "modelos": modelos_com_padrao,
                        "quantidade": len(modelos_com_padrao),
                        "recomendacao": f'Criar {padrao_nome.title()}Mixin com campos {", ".join(campos_padrao)}',
                    }
                )
                print(
                    f"   🔁 Padrão '{padrao_nome}' encontrado em {len(modelos_com_padrao)} modelos"
                )

        # Campos individuais repetidos com mesmo tipo
        for campo_nome, ocorrencias in campos_por_nome.items():
            if len(ocorrencias) >= 3:
                # Verificar se são do mesmo tipo
                tipos = [o["info"]["tipo"] for o in ocorrencias]
                if len(set(tipos)) == 1:
                    self.duplicidades["campos_repetidos"].append(
                        {
                            "campo": campo_nome,
                            "tipo": tipos[0],
                            "modelos": [o["modelo"] for o in ocorrencias],
                            "quantidade": len(ocorrencias),
                        }
                    )
                    print(
                        f"   🔁 Campo '{campo_nome}' repetido em {len(ocorrencias)} modelos"
                    )

    def encontrar_metodos_duplicados(self):
        """Etapa 4: Compara métodos usando difflib"""
        metodos_por_nome = defaultdict(list)

        for model_info in self.models:
            for metodo_nome, metodo_source in model_info["metodos"].items():
                metodos_por_nome[metodo_nome].append(
                    {
                        "modelo": model_info["nome"],
                        "source": metodo_source,
                    }
                )

        for metodo_nome, ocorrencias in metodos_por_nome.items():
            if len(ocorrencias) < 2:
                continue

            # Comparar cada par
            for i in range(len(ocorrencias)):
                for j in range(i + 1, len(ocorrencias)):
                    source1 = ocorrencias[i]["source"]
                    source2 = ocorrencias[j]["source"]

                    similaridade = SequenceMatcher(None, source1, source2).ratio()

                    if similaridade >= self.limiar_similaridade:
                        self.duplicidades["metodos_similares"].append(
                            {
                                "metodo": metodo_nome,
                                "modelo1": ocorrencias[i]["modelo"],
                                "modelo2": ocorrencias[j]["modelo"],
                                "similaridade": round(similaridade * 100, 1),
                                "recomendacao": f"Extrair para método utilitário ou mixin",
                            }
                        )
                        print(
                            f"   🔁 Método '{metodo_nome}' similar em {ocorrencias[i]['modelo']} e {ocorrencias[j]['modelo']} ({similaridade*100:.0f}%)"
                        )

    def centralizar_choices(self):
        """Etapa 5: Detecta choices duplicados"""
        choices_groups = defaultdict(list)

        for model_info in self.models:
            for campo_nome, campo_info in model_info["campos"].items():
                if campo_info["choices"]:
                    # Normalizar choices para comparação
                    choices_key = "|".join(sorted(campo_info["choices"]))
                    choices_groups[choices_key].append(
                        {
                            "modelo": model_info["nome"],
                            "campo": campo_nome,
                            "choices": campo_info["choices"],
                        }
                    )

        for choices_key, ocorrencias in choices_groups.items():
            if len(ocorrencias) >= 2:
                campos_afetados = [f"{o['modelo']}.{o['campo']}" for o in ocorrencias]
                self.duplicidades["choices_duplicados"].append(
                    {
                        "choices": ocorrencias[0]["choices"],
                        "campos": campos_afetados,
                        "quantidade": len(ocorrencias),
                        "recomendacao": f'Criar Enum centralizado para {", ".join(ocorrencias[0]["choices"][:3])}...',
                    }
                )
                print(
                    f"   🔁 Choices duplicados em {len(ocorrencias)} campos: {', '.join(ocorrencias[0]['choices'][:2])}"
                )

    def revisar_constraints(self):
        """Etapa 6: Analisa constraints e índices"""
        constraints_count = Counter()

        for model_info in self.models:
            meta = model_info["meta"]

            # unique_together
            for ut in meta["unique_together"]:
                constraints_count[f"unique_together: {ut}"] += 1

            # Verificar sobreposição de unique_together
            if len(meta["unique_together"]) > 1:
                # Detectar se um conjunto é subconjunto de outro
                for i, ut1 in enumerate(meta["unique_together"]):
                    for ut2 in meta["unique_together"][i + 1 :]:
                        if set(ut1).issubset(set(ut2)) or set(ut2).issubset(set(ut1)):
                            self.duplicidades["constraints_sobrepostos"].append(
                                {
                                    "modelo": model_info["nome"],
                                    "constraint1": ut1,
                                    "constraint2": ut2,
                                    "tipo": "unique_together sobreposto",
                                    "recomendacao": "Revisar se ambos são necessários",
                                }
                            )

    def mapear_relacionamentos(self):
        """Etapa 7: Mapeia ForeignKeys e detecta redundâncias"""
        relacionamentos = defaultdict(list)

        for model_info in self.models:
            for campo_nome, campo_info in model_info["campos"].items():
                if campo_info["relacionamento"]:
                    relacionamentos[campo_info["relacionamento"]].append(
                        {
                            "modelo_origem": model_info["nome"],
                            "campo": campo_nome,
                            "tipo": campo_info["tipo"],
                        }
                    )

        # Detectar múltiplos FKs para mesmo modelo
        for modelo_destino, refs in relacionamentos.items():
            modelos_origem = {}
            for ref in refs:
                origem = ref["modelo_origem"]
                if origem not in modelos_origem:
                    modelos_origem[origem] = []
                modelos_origem[origem].append(ref["campo"])

            # Se um modelo tem múltiplos FKs para o mesmo destino
            for origem, campos in modelos_origem.items():
                if len(campos) >= 2:
                    self.duplicidades["relacionamentos_redundantes"].append(
                        {
                            "modelo_origem": origem,
                            "modelo_destino": modelo_destino,
                            "campos": campos,
                            "quantidade": len(campos),
                            "recomendacao": "Verificar se todos os relacionamentos são necessários",
                        }
                    )
                    print(f"   🔁 {origem} tem {len(campos)} FKs para {modelo_destino}")

    def auditar_padroes_transversais(self):
        """Etapa 8: Já executada em detectar_campos_repetidos"""
        pass

    def gerar_relatorios(self):
        """Etapa 9: Gera arquivos de relatório"""
        # JSON
        resultado = {
            "data_auditoria": datetime.now().isoformat(),
            "total_modelos": len(self.models),
            "duplicidades": self.duplicidades,
            "estatisticas": {
                "campos_repetidos": len(self.duplicidades["campos_repetidos"]),
                "metodos_similares": len(self.duplicidades["metodos_similares"]),
                "choices_duplicados": len(self.duplicidades["choices_duplicados"]),
                "constraints_sobrepostos": len(
                    self.duplicidades["constraints_sobrepostos"]
                ),
                "relacionamentos_redundantes": len(
                    self.duplicidades["relacionamentos_redundantes"]
                ),
                "padroes_transversais": len(self.duplicidades["padroes_transversais"]),
            },
        }

        with open("docs/auditoria_models_resultado.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)

        # Markdown
        self._gerar_markdown(resultado)

    def _gerar_markdown(self, resultado):
        """Gera relatório em Markdown"""
        md = []
        md.append("# Auditoria de Duplicidades em Models Django\n")
        md.append(f"**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        md.append(f"**Total de Modelos**: {resultado['total_modelos']}\n")
        md.append("\n---\n")

        md.append("\n## 📊 Resumo Executivo\n")
        stats = resultado["estatisticas"]
        total_issues = sum(stats.values())
        md.append(f"\n**Total de Duplicidades Detectadas**: {total_issues}\n")
        md.append("\n| Categoria | Quantidade |\n")
        md.append("|-----------|------------|\n")
        for categoria, qtd in stats.items():
            md.append(f"| {categoria.replace('_', ' ').title()} | {qtd} |\n")

        # Padrões Transversais
        if self.duplicidades["padroes_transversais"]:
            md.append("\n## 🔁 Padrões Transversais (Alta Prioridade)\n")
            md.append(
                "\nEstes padrões aparecem em múltiplos modelos e são candidatos ideais para Mixins:\n"
            )
            for padrao in self.duplicidades["padroes_transversais"]:
                md.append(f"\n### {padrao['tipo']}\n")
                md.append(f"- **Campos**: `{', '.join(padrao['campos'])}`\n")
                md.append(
                    f"- **Modelos Afetados** ({padrao['quantidade']}): {', '.join(padrao['modelos'])}\n"
                )
                md.append(f"- **Recomendação**: {padrao['recomendacao']}\n")

        # Campos Repetidos
        if self.duplicidades["campos_repetidos"]:
            md.append("\n## 📝 Campos Repetidos\n")
            for campo in self.duplicidades["campos_repetidos"]:
                md.append(f"\n### Campo: `{campo['campo']}` ({campo['tipo']})\n")
                md.append(
                    f"- **Aparece em {campo['quantidade']} modelos**: {', '.join(campo['modelos'])}\n"
                )

        # Métodos Similares
        if self.duplicidades["metodos_similares"]:
            md.append("\n## 🔧 Métodos Similares\n")
            for metodo in self.duplicidades["metodos_similares"][:10]:  # Top 10
                md.append(f"\n### Método: `{metodo['metodo']}`\n")
                md.append(f"- **Similaridade**: {metodo['similaridade']}%\n")
                md.append(f"- **Modelos**: {metodo['modelo1']} ↔️ {metodo['modelo2']}\n")
                md.append(f"- **Recomendação**: {metodo['recomendacao']}\n")

        # Choices Duplicados
        if self.duplicidades["choices_duplicados"]:
            md.append("\n## 🎯 Choices Duplicados\n")
            for choice in self.duplicidades["choices_duplicados"]:
                md.append(f"\n### Choices: `{', '.join(choice['choices'][:3])}...`\n")
                md.append(
                    f"- **Campos Afetados** ({choice['quantidade']}): {', '.join(choice['campos'])}\n"
                )
                md.append(f"- **Recomendação**: {choice['recomendacao']}\n")

        # Relacionamentos Redundantes
        if self.duplicidades["relacionamentos_redundantes"]:
            md.append("\n## 🔗 Relacionamentos Redundantes\n")
            for rel in self.duplicidades["relacionamentos_redundantes"]:
                md.append(f"\n### {rel['modelo_origem']} → {rel['modelo_destino']}\n")
                md.append(f"- **Campos FK**: `{', '.join(rel['campos'])}`\n")
                md.append(f"- **Recomendação**: {rel['recomendacao']}\n")

        # Priorização
        md.append("\n## 📈 Priorização de Refatorações\n")
        md.append("\n### Alta Prioridade\n")
        md.append(
            "1. **Implementar Mixins para Padrões Transversais** (baixo risco, alto impacto)\n"
        )
        md.append("   - TimestampMixin (created_at, updated_at)\n")
        md.append("   - SoftDeleteMixin (ativo, deletado)\n")
        md.append("   - AuditoriaMixin (criado_por, atualizado_por)\n")
        md.append("\n### Média Prioridade\n")
        md.append("2. **Centralizar Choices em Enums**\n")
        md.append("3. **Extrair Métodos Similares para Utils**\n")
        md.append("\n### Baixa Prioridade\n")
        md.append("4. **Revisar Relacionamentos Redundantes**\n")
        md.append("5. **Otimizar Constraints Sobrepostos**\n")

        # Próximos Passos
        md.append("\n## 🚀 Próximos Passos Recomendados\n")
        md.append("\n1. Criar `avaliacao_docente/mixins.py` com classes base\n")
        md.append("2. Criar `avaliacao_docente/enums.py` com choices centralizados\n")
        md.append("3. Implementar migrações para adicionar campos dos mixins\n")
        md.append("4. Migração de dados (popular novos campos)\n")
        md.append("5. Atualizar models para herdar de mixins\n")
        md.append("6. Remover campos antigos via migração\n")
        md.append("7. Executar suite de testes completa\n")
        md.append("8. Atualizar documentação\n")

        with open("docs/AUDITORIA_MODELS_DUPLICIDADES.md", "w", encoding="utf-8") as f:
            f.write("".join(md))


if __name__ == "__main__":
    auditor = ModelAuditor()
    auditor.run()
