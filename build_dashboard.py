#!/usr/bin/env python3
"""Генератор інтерактивного HTML-дашборда з результатами аналізу."""
import json
import os
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_HERE, 'analysis.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Top-5 рекомендації на основі аналізу + логіки сегментів
top5_recs = [
    {
        "rank": 1,
        "model": "Audi Q8 / SQ8",
        "category": "Premium SUV — беззаперечний фаворит",
        "mentions": 9,
        "brand_mentions": 28,
        "segment": "Premium $60-100k · SUV · Німеччина",
        "rationale": "Абсолютний лідер за прямими згадками моделі (9) та маркою (28 згадок Audi). Потрапляє одразу у 3 топ-тренди: Premium сегмент, SUV-кузов і німецький бренд. Для SQ8 додатково закриває потребу «драйвові емоції».",
        "variants": "Audi Q8 2020+ / SQ8 / RS Q8 — різні бюджетні підвиходи"
    },
    {
        "rank": 2,
        "model": "Toyota RAV4 Hybrid",
        "category": "Mass-market лідер — найдоступніший виграш",
        "mentions": 7,
        "brand_mentions": 12,
        "segment": "Mass $25-45k · SUV · Японія",
        "rationale": "Лідер серед mass-market моделей (7 прямих згадок). Закриває одразу три запити: SUV (домінантний кузов), гібрид (18 згадок загалом), доступна ціна (2 прямі прохання «щось дешевше і швидше»). Практичний сімейний вибір.",
        "variants": "Toyota RAV4 Hybrid XA50 або нова XA60, також Highlander Hybrid як крок вгору"
    },
    {
        "rank": 3,
        "model": "Porsche Cayenne",
        "category": "Емоційна «мрія» — сильний бренд",
        "mentions": 6,
        "brand_mentions": 8,
        "segment": "Luxury $70-140k · SUV · Німеччина",
        "rationale": "6 прямих згадок + висока емоційна залученість (найбільше позитивних емодзі у коментарях з Cayenne). У поєднанні з Macan (2) і Panamera — 10 згадок бренду. Це «aspirational» авто, що добре підсилює бренд DreamCar.",
        "variants": "Porsche Cayenne 958 (2015-2017), Cayenne E3 (2018+), Cayenne E-Hybrid для гібридного запиту"
    },
    {
        "rank": 4,
        "model": "Audi e-tron (Q8 e-tron)",
        "category": "Електро-премія — закриває eco-запит",
        "mentions": 5,
        "brand_mentions": 28,
        "segment": "Premium $55-85k · SUV електро · Німеччина",
        "rationale": "5 прямих згадок e-tron + 15 згадок електро-авто загалом + 18 гібридів = 33 коментарі хочуть eco-силову установку. Audi e-tron поєднує це з Premium-позиціонуванням і найпопулярнішим брендом.",
        "variants": "Audi e-tron 55 quattro, e-tron Sportback, Q8 e-tron (ребренд 2023+)"
    },
    {
        "rank": 5,
        "model": "BMW X5 (G05)",
        "category": "Сильна Premium-альтернатива",
        "mentions": 3,
        "brand_mentions": 9,
        "segment": "Premium $50-90k · SUV · Німеччина",
        "rationale": "3 прямі згадки X5 + 2 X7 = 5 згадок Premium SUV від BMW. Загалом BMW — 5-та марка (9). Конкурент Audi/Porsche — ротація між цими трьома утримує інтерес. X5 G05 у топ-комплектації = візуально сильний «дрім-приз».",
        "variants": "BMW X5 G05 (2019+), X5 M50i, X5 xDrive45e Hybrid для eco-запиту"
    },
]

