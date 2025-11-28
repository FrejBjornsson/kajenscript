# Kajenscript - Lunch Menu Scraper

En avancerad Python-baserad webbskrapa för att extrahera och analysera lunchmenyer från Kajen Gävle. Projektet använder Playwright för robust webbskrapning och genererar en modern, interaktiv HTML-rapport med prisanalys och trendvisualisering.

## ✨ Funktioner

- 🍽️ **Automatisk menyskrapning** - Hämtar veckomeny från Kajen Gävles hemsida
- 📊 **Prishistorik** - Spårar fyra pristyper över tid (6 månaders retention):
  - Lunchbuffé
  - Tidig lunch
  - Pensionärspris
  - Take away
- 📈 **Interaktiva diagram** - Chart.js-baserad prisvisualisering med trendlinjer
- 🔄 **Veckovis jämförelse** - Identifierar nya, borttagna och återkommande rätter (12 veckors historik)
- 🎨 **Modern HTML-rapport** - Flikbaserat gränssnitt med minimalistisk design och Roboto Mono-typografi
- 🌐 **Automatisk webbläsaröppning** - Visar resultatet direkt efter skrapning
- 🔧 **Företagsproxy-kompatibel** - Använder installerad Chrome för att kringgå proxyproblem
- 🇸🇪 **Svenskt gränssnitt** - Alla meddelanden och rapporter på svenska

## 📋 Förutsättningar

- Python 3.9 eller högre
- Google Chrome installerad (för Playwright)
- pip (Python-paketinstallatör)

## 🚀 Installation

1. Klona eller navigera till detta repository:
```bash
cd Kajenscript
```

2. Skapa en virtuell miljö (rekommenderas):
```bash
python -m venv .venv
```

3. Aktivera den virtuella miljön:
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

4. Installera nödvändiga beroenden:
```bash
pip install -r requirements.txt
```

5. Installera Playwright-webbläsare:
```bash
playwright install chromium
```

**OBS:** Projektet är konfigurerat att använda din systeminstallerade Chrome för att hantera företagsproxyer.

## ⚙️ Konfiguration

Redigera `config.json` för att anpassa skraparen:

```json
{
  "target_url": "https://www.kajengavle.se/lunch/",
  "output_format": "json",
  "output_file": "output/menu_data",
  "save_to_file": false,
  "timeout": 30,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "headless": true,
  "use_installed_chrome": true,
  "verify_ssl": true
}
```

### Konfigurationsalternativ

- `target_url`: URL:en till webbplatsen som ska skrapas
- `output_format`: Utdataformat - "json" eller "csv"
- `output_file`: Sökväg för utdatafil (utan filändelse)
- `save_to_file`: Om true, sparar rå JSON-data till fil
- `timeout`: Timeout för förfrågningar i sekunder (30 rekommenderas)
- `user_agent`: User agent-sträng för förfrågningar
- `headless`: Kör webbläsaren i headless-läge (true = ingen synlig webbläsare)
- `use_installed_chrome`: Använd systeminstallerad Chrome istället för Chromium (rekommenderas för proxyer)
- `verify_ssl`: Verifiera SSL-certifikat

## 💻 Användning

### Grundläggande användning

Kör skraparen med standardkonfiguration:
```bash
python scraper.py
```

Detta kommer att:
1. Öppna Kajen Gävles lunchsida med Playwright
2. Extrahera veckomeny och priser
3. Uppdatera historikfiler (`menu_history.json` och `price_history.json`)
4. Generera en HTML-rapport (`menu.html`)
5. Öppna rapporten automatiskt i din webbläsare

### Använda anpassad konfiguration

Kör med en anpassad konfigurationsfil:
```bash
python scraper.py custom_config.json
```

### Testdata (simulering)

För att generera testdata för utveckling:
```bash
python simulate.py
```

Detta skapar historisk data för de senaste 12 veckorna med realistiska menyförändringar och prisvariationer.

## 🛠️ Teknisk arkitektur

### LunchMenuScraper-klassen

