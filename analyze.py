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
    r'\b(audi|audl|[аА]udl?|ауд[іи]|ауді?о)\b': 'Audi',
    # Окремі моделі Audi (без назви бренду)
    r'\b([еe]-?tron|sq\s*[5-9]|rsq\s*8|sq\s*[5-9])\b': 'Audi',
    r'\b(ку\s*[5-9]|ку8)\b': 'Audi',
    r'\b(sq5|sq7|sq8|rsq8)\b': 'Audi',
    r'\b(q8|q3|а8l?)\b': 'Audi',
    r'\b(rs6|rs\s*6|ауді\s*rs6)\b': 'Audi',
    r'\b(camry|кемрі|камрі)\b': 'Toyota',

    # BMW
    r'\b(bmw|бмв|бемве|бе\s*е\s*мве|беемве)\b': 'BMW',
    r'\bbmwx': 'BMW',                    # BMWX5 без пробілу
    r'\bвmw\b': 'BMW',                   # Cyrillic В + Latin MW
    r'\b(м\s*[3-9]|m\s*[3-9])\s*(купе|coupe|кабр|cabriolet)?\b': 'BMW',  # БеЕМве М 4
    r'\b(g20|g30|f10|f\s*10)\b': 'BMW', # chassis codes
    r'\b(x5m?|х5|x7|х7)\b': 'BMW',      # standalone BMW models

    # Porsche
    r'\b(porsche|порш[еа]?|пор[шс]е|porshe)\b': 'Porsche',
    # Окремі моделі Porsche без назви бренду
    r'\b(cayenne|каєн|каен|кайен)\b': 'Porsche',
    r'\b(cayman|кайман)\b': 'Porsche',
    r'\b(macan|макан)\b': 'Porsche',
    r'\b(panamera|панамера)\b': 'Porsche',
    r'\b(taycan|тайкан)\b': 'Porsche',

    # Mercedes
    r'\b(mercedes|mersedes|мерседес|mercedes-benz|мерс|mers)\b': 'Mercedes-Benz',
    r'\b(мерцедес|мерс\b)\b': 'Mercedes-Benz',
    r'\b(e-?coupe|е-?куп)\b': 'Mercedes-Benz',
    r'\b(cl\b)\b': 'Mercedes-Benz',
    # G-клас / Гелендваген
    r'\b(гелінтваген|гелентваген|гелік|гелик|geländewagen|g.?wagen|g.?class)\b': 'Mercedes-Benz',
    # Окремі моделі Мерседес
    r'\b(amg\s*gt|eqe|eqs|cle\b|е63|e63|gls\b|glecoupe|gle\b|gla\b|glb\b)\b': 'Mercedes-Benz',

    # Toyota
    r'\b(toyota|тойота|тайота)\b': 'Toyota',
    # Окремі моделі Toyota без назви бренду
    r'\b(крузак|крузер|крузера|крузака|landcruiser)\b': 'Toyota',
    r'\b(rav\s*4|rav4|рав\s*4|raw\s*4|raw4)\b': 'Toyota',
    r'(?<!\w)(пріус\w*|prius)': 'Toyota',
    r'\b(gr\s*86|gr86|gt\s*86|gt86)\b': 'Toyota',
    r'\b(sienna|сієна)\b': 'Toyota',
    r'\b(highlander|highlender|хайлендер)\b': 'Toyota',
    r'\b(sequoia|секвоя)\b': 'Toyota',
    r'\b(land\s*cruiser|lc\s*[0-9]{2,3})\b': 'Toyota',

    # Volkswagen
    r'\b(volkswagen|vw|wv|фольксваген|фольцваген|vag)\b': 'Volkswagen',
    # Окремі моделі VW без назви бренду
    r'\b(touareg|таурег|туарег|тауарег|tuareg)\b': 'Volkswagen',
    r'\b(гольф|golf)\b': 'Volkswagen',
    r'\b(тигуан|tiguan|kodiaq)\b': 'Skoda',  # kodiaq → Skoda (нижче)

    # Tesla
    r'\b(tesla|тесл[аиіу])\b': 'Tesla',
    # Окремі моделі Tesla без назви бренду
    r'\b(model\s*[s3xy]|модель\s*[s3xy]|model\s*s\b|model\s*3\b|model\s*x\b|model\s*y\b)\b': 'Tesla',

    # Volvo
    r'\b(volvo|вольво)\b': 'Volvo',
    r'\b(xc\s*90|xc\s*60|v\s*90\b)\b': 'Volvo',

    # Jeep
    r'\b(jeep|джип)\b': 'Jeep',
    r'\b(wrangler|врангл|rubicon|рубікон|grand\s*cherokee|гранд\s*черокі)\b': 'Jeep',

    # Ford
    r'\b(ford|форд)\b': 'Ford',
    r'\b(mustang|мустанг)\b': 'Ford',

    # Dodge
    r'\b(dodge|додж)\b': 'Dodge',
    r'\b(challenger|челленджер|charger|чарджер)\b': 'Dodge',

    # Honda
    r'\b(honda|хонда)\b': 'Honda',

    # Lexus
    r'\b(lexus|лексус)\b': 'Lexus',

    # Land Rover / Range Rover
    r'\b(land\s*rover|range\s*rover|рендж[\s\w]*ровер?|ленд\s*ровер|ренж|рендж)\b': 'Land Rover',
    r'\b(rang\s*rover|rng\s*rover|lend\s*rover)\b': 'Land Rover',   # типові опечатки
    r'\b(дискавері|дискавери|discovery)\b': 'Land Rover',
    r'\b(defender|дефендер|evoque|велар|velar)\b': 'Land Rover',

    # Jaguar
    r'\b(jaguar|ягуар)\b': 'Jaguar',

    # Infiniti
    r'\b(infiniti|infinit[iy]|інфініті|инфинити|infinity)\b': 'Infiniti',

    # Maserati
    r'\b(maserati|мазераті)\b': 'Maserati',

    # Mazda
    r'\b(mazda|мазда|мазд[уиі])\b': 'Mazda',
    r'\b(mx-?5|cx-?90|cx-?5|cx-?30)\b': 'Mazda',

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

    # ===== НОВІ БРЕНДИ =====

    # Alfa Romeo
    r'\b(alfa\s*romeo|альфа\s*ромео)\b': 'Alfa Romeo',
    r'\b(giulia|stelvio|giulietta|джулія|стельвіо)\b': 'Alfa Romeo',

    # Nissan
    r'\b(nissan|ніссан|нісан|нисан)\b': 'Nissan',
    r'\b(350z|370z|x-?trail|skyline|qashqai|pathfinder|навара)\b': 'Nissan',

    # Subaru
    r'\b(subaru|субару)\b': 'Subaru',
    r'\b(outback|аутбек|forester|форестер|brz|impreza|legacy)\b': 'Subaru',

    # KIA
    r'\b(kia|кіа|киа)\b': 'KIA',
    r'\b(ev6|ev3|ev9|carnival|карнавал|sorento|sportage|stinger)\b': 'KIA',

    # Skoda
    r'\b(skoda|шкода|škoda)\b': 'Skoda',
    r'\b(kodiaq|кодіак|octavia|октавія|superb|суперб)\b': 'Skoda',

    # Hyundai
    r'\b(hyundai|хюндай|хундай|хюндаі|хендай)\b': 'Hyundai',
    r'\b(palisade|паліcейд|пелісейд|tucson|santa\s*fe|sonata|ioniq)\b': 'Hyundai',

    # Chevrolet
    r'\b(chevrolet|шевроле|шевролет)\b': 'Chevrolet',
    r'\b(traverse|equinox|tahoe|suburban|silverado|camaro|corvette)\b': 'Chevrolet',

    # Acura
    r'\b(acura|акура)\b': 'Acura',
    r'\b(mdx|rdx|tlx)\b': 'Acura',

    # Rivian
    r'\b(rivian|рівіан)\b': 'Rivian',
    r'\b(r1s|r1t)\b': 'Rivian',

    # Bentley
    r'\b(bentley|бентлі)\b': 'Bentley',
    r'\b(bentayga|continental\s*gt|flying\s*spur|бентайга)\b': 'Bentley',

    # BYD
    r'\b(byd|б\.?ю\.?д)\b': 'BYD',
    r'\b(han\b|tang\b|atto\s*3|yuan|seagull|seal\b)\b': 'BYD',

    # Polestar
    r'\b(polestar|полестар|polestar\s*[0-9])\b': 'Polestar',

    # Li Auto (LiXiang)
    r'\b(li\s*auto|lixiang|ліксян|li\s*l[0-9])\b': 'Li Auto',

    # Denza (BYD subsidiary)
    r'\b(denza|денза)\b': 'Denza',

    # Peugeot
    r'\b(peugeot|пежо|пежó)\b': 'Peugeot',

    # Citroen
    r'\b(citroen|citroën|сітроен|ситроен)\b': 'Citroen',

    # Lincoln
    r'\b(lincoln|лінкольн|лінколн)\b': 'Lincoln',

    # Mitsubishi
    r'\b(mitsubishi|міцубісі|мицубиси|мітсубіші|мітсубіси)\b': 'Mitsubishi',
    r'\b(lancer|eclipse|pajero|outlander|asx|galant)\b': 'Mitsubishi',

    # RAM (окрема марка після відокремлення від Dodge)
    r'\b(ram\s*1500|ram\s*2500|ramcharger)\b': 'RAM',

    # Genesis
    r'\b(genesis|генезис|genesys)\b': 'Genesis',
    r'\b(gv80|gv70|gv60|g80|g90)\b': 'Genesis',

    # Cadillac
    r'\b(cadillac|кадилак|кадиллак)\b': 'Cadillac',
    r'\b(escalade|ескалейд|ct5|ct6)\b': 'Cadillac',

    # Lamborghini
    r'\b(lamborghini|ламборгіні|ламборгині)\b': 'Lamborghini',
    r'\b(urus|урус|huracán|huracan|aventador)\b': 'Lamborghini',

    # Ferrari
    r'\b(ferrari|феррарі|феррари)\b': 'Ferrari',

    # Rolls-Royce
    r'\b(rolls.?royce|роллс.?ройс)\b': 'Rolls-Royce',
    r'\b(cullinan|ghost\b|wraith\b|phantom\b)\b': 'Rolls-Royce',

    # Aston Martin
    r'\b(aston\s*martin|астон\s*мартін)\b': 'Aston Martin',
    r'\b(dbx|vantage|db11|db12)\b': 'Aston Martin',

    # McLaren
    r'\b(mclaren|маклерен|макларен)\b': 'McLaren',

    # Mercedes G-клас як окрема "модель" → Mercedes-Benz
    r'\b(g\s*[56][0-9]{1,2}[d]?|g\s*[0-9]{3}\b)\b': 'Mercedes-Benz',
}

