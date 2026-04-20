# DreamCar Audience Dashboard

Інтерактивний дашборд аналізу коментарів Instagram-опитування DreamCar
«Який буде наступний проєкт?» (пост [DXV7u2TjEe4](https://www.instagram.com/p/DXV7u2TjEe4/)).

**Live:** https://\<USERNAME\>.github.io/dreamcar-audience-dashboard/

## Вимірюються

- Марка, модель
- Тип кузова (SUV, седан, купе, кабріолет і т.п.)
- Тип силової установки (ICE, hybrid, EV)
- Країна походження бренду
- Ціновий сегмент (бюджет / середній / преміум / люкс)
- Sentiment коментаря (позитив / запит на економію / критика)

## Автооновлення

Запускається автоматично двічі на день (10:00 і 22:00 CET) через Cowork scheduled task
`dreamcar-instagram-dashboard-refresh`. Лог запусків — у sidebar «Scheduled».

## Ручне оновлення

```bash
python3 refresh.py            # повний цикл (fetch → analyze → build → push)
python3 refresh.py --no-push  # без пушу в GitHub
python3 refresh.py --skip-fetch  # лише перегенерувати HTML
```

## Стек

- Python 3 (без зовнішніх залежностей)
- Chart.js 4.4.1 (CDN)
- Без бекенду — статичний HTML, хоститься на GitHub Pages
