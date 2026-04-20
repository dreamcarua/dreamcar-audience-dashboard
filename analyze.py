#!/usr/bin/env python3
"""Аналізатор коментарів DreamCar з Instagram-посту."""
import json
import os
import re
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_HERE, 'comments.json'), 'r', encoding='utf-8') as f:
    comments = json.load(f)

# === NORMALIZATION DICTIONARIES ===

# Марка -> канонічна назва
BRAND_NORMALIZE = {
    # Audi
    r'\b(audi|ауд[іи]|ауді?о|аudl)\b': 'Audi',
    # BMW
    r'\b(bmw|бмв|бемве)\b': 'BMW',
    # Porsche
    r'\b(porsche|порш[еа]?|пор[шс]е|porshe)\b': 'Porsche',
    # Mercedes
    r'\b(mercedes|mersedes|мерседес|mercedes-benz|мерс)\b': 'Mercedes-Benz',
    # Toyota
    r'\b(toyota|тойота|тайота)\b': 'Toyota',
    # Volkswagen
    r'\b(volkswagen|vw|wv|фольксваген|фольцваген|vag)\b': 'Volkswagen',
    # Tesla
    r'\b(tesla|тесла)\b': 'Tesla',
    # Volvo
    r'\b(volvo|вольво)\b': 'Volvo',
    # Jeep
    r'\b(jeep|джип)\b': 'Jeep',
    # Ford
    r'\b(ford|форд)\b': 'Ford',
    # Dodge
    r'\b(dodge|додж)\b': 'Dodge',
    # Honda
    r'\b(honda|хонда)\b': 'Honda',
    # Lexus
    r'\b(lexus|лексус)\b': 'Lexus',
    # Land Rover / Range Rover
    r'\b(land rover|рендж|range rover|ренж)\b': 'Land Rover',
    # Jaguar
    r'\b(jaguar|ягуар)\b': 'Jaguar',
    # Infiniti
    r'\b(infiniti|інфініті|инфинити)\b': 'Infiniti',
    # Maserati
    r'\b(maserati|мазераті)\b': 'Maserati',
    # Mazda
    r'\b(mazda|мазда)\b': 'Mazda',
    # Suzuki
    r'\b(suzuki|сузукі)\b': 'Suzuki',
    # Cupra
    r'\b(cupra|купра)\b': 'Cupra',
    # Chrysler
    r'\b(chrysler|крайслер)\b': 'Chrysler',
    # Zeekr
    r'\b(zeekr|зікр)\b': 'Zeekr',
    # JETOUR
    r'\b(jetour)\b': 'JETOUR',
    # ЗАЗ
    r'\b(заз|zaz)\b': 'ZAZ',
}