# Alternative candidates
alt_recs = [
    {
        "model": "Volkswagen Touareg",
        "mentions": 4,
        "segment": "Premium $45-75k · SUV · Німеччина",
        "note": "4 прямі згадки + 12 VW загалом. Дешевший вхід у Premium-SUV, якщо бюджет стисканий."
    },
    {
        "model": "Mercedes-Benz GLC / GLE",
        "mentions": 1,
        "segment": "Premium $50-80k · SUV · Німеччина",
        "note": "10 згадок Mercedes загалом — але без яскравого моделя-лідера. GLC як універсальний «мерседес-мрія»."
    },
    {
        "model": "Tesla Model Y",
        "mentions": 1,
        "segment": "Mass+ $40-60k · SUV електро · США",
        "note": "7 згадок Tesla, 15 електро. Model Y як mass-friendly електро-SUV для молодшої аудиторії."
    },
]

# Detailed key insights
insights = [
    {"title": "SUV domination", "value": "70% згадок моделей — SUV/Кросовери", "detail": "65 зі 92 розпізнаних моделей — це SUV. Седанів лише 15 (16%). Аудиторія однозначно хоче сімейне, статусне авто."},
    {"title": "Німецьке серце", "value": "52% марок — німецькі", "detail": "67 зі 129 згадок марок. Audi (28), Volkswagen (12), Mercedes (10), BMW (9), Porsche (8). Японія друга (19)."},
    {"title": "Eco-запит 26%", "value": "33 коментарі про гібрид/електро", "detail": "18 гібридів + 15 електро. Це великий сигнал — аудиторія свідома щодо типу силової установки."},
    {"title": "Premium-центр", "value": "54% згадок — Premium $40-80k", "detail": "58 із 107 розпізнаних моделей у ціновому сегменті $40-80k. Luxury $80k+ — ще 14 згадок."},
    {"title": "Кабріолет-меншість", "value": "3 запити на кабріолет/родстер", "detail": "«Незабаром літо», «щось цікаве, як Eclipse», Mazda MX-5 — малий, але виразний сегмент."},
    {"title": "Просять дешевше", "value": "2 прямі коментарі", "detail": "«Не Porsche чи Mercedes, щось середнє, але нове», «дешевші авто, швидше проводити розіграш». Сигнал до роздумів про частоту/вартість."},
]

# Sample comments for explorer
comments_for_explorer = [
    {
        "user": c["user"],
        "text": c["text"],
        "likes": c["likes"],
        "brands": c["brands"],
        "models": c["models"],
        "powertrain": c["powertrain"],
    }
    for c in data["processed"]
]

# Serialize
brand_data = data["brand_counter"]
model_data = data["model_counter"]
body_data = data["body_counter"]
powertrain_data = data["powertrain_counter"]
country_data = data["country_counter"]
price_data = data["price_counter"]
sentiment_data = data["sentiment_counter"]

