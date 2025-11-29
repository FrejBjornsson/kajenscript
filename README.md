# Kajenscript - Lunch Menu Scraper

En Python-baserad webscraper för att extrahera och analysera lunchmenyer från Kajen Gävle. Projektet använder Playwright för webscraping och genererar en interaktiv HTML-rapport med prisanalys och trendvisualisering.

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

## Användning

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


#### Visualisering
- **`display_menu()`**: Konsoloutput med färgkodning och meddelanden
- **`generate_html()`**: Skapar flikbaserad HTML-rapport med Chart.js-integration

## Output och funktioner

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

## Säkerhet och integritet

- Projektet innehåller inga känsliga uppgifter (API-nycklar, lösenord, personuppgifter)
- Historikfiler exkluderas från Git via `.gitignore`
- Skrapar endast offentligt tillgänglig information från Kajen Gävles webbplats
- Respekterar webbplatsens robots.txt och terms of service

## Licens

Detta projekt tillhandahålls i befintligt skick för utbildnings- och personligt bruk.

## Ansvarsfriskrivning

Använd alltid webbskrapare ansvarsfullt och etiskt:
- Respektera webbplatsens användarvillkor och robots.txt
- Skrapa inte för ofta (undvik överbelastning av servern)
- Lagra endast data som är nödvändig för ditt ändamål
- Detta verktyg är utformat för personligt bruk och analys av offentlig lunchmenyinformation.