# Моделі (після вибору марки)
MODEL_NORMALIZE = {
    # Toyota
    'Toyota': {
        r'\b(rav\s*4|rav4|рав\s*4|raw4)\b': 'RAV4',
        r'\b(camry|кемрі)\b': 'Camry',
        r'\b(highlander|highlender|хайлендер)\b': 'Highlander',
        r'\b(prado|прадо)\b': 'Prado',
        r'\b(sequoia|секвоя)\b': 'Sequoia',
        r'\b(ch-?r|chr|сhr)\b': 'C-HR',
        r'\b(prius|пріус)\b': 'Prius',
        r'\b(land cruiser|лендкруз|лендкрузер|lc\s*300)\b': 'Land Cruiser',
    },
    'BMW': {
        r'\b(x5|х5)\b': 'X5',
        r'\b(x7|х7)\b': 'X7',
        r'\b(5 серія|5\s*series|g30|540|530)\b': '5 Series',
        r'\b(430|440|f32|f36|4 серія)\b': '4 Series',
        r'\b(330e|3 серія|3\s*series)\b': '3 Series',
    },
    'Porsche': {
        r'\b(cayenne|каєн|каен|cayen|каен3|кайен)\b': 'Cayenne',
        r'\b(macan|макан|масаn|масan)\b': 'Macan',
        r'\b(panamera|панамера)\b': 'Panamera',
        r'\b(911)\b': '911',
    },
    'Mercedes-Benz': {
        r'\b(glc)\b': 'GLC',
        r'\b(v-?class|vito)\b': 'V-Class',
        r'\b(c-?class|c-клас)\b': 'C-Class',
        r'\b(e-?class|e-?coupe|e-куп)\b': 'E-Class',
        r'\b(w140|s-?class)\b': 'S-Class',
    },
    'Volkswagen': {
        r'\b(touareg|таурег|туарег|тауарег)\b': 'Touareg',
        r'\b(atlas)\b': 'Atlas',
        r'\b(golf|гольф)\b': 'Golf',
        r'\b(passat|пасат)\b': 'Passat',
        r'\b(multivan)\b': 'Multivan',
        r'\b(tayron)\b': 'Tayron',
    },
    'Audi': {
        r'\b(e-?tron|ет?рон)\b': 'e-tron',
        r'\b(q8|sq8|rsq8)\b': 'Q8/SQ8',
        r'\b(q7|ку7)\b': 'Q7',
        r'\b(q5|sq5)\b': 'Q5/SQ5',
        r'\b(a8)\b': 'A8',
        r'\b(a7)\b': 'A7',
        r'\b(s6)\b': 'S6',
        r'\b(rs\s*3)\b': 'RS3',
    },
    'Tesla': {
        r'\b(model\s*s|модель\s*s|модел\s*s)\b': 'Model S',
        r'\b(model\s*3|модель\s*3|модел\s*3)\b': 'Model 3',
        r'\b(model\s*x|модель\s*x|tesla\s*x)\b': 'Model X',
        r'\b(model\s*y|модель\s*y)\b': 'Model Y',
    },
    'Volvo': {
        r'\b(xc90|xc\s*90)\b': 'XC90',
        r'\b(xc60|xc\s*60)\b': 'XC60',
        r'\b(s60)\b': 'S60',
        r'\b(v60)\b': 'V60',
    },
    'Jeep': {
        r'\b(grand cherokee|гранд черокі)\b': 'Grand Cherokee',
        r'\b(cherokee|черокі)\b': 'Cherokee',
        r'\b(compass|компас)\b': 'Compass',
    },
    'Ford': {
        r'\b(mustang|мустанг)\b': 'Mustang',
        r'\b(gt\s*40)\b': 'GT40',
    },
    'Dodge': {
        r'\b(challenger|челленджер)\b': 'Challenger',
        r'\b(charger|чарджер)\b': 'Charger',
        r'\b(ram|рам)\b': 'Ram',
    },
    'Lexus': {
        r'\b(rx)\b': 'RX',
        r'\b(es)\b': 'ES',
    },
    'Infiniti': {
        r'\b(qx55)\b': 'QX55',
    },
    'Honda': {
        r'\b(cr-?v|cr\s*v|crv)\b': 'CR-V',
    },
    'Maserati': {
        r'\b(levante)\b': 'Levante',
    },
    'Jaguar': {
        r'\b(e-?pace)\b': 'E-Pace',
        r'\b(i-?pace)\b': 'I-Pace',
    },
    'Suzuki': {
        r'\b(jimny|джимні)\b': 'Jimny',
    },
    'Mazda': {
        r'\b(mx-?5)\b': 'MX-5',
    },
    'Cupra': {
        r'\b(formentor)\b': 'Formentor',
    },
    'Chrysler': {
        r'\b(pacifica)\b': 'Pacifica',
    },
}

