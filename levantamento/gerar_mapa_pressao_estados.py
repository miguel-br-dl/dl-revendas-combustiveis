#!/usr/bin/env python3
"""Gera um painel HTML para destacar estados com maior pressão de preço."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


FULL_TO_UF = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPA": "AP",
    "AMAPÁ": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARA": "CE",
    "CEARÁ": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPIRITO SANTO": "ES",
    "ESPÍRITO SANTO": "ES",
    "GOIAS": "GO",
    "GOIÁS": "GO",
    "MARANHAO": "MA",
    "MARANHÃO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARA": "PA",
    "PARÁ": "PA",
    "PARAIBA": "PB",
    "PARAÍBA": "PB",
    "PARANA": "PR",
    "PARANÁ": "PR",
    "PERNAMBUCO": "PE",
    "PIAUI": "PI",
    "PIAUÍ": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDONIA": "RO",
    "RONDÔNIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SAO PAULO": "SP",
    "SÃO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO",
}

STATE_INFO = {
    "AC": {"nome": "Acre", "regiao": "Norte", "x": 0, "y": 4},
    "AL": {"nome": "Alagoas", "regiao": "Nordeste", "x": 8, "y": 5},
    "AP": {"nome": "Amapá", "regiao": "Norte", "x": 5, "y": 1},
    "AM": {"nome": "Amazonas", "regiao": "Norte", "x": 2, "y": 2},
    "BA": {"nome": "Bahia", "regiao": "Nordeste", "x": 7, "y": 5},
    "CE": {"nome": "Ceará", "regiao": "Nordeste", "x": 8, "y": 3},
    "DF": {"nome": "Distrito Federal", "regiao": "Centro-Oeste", "x": 6, "y": 6},
    "ES": {"nome": "Espírito Santo", "regiao": "Sudeste", "x": 8, "y": 6},
    "GO": {"nome": "Goiás", "regiao": "Centro-Oeste", "x": 5, "y": 6},
    "MA": {"nome": "Maranhão", "regiao": "Nordeste", "x": 6, "y": 3},
    "MG": {"nome": "Minas Gerais", "regiao": "Sudeste", "x": 7, "y": 6},
    "MS": {"nome": "Mato Grosso do Sul", "regiao": "Centro-Oeste", "x": 3, "y": 6},
    "MT": {"nome": "Mato Grosso", "regiao": "Centro-Oeste", "x": 4, "y": 5},
    "PA": {"nome": "Pará", "regiao": "Norte", "x": 5, "y": 2},
    "PB": {"nome": "Paraíba", "regiao": "Nordeste", "x": 9, "y": 4},
    "PE": {"nome": "Pernambuco", "regiao": "Nordeste", "x": 8, "y": 4},
    "PI": {"nome": "Piauí", "regiao": "Nordeste", "x": 7, "y": 3},
    "PR": {"nome": "Paraná", "regiao": "Sul", "x": 6, "y": 8},
    "RJ": {"nome": "Rio de Janeiro", "regiao": "Sudeste", "x": 8, "y": 7},
    "RN": {"nome": "Rio Grande do Norte", "regiao": "Nordeste", "x": 9, "y": 3},
    "RO": {"nome": "Rondônia", "regiao": "Norte", "x": 1, "y": 4},
    "RR": {"nome": "Roraima", "regiao": "Norte", "x": 2, "y": 0},
    "RS": {"nome": "Rio Grande do Sul", "regiao": "Sul", "x": 5, "y": 10},
    "SC": {"nome": "Santa Catarina", "regiao": "Sul", "x": 6, "y": 9},
    "SE": {"nome": "Sergipe", "regiao": "Nordeste", "x": 9, "y": 5},
    "SP": {"nome": "São Paulo", "regiao": "Sudeste", "x": 6, "y": 7},
    "TO": {"nome": "Tocantins", "regiao": "Norte", "x": 5, "y": 4},
}


HTML_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mapa de pressão sobre os preços dos combustíveis</title>
  <style>
__LEAFLET_CSS__
  </style>
  <style>
    :root {
      --bg: #f7f4ee;
      --panel: #fffdfa;
      --ink: #18212b;
      --muted: #6b7280;
      --line: #ddd4c6;
      --warm: #d9480f;
      --cool: #2563eb;
      --neutral: #f2ede5;
      --grid: #eadfce;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(249, 115, 22, 0.10), transparent 28%),
        linear-gradient(180deg, #faf7f1 0%, #f2ece2 100%);
    }
    .page {
      max-width: 1380px;
      margin: 0 auto;
      padding: 30px 18px 48px;
    }
    h1 {
      margin: 0 0 10px;
      font-size: clamp(30px, 4vw, 48px);
      line-height: 1.02;
      letter-spacing: -0.04em;
    }
    .lead {
      max-width: 980px;
      margin: 0 0 22px;
      color: var(--muted);
      line-height: 1.65;
      font-size: 16px;
    }
    .shell {
      display: grid;
      grid-template-columns: 420px minmax(0, 1fr);
      gap: 18px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(44, 33, 12, 0.08);
      padding: 18px;
    }
    .controls {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }
    .control-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .field {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .field label {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--muted);
    }
    select {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      color: var(--ink);
      font: inherit;
    }
    .action-button {
      width: 100%;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: white;
      color: var(--ink);
      font: inherit;
      cursor: pointer;
      transition: transform 0.12s ease, border-color 0.12s ease, background 0.12s ease;
    }
    .action-button:hover {
      transform: translateY(-1px);
      border-color: #d7a15f;
      background: #fffcf6;
    }
    .metric-explainer {
      margin: 12px 0 0;
      font-size: 13px;
      line-height: 1.55;
      color: var(--muted);
      background: #fbf6ee;
      border: 1px solid #eee1cb;
      border-radius: 16px;
      padding: 12px 14px;
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-top: 16px;
    }
    .card {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px;
      background: white;
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
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
    }
    .card-button {
      width: 100%;
      text-align: left;
      border: none;
      background: transparent;
      padding: 0;
      margin: 0;
      color: inherit;
      cursor: pointer;
      font: inherit;
    }
    .card-button:hover .label {
      color: #9a3412;
    }
    .section-title {
      font-size: 18px;
      margin: 18px 0 12px;
      font-weight: 700;
    }
    .ranking {
      display: grid;
      gap: 8px;
    }
    .rank-item {
      display: grid;
      grid-template-columns: 34px 1fr auto;
      gap: 10px;
      align-items: center;
      padding: 10px 12px;
      border-radius: 16px;
      background: #fff;
      border: 1px solid var(--line);
      cursor: pointer;
      transition: transform 0.12s ease, border-color 0.12s ease;
    }
    .rank-item:hover,
    .rank-item.active {
      transform: translateY(-1px);
      border-color: #e0a96a;
    }
    .rank-pos {
      width: 34px;
      height: 34px;
      border-radius: 999px;
      background: #fbf1df;
      display: grid;
      place-items: center;
      font-weight: 700;
      color: #9a5a05;
    }
    .rank-name {
      font-weight: 700;
    }
    .rank-region {
      font-size: 12px;
      color: var(--muted);
      margin-top: 2px;
    }
    .rank-value {
      font-weight: 700;
      color: #9a3412;
    }
    .board {
      display: grid;
      gap: 18px;
    }
    .legend {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .gradient {
      width: 220px;
      height: 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: linear-gradient(90deg, #2b6ef3 0%, #f6f0e7 50%, #d9480f 100%);
    }
    .map-shell {
      background: white;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 14px;
    }
    .map-title {
      margin: 2px 0 12px;
      font-size: 18px;
      font-weight: 700;
    }
    .map-canvas {
      height: 700px;
      border-radius: 18px;
      overflow: hidden;
      border: 1px solid #ede4d6;
      background: #f8f4eb;
    }
    .map-status {
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    .state-value-label {
      background: rgba(255, 253, 249, 0.90);
      border: 1px solid rgba(221, 212, 198, 0.94);
      border-radius: 12px;
      box-shadow: 0 8px 20px rgba(17, 24, 39, 0.10);
      padding: 4px 7px 5px;
      text-align: center;
      min-width: 52px;
      pointer-events: none;
      backdrop-filter: blur(2px);
    }
    .state-value-label.strong {
      background: rgba(255, 244, 235, 0.96);
      border-color: rgba(217, 72, 15, 0.26);
    }
    .state-value-label .uf {
      display: block;
      font-size: 11px;
      line-height: 1.1;
      font-weight: 700;
      color: #7c2d12;
      letter-spacing: 0.04em;
    }
    .state-value-label .val {
      display: block;
      font-size: 11px;
      line-height: 1.15;
      color: #374151;
      margin-top: 2px;
    }
    .map-svg {
      width: 100%;
      height: 100%;
      display: block;
    }
    .map-state {
      cursor: pointer;
      transition: opacity 0.12s ease;
    }
    .map-state:hover {
      opacity: 0.92;
    }
    .map-state-label text {
      pointer-events: none;
    }
    .map-popup-title {
      font-weight: 700;
      margin-bottom: 4px;
    }
    .metric-hint {
      margin-top: 10px;
      font-size: 12px;
      color: var(--muted);
      line-height: 1.5;
    }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(17, 24, 39, 0.52);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      z-index: 2000;
    }
    .modal-backdrop.open {
      display: flex;
    }
    .modal {
      width: min(760px, 100%);
      max-height: 90vh;
      overflow: auto;
      background: #fffdf9;
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: 0 30px 80px rgba(17, 24, 39, 0.24);
      padding: 22px;
    }
    .modal-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 12px;
    }
    .modal-title {
      margin: 0;
      font-size: 24px;
      line-height: 1.1;
      letter-spacing: -0.03em;
    }
    .modal-close {
      border: 1px solid var(--line);
      background: white;
      border-radius: 999px;
      width: 38px;
      height: 38px;
      cursor: pointer;
      font-size: 20px;
    }
    .modal-text {
      color: var(--muted);
      line-height: 1.65;
      font-size: 15px;
      margin: 0 0 14px;
    }
    .formula-box {
      background: #fbf6ee;
      border: 1px solid #ecdcc2;
      border-radius: 18px;
      padding: 14px 16px;
      margin-top: 14px;
    }
    .formula-label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 8px;
    }
    .formula-box code {
      display: block;
      white-space: pre-wrap;
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      font-size: 14px;
      color: #7c2d12;
      line-height: 1.6;
    }
    svg {
      width: 100%;
      height: auto;
      display: block;
    }
    .detail-grid {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 18px;
    }
    .chart-panel, .table-panel {
      background: white;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 14px;
    }
    .chart-title {
      font-size: 18px;
      font-weight: 700;
      margin: 2px 0 12px;
    }
    .detail-context {
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 10px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 11px 10px;
      text-align: left;
      border-bottom: 1px solid #f0e8db;
      font-size: 14px;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background: #fbf7ef;
    }
    tr:last-child td { border-bottom: none; }
    .empty {
      color: var(--muted);
      text-align: center;
      padding: 28px 12px;
    }
    @media (max-width: 1100px) {
      .shell { grid-template-columns: 1fr; }
      .detail-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <h1>Quais estados mais esticaram os preços?</h1>
    <p class="lead">
      Em vez de assumir distribuição normal, este painel usa como referência principal a <strong>mediana da própria região</strong>.
      Isso deixa a comparação mais justa entre estados com dinâmicas regionais diferentes. O destaque mais importante é o
      <strong>excesso sobre a mediana regional</strong>: quantos pontos percentuais um estado subiu acima do comportamento típico
      da sua própria região no período analisado.
    </p>

    <div class="shell">
      <aside class="panel">
        <div class="controls">
          <div class="field">
            <label for="produto">Produto</label>
            <select id="produto"></select>
          </div>
          <div class="field">
            <label for="metrica">Métrica do mapa</label>
            <select id="metrica"></select>
          </div>
          <div class="control-row">
            <button id="metric-help-button" class="action-button" type="button">Entenda esta métrica</button>
            <button id="clear-selection-button" class="action-button" type="button">Limpar seleção</button>
          </div>
        </div>

        <div class="metric-explainer" id="metric-explainer"></div>

        <div class="section-title">Resumo do estado selecionado</div>
        <div class="cards" id="cards"></div>

        <div id="ranking-title" class="section-title">Top 5 para puxão de orelha</div>
        <div class="ranking" id="ranking"></div>
      </aside>

      <section class="board">
        <div class="map-shell">
          <div class="map-title">Mapa comparativo por UF</div>
          <div class="legend">
            <span>Menor que a região</span>
            <div class="gradient"></div>
            <span>Maior que a região</span>
          </div>
          <div id="map-container" class="map-canvas"></div>
          <div id="map-status" class="map-status">Carregando mapa do Brasil...</div>
          <div class="metric-hint">Clique em um estado no mapa ou no ranking para ver os detalhes e entender cada métrica.</div>
        </div>

        <div class="detail-grid">
          <div class="chart-panel">
            <div class="chart-title" id="chart-title"></div>
            <div class="detail-context" id="chart-context"></div>
            <div id="chart-container"></div>
          </div>
          <div class="table-panel">
            <div class="chart-title">Ranking completo</div>
            <div id="table-container"></div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <div id="metric-modal-backdrop" class="modal-backdrop" aria-hidden="true">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="metric-modal-title">
      <div class="modal-top">
        <div>
          <h2 id="metric-modal-title" class="modal-title"></h2>
        </div>
        <button id="metric-modal-close" class="modal-close" type="button" aria-label="Fechar">×</button>
      </div>
      <p id="metric-modal-friendly" class="modal-text"></p>
      <div class="formula-box">
        <div class="formula-label">Como a conta funciona</div>
        <code id="metric-modal-formula"></code>
      </div>
    </div>
  </div>

  <script>
__LEAFLET_JS__
  </script>
  <script>
    const APP_DATA = __APP_DATA__;
    const GEOJSON_DATA = __GEOJSON_DATA__;
    const produtoSelect = document.getElementById("produto");
    const metricaSelect = document.getElementById("metrica");
    const metricHelpButtonEl = document.getElementById("metric-help-button");
    const clearSelectionButtonEl = document.getElementById("clear-selection-button");
    const metricExplainerEl = document.getElementById("metric-explainer");
    const cardsEl = document.getElementById("cards");
    const rankingTitleEl = document.getElementById("ranking-title");
    const rankingEl = document.getElementById("ranking");
    const mapContainerEl = document.getElementById("map-container");
    const mapStatusEl = document.getElementById("map-status");
    const chartTitleEl = document.getElementById("chart-title");
    const chartContextEl = document.getElementById("chart-context");
    const chartContainerEl = document.getElementById("chart-container");
    const tableContainerEl = document.getElementById("table-container");
    const modalBackdropEl = document.getElementById("metric-modal-backdrop");
    const modalCloseEl = document.getElementById("metric-modal-close");
    const modalTitleEl = document.getElementById("metric-modal-title");
    const modalFriendlyEl = document.getElementById("metric-modal-friendly");
    const modalFormulaEl = document.getElementById("metric-modal-formula");

    const metricOptions = [
      {
        key: "excesso_regional_pp",
        label: "Excesso sobre a região (p.p.)",
        description: "Mede quantos pontos percentuais o estado subiu acima ou abaixo da mediana da sua própria região. É a métrica principal para comparar quem forçou mais a barra regionalmente."
      },
      {
        key: "variacao_pct",
        label: "Variação acumulada (%)",
        description: "Mede a variação percentual entre a primeira e a última semana disponível para o estado."
      },
      {
        key: "z_regional_robusto",
        label: "Desvio robusto regional",
        description: "Versão padronizada por região usando mediana e MAD. Ajuda a ver o quão fora da curva um estado ficou sem depender de distribuição normal."
      },
      {
        key: "volatilidade_pct",
        label: "Volatilidade semanal (%)",
        description: "Desvio padrão das variações percentuais semana a semana. Mostra quão instável foi o preço médio no estado."
      }
    ];

    let selectedState = null;
    let ufLookup = null;

    function fillSelect(select, options, selected) {
      select.innerHTML = "";
      for (const option of options) {
        const el = document.createElement("option");
        el.value = option.value;
        el.textContent = option.label;
        if (option.value === selected) el.selected = true;
        select.appendChild(el);
      }
    }

    function formatPct(value) {
      return Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
    }

    function formatPrice(value) {
      return Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 3, maximumFractionDigits: 6 });
    }

    function formatNumber(value) {
      return Number(value).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 6 });
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function normalizeText(value) {
      return String(value || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .trim()
        .toUpperCase();
    }

    function colorFromValue(value, maxAbs) {
      if (!isFinite(value) || maxAbs <= 0) return "#efe8dc";
      const ratio = clamp(value / maxAbs, -1, 1);
      if (ratio >= 0) {
        const light = 92 - ratio * 42;
        return `hsl(18, 85%, ${light}%)`;
      }
      const light = 92 - Math.abs(ratio) * 34;
      return `hsl(216, 78%, ${light}%)`;
    }

    function getProductMetrics() {
      return APP_DATA.metrics[produtoSelect.value];
    }

    function buildUfLookup() {
      const lookup = {};
      Object.entries(APP_DATA.state_info).forEach(([uf, info]) => {
        lookup[normalizeText(uf)] = uf;
        lookup[normalizeText(info.nome)] = uf;
      });
      lookup["DISTRITO FEDERAL"] = "DF";
      return lookup;
    }

    function getSortedStates(metricKey) {
      return Object.entries(getProductMetrics())
        .map(([uf, item]) => ({ uf, ...item }))
        .sort((a, b) => {
          const bValue = typeof b[metricKey] === "number" ? b[metricKey] : -Infinity;
          const aValue = typeof a[metricKey] === "number" ? a[metricKey] : -Infinity;
          return bValue - aValue;
        });
    }

    function renderCards() {
      const sorted = getSortedStates("excesso_regional_pp");
      if (!selectedState) {
        const leader = sorted[0];
        const cards = [
          { label: "Recorte", value: "Panorama nacional" },
          { label: "Produto", value: produtoSelect.value },
          { label: "Estado líder", value: leader ? `${leader.nome} (${leader.uf})` : "-" },
          { label: "Excesso líder", value: leader ? formatPct(leader.excesso_regional_pp) : "-" },
          { label: "Maior variação", value: leader ? formatPct(leader.variacao_pct) : "-" },
          { label: "Estados avaliados", value: String(sorted.length) },
          { label: "Menor excesso", value: sorted.length ? formatPct(sorted[sorted.length - 1].excesso_regional_pp) : "-" },
          {
            label: "Métrica atual",
            value: (() => {
              const currentMetric = metricOptions.find((item) => item.key === metricaSelect.value);
              return currentMetric ? currentMetric.label : "-";
            })(),
          },
        ];
        cardsEl.innerHTML = cards.map((card) => `
          <div class="card">
            <div class="label">${card.label}</div>
            <div class="value">${card.value}</div>
          </div>
        `).join("");
        return;
      }
      const item = getProductMetrics()[selectedState];
      const cards = [
        { label: "Estado", value: item.nome },
        { label: "Região", value: item.regiao },
        { label: "Variação acumulada", value: formatPct(item.variacao_pct), metricKey: "variacao_pct" },
        { label: "Excesso vs região", value: formatPct(item.excesso_regional_pp), metricKey: "excesso_regional_pp" },
        { label: "Desvio robusto", value: Number(item.z_regional_robusto).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }), metricKey: "z_regional_robusto" },
        { label: "Volatilidade semanal", value: formatPct(item.volatilidade_pct), metricKey: "volatilidade_pct" },
        { label: "Primeiro preço", value: formatPrice(item.preco_inicial) },
        { label: "Último preço", value: formatPrice(item.preco_final) },
      ];

      cardsEl.innerHTML = cards.map((card) => {
        if (!card.metricKey) {
          return `
            <div class="card">
              <div class="label">${card.label}</div>
              <div class="value">${card.value}</div>
            </div>
          `;
        }
        return `
          <div class="card">
            <button class="card-button" type="button" data-metric-key="${card.metricKey}">
              <div class="label">${card.label}</div>
              <div class="value">${card.value}</div>
            </button>
          </div>
        `;
      }).join("");

      cardsEl.querySelectorAll("[data-metric-key]").forEach((button) => {
        button.addEventListener("click", () => openMetricModal(button.dataset.metricKey));
      });
    }

    function renderRanking() {
      const allStates = getSortedStates("excesso_regional_pp");
      let states = allStates.slice(0, 5);
      let title = "Top 5 para puxão de orelha";

      if (selectedState) {
        const index = allStates.findIndex((item) => item.uf === selectedState);
        if (index >= 0) {
          const start = Math.max(0, Math.min(index - 2, allStates.length - 5));
          states = allStates.slice(start, start + 5);
          title = `Ranking com foco em ${allStates[index].nome} (${selectedState})`;
        }
      }

      rankingTitleEl.textContent = title;
      rankingEl.innerHTML = states.map((item, index) => `
        <div class="rank-item ${item.uf === selectedState ? "active" : ""}" data-uf="${item.uf}">
          <div class="rank-pos">${allStates.findIndex((state) => state.uf === item.uf) + 1}</div>
          <div>
            <div class="rank-name">${item.nome} (${item.uf})</div>
            <div class="rank-region">${item.regiao}</div>
          </div>
          <div class="rank-value">${formatPct(item.excesso_regional_pp)}</div>
        </div>
      `).join("");

      rankingEl.querySelectorAll(".rank-item").forEach((el) => {
        el.addEventListener("click", () => {
          selectedState = el.dataset.uf;
          renderAll();
        });
      });
    }

    function renderTable() {
      const rows = getSortedStates("excesso_regional_pp");
      tableContainerEl.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>UF</th>
              <th>Estado</th>
              <th>Região</th>
              <th>Excesso região</th>
              <th>Variação</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((item) => `
              <tr>
                <td>${item.uf}</td>
                <td>${item.nome}</td>
                <td>${item.regiao}</td>
                <td>${formatPct(item.excesso_regional_pp)}</td>
                <td>${formatPct(item.variacao_pct)}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    }

    function resolveFeatureUf(feature) {
      const lookup = ufLookup || {};
      const props = feature && feature.properties ? feature.properties : {};
      const directCandidates = [
        props.sigla,
        props.uf,
        props.UF,
        props.abbrev,
        props.abbreviation,
        props.id,
        feature.id,
      ];
      for (const candidate of directCandidates) {
        const normalized = normalizeText(candidate);
        if (lookup[normalized]) return lookup[normalized];
      }

      const nameCandidates = [
        props.name,
        props.NAME,
        props.nome,
        props.NOME,
        props.state,
      ];
      for (const candidate of nameCandidates) {
        const normalized = normalizeText(candidate);
        if (lookup[normalized]) return lookup[normalized];
      }

      return null;
    }

    function buildPopupHtml(item, metricKey) {
      return `
        <div class="map-popup-title">${item.nome} (${item.uf})</div>
        <div>Região: ${item.regiao}</div>
        <div>Métrica atual: ${Number(item[metricKey]).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
        <div>Variação acumulada: ${formatPct(item.variacao_pct)}</div>
        <div>Excesso vs região: ${formatPct(item.excesso_regional_pp)}</div>
      `;
    }

    function renderMap() {
      const metricKey = metricaSelect.value;
      const states = getSortedStates(metricKey);
      const metricByUf = Object.fromEntries(states.map((item) => [item.uf, item]));
      const maxAbs = Math.max(
        ...states.map((item) => Math.abs(typeof item[metricKey] === "number" ? item[metricKey] : 0)),
        1
      );
      const features = GEOJSON_DATA.features
        .map((feature) => {
          const uf = resolveFeatureUf(feature);
          return { feature, uf, item: metricByUf[uf] || null };
        })
        .filter((entry) => entry.uf);

      const allCoords = [];
      features.forEach(({ feature }) => {
        extractCoordinates(feature.geometry).forEach(([lon, lat]) => allCoords.push([lon, lat]));
      });

      if (!allCoords.length) {
        mapStatusEl.textContent = "Não consegui montar o mapa a partir do GeoJSON.";
        mapContainerEl.innerHTML = '<div class="empty">Mapa indisponível.</div>';
        return;
      }

      const width = 920;
      const height = 700;
      const pad = 24;
      const lonValues = allCoords.map((coord) => coord[0]);
      const latValues = allCoords.map((coord) => coord[1]);
      const minLon = Math.min(...lonValues);
      const maxLon = Math.max(...lonValues);
      const minLat = Math.min(...latValues);
      const maxLat = Math.max(...latValues);
      const scaleX = (width - pad * 2) / (maxLon - minLon);
      const scaleY = (height - pad * 2) / (maxLat - minLat);
      const scale = Math.min(scaleX, scaleY);
      const offsetX = (width - (maxLon - minLon) * scale) / 2;
      const offsetY = (height - (maxLat - minLat) * scale) / 2;

      function project(coord) {
        const lon = coord[0];
        const lat = coord[1];
        return [
          offsetX + (lon - minLon) * scale,
          height - (offsetY + (lat - minLat) * scale),
        ];
      }

      const featureSvg = features.map(({ feature, uf, item }) => {
        const geometry = feature.geometry || {};
        const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : (geometry.coordinates || []);
        const pathData = polygons.map((polygon) => {
          const outer = (polygon[0] || []).map(project);
          if (!outer.length) return "";
          const outerPath = outer.map((point, index) => `${index === 0 ? "M" : "L"} ${point[0].toFixed(2)} ${point[1].toFixed(2)}`).join(" ") + " Z";
          const holes = polygon.slice(1).map((ring) => {
            const pts = ring.map(project);
            if (!pts.length) return "";
            return pts.map((point, index) => `${index === 0 ? "M" : "L"} ${point[0].toFixed(2)} ${point[1].toFixed(2)}`).join(" ") + " Z";
          }).join(" ");
          return `${outerPath} ${holes}`.trim();
        }).join(" ");

        const centroid = computeFeatureCenter(feature.geometry, project);
        const isSelected = item && item.uf === selectedState;
        const fill = item ? colorFromValue(item[metricKey], maxAbs) : "#efe8dc";
        const stroke = isSelected ? "#9f7b59" : "#fffaf2";
        const strokeWidth = isSelected ? 1.35 : 1.0;
        const labelClass = isSelected ? "state-value-label strong" : "state-value-label";
        const value = item
          ? Number(item[metricKey]).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
          : "";

        return `
          <g class="map-state" data-uf="${uf}">
            <path d="${pathData}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" fill-rule="evenodd"></path>
            ${
              item && centroid
                ? `<g class="map-state-label" transform="translate(${centroid[0].toFixed(2)} ${centroid[1].toFixed(2)})">
                    <rect x="-31" y="-17" width="62" height="34" rx="12" ry="12" fill="${isSelected ? "rgba(255, 244, 235, 0.96)" : "rgba(255, 253, 249, 0.90)"}" stroke="${isSelected ? "rgba(217, 72, 15, 0.26)" : "rgba(221, 212, 198, 0.94)"}"></rect>
                    <text x="0" y="-2" text-anchor="middle" font-size="11" font-weight="700" fill="#7c2d12">${item.uf}</text>
                    <text x="0" y="11" text-anchor="middle" font-size="11" fill="#374151">${value}</text>
                  </g>`
                : ""
            }
          </g>
        `;
      }).join("");

      mapContainerEl.innerHTML = `
        <svg class="map-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Mapa do Brasil por estado">
          ${featureSvg}
        </svg>
      `;
      mapStatusEl.textContent = "Mapa do Brasil carregado.";

      mapContainerEl.querySelectorAll("[data-uf]").forEach((element) => {
        element.addEventListener("click", () => {
          selectedState = element.getAttribute("data-uf");
          renderAll();
        });
      });
    }

    function extractCoordinates(geometry) {
      if (!geometry) return [];
      if (geometry.type === "Polygon") {
        return geometry.coordinates.flat();
      }
      if (geometry.type === "MultiPolygon") {
        return geometry.coordinates.flat(2);
      }
      return [];
    }

    function computeFeatureCenter(geometry, project) {
      const coords = extractCoordinates(geometry);
      if (!coords.length) return null;
      let minX = Infinity;
      let minY = Infinity;
      let maxX = -Infinity;
      let maxY = -Infinity;
      coords.forEach((coord) => {
        const point = project(coord);
        minX = Math.min(minX, point[0]);
        minY = Math.min(minY, point[1]);
        maxX = Math.max(maxX, point[0]);
        maxY = Math.max(maxY, point[1]);
      });
      return [(minX + maxX) / 2, (minY + maxY) / 2];
    }

    function getMetricModalContent(metricKey, item) {
      const friendlyByMetric = {
        variacao_pct: {
          title: "Variação acumulada",
          friendly: "Mostra o quanto o preço médio do estado subiu ou caiu entre a primeira e a última semana disponíveis. É a resposta mais direta para a pergunta: no fim do período, esse estado estava mais caro do que antes?",
          formula: `((preço final / preço inicial) - 1) × 100\n((${formatPrice(item.preco_final)} / ${formatPrice(item.preco_inicial)}) - 1) × 100 = ${formatPct(item.variacao_pct)}`
        },
        excesso_regional_pp: {
          title: "Excesso vs região",
          friendly: "Compara a alta do estado com o comportamento típico da própria região. Se ficar muito acima da mediana regional, isso sugere que o estado apertou mais o preço do que seus vizinhos comparáveis.",
          formula: `variação do estado - mediana regional das variações\n${formatPct(item.variacao_pct)} - ${formatPct(item.mediana_regional_variacao)} = ${formatPct(item.excesso_regional_pp)}`
        },
        z_regional_robusto: {
          title: "Desvio robusto",
          friendly: "É uma forma de medir o quão fora da curva o estado ficou dentro da sua região, mas sem depender tanto de extremos. Quanto maior esse número, mais o estado se afastou do padrão regional.",
          formula: item.mad_regional_variacao > 0
            ? `0,6745 × (variação do estado - mediana regional) / MAD regional\n0,6745 × (${formatNumber(item.variacao_pct)} - ${formatNumber(item.mediana_regional_variacao)}) / ${formatNumber(item.mad_regional_variacao)} = ${formatNumber(item.z_regional_robusto)}`
            : `MAD regional = 0, então o desvio robusto foi tratado como 0 para evitar divisão por zero.\nResultado atual: ${formatNumber(item.z_regional_robusto)}`
        },
        volatilidade_pct: {
          title: "Volatilidade semanal",
          friendly: "Mostra o quanto o preço médio do estado ficou chacoalhando de uma semana para outra. Mesmo que a alta final não seja tão grande, uma volatilidade alta indica um mercado mais errático.",
          formula: `desvio-padrão das variações percentuais semana a semana\nResultado atual para ${item.nome}: ${formatPct(item.volatilidade_pct)}`
        }
      };
      return friendlyByMetric[metricKey];
    }

    function getReferenceItemForExplanation() {
      if (selectedState) return getProductMetrics()[selectedState];
      return getSortedStates("excesso_regional_pp")[0] || null;
    }

    function openMetricModal(metricKey) {
      const item = getReferenceItemForExplanation();
      if (!item) return;
      const content = getMetricModalContent(metricKey, item);
      if (!content) return;

      modalTitleEl.textContent = `${content.title} em ${item.nome} (${selectedState})`;
      modalFriendlyEl.textContent = content.friendly;
      modalFormulaEl.textContent = content.formula;
      modalBackdropEl.classList.add("open");
      modalBackdropEl.setAttribute("aria-hidden", "false");
    }

    function closeMetricModal() {
      modalBackdropEl.classList.remove("open");
      modalBackdropEl.setAttribute("aria-hidden", "true");
    }

    function renderDetailChart() {
      if (!selectedState) {
        const series = APP_DATA.brazil_series[produtoSelect.value] || [];
        chartTitleEl.textContent = `Panorama nacional de ${produtoSelect.value.toLowerCase()}`;
        chartContextEl.textContent = "Sem estado selecionado: a linha mostra a média nacional ao longo das semanas.";
        if (!series.length) {
          chartContainerEl.innerHTML = '<div class="empty">Nenhum dado nacional disponível.</div>';
          return;
        }
        renderSingleSeriesChart(series, "Média nacional", "#b45309");
        return;
      }

      const item = getProductMetrics()[selectedState];
      const stateSeries = APP_DATA.series[produtoSelect.value][selectedState] || [];
      const regionSeries = APP_DATA.region_series[produtoSelect.value][item.regiao] || [];
      chartTitleEl.textContent = `${item.nome} (${selectedState}) x média da ${item.regiao}`;
      chartContextEl.textContent = `Produto: ${produtoSelect.value}. A linha laranja mostra o estado; a linha azul mostra a média regional no mesmo período.`;

      const merged = stateSeries.map(([date, price], index) => ({
        date,
        statePrice: Number(price),
        regionPrice: Number((regionSeries[index] || [null, null])[1]),
      }));

      if (!merged.length) {
        chartContainerEl.innerHTML = '<div class="empty">Sem série temporal para este estado.</div>';
        return;
      }

      const width = 760;
      const height = 360;
      const pad = { top: 24, right: 22, bottom: 52, left: 68 };
      const innerWidth = width - pad.left - pad.right;
      const innerHeight = height - pad.top - pad.bottom;
      const allValues = merged.flatMap((point) => [point.statePrice, point.regionPrice].filter((v) => Number.isFinite(v)));
      let minY = Math.min(...allValues);
      let maxY = Math.max(...allValues);
      if (minY === maxY) {
        minY -= 1;
        maxY += 1;
      }
      const yPad = (maxY - minY) * 0.12;
      minY -= yPad;
      maxY += yPad;

      const x = (index) => pad.left + (merged.length === 1 ? innerWidth / 2 : (index / (merged.length - 1)) * innerWidth);
      const y = (value) => pad.top + innerHeight - ((value - minY) / (maxY - minY)) * innerHeight;
      const tickEvery = Math.max(1, Math.ceil(merged.length / 6));

      const grid = [];
      for (let i = 0; i <= 5; i++) {
        const ratio = i / 5;
        const value = maxY - ratio * (maxY - minY);
        const yPos = pad.top + ratio * innerHeight;
        grid.push(`
          <line x1="${pad.left}" y1="${yPos}" x2="${width - pad.right}" y2="${yPos}" stroke="var(--grid)" stroke-width="1" />
          <text x="${pad.left - 10}" y="${yPos + 4}" text-anchor="end" font-size="12" fill="var(--muted)">${formatPrice(value)}</text>
        `);
      }

      const makePath = (key) => merged.map((point, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(point[key])}`).join(" ");
      const stateDots = merged.map((point, index) => `
        <circle cx="${x(index)}" cy="${y(point.statePrice)}" r="4.5" fill="#d9480f">
          <title>${point.date}: ${formatPrice(point.statePrice)}</title>
        </circle>
      `).join("");
      const regionDots = merged.map((point, index) => `
        <circle cx="${x(index)}" cy="${y(point.regionPrice)}" r="4" fill="#2563eb">
          <title>${point.date}: ${formatPrice(point.regionPrice)}</title>
        </circle>
      `).join("");
      const xLabels = merged
        .map((point, index) => ({ point, index }))
        .filter(({ index }) => index % tickEvery === 0 || index === merged.length - 1)
        .map(({ point, index }) => `
          <text x="${x(index)}" y="${height - 18}" text-anchor="middle" font-size="12" fill="var(--muted)">${point.date}</text>
        `)
        .join("");

      chartContainerEl.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Série temporal do estado e da região">
          ${grid.join("")}
          <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="var(--line)" stroke-width="1.2" />
          <path d="${makePath("regionPrice")}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
          <path d="${makePath("statePrice")}" fill="none" stroke="#d9480f" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"></path>
          ${regionDots}
          ${stateDots}
          ${xLabels}
        </svg>
      `;
    }

    function renderSingleSeriesChart(series, label, color) {
      const normalized = series.map(([date, value]) => ({ date, value: Number(value) }));
      const width = 760;
      const height = 360;
      const pad = { top: 24, right: 22, bottom: 52, left: 68 };
      const innerWidth = width - pad.left - pad.right;
      const innerHeight = height - pad.top - pad.bottom;
      let minY = Math.min(...normalized.map((point) => point.value));
      let maxY = Math.max(...normalized.map((point) => point.value));
      if (minY === maxY) {
        minY -= 1;
        maxY += 1;
      }
      const yPad = (maxY - minY) * 0.12;
      minY -= yPad;
      maxY += yPad;

      const x = (index) => pad.left + (normalized.length === 1 ? innerWidth / 2 : (index / (normalized.length - 1)) * innerWidth);
      const y = (value) => pad.top + innerHeight - ((value - minY) / (maxY - minY)) * innerHeight;
      const tickEvery = Math.max(1, Math.ceil(normalized.length / 6));

      const grid = [];
      for (let i = 0; i <= 5; i++) {
        const ratio = i / 5;
        const value = maxY - ratio * (maxY - minY);
        const yPos = pad.top + ratio * innerHeight;
        grid.push(`
          <line x1="${pad.left}" y1="${yPos}" x2="${width - pad.right}" y2="${yPos}" stroke="var(--grid)" stroke-width="1" />
          <text x="${pad.left - 10}" y="${yPos + 4}" text-anchor="end" font-size="12" fill="var(--muted)">${formatPrice(value)}</text>
        `);
      }

      const path = normalized.map((point, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(point.value)}`).join(" ");
      const dots = normalized.map((point, index) => `
        <circle cx="${x(index)}" cy="${y(point.value)}" r="4.5" fill="${color}">
          <title>${point.date}: ${formatPrice(point.value)}</title>
        </circle>
      `).join("");
      const xLabels = normalized
        .map((point, index) => ({ point, index }))
        .filter(({ index }) => index % tickEvery === 0 || index === normalized.length - 1)
        .map(({ point, index }) => `<text x="${x(index)}" y="${height - 18}" text-anchor="middle" font-size="12" fill="var(--muted)">${point.date}</text>`)
        .join("");

      chartContainerEl.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${label}">
          ${grid.join("")}
          <line x1="${pad.left}" y1="${height - pad.bottom}" x2="${width - pad.right}" y2="${height - pad.bottom}" stroke="var(--line)" stroke-width="1.2" />
          <path d="${path}" fill="none" stroke="${color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"></path>
          ${dots}
          ${xLabels}
        </svg>
      `;
    }

    function renderMetricExplainer() {
      const current = metricOptions.find((item) => item.key === metricaSelect.value);
      metricExplainerEl.textContent = current.description;
    }

    function renderAll() {
      renderMetricExplainer();
      renderCards();
      renderRanking();
      renderMap();
      renderDetailChart();
      renderTable();
    }

    function setup() {
      ufLookup = buildUfLookup();
      const products = Object.keys(APP_DATA.metrics).sort((a, b) => a.localeCompare(b));
      fillSelect(
        produtoSelect,
        products.map((item) => ({ value: item, label: item })),
        products.includes("GASOLINA COMUM") ? "GASOLINA COMUM" : products[0]
      );
      fillSelect(
        metricaSelect,
        metricOptions.map((item) => ({ value: item.key, label: item.label })),
        "excesso_regional_pp"
      );

      produtoSelect.addEventListener("change", () => {
        selectedState = null;
        renderAll();
      });
      metricaSelect.addEventListener("change", renderAll);
      metricHelpButtonEl.addEventListener("click", () => openMetricModal(metricaSelect.value));
      clearSelectionButtonEl.addEventListener("click", () => {
        selectedState = null;
        renderAll();
      });
      modalCloseEl.addEventListener("click", closeMetricModal);
      modalBackdropEl.addEventListener("click", (event) => {
        if (event.target === modalBackdropEl) closeMetricModal();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closeMetricModal();
      });

      renderAll();
    }

    setup();
  </script>
</body>
</html>
"""