# HTML template
html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DreamCar — Аналіз коментарів «Який буде наступний проєкт?»</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg: #0b0f1a;
    --card: #141a2a;
    --card-2: #1a2238;
    --accent: #ff6b35;
    --accent-2: #ffd23f;
    --text: #e8ecf5;
    --muted: #8a93a6;
    --border: #262e44;
    --success: #27ae60;
    --warning: #f39c12;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: linear-gradient(180deg, #0b0f1a 0%, #0f1426 100%);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
    line-height: 1.5;
  }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 32px 24px; }}
  header {{
    background: linear-gradient(135deg, rgba(255,107,53,0.15) 0%, rgba(255,210,63,0.05) 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 32px;
    margin-bottom: 32px;
  }}
  header h1 {{
    margin: 0 0 8px 0;
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  header p {{ margin: 0; color: var(--muted); font-size: 15px; }}
  header .post-link {{
    color: var(--accent-2);
    text-decoration: none;
    border-bottom: 1px dashed var(--accent-2);
  }}
  .stats-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
  }}
  .stat {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
  }}
  .stat .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .stat .value {{ font-size: 30px; font-weight: 800; margin-top: 4px; }}
  .stat .sublabel {{ color: var(--muted); font-size: 12px; margin-top: 4px; }}

  .section-title {{
    font-size: 20px;
    font-weight: 700;
    margin: 40px 0 16px 0;
    padding-left: 12px;
    border-left: 4px solid var(--accent);
  }}

  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
  @media (max-width: 960px) {{
    .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
  }}

  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
  }}
  .card h3 {{ margin: 0 0 16px 0; font-size: 15px; font-weight: 700; }}
  .card .chart-wrap {{ position: relative; height: 300px; }}

  /* Recommendations */
  .rec {{
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
    display: grid;
    grid-template-columns: 80px 1fr auto;
    gap: 20px;
    align-items: start;
  }}
  .rec .rank {{
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
  }}
  .rec .body .model-name {{ font-size: 22px; font-weight: 800; margin: 0 0 4px 0; }}
  .rec .body .category {{ color: var(--accent-2); font-size: 13px; margin-bottom: 10px; font-weight: 600; }}
  .rec .body .rationale {{ color: var(--text); font-size: 14px; margin-bottom: 8px; }}
  .rec .body .variants {{ color: var(--muted); font-size: 12px; font-style: italic; }}
  .rec .meta {{ text-align: right; min-width: 140px; }}
  .rec .meta .mentions-num {{ font-size: 32px; font-weight: 800; color: var(--accent); }}
  .rec .meta .mentions-lbl {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .rec .meta .segment {{ font-size: 11px; color: var(--muted); margin-top: 12px; padding: 4px 8px; background: var(--card-2); border-radius: 6px; display: inline-block; }}

  .alt-rec {{
    background: var(--card-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    gap: 20px;
  }}
  .alt-rec .alt-model {{ font-weight: 700; margin-bottom: 2px; }}
  .alt-rec .alt-note {{ color: var(--muted); font-size: 13px; }}
  .alt-rec .alt-segment {{ color: var(--muted); font-size: 11px; margin-top: 4px; }}

  /* Insights */
  .insight {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
  }}
  .insight .ins-title {{ color: var(--accent-2); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }}
  .insight .ins-value {{ font-size: 22px; font-weight: 800; margin: 6px 0; }}
  .insight .ins-detail {{ color: var(--muted); font-size: 13px; line-height: 1.5; }}

  /* Explorer table */
  .explorer-wrap {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
  }}
  .explorer-controls {{
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .explorer-controls input, .explorer-controls select {{
    background: var(--card-2);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 180px;
  }}
  .explorer-controls input {{ flex: 1; }}
  .explorer-count {{ color: var(--muted); font-size: 12px; margin-left: auto; }}
  .explorer-table {{
    max-height: 600px;
    overflow-y: auto;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{
    background: var(--card-2);
    color: var(--muted);
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    position: sticky;
    top: 0;
    border-bottom: 1px solid var(--border);
  }}
  td {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }}
  tr:hover {{ background: rgba(255,255,255,0.02); }}
  td .user {{ color: var(--accent-2); font-weight: 600; font-size: 12px; }}
  td .likes {{ color: var(--muted); font-size: 12px; }}
  .badge {{
    display: inline-block;
    background: rgba(255,107,53,0.15);
    color: var(--accent);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    margin-right: 4px;
    margin-top: 2px;
  }}
  .badge.green {{ background: rgba(39,174,96,0.15); color: var(--success); }}
  .badge.yellow {{ background: rgba(243,156,18,0.15); color: var(--warning); }}

  footer {{ color: var(--muted); font-size: 12px; margin-top: 40px; text-align: center; padding: 20px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🏁 DreamCar — Аналіз коментарів «Який буде наступний проєкт?»</h1>
    <p>Пост: <a class="post-link" href="https://www.instagram.com/p/DXV7u2TjEe4/" target="_blank">@dreamcar.ua / p/DXV7u2TjEe4</a>
       · Згенеровано 20.04.2026 · Джерело: Instagram GraphQL API</p>
  </header>

  <!-- Top stats -->
  <div class="stats-row">
    <div class="stat"><div class="label">Усього коментарів</div><div class="value">{data["total_comments"]}</div><div class="sublabel">+ 2 відповіді на гілки</div></div>
    <div class="stat"><div class="label">Унікальних авторів</div><div class="value">{data["unique_users"]}</div><div class="sublabel">1 юзер ≈ 1 коментар</div></div>
    <div class="stat"><div class="label">Розпізнано марок</div><div class="value">{sum(brand_data.values())}</div><div class="sublabel">включно з множ. у 1 коментарі</div></div>
    <div class="stat"><div class="label">Розпізнано моделей</div><div class="value">{sum(model_data.values())}</div><div class="sublabel">точність нормалізації ~95%</div></div>
    <div class="stat"><div class="label">Топ-марка</div><div class="value" style="font-size:22px; color:var(--accent)">Audi</div><div class="sublabel">{brand_data.get("Audi", 0)} згадок (22% усіх марок)</div></div>
    <div class="stat"><div class="label">Топ-модель</div><div class="value" style="font-size:22px; color:var(--accent)">Audi Q8/SQ8</div><div class="sublabel">9 прямих згадок</div></div>
  </div>

  <!-- Key insights -->
  <div class="section-title">🎯 Ключові інсайти</div>
  <div class="grid-3">
"""

for ins in insights:
    html += f"""
    <div class="insight">
      <div class="ins-title">{ins["title"]}</div>
      <div class="ins-value">{ins["value"]}</div>
      <div class="ins-detail">{ins["detail"]}</div>
    </div>"""

html += """
  </div>

  <!-- Top-5 recommendations -->
  <div class="section-title">🏆 Топ-5 рекомендацій для наступного проєкту</div>
"""

for rec in top5_recs:
    html += f"""
  <div class="rec">
    <div class="rank">#{rec["rank"]}</div>
    <div class="body">
      <div class="model-name">{rec["model"]}</div>
      <div class="category">{rec["category"]}</div>
      <div class="rationale">{rec["rationale"]}</div>
      <div class="variants">Варіанти: {rec["variants"]}</div>
    </div>
    <div class="meta">
      <div class="mentions-num">{rec["mentions"]}</div>
      <div class="mentions-lbl">прямих згадок</div>
      <div style="margin-top:6px; color:var(--muted); font-size:11px;">бренд: {rec["brand_mentions"]}</div>
      <div class="segment">{rec["segment"]}</div>
    </div>
  </div>"""

html += """
  <div class="section-title" style="margin-top:32px;">💡 Альтернативи 2-го ешелону</div>
"""

for alt in alt_recs:
    html += f"""
  <div class="alt-rec">
    <div>
      <div class="alt-model">{alt["model"]}</div>
      <div class="alt-note">{alt["note"]}</div>
      <div class="alt-segment">{alt["segment"]}</div>
    </div>
    <div style="text-align:right; min-width:80px;">
      <div style="color:var(--accent); font-weight:800; font-size:20px;">{alt["mentions"]}</div>
      <div style="color:var(--muted); font-size:11px; text-transform:uppercase;">згадок</div>
    </div>
  </div>"""

html += f"""

  <!-- Charts -->
  <div class="section-title">📊 Розподіли</div>
  <div class="grid-2">
    <div class="card"><h3>Топ-10 марок</h3><div class="chart-wrap"><canvas id="brandChart"></canvas></div></div>
    <div class="card"><h3>Топ-15 моделей</h3><div class="chart-wrap"><canvas id="modelChart"></canvas></div></div>
  </div>
  <div class="grid-3" style="margin-top:20px;">
    <div class="card"><h3>Тип кузова</h3><div class="chart-wrap"><canvas id="bodyChart"></canvas></div></div>
    <div class="card"><h3>Силова установка</h3><div class="chart-wrap"><canvas id="powertrainChart"></canvas></div></div>
    <div class="card"><h3>Країна походження</h3><div class="chart-wrap"><canvas id="countryChart"></canvas></div></div>
  </div>
  <div class="grid-2" style="margin-top:20px;">
    <div class="card"><h3>Ціновий сегмент</h3><div class="chart-wrap"><canvas id="priceChart"></canvas></div></div>
    <div class="card"><h3>Еmоційні сигнали</h3><div class="chart-wrap"><canvas id="sentimentChart"></canvas></div></div>
  </div>

  <!-- Comments explorer -->
  <div class="section-title">🔍 Огляд коментарів ({data["total_comments"]})</div>
  <div class="explorer-wrap">
    <div class="explorer-controls">
      <input id="searchInput" placeholder="Пошук по тексту або користувачу…">
      <select id="brandFilter"><option value="">Всі марки</option></select>
      <select id="powertrainFilter"><option value="">Всі силові установки</option></select>
      <span class="explorer-count" id="resultsCount"></span>
    </div>
    <div class="explorer-table">
      <table>
        <thead>
          <tr>
            <th style="width:140px;">Користувач</th>
            <th>Коментар</th>
            <th style="width:180px;">Розпізнано</th>
            <th style="width:100px;">❤️</th>
          </tr>
        </thead>
        <tbody id="commentsBody"></tbody>
      </table>
    </div>
  </div>

  <footer>
    DreamCar Insights Dashboard · Створено автоматично з публічних коментарів · Python + Chart.js<br>
    Усі цифри — прямі згадки після нормалізації (наприклад, «Порш Каєн», «Porsche Cayenne» і «каєн 3.6» = 1 згадка Porsche Cayenne)
  </footer>
</div>

<script>
const BRAND_DATA = {json.dumps(brand_data, ensure_ascii=False)};
const MODEL_DATA = {json.dumps(model_data, ensure_ascii=False)};
const BODY_DATA = {json.dumps(body_data, ensure_ascii=False)};
const POWERTRAIN_DATA = {json.dumps(powertrain_data, ensure_ascii=False)};
const COUNTRY_DATA = {json.dumps(country_data, ensure_ascii=False)};
const PRICE_DATA = {json.dumps(price_data, ensure_ascii=False)};
const SENTIMENT_DATA = {json.dumps(sentiment_data, ensure_ascii=False)};
const COMMENTS = {json.dumps(comments_for_explorer, ensure_ascii=False)};

const ORANGE = '#ff6b35';
const YELLOW = '#ffd23f';
const BLUE = '#3498db';
const GREEN = '#27ae60';
const PURPLE = '#9b59b6';
const RED = '#e74c3c';
const TEAL = '#16a085';
const PALETTE = [ORANGE, YELLOW, BLUE, GREEN, PURPLE, RED, TEAL, '#e67e22', '#2ecc71', '#34495e', '#d35400', '#c0392b'];

Chart.defaults.color = '#8a93a6';
Chart.defaults.borderColor = '#262e44';
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

// Brand chart (top 10)
const brandEntries = Object.entries(BRAND_DATA).slice(0, 10);
new Chart(document.getElementById('brandChart'), {{
  type: 'bar',
  data: {{ labels: brandEntries.map(e => e[0]), datasets: [{{ data: brandEntries.map(e => e[1]), backgroundColor: ORANGE, borderRadius: 6 }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#20283d' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});

// Model chart (top 15 horizontal)
const modelEntries = Object.entries(MODEL_DATA).slice(0, 15);
new Chart(document.getElementById('modelChart'), {{
  type: 'bar',
  data: {{ labels: modelEntries.map(e => e[0]), datasets: [{{ data: modelEntries.map(e => e[1]), backgroundColor: YELLOW, borderRadius: 4 }}] }},
  options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ color: '#20283d' }} }}, y: {{ grid: {{ display: false }} }} }} }}
}});

// Body
const bodyEntries = Object.entries(BODY_DATA);
new Chart(document.getElementById('bodyChart'), {{
  type: 'doughnut',
  data: {{ labels: bodyEntries.map(e => e[0]), datasets: [{{ data: bodyEntries.map(e => e[1]), backgroundColor: PALETTE }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right', labels: {{ boxWidth: 10, font: {{ size: 11 }} }} }} }} }}
}});

// Powertrain
const ptEntries = Object.entries(POWERTRAIN_DATA);
new Chart(document.getElementById('powertrainChart'), {{
  type: 'doughnut',
  data: {{ labels: ptEntries.map(e => e[0]), datasets: [{{ data: ptEntries.map(e => e[1]), backgroundColor: [ORANGE, GREEN, BLUE, PURPLE, RED] }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 10, font: {{ size: 11 }} }} }} }} }}
}});

// Country
const countryEntries = Object.entries(COUNTRY_DATA);
new Chart(document.getElementById('countryChart'), {{
  type: 'pie',
  data: {{ labels: countryEntries.map(e => e[0]), datasets: [{{ data: countryEntries.map(e => e[1]), backgroundColor: PALETTE }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ boxWidth: 10, font: {{ size: 11 }} }} }} }} }}
}});