# Моделі (після вибору марки)
MODEL_NORMALIZE = {
    # Toyota
    'Toyota': {
        r'\b(rav\s*4|rav4|рав\s*4|raw\s*4|raw4)\b': 'RAV4',
        r'\b(camry|кемрі|камрі)\b': 'Camry',
        r'\b(highlander|highlender|хайлендер)\b': 'Highlander',
        r'\b(prado|прадо)\b': 'Prado',
        r'\b(sequoia|секвоя)\b': 'Sequoia',
        r'\b(ch-?r|chr|сhr)\b': 'C-HR',
        r'\b(prius|пріус\w*)\b': 'Prius',
        r'\b(land\s*cruiser|лендкруз|лендкрузер|lc\s*300|крузак|крузер[аи]?|крузака|landcruiser)\b': 'Land Cruiser',
        r'\blc\s*200\b|\bленд\s*крузер\s*200\b|\bкрузер\s*200\b|\bкрузак\s*300\b': 'Land Cruiser 200',
        r'\blc\s*300\b|\bland\s*cruiser\s*300\b|\bкрузак\s*300\b|\bкрузер\s*300\b': 'Land Cruiser 300',
        r'\b(gr\s*86|gr86|gt\s*86|gt86)\b': 'GR86',
        r'\b(sienna|сієна|siena)\b': 'Sienna',
        r'\b(camry\s*3[\.,]5)\b': 'Camry',
        r'\b(supra|супра)\b': 'Supra',
        r'\b(tundra|тундра)\b': 'Tundra',
        r'\b(corolla\s*cross|корол[а-я]*\s*кросс?)\b': 'Corolla Cross',
        r'\b(yaris\s*cross?|yaris|яріс)\b': 'Yaris',
        r'\b(corolla|королл?а)\b': 'Corolla',
        r'\blc\s*80\b|\bland\s*cruiser\s*80\b|\bкрузак\s*80\b|\b80\s*серії?\b|\btoyota\s*80\b': 'Land Cruiser 80',
    },
    'BMW': {
        r'\b(x3|х3)\b': 'X3',
        r'\b(x5|х5)\b': 'X5',
        r'\b(x6|х6)\b': 'X6',
        r'\b(x7|х7)\b': 'X7',
        r'\b(ix|ix3|ix[^a-z])\b': 'iX',
        r'\b(5\s*серія|5\s*series|g30|540|530|m5)\b': '5 Series',
        r'\b(430|440|f32|f36|4\s*серія|m4|м4)\b': '4 Series',
        r'\b(330e|3\s*серія|3\s*series|g20|m3)\b': '3 Series',
        r'\b(m8|bmw\s*m8)\b': 'M8',
        r'\b(g05)\b': 'X5',
        r'\b(x5\s*g05|x5\s*hybrid|530e)\b': 'X5',
        r'\b(бе\s*е\s*мве\s*м\s*[3-9]|бемве\s*м\s*[3-9]|bmw\s*m[3-9])\b': 'M Series',
        r'\b(z4)\b': 'Z4',
        r'\b(2\s*series|2\s*серія|f22|f44|m2|218|220|228|230|235|240)\b': '2 Series',
        r'\b(6\s*series|6\s*серія|f06|f12|f13|m6|630|640|650|gran\s*coup[eе])\b': '6 Series',
        r'\b(i8)\b': 'i8',
        r'\b(g20|f30|328|330|335|340)\b': '3 Series',
        r'\b(f10|525|528|530|535|540)\b': '5 Series',
        r'\b(ф\s*10|ф10)\b': '5 Series',
    },
    'Porsche': {
        r'\b(cayenne|каєн|каен|cayen|каен3|кайен)\b': 'Cayenne',
        r'\b(cayman|кайман)\b': 'Cayman',
        r'\b(macan|макан|масаn|масan)\b': 'Macan',
        r'\b(panamera|панамера)\b': 'Panamera',
        r'\b(911)\b': '911',
        r'\b(taycan|тайкан)\b': 'Taycan',
        r'\b(cayenne\s*3[\.,]6|каєн\s*3[\.,]6)\b': 'Cayenne',
    },
    'Mercedes-Benz': {
        r'\b(glc)\b': 'GLC',
        r'\b(gle)\b': 'GLE',
        r'\b(gls)\b': 'GLS',
        r'\b(gla)\b': 'GLA',
        r'\b(glb)\b': 'GLB',
        r'\b(v-?class|v\s*class|vito)\b': 'V-Class',
        r'\b(c-?class|c-клас)\b': 'C-Class',
        r'\b(e-?class|e-?coupe|e-куп|e63|є63)\b': 'E-Class',
        r'\b(w140|s-?class|s\s*[0-9]{3}|222\b|w222|s\s*клас[иу]?|s-?кл)\b': 'S-Class',
        r'\b(g-?class|g\s*[56]\d\d|гелінтваген|гелентваген|гелік|гелик|g.?wagen)\b': 'G-Class',
        r'\b(cle|цле)\b': 'CLE',
        r'\b(eqe)\b': 'EQE',
        r'\b(eqs)\b': 'EQS',
        r'\b(amg\s*gt)\b': 'AMG GT',
        r'\b(cl\b)\b': 'CL',
        r'\b(mers\s*s.class|mers\s*s)\b': 'S-Class',
    },
    'Volkswagen': {
        r'\b(touareg|таурег|туарег|тауарег|tuareg)\b': 'Touareg',
        r'\b(atlas)\b': 'Atlas',
        r'\b(гольф|golf)\b': 'Golf',
        r'\b(passat|пасат)\b': 'Passat',
        r'\b(multivan)\b': 'Multivan',
        r'\b(tayron)\b': 'Tayron',
        r'\b(tiguan|тигуан)\b': 'Tiguan',
        r'\b(golf\s*gti|гольф\s*gti|gti)\b': 'Golf GTI',
        r'\b(golf\s*[rг]|гольф\s*[rг])\b': 'Golf R',
        r'\b(golf\s*[rг][\/\|]gti|гольф\s*[rг][\/\|]gti)\b': 'Golf GTI/R',
        r'\b(tuareg|tuareg\s*v8)\b': 'Touareg',
        r'\b(arteon)\b': 'Arteon',
        r'\b(id[\.\s]*4)\b': 'ID.4',
        r'\b(volkswagen\s*cc|vw\s*cc|\bcc\b)\b': 'CC',
        r'\b(tigun|tiguan|тигуан)\b': 'Tiguan',
    },
    'Audi': {
        r'\b([еe]-?tron|е-?\s*трон|аудіо?\s*[еe]-?\s*tron|audi\s*e-?tron)\b': 'e-tron',
        r'\b(q4\s*e-?tron|q4)\b': 'Q4 e-tron',
        r'\b(q8|sq8|rsq8)\b': 'Q8/SQ8',
        r'\b(q7|ку\s*7|ку7|q\s*7)\b': 'Q7',
        r'\b(q5|sq5|ку\s*5)\b': 'Q5/SQ5',
        r'\b(sq7)\b': 'SQ7',
        r'\b(a8|а8|a8l)\b': 'A8',
        r'\b(a7)\b': 'A7',
        r'\b(s6)\b': 'S6',
        r'\b(rs\s*3)\b': 'RS3',
        r'\b(a5|a5\s*sportback)\b': 'A5',
        r'\b(аudl?\s*8)\b': 'A8',
        r'\b(a6\s*allroad|a6\s*all\s*road|allroad|а6\s*олроуд)\b': 'A6 Allroad',
        r'\b(a6|а\s*6|a6\s*c[5-8])\b': 'A6',
        r'\b(a3|а3)\b': 'A3',
        r'\b(q3|ку\s*3)\b': 'Q3',
        r'\b([oо]5)\b': 'Q5/SQ5',
        r'\b(s5)\b': 'S5',
        r'\b(rs\s*6|rs6)\b': 'RS6',
        r'\b(а8l?)\b': 'A8',
    },
    'Tesla': {
        r'\b(model\s*s|модель\s*s|модел\s*s)\b': 'Model S',
        r'\b(model\s*3|модель\s*3|модел\s*3)\b': 'Model 3',
        r'\b(model\s*x|модель\s*x|tesla\s*x)\b': 'Model X',
        r'\b(model\s*y|модель\s*y)\b': 'Model Y',
        r'\b(cybertruck|кібертрак)\b': 'Cybertruck',
        r'\b(тесла\s*3|tesla\s*3)\b': 'Model 3',
        r'\b(тесла\s*x|tesla\s*x)\b': 'Model X',
    },
    'Volvo': {
        r'\b(xc90|xc\s*90)\b': 'XC90',
        r'\b(xc60|xc\s*60)\b': 'XC60',
        r'\b(xc40|xc\s*40)\b': 'XC40',
        r'\b(s60)\b': 'S60',
        r'\b(v60)\b': 'V60',
        r'\b(v90\b|v90\s*cross\s*country|v90cc|v\s*90\s*cross)\b': 'V90',
        r'\b(xc70|xc\s*70|хс\s*70)\b': 'XC70',
        r'\b(s90|s\s*90)\b': 'S90',
        r'\b(хс\s*90)\b': 'XC90',
        r'\b(вольво\s*хс\s*90|volvo\s*xc\s*90)\b': 'XC90',
    },
    'Jeep': {
        r'\b(grand\s*cherokee|гранд\s*черокі)\b': 'Grand Cherokee',
        r'\b(cherokee|черокі)\b': 'Cherokee',
        r'\b(compass|компас)\b': 'Compass',
        r'\b(wrangler|врангл|rubicon|рубікон)\b': 'Wrangler',
        r'\b(gladiator)\b': 'Gladiator',
    },
    'Ford': {
        r'\b(mustang|мустанг)\b': 'Mustang',
        r'\b(gt\s*40)\b': 'GT40',
        r'\b(explorer)\b': 'Explorer',
        r'\b(ranger)\b': 'Ranger',
        r'\b(bronco)\b': 'Bronco',
        r'\b(focus\s*rs|фокус\s*рс)\b': 'Focus RS',
        r'\b(focus|фокус)\b': 'Focus',
        r'\b(flex)\b': 'Flex',
        r'\b(f-?150|f150)\b': 'F-150',
    },
    'Dodge': {
        r'\b(challenger|челленджер)\b': 'Challenger',
        r'\b(charger|чарджер)\b': 'Charger',
        r'\b(ram|рам)\b': 'Ram',
        r'\b(durango)\b': 'Durango',
        r'\b(viper)\b': 'Viper',
    },
    'RAM': {
        r'\b(ram\s*1500|1500)\b': 'RAM 1500',
        r'\b(ram\s*2500|2500)\b': 'RAM 2500',
        r'\b(ramcharger)\b': 'RAM 1500 Ramcharger',
    },
    'Lexus': {
        r'\b(rx|rx\s*[0-9]{3})\b': 'RX',
        r'\b(es)\b': 'ES',
        r'\b(lx|lx\s*[0-9]{3}|lx\s*450)\b': 'LX',
        r'\b(nx)\b': 'NX',
        r'\b(gx)\b': 'GX',
        r'\b(ls)\b': 'LS',
        r'\b(px|px\s*hybrid)\b': 'LX',  # можлива помилка "PX" → LX
    },
    'Infiniti': {
        r'\b(qx55)\b': 'QX55',
        r'\b(qx60)\b': 'QX60',
        r'\b(qx50)\b': 'QX50',
        r'\b(q50)\b': 'Q50',
        r'\b(qx\s*55)\b': 'QX55',
        r'\b(qx56)\b': 'QX56',
        r'\b(qx80)\b': 'QX80',
    },
    'Honda': {
        r'\b(cr-?v|cr\s*v|crv)\b': 'CR-V',
        r'\b(hrv|hr-?v)\b': 'HR-V',
        r'\b(pilot)\b': 'Pilot',
        r'\b(civic)\b': 'Civic',
        r'\b(prologue)\b': 'Prologue',
        r'\b(accord)\b': 'Accord',
    },
    'Maserati': {
        r'\b(levante)\b': 'Levante',
        r'\b(ghibli)\b': 'Ghibli',
        r'\b(quattroporte)\b': 'Quattroporte',
    },
    'Jaguar': {
        r'\b(e-?pace)\b': 'E-Pace',
        r'\b(i-?pace)\b': 'I-Pace',
        r'\b(f-?pace)\b': 'F-Pace',
        r'\b(xe)\b': 'XE',
        r'\b(xf)\b': 'XF',
        r'\b(f[- ]?type)\b': 'F-Type',
    },
    'Suzuki': {
        r'\b(jimny|джимні)\b': 'Jimny',
        r'\b(vitara)\b': 'Vitara',
        r'\b(s-?cross|sx4)\b': 'S-Cross',
    },
    'Mazda': {
        r'\b(mx-?5)\b': 'MX-5',
        r'\b(cx-?90|cx\s*90|мазду?\s*сх-?90)\b': 'CX-90',
        r'\b(cx-?5|cx\s*5)\b': 'CX-5',
        r'\b(cx-?30|cx\s*30)\b': 'CX-30',
        r'\b(mazda\s*6|мазда\s*6|mazda6)\b': 'Mazda6',
    },
    'Cupra': {
        r'\b(formentor)\b': 'Formentor',
        r'\b(born)\b': 'Born',
        r'\b(ateca)\b': 'Ateca',
    },
    'Chrysler': {
        r'\b(pacifica)\b': 'Pacifica',
        r'\b(300c|300\s*c)\b': '300C',
    },
    'Land Rover': {
        r'\b(range\s*rover|рендж[^а-яa-z0-9]*ровер|rang\s*rover|rng\s*rover)\b': 'Range Rover',
        r'\b(рендж\s*ровер)\b': 'Range Rover',
        r'\b(velar|велар)\b': 'Range Rover Velar',
        r'\b(evoque|евок|ивок)\b': 'Range Rover Evoque',
        r'\b(sport\b)\b': 'Range Rover Sport',
        r'\b(discovery\s*sport|д[іи]скавері\s*спорт)\b': 'Discovery Sport',
        r'\b(discovery|дискавері|дискавери)\b': 'Discovery',
        r'\b(defender|дефендер)\b': 'Defender',
        r'\b(freelander)\b': 'Freelander',
    },
    'Alfa Romeo': {
        r'\b(giulia|джулія)\b': 'Giulia',
        r'\b(stelvio|стельвіо)\b': 'Stelvio',
        r'\b(giulietta)\b': 'Giulietta',
        r'\b(tonale)\b': 'Tonale',
    },
    'Nissan': {
        r'\b(350z)\b': '350Z',
        r'\b(370z)\b': '370Z',
        r'\b(x-?trail|x\s*trail)\b': 'X-Trail',
        r'\b(qashqai)\b': 'Qashqai',
        r'\b(skyline\s*[rR]\s*[0-9]{2}|skyline)\b': 'Skyline',
        r'\b(pathfinder)\b': 'Pathfinder',
        r'\b(ariya)\b': 'Ariya',
    },
    'Subaru': {
        r'\b(outback|аутбек)\b': 'Outback',
        r'\b(forester|форестер)\b': 'Forester',
        r'\b(brz)\b': 'BRZ',
        r'\b(impreza)\b': 'Impreza',
        r'\b(legacy)\b': 'Legacy',
        r'\b(wrx)\b': 'WRX',
    },
    'KIA': {
        r'\b(ev6)\b': 'EV6',
        r'\b(ev3)\b': 'EV3',
        r'\b(ev9)\b': 'EV9',
        r'\b(carnival|карнавал)\b': 'Carnival',
        r'\b(sorento|сорренто)\b': 'Sorento',
        r'\b(sportage|спортейдж)\b': 'Sportage',
        r'\b(stinger)\b': 'Stinger',
    },
    'Skoda': {
        r'\b(kodiaq\s*rs|kodiak\s*rs)\b': 'Kodiaq RS',
        r'\b(kodiaq|кодіак|kodiak)\b': 'Kodiaq',
        r'\b(octavia|октавія)\b': 'Octavia',
        r'\b(superb|суперб)\b': 'Superb',
        r'\b(enyaq)\b': 'Enyaq',
    },
    'Hyundai': {
        r'\b(palisade|паліcейд)\b': 'Palisade',
        r'\b(tucson|туксон)\b': 'Tucson',
        r'\b(santa\s*fe|санта\s*фе)\b': 'Santa Fe',
        r'\b(sonata|соната)\b': 'Sonata',
        r'\b(ioniq\s*5|ioniq5)\b': 'IONIQ 5',
        r'\b(ioniq\s*6|ioniq6)\b': 'IONIQ 6',
    },
    'Chevrolet': {
        r'\b(traverse)\b': 'Traverse',
        r'\b(equinox)\b': 'Equinox',
        r'\b(tahoe)\b': 'Tahoe',
        r'\b(suburban)\b': 'Suburban',
        r'\b(silverado)\b': 'Silverado',
        r'\b(camaro)\b': 'Camaro',
        r'\b(corvette)\b': 'Corvette',
    },
    'Acura': {
        r'\b(mdx)\b': 'MDX',
        r'\b(rdx)\b': 'RDX',
        r'\b(tlx)\b': 'TLX',
    },
    'Rivian': {
        r'\b(r1s)\b': 'R1S',
        r'\b(r1t)\b': 'R1T',
    },
    'Bentley': {
        r'\b(bentayga|бентайга)\b': 'Bentayga',
        r'\b(continental\s*gt)\b': 'Continental GT',
        r'\b(flying\s*spur)\b': 'Flying Spur',
    },
    'BYD': {
        r'\b(han\b)\b': 'Han',
        r'\b(tang\b)\b': 'Tang',
        r'\b(atto\s*3)\b': 'Atto 3',
        r'\b(yuan)\b': 'Yuan',
        r'\b(seal\b)\b': 'Seal',
    },
    'Polestar': {
        r'\b(polestar\s*[0-9]|[0-9]\b)\b': 'Polestar 4',
    },
    'Li Auto': {
        r'\b(l[579]\b|li\s*l[579])\b': 'L7',
    },
    'Denza': {
        r'\b(z9|z9\s*gt)\b': 'Z9 GT',
        r'\b(d9)\b': 'D9',
    },
    'Zeekr': {
        r'\b(001(?:\s*ultra\s*plus)?)\b': '001',
        r'\b(7x)\b': '7X',
        r'\b(9x)\b': '9X',
    },
    'JETOUR': {
        r'\b([тt]2|t\s*2)\b': 'T2',
    },
    'Peugeot': {
        r'\b(4008)\b': '4008',
        r'\b(3008)\b': '3008',
        r'\b(508)\b': '508',
        r'\b(2008)\b': '2008',
        r'\b(ds\s*5|ds5)\b': 'DS5',
    },
    'Citroen': {
        r'\b(гранд\s*пікассо|grand\s*picasso|c4\s*picasso|c4\s*grand)\b': 'C4 Grand Picasso',
        r'\b(c5\s*aircross)\b': 'C5 Aircross',
        r'\b(ds\s*5|ds5)\b': 'DS5',
    },
    'Lincoln': {
        r'\b(continental|навігатор|navigator|aviator)\b': 'Continental',
    },
    'Mitsubishi': {
        r'\b(lancer|lancer\s*evo|lancer\s*x|evo\s*[0-9x]|lancer\s*[xх]\s*evo)\b': 'Lancer Evolution',
        r'\b(eclipse)\b': 'Eclipse',
        r'\b(pajero)\b': 'Pajero',
        r'\b(outlander)\b': 'Outlander',
        r'\b(asx)\b': 'ASX',
    },
    'Genesis': {
        r'\b(gv80)\b': 'GV80',
        r'\b(gv70)\b': 'GV70',
        r'\b(gv60)\b': 'GV60',
        r'\b(g80)\b': 'G80',
        r'\b(g90)\b': 'G90',
    },
    'Cadillac': {
        r'\b(escalade|ескалейд)\b': 'Escalade',
        r'\b(ct5)\b': 'CT5',
        r'\b(ct6)\b': 'CT6',
        r'\b(lyriq)\b': 'LYRIQ',
    },
    'Lamborghini': {
        r'\b(urus|урус)\b': 'Urus',
        r'\b(hurac[aá]n|huracan)\b': 'Huracán',
        r'\b(aventador)\b': 'Aventador',
    },
    'Rolls-Royce': {
        r'\b(cullinan)\b': 'Cullinan',
        r'\b(ghost)\b': 'Ghost',
        r'\b(wraith)\b': 'Wraith',
        r'\b(phantom)\b': 'Phantom',
        r'\b(spectre)\b': 'Spectre',
    },
    'Aston Martin': {
        r'\b(dbx)\b': 'DBX',
        r'\b(vantage)\b': 'Vantage',
        r'\b(db11|db12)\b': 'DB11',
    },
}