def robust_zscore(series: pd.Series) -> pd.Series:
    median = series.median()
    mad = (series - median).abs().median()
    if pd.isna(mad) or mad == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    return 0.6745 * (series - median) / mad


def load_brazil_states_geojson(base_dir: Path) -> dict:
    geojson_path = base_dir / "levantamento" / "vendor" / "geojson" / "brazil-states.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(
            f"GeoJSON local não encontrado em {geojson_path}. "
            "Baixe o arquivo local antes de gerar o HTML."
        )
    return json.loads(geojson_path.read_text(encoding="utf-8"))


SERVER_HTML_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mapa de pressão sobre os preços dos combustíveis</title>
  <link rel="stylesheet" href="mapa_pressao_estados.css">
</head>
<body>
  <div class="page">
    <h1>Quais estados mais esticaram os preços?</h1>
    <p class="lead">
      Em vez de assumir distribuição normal, este painel usa como referência principal a <strong>mediana da própria região</strong>.
      Isso deixa a comparação mais justa entre estados com dinâmicas regionais diferentes. O destaque mais importante é o
      <strong>excesso sobre a mediana regional</strong>: quantos pontos percentuais um estado subiu acima do comportamento típico
      da sua própria região no período analisado.
    </p>

    <div class="shell">
      <aside class="panel">
        <div class="controls">
          <div class="field">
            <label for="produto">Produto</label>
            <select id="produto"></select>
          </div>
          <div class="field">
            <label for="metrica">Métrica do mapa</label>
            <select id="metrica"></select>
          </div>
          <div class="control-row">
            <button id="metric-help-button" class="action-button" type="button">Entenda esta métrica</button>
            <button id="clear-selection-button" class="action-button" type="button">Limpar seleção</button>
          </div>
        </div>

        <div class="metric-explainer" id="metric-explainer"></div>

        <div class="section-title">Resumo do estado selecionado</div>
        <div class="cards" id="cards"></div>

        <div id="ranking-title" class="section-title">Top 5 para puxão de orelha</div>
        <div class="ranking" id="ranking"></div>
      </aside>

      <section class="board">
        <div class="map-shell">
          <div class="map-title">Mapa comparativo por UF</div>
          <div class="legend">
            <span>Menor que a região</span>
            <div class="gradient"></div>
            <span>Maior que a região</span>
          </div>
          <div id="map-container" class="map-canvas"></div>
          <div id="map-status" class="map-status">Carregando mapa do Brasil...</div>
          <div class="metric-hint">Clique em um estado no mapa ou no ranking para ver os detalhes e entender cada métrica.</div>
        </div>

        <div class="detail-grid">
          <div class="chart-panel">
            <div class="chart-title" id="chart-title"></div>
            <div class="detail-context" id="chart-context"></div>
            <div id="chart-container"></div>
          </div>
          <div class="table-panel">
            <div class="chart-title">Ranking completo</div>
            <div id="table-container"></div>
          </div>
        </div>
      </section>
    </div>
  </div>

  <div id="metric-modal-backdrop" class="modal-backdrop" aria-hidden="true">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="metric-modal-title">
      <div class="modal-top">
        <div>
          <h2 id="metric-modal-title" class="modal-title"></h2>
        </div>
        <button id="metric-modal-close" class="modal-close" type="button" aria-label="Fechar">×</button>
      </div>
      <p id="metric-modal-friendly" class="modal-text"></p>
      <div class="formula-box">
        <div class="formula-label">Como a conta funciona</div>
        <code id="metric-modal-formula"></code>
      </div>
    </div>
  </div>

  <script defer src="mapa_pressao_estados.js"></script>
