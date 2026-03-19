#!/usr/bin/env python3
"""Baixa planilhas semanais de preços por posto revendedor da ANP.

Uso comum:
    python temp/combustiveis/levantamento/download.py

Por padrão, o script baixa os arquivos de 2026 listados na página:
https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


PAGE_URL = (
    "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/"
    "precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas"
)
DEFAULT_YEAR = "2026"
USER_AGENT = "Mozilla/5.0"


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def extract_spreadsheet_urls(page_url: str, year: str) -> list[str]:
    html = fetch_text(page_url)
    pattern = (
        r'href=["\']([^"\']*arquivos-lpc/'
        + re.escape(year)
        + r'/revendas_lpc_[^"\']+\.xlsx)["\']'
    )

    urls: list[str] = []
    for href in re.findall(pattern, html, flags=re.IGNORECASE):
        full_url = urljoin(page_url, href)
        if full_url not in urls:
            urls.append(full_url)
    return urls


def download_files(urls: list[str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for url in urls:
        filename = os.path.basename(url)
        destination = output_dir / filename
        data = fetch_bytes(url)
        destination.write_bytes(data)
        print(f"{filename}\t{len(data)} bytes")


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(
        description="Baixa planilhas de preços por posto revendedor da ANP."
    )
    parser.add_argument(
        "--year",
        default=DEFAULT_YEAR,
        help=f"Ano da pasta arquivos-lpc a baixar. Padrão: {DEFAULT_YEAR}.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(base_dir / "planilhas_originais"),
        help="Pasta onde os arquivos .xlsx serão gravados.",
    )
    parser.add_argument(
        "--page-url",
        default=PAGE_URL,
        help="URL da página da ANP que lista as planilhas semanais.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()

    urls = extract_spreadsheet_urls(args.page_url, str(args.year))
    if not urls:
        print(
            f"Nenhuma planilha encontrada para o ano {args.year} em {args.page_url}.",
            file=sys.stderr,
        )
        return 1

    download_files(urls, output_dir)
    print(f"TOTAL_DOWNLOADED={len(urls)}")
    print(f"OUTPUT_DIR={output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
