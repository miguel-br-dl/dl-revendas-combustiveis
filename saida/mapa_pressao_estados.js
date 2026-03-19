    let APP_DATA = null;
    let GEOJSON_DATA = null;
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
        .replace(/[̀-ͯ]/g, "")
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
          formula: `((preço final / preço inicial) - 1) × 100
((${formatPrice(item.preco_final)} / ${formatPrice(item.preco_inicial)}) - 1) × 100 = ${formatPct(item.variacao_pct)}`
        },
        excesso_regional_pp: {
          title: "Excesso vs região",
          friendly: "Compara a alta do estado com o comportamento típico da própria região. Se ficar muito acima da mediana regional, isso sugere que o estado apertou mais o preço do que seus vizinhos comparáveis.",
          formula: `variação do estado - mediana regional das variações
${formatPct(item.variacao_pct)} - ${formatPct(item.mediana_regional_variacao)} = ${formatPct(item.excesso_regional_pp)}`
        },
        z_regional_robusto: {
          title: "Desvio robusto",
          friendly: "É uma forma de medir o quão fora da curva o estado ficou dentro da sua região, mas sem depender tanto de extremos. Quanto maior esse número, mais o estado se afastou do padrão regional.",
          formula: item.mad_regional_variacao > 0
            ? `0,6745 × (variação do estado - mediana regional) / MAD regional
0,6745 × (${formatNumber(item.variacao_pct)} - ${formatNumber(item.mediana_regional_variacao)}) / ${formatNumber(item.mad_regional_variacao)} = ${formatNumber(item.z_regional_robusto)}`
            : `MAD regional = 0, então o desvio robusto foi tratado como 0 para evitar divisão por zero.
Resultado atual: ${formatNumber(item.z_regional_robusto)}`
        },
        volatilidade_pct: {
          title: "Volatilidade semanal",
          friendly: "Mostra o quanto o preço médio do estado ficou chacoalhando de uma semana para outra. Mesmo que a alta final não seja tão grande, uma volatilidade alta indica um mercado mais errático.",
          formula: `desvio-padrão das variações percentuais semana a semana
Resultado atual para ${item.nome}: ${formatPct(item.volatilidade_pct)}`
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

    init();
  