# Типи кузовів на основі моделей
BODY_TYPE = {
    'Audi': {
        'e-tron': 'SUV/Кросовер (електро)',
        'Q4 e-tron': 'SUV/Кросовер (електро)',
        'Q8/SQ8': 'SUV/Кросовер',
        'SQ7': 'SUV/Кросовер',
        'Q7': 'SUV/Кросовер',
        'Q5/SQ5': 'SUV/Кросовер',
        'A8': 'Седан',
        'A7': 'Ліфтбек',
        'A5': 'Купе/Ліфтбек',
        'S6': 'Седан',
        'RS3': 'Седан/Хетчбек',
        'A6': 'Седан',
        'A6 Allroad': 'Універсал',
        'A3': 'Седан/Хетчбек',
        'Q3': 'SUV/Кросовер',
        'S5': 'Купе/Седан',
        'RS6': 'Універсал/Спорткар',
    },
    'BMW': {
        'X3': 'SUV/Кросовер',
        'X5': 'SUV/Кросовер',
        'X6': 'SUV/Купе-кросовер',
        'X7': 'SUV/Кросовер',
        'iX': 'SUV/Кросовер (електро)',
        '5 Series': 'Седан',
        '4 Series': 'Купе',
        '3 Series': 'Седан',
        'M8': 'Купе/Спорткар',
        'M Series': 'Спорткар/Седан',
        'Z4': 'Родстер/Кабріолет',
        '2 Series': 'Купе/Хетчбек',
        '6 Series': 'Купе/Ліфтбек',
        'i8': 'Гібридний Спорткар',
    },
    'Porsche': {
        'Cayenne': 'SUV/Кросовер',
        'Macan': 'SUV/Кросовер',
        'Panamera': 'Седан/Ліфтбек',
        '911': 'Спорткар',
        'Taycan': 'Седан (електро)',
        'Cayman': 'Купе/Спорткар',
    },
    'Mercedes-Benz': {
        'GLC': 'SUV/Кросовер',
        'GLE': 'SUV/Кросовер',
        'GLS': 'SUV/Кросовер',
        'GLA': 'SUV/Кросовер',
        'GLB': 'SUV/Кросовер',
        'G-Class': 'SUV/Позашляховик',
        'V-Class': 'Мінівен/Мікроавтобус',
        'C-Class': 'Седан',
        'E-Class': 'Седан/Купе',
        'S-Class': 'Седан',
        'CLE': 'Купе',
        'EQE': 'Седан (електро)',
        'EQS': 'Седан (електро)',
        'AMG GT': 'Спорткар',
        'CL': 'Купе',
    },
    'Toyota': {
        'RAV4': 'SUV/Кросовер',
        'Highlander': 'SUV/Кросовер',
        'Prado': 'SUV/Кросовер',
        'Land Cruiser': 'SUV/Кросовер',
        'Land Cruiser 200': 'SUV/Кросовер',
        'Land Cruiser 300': 'SUV/Кросовер',
        'Sequoia': 'SUV/Кросовер',
        'C-HR': 'SUV/Кросовер',
        'Camry': 'Седан',
        'Prius': 'Седан/Хетчбек',
        'GR86': 'Купе/Спорткар',
        'Sienna': 'Мінівен',
        'Supra': 'Купе/Спорткар',
        'Tundra': 'Пікап',
        'Corolla Cross': 'SUV/Кросовер',
        'Yaris': 'Хетчбек',
        'Corolla': 'Седан',
        'Land Cruiser 80': 'SUV/Кросовер',
    },
    'Volkswagen': {
        'Touareg': 'SUV/Кросовер',
        'Atlas': 'SUV/Кросовер',
        'Tayron': 'SUV/Кросовер',
        'Tiguan': 'SUV/Кросовер',
        'Golf': 'Хетчбек',
        'Golf GTI': 'Хетчбек/Спорт',
        'Golf R': 'Хетчбек/Спорт',
        'Golf GTI/R': 'Хетчбек/Спорт',
        'Arteon': 'Ліфтбек',
        'ID.4': 'SUV/Кросовер (електро)',
        'CC': 'Ліфтбек',
        'Passat': 'Седан',
        'Multivan': 'Мінівен/Мікроавтобус',
    },
    'Tesla': {
        'Model S': 'Седан',
        'Model 3': 'Седан',
        'Model X': 'SUV/Кросовер (електро)',
        'Model Y': 'SUV/Кросовер (електро)',
        'Cybertruck': 'Пікап (електро)',
    },
    'Volvo': {
        'XC90': 'SUV/Кросовер',
        'XC60': 'SUV/Кросовер',
        'XC40': 'SUV/Кросовер',
        'XC70': 'SUV/Кросовер',
        'S60': 'Седан',
        'S90': 'Седан',
        'V60': 'Універсал',
        'V90': 'Універсал',
    },
    'Jeep': {
        'Grand Cherokee': 'SUV/Кросовер',
        'Cherokee': 'SUV/Кросовер',
        'Compass': 'SUV/Кросовер',
        'Wrangler': 'SUV/Позашляховик',
        'Gladiator': 'Пікап',
    },
    'Ford': {
        'Mustang': 'Купе/Спорткар',
        'GT40': 'Спорткар',
        'Explorer': 'SUV/Кросовер',
        'Ranger': 'Пікап',
        'Bronco': 'SUV/Позашляховик',
        'Focus RS': 'Хетчбек/Спорт',
        'Focus': 'Хетчбек/Седан',
        'Flex': 'SUV/Кросовер',
        'F-150': 'Пікап',
    },
    'Dodge': {
        'Challenger': 'Купе/Спорткар',
        'Charger': 'Седан/Спорткар',
        'Ram': 'Пікап',
        'Durango': 'SUV/Кросовер',
        'Viper': 'Спорткар',
    },
    'RAM': {
        'RAM 1500': 'Пікап',
        'RAM 2500': 'Пікап',
        'RAM 1500 Ramcharger': 'Пікап (PHEV)',
    },
    'Lexus': {'RX': 'SUV/Кросовер', 'ES': 'Седан', 'LX': 'SUV/Кросовер', 'NX': 'SUV/Кросовер', 'GX': 'SUV/Кросовер', 'LS': 'Седан'},
    'Infiniti': {'QX55': 'SUV/Кросовер', 'QX60': 'SUV/Кросовер', 'QX50': 'SUV/Кросовер', 'Q50': 'Седан', 'QX56': 'SUV/Кросовер', 'QX80': 'SUV/Кросовер'},
    'Honda': {'CR-V': 'SUV/Кросовер', 'HR-V': 'SUV/Кросовер', 'Pilot': 'SUV/Кросовер', 'Civic': 'Седан/Хетчбек'},
    'Maserati': {'Levante': 'SUV/Кросовер', 'Ghibli': 'Седан', 'Quattroporte': 'Седан'},
    'Jaguar': {'E-Pace': 'SUV/Кросовер', 'I-Pace': 'SUV/Кросовер (електро)', 'F-Pace': 'SUV/Кросовер', 'XE': 'Седан', 'XF': 'Седан'},
    'Suzuki': {'Jimny': 'SUV/Позашляховик', 'Vitara': 'SUV/Кросовер'},
    'Mazda': {'MX-5': 'Родстер/Кабріолет', 'CX-90': 'SUV/Кросовер', 'CX-5': 'SUV/Кросовер', 'CX-30': 'SUV/Кросовер', 'Mazda6': 'Седан'},
    'Cupra': {'Formentor': 'SUV/Кросовер', 'Born': 'Хетчбек (електро)', 'Ateca': 'SUV/Кросовер'},
    'Chrysler': {'Pacifica': 'Мінівен', '300C': 'Седан'},
    'Land Rover': {
        'Range Rover': 'SUV/Кросовер',
        'Range Rover Velar': 'SUV/Кросовер',
        'Range Rover Evoque': 'SUV/Кросовер',
        'Range Rover Sport': 'SUV/Кросовер',
        'Discovery': 'SUV/Кросовер',
        'Discovery Sport': 'SUV/Кросовер',
        'Defender': 'SUV/Позашляховик',
        'Freelander': 'SUV/Кросовер',
    },
    'Alfa Romeo': {'Giulia': 'Седан/Спорткар', 'Stelvio': 'SUV/Кросовер', 'Giulietta': 'Хетчбек', 'Tonale': 'SUV/Кросовер'},
    'Nissan': {'350Z': 'Купе/Спорткар', '370Z': 'Купе/Спорткар', 'X-Trail': 'SUV/Кросовер', 'Qashqai': 'SUV/Кросовер', 'Skyline': 'Купе/Спорткар', 'Ariya': 'SUV/Кросовер (електро)'},
    'Subaru': {'Outback': 'Універсал/SUV', 'Forester': 'SUV/Кросовер', 'BRZ': 'Купе/Спорткар', 'Impreza': 'Хетчбек', 'Legacy': 'Седан', 'WRX': 'Седан/Спорткар'},
    'KIA': {'EV6': 'Кросовер (електро)', 'EV3': 'Хетчбек (електро)', 'EV9': 'SUV/Кросовер (електро)', 'Carnival': 'Мінівен', 'Sorento': 'SUV/Кросовер', 'Sportage': 'SUV/Кросовер', 'Stinger': 'Седан/Спорткар'},
    'Skoda': {'Kodiaq': 'SUV/Кросовер', 'Kodiaq RS': 'SUV/Кросовер (спорт)', 'Octavia': 'Седан/Хетчбек', 'Superb': 'Седан', 'Enyaq': 'SUV/Кросовер (електро)'},
    'Hyundai': {'Palisade': 'SUV/Кросовер', 'Tucson': 'SUV/Кросовер', 'Santa Fe': 'SUV/Кросовер', 'Sonata': 'Седан', 'IONIQ 5': 'Кросовер (електро)', 'IONIQ 6': 'Седан (електро)'},
    'Chevrolet': {'Traverse': 'SUV/Кросовер', 'Equinox': 'SUV/Кросовер', 'Tahoe': 'SUV/Кросовер', 'Suburban': 'SUV/Кросовер', 'Silverado': 'Пікап', 'Camaro': 'Купе/Спорткар', 'Corvette': 'Спорткар'},
    'Acura': {'MDX': 'SUV/Кросовер', 'RDX': 'SUV/Кросовер', 'TLX': 'Седан/Спорткар'},
    'Rivian': {'R1S': 'SUV/Кросовер (електро)', 'R1T': 'Пікап (електро)'},
    'Bentley': {'Bentayga': 'SUV/Кросовер', 'Continental GT': 'Купе', 'Flying Spur': 'Седан'},
    'BYD': {'Han': 'Седан (електро)', 'Tang': 'SUV (електро)', 'Atto 3': 'SUV/Кросовер (електро)', 'Yuan': 'SUV/Кросовер (електро)', 'Seal': 'Седан (електро)'},
    'Polestar': {'Polestar 4': 'SUV/Кросовер (електро)'},
    'Li Auto': {'L7': 'SUV/Кросовер (PHEV)'},
    'Denza': {'Z9 GT': 'Універсал/Спорткар (електро)', 'D9': 'Мінівен (електро)'},
    'Peugeot': {'4008': 'SUV/Кросовер', '3008': 'SUV/Кросовер', '508': 'Седан', '2008': 'SUV/Кросовер'},
    'Citroen': {'C4 Grand Picasso': 'Мінівен', 'C5 Aircross': 'SUV/Кросовер'},
    'Lincoln': {'Continental': 'Седан'},
    'Mitsubishi': {'Lancer Evolution': 'Седан/Спорткар', 'Eclipse': 'Купе/Спорткар', 'Pajero': 'SUV/Позашляховик', 'Outlander': 'SUV/Кросовер', 'ASX': 'SUV/Кросовер'},
    'Genesis': {'GV80': 'SUV/Кросовер', 'GV70': 'SUV/Кросовер', 'GV60': 'SUV/Кросовер (електро)', 'G80': 'Седан', 'G90': 'Седан'},
    'Cadillac': {'Escalade': 'SUV/Кросовер', 'CT5': 'Седан', 'CT6': 'Седан', 'LYRIQ': 'SUV/Кросовер (електро)'},
    'Lamborghini': {'Urus': 'SUV/Кросовер', 'Huracán': 'Спорткар', 'Aventador': 'Спорткар'},
    'Rolls-Royce': {'Cullinan': 'SUV/Кросовер', 'Ghost': 'Седан', 'Wraith': 'Купе', 'Phantom': 'Седан', 'Spectre': 'Купе (електро)'},
    'Aston Martin': {'DBX': 'SUV/Кросовер', 'Vantage': 'Спорткар', 'DB11': 'Купе/Спорткар'},
    'Zeekr': {
        '001': 'Універсал/Шутинг-брейк (електро)',
        '7X': 'SUV/Кросовер (електро)',
        '9X': 'SUV/Кросовер (електро)',
    },
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
    'Nissan': 'Японія',
    'Subaru': 'Японія',
    'Mitsubishi': 'Японія',
    'Acura': 'Японія',
    'Tesla': 'США',
    'Ford': 'США',
    'Dodge': 'США',
    'RAM': 'США',
    'Jeep': 'США',
    'Chrysler': 'США',
    'Chevrolet': 'США',
    'Cadillac': 'США',
    'Lincoln': 'США',
    'Rivian': 'США',
    'Volvo': 'Швеція',
    'Polestar': 'Швеція/Китай',
    'Land Rover': 'Велика Британія',
    'Jaguar': 'Велика Британія',
    'Rolls-Royce': 'Велика Британія',
    'Aston Martin': 'Велика Британія',
    'McLaren': 'Велика Британія',
    'Maserati': 'Італія',
    'Ferrari': 'Італія',
    'Lamborghini': 'Італія',
    'Alfa Romeo': 'Італія',
    'Cupra': 'Іспанія',
    'Peugeot': 'Франція',
    'Citroen': 'Франція',
    'Zeekr': 'Китай',
    'JETOUR': 'Китай',
    'BYD': 'Китай',
    'Li Auto': 'Китай',
    'Denza': 'Китай',
    'KIA': 'Південна Корея',
    'Hyundai': 'Південна Корея',
    'Genesis': 'Південна Корея',
    'Skoda': 'Чехія',
    'Bentley': 'Велика Британія',
    'ZAZ': 'Україна',
}

