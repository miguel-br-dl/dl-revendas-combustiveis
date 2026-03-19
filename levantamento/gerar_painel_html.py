#!/usr/bin/env python3
"""Gera um painel HTML leve com filtros e gráfico em JavaScript puro."""

from __future__ import annotations

import csv
import json
from pathlib import Path


TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Painel de Evolução Semanal de Combustíveis</title>
  <style>
    :root {
      --bg: #f6f3ee;
      --panel: #fffdf9;
      --ink: #1f2937;
      --muted: #6b7280;
      --line: #d6cfc2;
      --accent: #b45309;
      --accent-soft: #f59e0b;
      --grid: #e5ddd0;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, #fff9ed 0, transparent 32%),
        linear-gradient(180deg, #f8f4ec 0%, #f2ede5 100%);
      color: var(--ink);
    }
    .page {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.05;
      letter-spacing: -0.03em;
    }
    .lead {
      margin: 0 0 24px;
      max-width: 880px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.6;
    }
    .panel {
      background: color-mix(in srgb, var(--panel) 92%, white 8%);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: 0 18px 50px rgba(71, 50, 14, 0.08);
      padding: 20px;
    }
    .controls {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .field label {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      color: var(--muted);
    }
    select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      padding: 12px 14px;
      font: inherit;
      color: var(--ink);
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }
    .card {
      background: white;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px 16px;
      min-height: 92px;
    }
    .card .label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
    }
    .card .value {
      font-size: clamp(18px, 2vw, 28px);
      font-weight: 700;
      letter-spacing: -0.03em;
    }
    .context {
      margin: 10px 0 8px;
      font-size: 14px;
      color: var(--muted);
    }
    .chart-wrap {
      margin-top: 18px;
      background: white;
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 12px;
      overflow: hidden;
    }
    .chart-title {
      font-size: 18px;
      font-weight: 700;
      margin: 4px 0 12px;
    }
    svg {
      width: 100%;
      height: auto;
      display: block;
    }
    .empty {
      padding: 32px 16px;
      text-align: center;
      color: var(--muted);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
      background: white;
      border-radius: 18px;
      overflow: hidden;
      border: 1px solid var(--line);
    }
    th, td {
      padding: 12px 14px;
      text-align: left;
      border-bottom: 1px solid #efe7da;
      font-size: 14px;
    }
    th {
      background: #fbf7ef;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-size: 12px;
    }
    tr:last-child td { border-bottom: none; }
    .note {
      margin-top: 14px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    @media (max-width: 900px) {
      .controls, .cards { grid-template-columns: 1fr; }
      .page { padding: 24px 14px 40px; }
      .panel { padding: 16px; }
    }
  </style>
</head>
<body>
  <div class="page">
    <h1>Evolução semanal dos preços de combustíveis</h1>
    <p class="lead">
      Os filtros atualizam o gráfico sem precisar reprocessar as planilhas.
    </p>

    <section class="panel">
      <div class="controls">
        <div class="field">
          <label for="produto">Produto</label>
          <select id="produto"></select>
        </div>
        <div class="field">
          <label for="estado">Estado</label>
          <select id="estado"></select>
        </div>
        <div class="field">
          <label for="cidade">Cidade</label>
          <select id="cidade"></select>
        </div>
      </div>

      <div class="context" id="contexto"></div>

      <div class="cards" id="cards"></div>

      <div class="chart-wrap">
        <div class="chart-title" id="chart-title"></div>
        <div id="chart-container"></div>
      </div>

      <div id="table-container"></div>

      <p class="note">
        Quando você deixa estado ou cidade em "todos", o painel calcula a média dos preços médios
        das cidades selecionadas em cada semana.
      </p>
    </section>
  </div>

  <script>
    const DATA = __DATA__;
    const IDX_DATE = 0;
    const IDX_ESTADO = 1;
    const IDX_CIDADE = 2;
    const IDX_PRODUTO = 3;
    const IDX_PRECO = 4;
    const TODOS_ESTADOS = "__TODOS_ESTADOS__";
    const TODAS_CIDADES = "__TODAS_CIDADES__";

    const produtoSelect = document.getElementById("produto");
    const estadoSelect = document.getElementById("estado");
    const cidadeSelect = document.getElementById("cidade");
    const contextoEl = document.getElementById("contexto");
    const cardsEl = document.getElementById("cards");
    const chartTitleEl = document.getElementById("chart-title");
    const chartContainerEl = document.getElementById("chart-container");
    const tableContainerEl = document.getElementById("table-container");

    function uniqueSorted(values) {
      return Array.from(new Set(values)).sort((a, b) => a.localeCompare(b));
    }

    const produtos = uniqueSorted(DATA.map((row) => row[IDX_PRODUTO]));
    const estados = uniqueSorted(DATA.map((row) => row[IDX_ESTADO]));

    function fillSelect(select, options, selectedValue) {
      select.innerHTML = "";
      for (const option of options) {
        const el = document.createElement("option");
        el.value = option.value;
        el.textContent = option.label;
        if (option.value === selectedValue) {
          el.selected = true;
        }
        select.appendChild(el);
      }
    }

    function setupControls() {
      fillSelect(
        produtoSelect,
        produtos.map((item) => ({ value: item, label: item })),
        produtos.includes("GASOLINA COMUM") ? "GASOLINA COMUM" : produtos[0]
      );

      fillSelect(
        estadoSelect,
        [{ value: TODOS_ESTADOS, label: "Todos os estados" }].concat(
          estados.map((item) => ({ value: item, label: item }))
        ),
        TODOS_ESTADOS
      );

      refreshCities();
    }

    function refreshCities() {
      const estado = estadoSelect.value;
      const selectedCity = cidadeSelect.value;
      const cityRows = estado === TODOS_ESTADOS
        ? DATA
        : DATA.filter((row) => row[IDX_ESTADO] === estado);
      const cidades = uniqueSorted(cityRows.map((row) => row[IDX_CIDADE]));

      fillSelect(
        cidadeSelect,
        [{ value: TODAS_CIDADES, label: "Todas as cidades" }].concat(
          cidades.map((item) => ({ value: item, label: item }))
        ),
        cidades.includes(selectedCity) ? selectedCity : TODAS_CIDADES
      );
    }

    function getFilteredRows() {
      return DATA.filter((row) => {
        if (row[IDX_PRODUTO] !== produtoSelect.value) return false;
        if (estadoSelect.value !== TODOS_ESTADOS && row[IDX_ESTADO] !== estadoSelect.value) return false;
        if (cidadeSelect.value !== TODAS_CIDADES && row[IDX_CIDADE] !== cidadeSelect.value) return false;
        return true;
      });
    }

    function aggregateByWeek(rows) {
      const grouped = new Map();

      for (const row of rows) {
        const date = row[IDX_DATE];
        const price = Number(row[IDX_PRECO]);
        const current = grouped.get(date) || { sum: 0, count: 0 };
        current.sum += price;
        current.count += 1;
        grouped.set(date, current);
      }

      return Array.from(grouped.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([date, entry]) => ({
          date,
          price: Number((entry.sum / entry.count).toFixed(6)),
        }));
    }

    function formatNumber(value) {
      return Number(value).toLocaleString("pt-BR", {
        minimumFractionDigits: 3,
        maximumFractionDigits: 6,
      });
    }
    
    function formatDateBr(value) {
      if (!value) return "";
      const [year, month, day] = value.split("-");
      const date = new Date(year, month - 1, day);
      return new Intl.DateTimeFormat("pt-BR").format(date);
    }

    function describeSelection() {
      const estado = estadoSelect.value === TODOS_ESTADOS ? "Brasil" : estadoSelect.value;
      const cidade = cidadeSelect.value === TODAS_CIDADES ? "todas as cidades" : cidadeSelect.value;
      return produtoSelect.value + " | " + estado + " | " + cidade;
    }

    function renderCards(series, rowCount) {
      const latest = series[series.length - 1].price;
      const first = series[0].price;
      const variation = latest - first;
      const min = Math.min(...series.map((item) => item.price));
      const max = Math.max(...series.map((item) => item.price));

      const cards = [
        ["Semanas", "", String(series.length)],
        ["Registros filtrados", "", String(rowCount)],
        ["Último preço médio", "R$", formatNumber(latest)],
        ["Variação total", "R$", formatNumber(variation)],
        ["Mínimo", "R$", formatNumber(min)],
        ["Máximo", "R$", formatNumber(max)],
        ["Primeira data", "", formatDateBr(series[0].date)],
        ["Última data", "", formatDateBr(series[series.length - 1].date)],
      ];

      cardsEl.innerHTML = cards.map(([label, prevalue, value]) => `
        <div class="card">
          <div class="label">${label}</div>
          <div class="value">${prevalue} ${value}</div>
        </div>
      `).join("");
    }

    function renderChart(series) {
      if (!series.length) {
        chartContainerEl.innerHTML = '<div class="empty">Nenhum dado encontrado para a combinação selecionada.</div>';
        return;
      }

      const width = 1040;
      const height = 420;
      const pad = { top: 24, right: 24, bottom: 54, left: 72 };
      const innerWidth = width - pad.left - pad.right;
      const innerHeight = height - pad.top - pad.bottom;

      const values = series.map((item) => item.price);
      let minY = Math.min(...values);
      let maxY = Math.max(...values);
      if (minY === maxY) {
        minY -= 1;
        maxY += 1;
      }
      const yPadding = (maxY - minY) * 0.12;
      minY -= yPadding;
      maxY += yPadding;

      const x = (index) => pad.left + (series.length === 1 ? innerWidth / 2 : (index / (series.length - 1)) * innerWidth);
      const y = (value) => pad.top + innerHeight - ((value - minY) / (maxY - minY)) * innerHeight;

      const gridLines = 5;
      const grid = [];
      for (let i = 0; i <= gridLines; i++) {
        const ratio = i / gridLines;
        const value = maxY - ratio * (maxY - minY);
        const yPos = pad.top + ratio * innerHeight;
        grid.push(`
          <line x1="${pad.left}" y1="${yPos}" x2="${width - pad.right}" y2="${yPos}" stroke="var(--grid)" stroke-width="1" />
          <text x="${pad.left}" y="${yPos + 4}" text-anchor="end" font-size="12" fill="var(--muted)">R$ ${formatNumber(value)}</text>
        `);
      }

      const tickEvery = Math.max(1, Math.ceil(series.length / 6));
      const xLabels = series
        .map((item, index) => ({ item, index }))
        .filter(({ index }) => index % tickEvery === 0 || index === series.length - 1)
        .map(({ item, index }) => `
          <text x="${x(index)-10}" y="${height - 18}" text-anchor="middle" font-size="12" fill="var(--muted)">${formatDateBr(item.date)}</text>
        `);

      const areaPoints = series.map((item, index) => `${x(index)},${y(item.price)}`).join(" ");
      const areaPath = `M ${x(0)} ${height - pad.bottom} L ${areaPoints.replace(/ /g, " L ")} L ${x(series.length - 1)} ${height - pad.bottom} Z`;
      const linePath = series.map((item, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(item.price)}`).join(" ");

      const dots = series.map((item, index) => `
        <g>
          <circle cx="${x(index)}" cy="${y(item.price)}" r="4.5" fill="var(--accent)" stroke="white" stroke-width="2">
            <title>${item.date}: R$ ${formatNumber(item.price)}</title>
          </circle>
        </g>
      `).join("");

      chartContainerEl.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Gráfico de linha da evolução semanal">
          <defs>
            <linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color="var(--accent-soft)" stop-opacity="0.35"></stop>
              <stop offset="100%" stop-color="var(--accent-soft)" stop-opacity="0.04"></stop>
            </linearGradient>
          </defs>
          ${grid.join("")}
          <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="var(--line)" stroke-width="1.2" />
          <path d="${areaPath}" fill="url(#areaFill)"></path>
          <path d="${linePath}" fill="none" stroke="var(--accent)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"></path>
          ${dots}
          ${xLabels.join("")}
        </svg>
      `;
    }

    function renderTable(series) {
      const recent = series.slice(-12);
      tableContainerEl.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Data da planilha</th>
              <th>Preço médio</th>
            </tr>
          </thead>
          <tbody>
            ${recent.map((item) => `
              <tr>
                <td>${formatDateBr(item.date)}</td>
                <td>R$ ${formatNumber(item.price)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    }

    function render() {
      const rows = getFilteredRows();
      const series = aggregateByWeek(rows);

      contextoEl.textContent = "Filtro atual: " + describeSelection();
      chartTitleEl.textContent = "Preço médio semanal";

      if (!series.length) {
        cardsEl.innerHTML = "";
        renderChart(series);
        tableContainerEl.innerHTML = "";
        return;
      }

      renderCards(series, rows.length);
      renderChart(series);
      renderTable(series);
    }

    produtoSelect.addEventListener("change", render);
    estadoSelect.addEventListener("change", () => {
      refreshCities();
      render();
    });
    cidadeSelect.addEventListener("change", render);

    setupControls();
    render();
  </script>
</body>
</html>
"""


def load_rows(csv_path: Path) -> list[list[object]]:
    rows: list[list[object]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                [
                    row["data_planilha"],
                    row["estado"],
                    row["cidade"],
                    row["produto"],
                    float(row["preco_revenda"]),
                ]
            )
    return rows


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "saida" / "planilha_consolidada.csv"
    output_path = base_dir / "saida" / "painel_evolucao_semanal.html"

    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {csv_path}")

    rows = load_rows(csv_path)
    html = TEMPLATE.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
    html = html.replace("__TODOS_ESTADOS__", "__TODOS_ESTADOS__")
    html = html.replace("__TODAS_CIDADES__", "__TODAS_CIDADES__")
    output_path.write_text(html, encoding="utf-8")

    print(f"CSV lido: {csv_path}")
    print(f"Linhas embarcadas no HTML: {len(rows)}")
    print(f"Painel gerado em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