Huvudklassen innehåller följande viktiga metoder:

#### Webbskrapning
- **`fetch_page()`**: Använder Playwright för att hämta sidan och returnerar `(menu_items, week_number)`
- **`extract_menu_data_from_page()`**: Extraherar menydata från DOM och beräknar veckonummer
- **`extract_prices()`**: Regex-baserad prisextraktion för fyra priskategorier

#### Datahantering
- **`save_menu_history()`**: Sparar menydata med 12 veckors retention
- **`save_price_history()`**: Sparar prisdata med 6 månaders retention
- **`compare_with_previous_week()`**: Identifierar nya, borttagna och vanliga rätter
- **`get_price_changes()`**: Jämför två senaste prisposter
- **`get_all_price_history()`**: Returnerar fullständig prishistorik för diagram

#### Visualisering
- **`display_menu()`**: Konsoloutput med färgkodning och svenska meddelanden
- **`generate_html()`**: Skapar flikbaserad HTML-rapport med Chart.js-integration

### Teknologier

- **Playwright**: Webbläsarautomation för robust skrapning
- **HTMLParser**: Fallback-parser för lokal HTML-bearbetning
- **Chart.js 4.4.0**: Klientbaserat diagrambibliotek (CDN)
- **Roboto Mono**: Google Fonts webfont för monospace-typografi
- **ANSI-färgkoder**: Terminal-styling via Colors-klass

### Företagsproxy-hantering

Projektet är konfigurerat för att fungera bakom företagsproxyer:
- Använder `channel="chrome"` i Playwright för att använda systeminstallerad Chrome
- `use_installed_chrome=true` i config.json
- Detta kringgår problem med McAfee Web Gateway och andra proxylösningar

## 🏗️ Projektstruktur

```
Kajenscript/
├── scraper.py                  # Huvudskript med LunchMenuScraper-klass
├── simulate.py                 # Testdatagenerator för utveckling
├── config.json                 # Konfigurationsfil
├── requirements.txt            # Python-beroenden (Playwright)
├── README.md                   # Denna fil
├── .gitignore                  # Git-exkluderingar
├── menu_history.json           # Autogenererad menyhistorik (12 veckor)
├── price_history.json          # Autogenererad prishistorik (6 månader)
├── menu.html                   # Genererad HTML-rapport
└── .github/
    └── copilot-instructions.md # Workspace-instruktioner
```

**OBS:** Historikfilerna (`*_history.json`) och `menu.html` exkluderas från Git via `.gitignore` eftersom de innehåller lokala data.

## 📊 Output och funktioner

### HTML-rapport (menu.html)

Den genererade rapporten innehåller två flikar:

#### **Meny-fliken**
- Veckans lunchmeny sorterad efter veckodag (Måndag–Fredag)
- Veckonummer från webbplatsen
- Färgkodade symboler för menyförändringar:
  - ⭐ Ny rätt (denna vecka)
  - 🔄 Borttagen rätt (fanns förra veckan)
  - ✓ Vanlig rätt (finns kontinuerligt)
- Totalt antal rätter per kategori

#### **Prisutveckling-fliken**
- Interaktivt linjediagram (Chart.js) som visar pristrender över tid
- Tabell med de senaste 5 prisdatumen
- Förändringsindikatorer (↑↓) för varje pristyp
- Spårar fyra priskategorier:
  - **Lunchbuffé**: 129 kr
  - **Tidig lunch**: 115 kr
  - **Pensionärspris**: 105 kr
  - **Take away**: 99 kr

### JSON-historikfiler

**menu_history.json**
- Behåller 12 veckors menydata
- Struktur:
```json
[
  {
    "week": 48,
    "year": 2024,
    "week_number": "Vecka 48",
    "items": ["Rätt 1", "Rätt 2", ...],
    "scraped_at": "2024-11-28T10:30:00",
    "updated_at": "2024-11-28T10:30:00"
  }
]
```