# Цінові сегменти
BRAND_TIER = {
    'Audi': 'Premium',
    'BMW': 'Premium',
    'Mercedes-Benz': 'Premium',
    'Porsche': 'Luxury/Sport',
    'Maserati': 'Luxury',
    'Lexus': 'Premium',
    'Land Rover': 'Premium/Luxury',
    'Jaguar': 'Premium',
    'Infiniti': 'Premium',
    'Acura': 'Premium',
    'Genesis': 'Premium',
    'Alfa Romeo': 'Premium/Sport',
    'Cadillac': 'Premium',
    'Rolls-Royce': 'Ultra Luxury',
    'Bentley': 'Ultra Luxury',
    'Aston Martin': 'Ultra Luxury/Sport',
    'Lamborghini': 'Ultra Luxury/Sport',
    'Ferrari': 'Ultra Luxury/Sport',
    'McLaren': 'Ultra Luxury/Sport',
    'Toyota': 'Mass',
    'Honda': 'Mass',
    'Mazda': 'Mass',
    'Nissan': 'Mass',
    'Subaru': 'Mass',
    'Mitsubishi': 'Mass',
    'Volkswagen': 'Mass/Premium',
    'Skoda': 'Mass',
    'Ford': 'Mass',
    'Dodge': 'Mass/Sport',
    'RAM': 'Mass',
    'Jeep': 'Mass/Premium',
    'Chrysler': 'Mass',
    'Chevrolet': 'Mass',
    'Lincoln': 'Premium',
    'Volvo': 'Premium',
    'Suzuki': 'Mass',
    'Cupra': 'Premium/Sport',
    'Peugeot': 'Mass',
    'Citroen': 'Mass',
    'KIA': 'Mass',
    'Hyundai': 'Mass',
    'Tesla': 'EV-Premium',
    'Polestar': 'EV-Premium',
    'Rivian': 'EV-Premium',
    'Zeekr': 'EV-Premium',
    'BYD': 'EV-Mass/Premium',
    'Li Auto': 'EV-Premium',
    'Denza': 'EV-Premium',
    'JETOUR': 'Mass',
    'ZAZ': 'Mass/Budget',
}