</body>
</html>
"""


def extract_inline_assets_from_template(template: str) -> tuple[str, str]:
    css_start = template.rindex("<style>") + len("<style>")
    css_end = template.index("</style>", css_start)
    css_text = template[css_start:css_end].strip("\n")

    script_start = template.rindex("<script>") + len("<script>")
    script_end = template.rindex("</script>")
    js_text = template[script_start:script_end].strip("\n")
    return css_text, js_text


def build_server_js(js_text: str) -> str:
    js_text = js_text.replace("const APP_DATA = __APP_DATA__;", "let APP_DATA = null;")
    js_text = js_text.replace("const GEOJSON_DATA = __GEOJSON_DATA__;", "let GEOJSON_DATA = null;")

    init_block = """
    async function init() {
      try {
        const [appResponse, geoResponse] = await Promise.all([
          fetch("mapa_pressao_estados_data.json", { cache: "no-store" }),
          fetch("brazil-states.geojson", { cache: "no-store" }),
        ]);
        if (!appResponse.ok) {
          throw new Error(`Falha ao carregar mapa_pressao_estados_data.json: ${appResponse.status}`);
        }
        if (!geoResponse.ok) {
          throw new Error(`Falha ao carregar brazil-states.geojson: ${geoResponse.status}`);
        }
        APP_DATA = await appResponse.json();
        GEOJSON_DATA = await geoResponse.json();
        setup();
      } catch (error) {
        console.error(error);
        const message = error && error.message ? error.message : String(error);
        mapStatusEl.textContent = "Falha ao carregar os arquivos do painel.";
        chartContextEl.textContent = message;
        mapContainerEl.innerHTML = '<div class="empty">Não foi possível carregar o mapa.</div>';
      }
    }