**price_history.json**
- Behåller 6 månaders prisdata
- Struktur:
```json
[
  {
    "date": "2024-11-28",
    "prices": {
      "Lunchbuffé": 129,
      "Tidig lunch": 115,
      "Pensionärspris": 105,
      "Take away": 99
    }
  }
]
```

### Konsoloutput

Skriptet ger färgkodad feedback i konsolen:
- ✓ Gröna meddelanden = framgång
- ℹ Blå meddelanden = information
- ⚠ Gula meddelanden = varningar
- ✗ Röda meddelanden = fel

## 🎨 Design och UX

HTML-rapporten är designad enligt modern UX-praxis:

- **Minimalistisk estetik**: Ren design utan AI-genererad känsla
- **Roboto Mono**: Monospace-font för tydlighet och läsbarhet
- **Färgschema**: Neutrala toner med subtila accentfärger
- **Responsiv**: Fungerar på desktop och mobila enheter
- **Flikbaserat gränssnitt**: Separata vyer för meny och prisanalys
- **Interaktiva diagram**: Hover-effekter och tooltips i Chart.js
- **Emoji-ikoner**: Visuella indikatorer för menyförändringar

## 📝 Utvecklingsriktlinjer

När du bidrar till detta projekt:
- Följ PEP 8-stilriktlinjer för Python-kod
- Använd svenska språket för användargränssnitt och kommentarer
- Lägg till felhantering för nya funktioner
- Uppdatera README.md med ny funktionalitet
- Testa dina ändringar noggrant
- Behåll den minimalistiska designfilosofin för HTML-output

## 🔒 Säkerhet och integritet

- Projektet innehåller inga känsliga uppgifter (API-nycklar, lösenord, personuppgifter)
- Historikfiler exkluderas från Git via `.gitignore`
- Skrapar endast offentligt tillgänglig information från Kajen Gävles webbplats
- Respekterar webbplatsens robots.txt och terms of service

## 📜 Licens

Detta projekt tillhandahålls i befintligt skick för utbildnings- och personligt bruk.

## ⚖️ Ansvarsfriskrivning

Använd alltid webbskrapare ansvarsfullt och etiskt:
- Respektera webbplatsens användarvillkor och robots.txt
- Skrapa inte för ofta (undvik överbelastning av servern)
- Lagra endast data som är nödvändig för ditt ändamål
- Detta verktyg är utformat för personligt bruk och analys av offentlig lunchmenyinformation

## � Tack till

- **Kajen Gävle** för att tillhandahålla lunchmenyinformation online
- **Playwright** för robust webbläsarautomation
- **Chart.js** för vackra och responsiva diagram

### Inga menyposter hittades
- Verifiera att `target_url` i `config.json` är korrekt
- Kontrollera webbplatsens HTML-struktur (kan ha ändrats)
- Kör med `headless: false` för att se webbläsaren i aktion

### Request timeout
- Öka `timeout`-värdet i `config.json` (standard: 30 sekunder)
- Kontrollera din internetanslutning
- Se till att webbplatsen är tillgänglig

### Playwright-fel
- Kör `playwright install chromium` för att installera webbläsare
- Kontrollera att Chrome är installerad på systemet (för `use_installed_chrome: true`)
- Testa med `headless: false` för att se om det är ett visualiseringsproblem

### Proxy-problem (407 Proxy Authentication Required)
- Se till att `use_installed_chrome: true` är aktiverat i `config.json`
- Detta använder din systeminstallerade Chrome som redan är konfigurerad för företagets proxy
- Alternativt: Kör skriptet utanför företagsnätverket

### HTML-filen öppnas inte
- Kontrollera att du har en standardwebbläsare konfigurerad
- Öppna `menu.html` manuellt från projektmappen
- Kontrollera filbehörigheter

### Priserna visas inte
- Priserna extraheras från en specifik sektion på webbplatsen
- Om webbplatsens struktur ändras kan regex-mönstren behöva uppdateras
- Se `extract_prices()`-metoden i `scraper.py`

## 🎨 Design och UX