# Приблизний ціновий сегмент для моделі
PRICE_SEGMENT = {
    ('Audi', 'e-tron'): 'Premium ($60-100k)',
    ('Audi', 'Q4 e-tron'): 'Premium ($40-60k)',
    ('Audi', 'Q8/SQ8'): 'Premium ($60-100k)',
    ('Audi', 'SQ7'): 'Premium ($60-90k)',
    ('Audi', 'Q7'): 'Premium ($40-70k)',
    ('Audi', 'Q5/SQ5'): 'Premium ($30-55k)',
    ('Audi', 'A8'): 'Premium ($40-90k)',
    ('Audi', 'A7'): 'Premium ($35-65k)',
    ('Audi', 'A5'): 'Premium ($30-50k)',
    ('Audi', 'S6'): 'Premium ($40-70k)',
    ('Audi', 'RS3'): 'Premium/Sport ($50-70k)',
    ('BMW', 'X3'): 'Premium ($35-60k)',
    ('BMW', 'X5'): 'Premium ($50-90k)',
    ('BMW', 'X6'): 'Premium ($55-95k)',
    ('BMW', 'X7'): 'Luxury ($70-120k)',
    ('BMW', 'iX'): 'Premium ($65-100k)',
    ('BMW', '5 Series'): 'Premium ($40-70k)',
    ('BMW', '4 Series'): 'Premium ($35-60k)',
    ('BMW', '3 Series'): 'Premium ($30-55k)',
    ('BMW', 'M8'): 'Luxury/Sport ($120-200k)',
    ('BMW', 'M Series'): 'Premium/Sport ($60-120k)',
    ('Porsche', 'Cayenne'): 'Luxury ($70-140k)',
    ('Porsche', 'Macan'): 'Luxury ($55-95k)',
    ('Porsche', 'Panamera'): 'Luxury ($90-180k)',
    ('Porsche', '911'): 'Luxury/Sport ($120-250k)',
    ('Porsche', 'Taycan'): 'Luxury ($90-160k)',
    ('Mercedes-Benz', 'GLC'): 'Premium ($45-75k)',
    ('Mercedes-Benz', 'GLE'): 'Premium ($60-100k)',
    ('Mercedes-Benz', 'GLS'): 'Premium ($80-130k)',
    ('Mercedes-Benz', 'GLA'): 'Premium ($40-60k)',
    ('Mercedes-Benz', 'GLB'): 'Premium ($45-65k)',
    ('Mercedes-Benz', 'G-Class'): 'Luxury ($120-200k)',
    ('Mercedes-Benz', 'V-Class'): 'Premium ($65-110k)',
    ('Mercedes-Benz', 'C-Class'): 'Premium ($40-65k)',
    ('Mercedes-Benz', 'E-Class'): 'Premium ($55-90k)',
    ('Mercedes-Benz', 'S-Class'): 'Luxury ($100-180k)',
    ('Mercedes-Benz', 'CLE'): 'Premium ($60-90k)',
    ('Mercedes-Benz', 'EQE'): 'Premium ($70-100k)',
    ('Mercedes-Benz', 'EQS'): 'Luxury ($100-150k)',
    ('Mercedes-Benz', 'AMG GT'): 'Luxury/Sport ($130-200k)',
    ('Toyota', 'RAV4'): 'Mass ($25-45k)',
    ('Toyota', 'Highlander'): 'Mass+ ($40-60k)',
    ('Toyota', 'Prado'): 'Mass+ ($50-75k)',
    ('Toyota', 'Land Cruiser'): 'Premium ($80-120k)',
    ('Toyota', 'Land Cruiser 200'): 'Premium ($65-100k)',
    ('Toyota', 'Land Cruiser 300'): 'Premium ($80-120k)',
    ('Toyota', 'Sequoia'): 'Premium ($70-90k)',
    ('Toyota', 'C-HR'): 'Mass ($25-40k)',
    ('Toyota', 'Camry'): 'Mass ($28-45k)',
    ('Toyota', 'Prius'): 'Mass ($25-40k)',
    ('Toyota', 'GR86'): 'Mass/Sport ($30-45k)',
    ('Toyota', 'Sienna'): 'Mass+ ($45-60k)',
    ('Volkswagen', 'Touareg'): 'Premium ($45-75k)',
    ('Volkswagen', 'Atlas'): 'Mass+ ($40-55k)',
    ('Volkswagen', 'Golf'): 'Mass ($25-45k)',
    ('Volkswagen', 'Golf GTI'): 'Mass/Sport ($35-50k)',
    ('Volkswagen', 'Golf R'): 'Mass/Sport ($45-60k)',
    ('Volkswagen', 'Golf GTI/R'): 'Mass/Sport ($35-60k)',
    ('Volkswagen', 'Passat'): 'Mass ($30-45k)',
    ('Volkswagen', 'Multivan'): 'Premium ($60-90k)',
    ('Volkswagen', 'Tayron'): 'Mass+ ($35-50k)',
    ('Volkswagen', 'Tiguan'): 'Mass ($30-50k)',
    ('Tesla', 'Model S'): 'Premium ($70-110k)',
    ('Tesla', 'Model 3'): 'Mass+ ($35-50k)',
    ('Tesla', 'Model X'): 'Premium ($80-120k)',
    ('Tesla', 'Model Y'): 'Mass+ ($40-60k)',
    ('Volvo', 'XC90'): 'Premium ($55-85k)',
    ('Volvo', 'XC60'): 'Premium ($45-65k)',
    ('Volvo', 'XC40'): 'Premium ($35-50k)',
    ('Volvo', 'S60'): 'Premium ($35-50k)',
    ('Volvo', 'V60'): 'Premium ($40-55k)',
    ('Volvo', 'V90'): 'Premium ($45-65k)',
    ('Jeep', 'Grand Cherokee'): 'Premium ($45-80k)',
    ('Jeep', 'Cherokee'): 'Mass ($30-45k)',
    ('Jeep', 'Compass'): 'Mass ($28-40k)',
    ('Jeep', 'Wrangler'): 'Mass+ ($40-65k)',
    ('Ford', 'Mustang'): 'Mass/Sport ($40-65k)',
    ('Ford', 'GT40'): 'Luxury/Sport ($400k+)',
    ('Ford', 'Explorer'): 'Mass+ ($40-55k)',
    ('Dodge', 'Challenger'): 'Mass/Sport ($40-70k)',
    ('Dodge', 'Charger'): 'Mass/Sport ($40-65k)',
    ('Dodge', 'Ram'): 'Mass+ ($50-75k)',
    ('RAM', 'RAM 1500'): 'Mass+ ($50-75k)',
    ('RAM', 'RAM 1500 Ramcharger'): 'Premium ($65-85k)',
    ('Lexus', 'RX'): 'Premium ($55-75k)',
    ('Lexus', 'ES'): 'Premium ($40-55k)',
    ('Lexus', 'LX'): 'Luxury ($90-130k)',
    ('Lexus', 'NX'): 'Premium ($40-60k)',
    ('Lexus', 'GX'): 'Premium ($60-85k)',
    ('Infiniti', 'QX55'): 'Premium ($50-65k)',
    ('Infiniti', 'QX60'): 'Premium ($55-70k)',
    ('Infiniti', 'QX50'): 'Premium ($45-60k)',
    ('Infiniti', 'Q50'): 'Premium ($35-50k)',
    ('Honda', 'CR-V'): 'Mass ($30-40k)',
    ('Maserati', 'Levante'): 'Luxury ($80-130k)',
    ('Jaguar', 'E-Pace'): 'Premium ($45-60k)',
    ('Jaguar', 'I-Pace'): 'Premium ($70-100k)',
    ('Jaguar', 'F-Pace'): 'Premium ($55-80k)',
    ('Suzuki', 'Jimny'): 'Mass ($22-30k)',
    ('Mazda', 'MX-5'): 'Mass/Sport ($30-40k)',
    ('Mazda', 'CX-90'): 'Mass+ ($45-60k)',
    ('Mazda', 'CX-5'): 'Mass ($28-42k)',
    ('Cupra', 'Formentor'): 'Premium ($40-55k)',
    ('Chrysler', 'Pacifica'): 'Mass+ ($45-60k)',
    ('Land Rover', 'Range Rover'): 'Luxury ($100-200k)',
    ('Land Rover', 'Range Rover Velar'): 'Premium ($65-100k)',
    ('Land Rover', 'Range Rover Evoque'): 'Premium ($50-75k)',
    ('Land Rover', 'Range Rover Sport'): 'Luxury ($80-140k)',
    ('Land Rover', 'Discovery'): 'Premium ($65-95k)',
    ('Land Rover', 'Discovery Sport'): 'Premium ($45-65k)',
    ('Land Rover', 'Defender'): 'Premium ($60-100k)',
    ('Zeekr', '001'): 'Premium ($50-70k)',
    ('JETOUR', 'T2'): 'Mass ($25-35k)',
    ('Alfa Romeo', 'Giulia'): 'Premium/Sport ($45-80k)',
    ('Alfa Romeo', 'Stelvio'): 'Premium ($45-75k)',
    ('Nissan', '350Z'): 'Mass/Sport ($25-40k)',
    ('Nissan', 'X-Trail'): 'Mass ($30-45k)',
    ('Subaru', 'Outback'): 'Mass ($35-50k)',
    ('Subaru', 'BRZ'): 'Mass/Sport ($30-42k)',
    ('KIA', 'EV6'): 'Mass+ ($40-60k)',
    ('KIA', 'Carnival'): 'Mass+ ($40-55k)',
    ('Skoda', 'Kodiaq'): 'Mass ($35-55k)',
    ('Skoda', 'Kodiaq RS'): 'Mass/Sport ($55-70k)',
    ('Hyundai', 'Palisade'): 'Mass+ ($45-65k)',
    ('Chevrolet', 'Traverse'): 'Mass+ ($40-55k)',
    ('Chevrolet', 'Equinox'): 'Mass ($30-45k)',
    ('Acura', 'MDX'): 'Premium ($55-75k)',
    ('Rivian', 'R1S'): 'Premium ($70-100k)',
    ('Bentley', 'Bentayga'): 'Ultra Luxury ($180-300k)',
    ('BYD', 'Yuan'): 'Mass ($25-40k)',
    ('Polestar', 'Polestar 4'): 'Premium ($55-75k)',
    ('Li Auto', 'L7'): 'Premium ($50-70k)',
    ('Denza', 'Z9 GT'): 'Premium ($60-90k)',
    ('Peugeot', '4008'): 'Mass ($28-40k)',
    ('Citroen', 'C4 Grand Picasso'): 'Mass ($25-38k)',
    ('Mitsubishi', 'Lancer Evolution'): 'Mass/Sport ($25-45k)',
    ('Genesis', 'GV80'): 'Premium ($65-90k)',
    ('Cadillac', 'Escalade'): 'Luxury ($100-150k)',
    ('Lamborghini', 'Urus'): 'Ultra Luxury ($200-300k)',
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
    if re.search(r'e-?tron|i-?pace|tesla|електро|electric|eв|zeekr|mach-?e|e-coupe|ev6|ev3|ev9|polestar|rivian|ioniq|byd|юань|model\s*[sxy3]|model\s*y|eqe|eqs|зікр|li\s*auto|lixiang|denza|atto\s*3', text_lower):
        return 'Електро'
    if re.search(r'гібрид|hybrid|4xe|e-?coupe|plug-?in|330e|phev|prius|пріус|ramcharger|l7\b', text_lower):
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

# Вага: 1 коментар = 1.0, 1 лайк = LIKE_WEIGHT (default 0.3)
LIKE_WEIGHT = float(os.environ.get('LIKE_WEIGHT', '0.3'))

for c in comments:
    text = c['t']
    user = c['u']
    likes = c['l']
    w = 1.0 + likes * LIKE_WEIGHT

    unique_parent_users.add(user)

    brands = normalize_brand(text)
    models_detected = []

    for brand in brands:
        brand_counter[brand] += w
        country_counter[BRAND_COUNTRY.get(brand, '—')] += w
        tier_counter[BRAND_TIER.get(brand, '—')] += w

        models = normalize_model(text, brand)
        if not models:
            pass
        for m in models:
            model_counter[(brand, m)] += w
            body = BODY_TYPE.get(brand, {}).get(m)
            if body:
                body_counter[body] += w
            seg = PRICE_SEGMENT.get((brand, m))
            if seg:
                if 'Ultra Luxury' in seg:
                    price_counter['Ultra Luxury ($150k+)'] += w
                elif 'Luxury' in seg and 'Mass' not in seg:
                    price_counter['Luxury ($80-150k)'] += w
                elif 'Premium' in seg and 'Mass' not in seg:
                    price_counter['Premium ($40-80k)'] += w
                elif 'Mass+' in seg:
                    price_counter['Mass+ ($35-55k)'] += w
                elif 'Mass' in seg:
                    price_counter['Mass ($20-40k)'] += w
                else:
                    price_counter['Other'] += w
            models_detected.append(f'{brand} {m}')

    pt = detect_powertrain(text)
    powertrain_counter[pt] += w

    sentiments = detect_sentiment(text)
    for s in sentiments:
        sentiment_counter[s] += w

    processed.append({
        'user': user,
        'text': text,
        'likes': likes,
        'brands': brands,
        'models': models_detected,
        'powertrain': pt,
        'sentiment': sentiments,
    })

# Additional: cabriolet mentions (зважені з лайками)
cabriolet_mentions = 0.0
for c in comments:
    if re.search(r'кабріолет|cabriolet|родстер|roadster|mx-?5|кабрік|cabrio', c['t'].lower()):
        cabriolet_mentions += 1.0 + c['l'] * LIKE_WEIGHT
if cabriolet_mentions:
    body_counter['Кабріолет/Родстер'] = body_counter.get('Кабріолет/Родстер', 0) + cabriolet_mentions

# Sport car mentions
sport_mentions = sum(1 for c in comments if re.search(
    r'спорт|mustang|challenger|911|rs\s*3|gt\s*40|sq8|rsq8|audi\s*s6|gr86|brz|350z|evo|giulia',
    c['t'].lower()))


# === BUILD REPORT DATA ===
def _round(d, k=1):
    return {key: round(v, k) for key, v in d.items()}


total_likes = sum(c['l'] for c in comments)
report = {
    'total_comments': len(comments),
    'total_likes': total_likes,
    'like_weight': LIKE_WEIGHT,
    'weighting_note': f'Кожен лайк додає {LIKE_WEIGHT} до ваги коментаря',
    'unique_users': len(unique_parent_users),
    'brand_counter': _round(dict(brand_counter.most_common())),
    'model_counter': _round({f'{b} {m}': v for (b, m), v in model_counter.most_common()}),
    'body_counter': _round(dict(body_counter.most_common())),
    'powertrain_counter': _round(dict(powertrain_counter.most_common())),
    'country_counter': _round(dict(country_counter.most_common())),
    'tier_counter': _round(dict(tier_counter.most_common())),
    'price_counter': _round(dict(price_counter.most_common())),
    'sentiment_counter': _round(dict(sentiment_counter.most_common())),
    'cabriolet_mentions': round(cabriolet_mentions, 1),
    'processed': processed,
}

_out_name = os.environ.get('ANALYSIS_OUT', 'analysis.json')
with open(os.path.join(_HERE, _out_name), 'w', encoding='utf-8') as f:
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