# Типи кузовів на основі моделей
BODY_TYPE = {
    'Audi': {
        'e-tron': 'SUV/Кросовер (електро)',
        'Q8/SQ8': 'SUV/Кросовер', 'Q7': 'SUV/Кросовер', 'Q5/SQ5': 'SUV/Кросовер',
        'A8': 'Седан', 'A7': 'Ліфтбек', 'S6': 'Седан', 'RS3': 'Седан/Хетчбек',
    },
    'BMW': {
        'X5': 'SUV/Кросовер', 'X7': 'SUV/Кросовер',
        '5 Series': 'Седан', '4 Series': 'Купе', '3 Series': 'Седан',
    },
    'Porsche': {
        'Cayenne': 'SUV/Кросовер', 'Macan': 'SUV/Кросовер',
        'Panamera': 'Седан/Ліфтбек', '911': 'Спорткар',
    },
    'Mercedes-Benz': {
        'GLC': 'SUV/Кросовер', 'V-Class': 'Мінівен/Мікроавтобус',
        'C-Class': 'Седан', 'E-Class': 'Седан/Купе', 'S-Class': 'Седан',
    },
    'Toyota': {
        'RAV4': 'SUV/Кросовер', 'Highlander': 'SUV/Кросовер', 'Prado': 'SUV/Кросовер',
        'Sequoia': 'SUV/Кросовер', 'C-HR': 'SUV/Кросовер',
        'Camry': 'Седан', 'Prius': 'Седан/Хетчбек', 'Land Cruiser': 'SUV/Кросовер',
    },
    'Volkswagen': {
        'Touareg': 'SUV/Кросовер', 'Atlas': 'SUV/Кросовер',
        'Tayron': 'SUV/Кросовер',
        'Golf': 'Хетчбек', 'Passat': 'Седан',
        'Multivan': 'Мінівен/Мікроавтобус',
    },
    'Tesla': {
        'Model S': 'Седан', 'Model 3': 'Седан',
        'Model X': 'SUV/Кросовер', 'Model Y': 'SUV/Кросовер',
    },
    'Volvo': {
        'XC90': 'SUV/Кросовер', 'XC60': 'SUV/Кросовер',
        'S60': 'Седан', 'V60': 'Універсал',
    },
    'Jeep': {
        'Grand Cherokee': 'SUV/Кросовер', 'Cherokee': 'SUV/Кросовер', 'Compass': 'SUV/Кросовер',
    },
    'Ford': {
        'Mustang': 'Купе/Спорткар', 'GT40': 'Спорткар',
    },
    'Dodge': {
        'Challenger': 'Купе/Спорткар', 'Charger': 'Седан/Спорткар', 'Ram': 'Пікап',
    },
    'Lexus': {'RX': 'SUV/Кросовер', 'ES': 'Седан'},
    'Infiniti': {'QX55': 'SUV/Кросовер'},
    'Honda': {'CR-V': 'SUV/Кросовер'},
    'Maserati': {'Levante': 'SUV/Кросовер'},
    'Jaguar': {'E-Pace': 'SUV/Кросовер', 'I-Pace': 'SUV/Кросовер (електро)'},
    'Suzuki': {'Jimny': 'SUV/Позашляховик'},
    'Mazda': {'MX-5': 'Родстер/Кабріолет'},
    'Cupra': {'Formentor': 'SUV/Кросовер'},
    'Chrysler': {'Pacifica': 'Мінівен'},
    'Land Rover': {'Range Rover': 'SUV/Кросовер'},
    'Zeekr': {'001': 'Універсал/Шутинг-брейк'},
    'JETOUR': {'T2': 'SUV/Кросовер'},
}

# Країна походження (бренду)
BRAND_COUNTRY = {
    'Audi': 'Німеччина',
    'BMW': 'Німеччина',
    'Porsche': 'Німеччина',
    'Mercedes-Benz': 'Німеччина',
    'Volkswagen': 'Німеччина',
    'Toyota': 'Японія',
    'Honda': 'Японія',
    'Lexus': 'Японія',
    'Mazda': 'Японія',
    'Infiniti': 'Японія',
    'Suzuki': 'Японія',
    'Tesla': 'США',
    'Ford': 'США',
    'Dodge': 'США',
    'Jeep': 'США',
    'Chrysler': 'США',
    'Volvo': 'Швеція',
    'Land Rover': 'Велика Британія',
    'Jaguar': 'Велика Британія',
    'Maserati': 'Італія',
    'Cupra': 'Іспанія',
    'Zeekr': 'Китай',
    'JETOUR': 'Китай',
    'ZAZ': 'Україна',
}