"""
    js_text = js_text.replace("    function setup() {", init_block + "    function setup() {", 1)
    js_text = js_text.replace("\n    setup();\n", "\n    init();\n", 1)
    return js_text


def build_app_data(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["data_planilha"] = pd.to_datetime(df["data_planilha"])
    df["uf"] = df["estado"].map(FULL_TO_UF)
    df = df.dropna(subset=["uf"]).copy()
    df["regiao"] = df["uf"].map(lambda uf: STATE_INFO[uf]["regiao"])

    state_week = (
        df.groupby(["produto", "data_planilha", "estado", "uf", "regiao"], as_index=False)["preco_revenda"]
        .mean()
        .sort_values(["produto", "uf", "data_planilha"])
    )

    region_week = (
        state_week.groupby(["produto", "data_planilha", "regiao"], as_index=False)["preco_revenda"]
        .mean()
        .sort_values(["produto", "regiao", "data_planilha"])
    )

    brazil_week = (
        state_week.groupby(["produto", "data_planilha"], as_index=False)["preco_revenda"]
        .mean()
        .sort_values(["produto", "data_planilha"])
    )

    metrics_rows = []
    for (produto, uf), group in state_week.groupby(["produto", "uf"], sort=True):
        group = group.sort_values("data_planilha").reset_index(drop=True)
        first_price = float(group.iloc[0]["preco_revenda"])
        last_price = float(group.iloc[-1]["preco_revenda"])
        pct_changes = group["preco_revenda"].pct_change().dropna()
        metrics_rows.append(
            {
                "produto": produto,
                "uf": uf,
                "estado": group.iloc[0]["estado"],
                "regiao": group.iloc[0]["regiao"],
                "nome": STATE_INFO[uf]["nome"],
                "primeira_data": group.iloc[0]["data_planilha"].strftime("%Y-%m-%d"),
                "ultima_data": group.iloc[-1]["data_planilha"].strftime("%Y-%m-%d"),
                "semanas": int(len(group)),
                "preco_inicial": round(first_price, 6),
                "preco_final": round(last_price, 6),
                "variacao_pct": round(((last_price / first_price) - 1) * 100, 6),
                "variacao_abs": round(last_price - first_price, 6),
                "volatilidade_pct": round(float(pct_changes.std() * 100) if not pct_changes.empty else 0.0, 6),
                "salto_maximo_pct": round(float(pct_changes.max() * 100) if not pct_changes.empty else 0.0, 6),
            }
        )

    metrics = pd.DataFrame(metrics_rows)
    metrics["mediana_regional_variacao"] = metrics.groupby(["produto", "regiao"])["variacao_pct"].transform("median")
    metrics["mad_regional_variacao"] = metrics.groupby(["produto", "regiao"])["variacao_pct"].transform(
        lambda s: (s - s.median()).abs().median()
    )
    metrics["excesso_regional_pp"] = metrics["variacao_pct"] - metrics["mediana_regional_variacao"]
    metrics["z_regional_robusto"] = (
        metrics.groupby(["produto", "regiao"])["variacao_pct"].transform(robust_zscore).round(6)
    )
    metrics["volatilidade_pct"] = metrics["volatilidade_pct"].round(6)
    metrics["excesso_regional_pp"] = metrics["excesso_regional_pp"].round(6)
    metrics["mad_regional_variacao"] = metrics["mad_regional_variacao"].round(6)

    metrics_by_product: dict[str, dict[str, dict]] = {}
    for produto, group in metrics.groupby("produto", sort=True):
        metrics_by_product[produto] = {}
        for _, row in group.iterrows():
            metrics_by_product[produto][row["uf"]] = {
                "uf": row["uf"],
                "estado": row["estado"],
                "nome": row["nome"],
                "regiao": row["regiao"],
                "primeira_data": row["primeira_data"],
                "ultima_data": row["ultima_data"],
                "semanas": int(row["semanas"]),
                "preco_inicial": float(row["preco_inicial"]),
                "preco_final": float(row["preco_final"]),
                "variacao_pct": float(row["variacao_pct"]),
                "variacao_abs": float(row["variacao_abs"]),
                "volatilidade_pct": float(row["volatilidade_pct"]),
                "salto_maximo_pct": float(row["salto_maximo_pct"]),
                "mediana_regional_variacao": float(row["mediana_regional_variacao"]),
                "mad_regional_variacao": float(row["mad_regional_variacao"]),
                "excesso_regional_pp": float(row["excesso_regional_pp"]),
                "z_regional_robusto": float(row["z_regional_robusto"]),
            }

    series_by_product: dict[str, dict[str, list[list[object]]]] = {}
    for (produto, uf), group in state_week.groupby(["produto", "uf"], sort=True):
        series_by_product.setdefault(produto, {})[uf] = [
            [row["data_planilha"].strftime("%Y-%m-%d"), round(float(row["preco_revenda"]), 6)]
            for _, row in group.iterrows()
        ]

    region_series_by_product: dict[str, dict[str, list[list[object]]]] = {}
    for (produto, regiao), group in region_week.groupby(["produto", "regiao"], sort=True):
        region_series_by_product.setdefault(produto, {})[regiao] = [
            [row["data_planilha"].strftime("%Y-%m-%d"), round(float(row["preco_revenda"]), 6)]
            for _, row in group.iterrows()
        ]

    brazil_series_by_product: dict[str, list[list[object]]] = {}
    for produto, group in brazil_week.groupby("produto", sort=True):
        brazil_series_by_product[produto] = [
            [row["data_planilha"].strftime("%Y-%m-%d"), round(float(row["preco_revenda"]), 6)]
            for _, row in group.iterrows()
        ]

    return {
        "state_info": STATE_INFO,
        "metrics": metrics_by_product,
        "series": series_by_product,
        "region_series": region_series_by_product,
        "brazil_series": brazil_series_by_product,
    }


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "saida" / "planilha_consolidada.csv"
    output_dir = base_dir / "saida"
    output_path = output_dir / "mapa_pressao_estados.html"
    offline_output_path = output_dir / "mapa_pressao_estados_offline.html"
    css_output_path = output_dir / "mapa_pressao_estados.css"
    js_output_path = output_dir / "mapa_pressao_estados.js"
    data_output_path = output_dir / "mapa_pressao_estados_data.json"
    geojson_output_path = output_dir / "brazil-states.geojson"

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {input_path}")

    df = pd.read_csv(input_path)
    app_data = build_app_data(df)
    geojson_data = load_brazil_states_geojson(base_dir)

    # Mantemos uma versão offline/autônoma para abrir direto do disco.
    compact_app_data = json.dumps(app_data, ensure_ascii=False, separators=(",", ":"))
    compact_geojson_data = json.dumps(geojson_data, ensure_ascii=False, separators=(",", ":"))

    offline_html = HTML_TEMPLATE.replace("__APP_DATA__", compact_app_data)
    offline_html = offline_html.replace("__GEOJSON_DATA__", compact_geojson_data)
    offline_html = offline_html.replace("__LEAFLET_CSS__", "")
    offline_html = offline_html.replace("__LEAFLET_JS__", "")
    offline_output_path.write_text(offline_html, encoding="utf-8")

    # E geramos uma versão para servidor com assets separados.
    inline_css, inline_js = extract_inline_assets_from_template(HTML_TEMPLATE)
    server_js = build_server_js(inline_js)
    css_output_path.write_text(inline_css, encoding="utf-8")
    js_output_path.write_text(server_js, encoding="utf-8")
    data_output_path.write_text(compact_app_data, encoding="utf-8")
    geojson_output_path.write_text(compact_geojson_data, encoding="utf-8")
    output_path.write_text(SERVER_HTML_TEMPLATE, encoding="utf-8")

    print(f"CSV lido: {input_path}")
    print(f"Painel servidor gerado em: {output_path}")
    print(f"Painel offline gerado em: {offline_output_path}")
    print(f"Produtos: {', '.join(sorted(app_data['metrics']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
