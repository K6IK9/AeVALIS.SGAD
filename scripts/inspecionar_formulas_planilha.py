#!/usr/bin/env python3
"""
Extrai fórmulas de um arquivo .xlsx sem dependências externas (usa zipfile + XML).

Uso:
    python scripts/inspecionar_formulas_planilha.py "docs/Planilha de Cálculo.xlsx"

Saída:
    - Lista fórmulas por aba (célula, expressão, atributos relevantes)
    - Lista nomes definidos (Defined Names) com suas fórmulas/referências
"""

from __future__ import annotations

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def _et_parse_xml(zf: zipfile.ZipFile, inner_path: str) -> ET.Element:
    with zf.open(inner_path) as fp:
        return ET.fromstring(fp.read())


def _map_sheets(zf: zipfile.ZipFile) -> List[Tuple[str, str]]:
    """
    Retorna lista de tuplas (sheet_name, sheet_xml_path)
    Mapeia workbook.xml e seu .rels para resolver os alvos das abas.
    """
    workbook_xml = "xl/workbook.xml"
    rels_xml = "xl/_rels/workbook.xml.rels"

    wb = _et_parse_xml(zf, workbook_xml)
    # Map rId -> Target (e.g., worksheets/sheet1.xml)
    rels = {}
    try:
        rels_root = _et_parse_xml(zf, rels_xml)
        for rel in rels_root.findall(
            ".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
        ):
            r_id = rel.attrib.get("Id")
            target = rel.attrib.get("Target")
            if r_id and target:
                # Targets are relative to xl/
                rels[r_id] = f"xl/{target}"
    except KeyError:
        # No relationships file found; fallback to default sheet paths
        pass

    sheets = []
    for sheet in wb.findall("main:sheets/main:sheet", NS):
        name = sheet.attrib.get("name", "SemNome")
        r_id = sheet.attrib.get(f"{{{NS['r']}}}id")
        target = rels.get(r_id)
        if not target:
            # Fallback heuristic: sheet{sheetId}.xml
            sheet_id = sheet.attrib.get("sheetId", "1")
            target = f"xl/worksheets/sheet{sheet_id}.xml"
        sheets.append((name, target))
    return sheets


def _extract_defined_names(zf: zipfile.ZipFile) -> List[Tuple[str, str]]:
    """Retorna lista de nomes definidos (name, text)."""
    out: List[Tuple[str, str]] = []
    try:
        wb = _et_parse_xml(zf, "xl/workbook.xml")
        for dn in wb.findall("main:definedNames/main:definedName", NS):
            name = dn.attrib.get("name", "")
            text = (dn.text or "").strip()
            if name or text:
                out.append((name, text))
    except KeyError:
        pass
    return out


def _extract_sheet_formulas(
    zf: zipfile.ZipFile, sheet_path: str
) -> List[Dict[str, str]]:
    """Extrai fórmulas de uma planilha específica (por caminho interno)."""
    root = _et_parse_xml(zf, sheet_path)
    rows = []
    # Percorre células: sheetData/row/c
    for cell in root.findall(".//main:sheetData/main:row/main:c", NS):
        addr = cell.attrib.get("r", "")  # ex: A1
        f = cell.find("main:f", NS)
        if f is not None:
            formula_text = (f.text or "").strip()
            v = cell.find("main:v", NS)
            value_text = (v.text or "").strip() if v is not None else ""
            # Atributos úteis: t (tipo), ref (shared), si (id de compartilhamento)
            attrs = []
            for key in ("t", "ref", "si"):  # t="shared" etc.
                if key in f.attrib:
                    attrs.append(f"{key}={f.attrib[key]}")
            rows.append(
                {
                    "cell": addr,
                    "formula": formula_text,
                    "attrs": ", ".join(attrs),
                    "cached_value": value_text,
                }
            )
    return rows


def listar_formulas(xlsx_path: Path) -> None:
    if not xlsx_path.exists():
        print(f"Arquivo não encontrado: {xlsx_path}")
        sys.exit(1)

    with zipfile.ZipFile(xlsx_path) as zf:
        print(f"📄 Arquivo: {xlsx_path}")
        print()

        # Nomes definidos
        defined = _extract_defined_names(zf)
        if defined:
            print("🔖 Nomes definidos (Defined Names):")
            for name, text in defined:
                print(f"  - {name}: {text}")
            print()

        # Fórmulas por aba
        sheets = _map_sheets(zf)
        if not sheets:
            print("Nenhuma aba encontrada no arquivo.")
            return

        for sheet_name, inner_path in sheets:
            print(f"📑 Aba: {sheet_name}")
            try:
                formulas = _extract_sheet_formulas(zf, inner_path)
            except KeyError:
                print("  (Não foi possível abrir o XML desta aba)")
                print()
                continue

            if not formulas:
                print("  (Sem fórmulas nesta aba)")
            else:
                for item in formulas:
                    attrs = f" [{item['attrs']}]" if item["attrs"] else ""
                    cached = (
                        f" => valor em cache: {item['cached_value']}"
                        if item["cached_value"]
                        else ""
                    )
                    print(f"  - {item['cell']}: {item['formula']}{attrs}{cached}")
            print()


def main() -> None:
    if len(sys.argv) > 1:
        xlsx = Path(sys.argv[1])
    else:
        xlsx = Path("docs/Planilha de Cálculo.xlsx")
    listar_formulas(xlsx)


if __name__ == "__main__":
    main()