# Orientation by brand
BRAND_TIER = {  # Premium/Luxury/Mass/Sport/EV-first
    'Audi': 'Premium', 'BMW': 'Premium', 'Mercedes-Benz': 'Premium',
    'Porsche': 'Luxury/Sport', 'Maserati': 'Luxury', 'Lexus': 'Premium',
    'Land Rover': 'Premium/Luxury', 'Jaguar': 'Premium',
    'Infiniti': 'Premium',
    'Toyota': 'Mass', 'Honda': 'Mass', 'Mazda': 'Mass', 'Volkswagen': 'Mass/Premium',
    'Ford': 'Mass', 'Dodge': 'Mass/Sport', 'Jeep': 'Mass/Premium', 'Chrysler': 'Mass',
    'Volvo': 'Premium', 'Suzuki': 'Mass', 'Cupra': 'Premium/Sport',
    'Tesla': 'EV-Premium', 'Zeekr': 'EV-Premium', 'JETOUR': 'Mass', 'ZAZ': 'Mass/Budget',
}

# Приблизний ціновий сегмент для моделі (ринок України, б/в 2020-2024)
PRICE_SEGMENT = {
    ('Audi', 'e-tron'): 'Premium ($60-100k)',
    ('Audi', 'Q8/SQ8'): 'Premium ($60-100k)',
    ('Audi', 'Q7'): 'Premium ($40-70k)',
    ('Audi', 'Q5/SQ5'): 'Premium ($30-55k)',
    ('Audi', 'A8'): 'Premium ($40-90k)',
    ('Audi', 'A7'): 'Premium ($35-65k)',
    ('Audi', 'S6'): 'Premium ($40-70k)',
    ('Audi', 'RS3'): 'Premium/Sport ($50-70k)',
    ('BMW', 'X5'): 'Premium ($50-90k)',
    ('BMW', 'X7'): 'Luxury ($70-120k)',
    ('BMW', '5 Series'): 'Premium ($40-70k)',
    ('BMW', '4 Series'): 'Premium ($35-60k)',
    ('BMW', '3 Series'): 'Premium ($30-55k)',
    ('Porsche', 'Cayenne'): 'Luxury ($70-140k)',
    ('Porsche', 'Macan'): 'Luxury ($55-95k)',
    ('Porsche', 'Panamera'): 'Luxury ($90-180k)',
    ('Porsche', '911'): 'Luxury/Sport ($120-250k)',
    ('Mercedes-Benz', 'GLC'): 'Premium ($45-75k)',
    ('Mercedes-Benz', 'V-Class'): 'Premium ($65-110k)',
    ('Mercedes-Benz', 'C-Class'): 'Premium ($40-65k)',
    ('Mercedes-Benz', 'E-Class'): 'Premium ($55-90k)',
    ('Mercedes-Benz', 'S-Class'): 'Luxury ($100-180k)',
    ('Toyota', 'RAV4'): 'Mass ($25-45k)',
    ('Toyota', 'Highlander'): 'Mass+ ($40-60k)',
    ('Toyota', 'Prado'): 'Mass+ ($50-75k)',
    ('Toyota', 'Sequoia'): 'Premium ($70-90k)',
    ('Toyota', 'C-HR'): 'Mass ($25-40k)',
    ('Toyota', 'Camry'): 'Mass ($28-45k)',
    ('Toyota', 'Prius'): 'Mass ($25-40k)',
    ('Toyota', 'Land Cruiser'): 'Premium ($80-120k)',
    ('Volkswagen', 'Touareg'): 'Premium ($45-75k)',
    ('Volkswagen', 'Atlas'): 'Mass+ ($40-55k)',
    ('Volkswagen', 'Golf'): 'Mass ($25-45k)',
    ('Volkswagen', 'Passat'): 'Mass ($30-45k)',
    ('Volkswagen', 'Multivan'): 'Premium ($60-90k)',
    ('Volkswagen', 'Tayron'): 'Mass+ ($35-50k)',
    ('Tesla', 'Model S'): 'Premium ($70-110k)',
    ('Tesla', 'Model 3'): 'Mass+ ($35-50k)',
    ('Tesla', 'Model X'): 'Premium ($80-120k)',
    ('Tesla', 'Model Y'): 'Mass+ ($40-60k)',
    ('Volvo', 'XC90'): 'Premium ($55-85k)',
    ('Volvo', 'XC60'): 'Premium ($45-65k)',
    ('Volvo', 'S60'): 'Premium ($35-50k)',
    ('Volvo', 'V60'): 'Premium ($40-55k)',
    ('Jeep', 'Grand Cherokee'): 'Premium ($45-80k)',
    ('Jeep', 'Cherokee'): 'Mass ($30-45k)',
    ('Jeep', 'Compass'): 'Mass ($28-40k)',
    ('Ford', 'Mustang'): 'Mass/Sport ($40-65k)',
    ('Ford', 'GT40'): 'Luxury/Sport ($400k+)',
    ('Dodge', 'Challenger'): 'Mass/Sport ($40-70k)',
    ('Dodge', 'Charger'): 'Mass/Sport ($40-65k)',
    ('Dodge', 'Ram'): 'Mass+ ($50-75k)',
    ('Lexus', 'RX'): 'Premium ($55-75k)',
    ('Lexus', 'ES'): 'Premium ($40-55k)',
    ('Infiniti', 'QX55'): 'Premium ($50-65k)',
    ('Honda', 'CR-V'): 'Mass ($30-40k)',
    ('Maserati', 'Levante'): 'Luxury ($80-130k)',
    ('Jaguar', 'E-Pace'): 'Premium ($45-60k)',
    ('Jaguar', 'I-Pace'): 'Premium ($70-100k)',
    ('Suzuki', 'Jimny'): 'Mass ($22-30k)',
    ('Mazda', 'MX-5'): 'Mass/Sport ($30-40k)',
    ('Cupra', 'Formentor'): 'Premium ($40-55k)',
    ('Chrysler', 'Pacifica'): 'Mass+ ($45-60k)',
    ('Land Rover', 'Range Rover'): 'Luxury ($100-200k)',
    ('Zeekr', '001'): 'Premium ($50-70k)',
    ('JETOUR', 'T2'): 'Mass ($25-35k)',
}