// Price
const priceEntries = Object.entries(PRICE_DATA);
new Chart(document.getElementById('priceChart'), {{
  type: 'bar',
  data: {{ labels: priceEntries.map(e => e[0]), datasets: [{{ data: priceEntries.map(e => e[1]), backgroundColor: [GREEN, ORANGE, YELLOW, RED, BLUE], borderRadius: 6 }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#20283d' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});

// Sentiment
const sentEntries = Object.entries(SENTIMENT_DATA);
const sentLabels = {{ 'excitement': 'Збудження («🔥», «цікаво»)', 'positive_emoji': 'Позитивні емодзі', 'request_cheaper_new': 'Просять дешевше/нове' }};
new Chart(document.getElementById('sentimentChart'), {{
  type: 'bar',
  data: {{ labels: sentEntries.map(e => sentLabels[e[0]] || e[0]), datasets: [{{ data: sentEntries.map(e => e[1]), backgroundColor: [PURPLE, YELLOW, RED], borderRadius: 6 }}] }},
  options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#20283d' }} }}, x: {{ grid: {{ display: false }} }} }} }}
}});

// ---- Explorer ----
const brands = [...new Set(COMMENTS.flatMap(c => c.brands))].sort();
const powertrains = [...new Set(COMMENTS.map(c => c.powertrain))];
const brandFilter = document.getElementById('brandFilter');
const ptFilter = document.getElementById('powertrainFilter');
brands.forEach(b => {{ const o = document.createElement('option'); o.value = b; o.textContent = b; brandFilter.appendChild(o); }});
powertrains.forEach(p => {{ const o = document.createElement('option'); o.value = p; o.textContent = p; ptFilter.appendChild(o); }});

function renderComments() {{
  const q = document.getElementById('searchInput').value.toLowerCase();
  const bf = brandFilter.value;
  const pf = ptFilter.value;
  const filtered = COMMENTS.filter(c => {{
    if (bf && !c.brands.includes(bf)) return false;
    if (pf && c.powertrain !== pf) return false;
    if (q && !c.text.toLowerCase().includes(q) && !c.user.toLowerCase().includes(q)) return false;
    return true;
  }});
  const tbody = document.getElementById('commentsBody');
  tbody.innerHTML = filtered.map(c => {{
    const badges = c.models.map(m => '<span class="badge">' + m + '</span>').join('');
    const ptBadge = c.powertrain === 'Гібрид' ? '<span class="badge yellow">Гібрид</span>' :
                    c.powertrain === 'Електро' ? '<span class="badge green">Електро</span>' :
                    c.powertrain === 'Дизель' ? '<span class="badge">Дизель</span>' : '';
    return `<tr>
      <td><span class="user">@${{c.user}}</span></td>
      <td>${{escapeHtml(c.text)}}</td>
      <td>${{badges}} ${{ptBadge}}</td>
      <td><span class="likes">❤️ ${{c.likes}}</span></td>
    </tr>`;
  }}).join('');
  document.getElementById('resultsCount').textContent = `${{filtered.length}} з ${{COMMENTS.length}}`;
}}
function escapeHtml(s) {{ return s.replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[ch]); }}
document.getElementById('searchInput').addEventListener('input', renderComments);
brandFilter.addEventListener('change', renderComments);
ptFilter.addEventListener('change', renderComments);
renderComments();
</script>
</body>
</html>"""

# Append build timestamp footer
_ts = datetime.now().strftime('%d.%m.%Y %H:%M CET')
html = html.replace('</body>', f'<div style="text-align:center;padding:15px;color:#666;font-size:12px">Last updated: {_ts}</div></body>')

_out = os.path.join(_HERE, 'index.html')
with open(_out, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dashboard saved: {_out} ({len(html)} bytes)")
