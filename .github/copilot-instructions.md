# Kajenscript - Lunch Menu Scraper Project

Detta är ett Python-webbskrapningsprojekt designat för att skrapa lunchmenyer från Kajen Gävles webbplats och generera interaktiva HTML-rapporter med prisanalys.

## Projekttyp
- Språk: Python 3.9+
- Syfte: Webbskrapning av lunchmenyer med historikspårning och prisanalys
- Huvudbibliotek: Playwright, Chart.js
- Målwebbplats: https://www.kajengavle.se/lunch/

## Teknisk stack
- **Playwright**: Webbläsarautomation för robust skrapning (använder systeminstallerad Chrome)
- **HTMLParser**: Fallback-parser för lokal HTML-bearbetning
- **Chart.js 4.4.0**: Klientbaserat diagrambibliotek för prisvisualisering
- **Roboto Mono**: Google Fonts webfont för monospace-typografi
- **JSON**: Datalagring för meny- och prishistorik

## Huvudfunktioner
1. **Webbskrapning**: Extraherar veckomeny från matochmat-wrap HTML-struktur
2. **Prishistorik**: Spårar 4 pristyper över 6 månader (Lunchbuffé, Tidig lunch, Pensionärspris, Take away)
3. **Menyhistorik**: Spårar och jämför menyer över 12 veckor
4. **Veckovis jämförelse**: Identifierar nya, borttagna och återkommande rätter
5. **HTML-rapport**: Flikbaserat gränssnitt med "Meny" och "Prisutveckling" tabs
6. **Prisdiagram**: Chart.js line graph som visar pristrender över tid
7. **Svenskt gränssnitt**: All UI och feedback på svenska

## Utvecklingsriktlinjer
- Följ PEP 8-stilriktlinjer
- Använd svenska språket för användargränssnitt, kommentarer och meddelanden
- Inkludera felhantering för nätverksförfrågningar
- Använd färgkodad konsoloutput (ANSI-färgkoder via Colors-klass)
- Behåll minimalistisk designfilosofi för HTML-output
- Testa med både headless och synlig webbläsarläge
- Hantera företagsproxyer med use_installed_chrome=true

## Datalagring
- `menu_history.json`: 12 veckors retention, struktur med week, year, items[], scraped_at
- `price_history.json`: 6 månaders retention, struktur med date och prices dict
- `menu.html`: Genererad HTML-rapport (exkluderas från Git)

## Viktig information
- Projektet är konfigurerat för att fungera bakom företagsproxyer
- Använder channel="chrome" för att kringgå proxyproblem
- Historikfiler exkluderas från Git via .gitignore
- Inga känsliga uppgifter i koden (säkert för offentlig GitHub)