# Emotional markers
EMOJI_POSITIVE = ['🔥', '😍', '❤️', '🙌', '👌', '😌', '😉', '🥹']
SENTIMENT_WORDS = {
    'positive': ['круто', 'актуально', 'мрі', 'цікав', 'гарн'],
    'request_cheaper': ['дешевш', 'простіш', 'середн', 'не porsche', 'не мерседес'],
    'request_excitement': ['цікав', 'емоці', 'літо', 'кабріолет', 'спорт'],
}

def normalize_brand(text):
    """Return list of detected brands in comment."""
    text_lower = text.lower()
    found = []
    for pattern, brand in BRAND_NORMALIZE.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            if brand not in found:
                found.append(brand)
    return found

def normalize_model(text, brand):
    """Return list of models for given brand in comment."""
    if brand not in MODEL_NORMALIZE:
        return []
    text_lower = text.lower()
    found = []
    for pattern, model in MODEL_NORMALIZE[brand].items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            if model not in found:
                found.append(model)
    return found

def detect_powertrain(text):
    text_lower = text.lower()
    if re.search(r'e-?tron|i-?pace|tesla|електро|electric|eв|zeekr|mach-?e|e-coupe', text_lower):
        return 'Електро'
    if re.search(r'гібрид|hybrid|4xe|e-?coupe|plug-?in|330e|phev|prius', text_lower):
        return 'Гібрид'
    if re.search(r'tdi|дизел|diesel', text_lower):
        return 'Дизель'
    return 'Не вказано (ймовірно бензин)'

def detect_sentiment(text):
    tags = []
    text_lower = text.lower()
    for em in EMOJI_POSITIVE:
        if em in text:
            tags.append('positive_emoji')
            break
    if re.search(r'дешевш|простіш|середн|не porsche|не мерседес|нове', text_lower):
        tags.append('request_cheaper_new')
    if re.search(r'кабріолет|літо|емоці|цікав|🔥', text_lower):
        tags.append('excitement')
    return tags

# === PROCESS COMMENTS ===

brand_counter = Counter()
model_counter = Counter()  # (brand, model)
body_counter = Counter()
powertrain_counter = Counter()
country_counter = Counter()
tier_counter = Counter()
price_counter = Counter()
sentiment_counter = Counter()
comment_unique_users = set()
unique_parent_users = set()

processed = []

