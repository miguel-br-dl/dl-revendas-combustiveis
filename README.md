# ⛽ Análise de preço de combustível no Brasil

Análise de dados públicos da ANP para entender padrões, variações regionais e comportamentos fora da curva nos preços de combustíveis no Brasil.

---

## 🎯 Sobre o Projeto

Este projeto demonstra um pipeline completo de dados aplicado a um problema do cotidiano: o preço dos combustíveis.

A proposta é transformar dados públicos brutos em insights claros, utilizando análise estatística e visualizações acessíveis.

---

## 🌐 Visualização do Projeto

Os dashboards gerados podem ser acessados via GitHub Pages:

🔗 **Acesse aqui:** https://miguel-br-dl.github.io/dl-revendas-combustiveis/

---

## 📊 Dashboards Disponíveis

* 📈 **Variação de Preços por Região**
  Análise da variação percentual ao longo do tempo, destacando regiões com aumentos mais acelerados.

* 🗺️ **Mapa de Preços no Brasil**
  Visualização geográfica com diferenças de preço entre estados.

---

## 🧰 Tecnologias Utilizadas

* **Python** → coleta e processamento de dados
* **Pandas** → manipulação e análise
* **JavaScript** → visualização no frontend
* **Chart.js** → gráficos interativos
* CSV / Excel → armazenamento intermediário

---

## 📥 Fonte dos Dados

Dados oficiais da Agência Nacional do Petróleo (ANP):

🔗 https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas

---

## ⚙️ Pipeline do Projeto

### 1. 📥 Coleta de Dados

* Download das planilhas semanais da ANP

### 2. 🧹 Tratamento

* Filtragem por combustível (gasolina, etanol, GLP)
* Padronização dos dados
* Exportação para CSV

### 3. 📊 Análise

* Cálculo de médias por estado e região
* Variação percentual ao longo do tempo
* Detecção de desvios com Z-score

### 4. 🌐 Visualização

* Geração de dashboards estáticos com JavaScript
* Gráficos interativos e visualizações geográficas

---

## ⚙️ Como os Dashboards são Gerados

Os arquivos HTML são gerados automaticamente a partir dos dados processados.

Pipeline resumido:

1. Download das planilhas da ANP
2. Processamento com Python + Pandas
3. Exportação para CSV
4. Geração de HTML + JavaScript

---

## 🧪 Executando Localmente

Para rodar os dashboards localmente:

```bash
cd docs
python -m http.server
```

Acesse:

```
http://localhost:8000
```

---

## 📁 Estrutura do Projeto

```
/levantamento
    scripts de coleta e processamento

/saida
    dashboards gerados (HTML, JS, CSV, JSON)
```

A pasta `/docs` é gerada em um mini-pipeline para publicação via GitHub Pages.

---

## 🔎 Exemplos de Análise

* Estados com maior preço médio de gasolina
* Regiões com maior variação semanal
* Identificação de valores fora da curva

---

## 💡 Exemplo de Insight

> Nem todas as regiões apresentam o mesmo comportamento de preço.
> Algumas registram aumentos mais rápidos, indicando pressões locais ou dinâmicas específicas de mercado.

---

## ⚠️ Disclaimer

Os dados são públicos e fornecidos pela ANP.
As análises possuem caráter exploratório e não representam conclusões definitivas sobre práticas de mercado.

---

## 👨‍💻 Autor

Projeto desenvolvido como parte de estudos em análise de dados, visualização e aplicações práticas do cotidiano.

---