for c in comments:
    text = c['t']
    user = c['u']
    likes = c['l']
    unique_parent_users.add(user)
    brands = normalize_brand(text)
    models_detected = []
    for brand in brands:
        brand_counter[brand] += 1
        country_counter[BRAND_COUNTRY.get(brand, '—')] += 1
        tier_counter[BRAND_TIER.get(brand, '—')] += 1
        models = normalize_model(text, brand)
        if not models:
            # Generic mention of brand - count as brand only
            pass
        for m in models:
            model_counter[(brand, m)] += 1
            body = BODY_TYPE.get(brand, {}).get(m)
            if body:
                body_counter[body] += 1
            seg = PRICE_SEGMENT.get((brand, m))
            if seg:
                # Extract tier (Mass/Premium/Luxury)
                if 'Luxury' in seg:
                    price_counter['Luxury ($80k+)'] += 1
                elif 'Premium' in seg and 'Mass' not in seg:
                    price_counter['Premium ($40-80k)'] += 1
                elif 'Mass+' in seg:
                    price_counter['Mass+ ($35-55k)'] += 1
                elif 'Mass' in seg:
                    price_counter['Mass ($20-40k)'] += 1
                else:
                    price_counter['Other'] += 1
            models_detected.append(f'{brand} {m}')

    pt = detect_powertrain(text)
    powertrain_counter[pt] += 1
    sentiments = detect_sentiment(text)
    for s in sentiments:
        sentiment_counter[s] += 1

    processed.append({
        'user': user,
        'text': text,
        'likes': likes,
        'brands': brands,
        'models': models_detected,
        'powertrain': pt,
        'sentiment': sentiments,
    })

# Additional: cabriolet mentions
cabriolet_mentions = sum(1 for c in comments if re.search(r'кабріолет|cabriolet|родстер|roadster|mx-?5', c['t'].lower()))
if cabriolet_mentions:
    body_counter['Кабріолет/Родстер'] = body_counter.get('Кабріолет/Родстер', 0) + cabriolet_mentions

# Sport car mentions (generic)
sport_mentions = sum(1 for c in comments if re.search(r'спорт|mustang|challenger|911|rs\s*3|gt\s*40|sq8|rsq8|audi\s*s6', c['t'].lower()))
# (already captured by models - just for reference)

# === BUILD REPORT DATA ===

report = {
    'total_comments': len(comments),
    'unique_users': len(unique_parent_users),
    'brand_counter': dict(brand_counter.most_common()),
    'model_counter': {f'{b} {m}': v for (b, m), v in model_counter.most_common()},
    'body_counter': dict(body_counter.most_common()),
    'powertrain_counter': dict(powertrain_counter.most_common()),
    'country_counter': dict(country_counter.most_common()),
    'tier_counter': dict(tier_counter.most_common()),
    'price_counter': dict(price_counter.most_common()),
    'sentiment_counter': dict(sentiment_counter.most_common()),
    'cabriolet_mentions': cabriolet_mentions,
    'processed': processed,
}

with open(os.path.join(_HERE, 'analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("=== ВСЬОГО КОМЕНТАРІВ ===")
print(f"Коментарів: {len(comments)}")
print(f"Унікальних користувачів: {len(unique_parent_users)}")
print()
print("=== ТОП-10 МАРКИ ===")
for brand, count in brand_counter.most_common(10):
    print(f"  {brand:20s} — {count}")
print()
print("=== ТОП-15 МОДЕЛІ ===")
for (brand, model), count in model_counter.most_common(15):
    print(f"  {brand} {model:20s} — {count}")
print()
print("=== ТИПИ КУЗОВА ===")
for body, count in body_counter.most_common():
    print(f"  {body:30s} — {count}")
print()
print("=== СИЛОВІ УСТАНОВКИ ===")
for pt, count in powertrain_counter.most_common():
    print(f"  {pt:30s} — {count}")
print()
print("=== КРАЇНА ПОХОДЖЕННЯ ===")
for country, count in country_counter.most_common():
    print(f"  {country:20s} — {count}")
print()
print("=== ЦІНОВИЙ СЕГМЕНТ ===")
for seg, count in price_counter.most_common():
    print(f"  {seg:30s} — {count}")
print()
print("=== СЕНТИМЕНТ ===")
for s, count in sentiment_counter.most_common():
    print(f"  {s:30s} — {count}")
