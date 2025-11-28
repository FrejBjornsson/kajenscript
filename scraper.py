"""
Lunch Menu Scraper
A web scraper to extract lunch menu information from websites using Playwright.
"""

import json
import csv
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from html.parser import HTMLParser
from collections import defaultdict
import re
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout


# ANSI color codes for pretty console output
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


class MenuHTMLParser(HTMLParser):
    """Custom HTML parser for extracting menu data from matochmat-wrap format."""
    
    def __init__(self):
        super().__init__()
        self.menu_items = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_day = None
        self.in_day_heading = False
        self.in_menu_paragraph = False
        self.current_data = []
        self.skip_next_p = False  # To avoid duplicate entries
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = dict(attrs)
        
        if tag == 'h3':
            # Check if it's a day heading
            class_attr = self.current_attrs.get('class', '')
            if 'matochmat-wrap__day-heading' in class_attr:
                self.in_day_heading = True
                self.current_data = []
                
        elif tag == 'p' and self.current_day and not self.skip_next_p:
            # Check if it's a menu item paragraph (not pricing info)
            class_attr = self.current_attrs.get('class', '')
            # Skip paragraphs with text-align-center or matochmat__menu-text (pricing info)
            if 'has-text-align-center' not in class_attr and 'matochmat__menu-text' not in class_attr:
                self.in_menu_paragraph = True
                self.current_data = []
        
        elif tag == 'div':
            class_attr = self.current_attrs.get('class', '')
            if 'matochmat__menu-text' in class_attr:
                # End of menu section, reset current_day
                self.current_day = None
    
    def handle_endtag(self, tag):
        if tag == 'h3' and self.in_day_heading:
            self.in_day_heading = False
            day_text = ''.join(self.current_data).strip()
            if day_text:
                self.current_day = day_text
            self.current_data = []
            
        elif tag == 'p' and self.in_menu_paragraph:
            self.in_menu_paragraph = False
            menu_text = ''.join(self.current_data).strip()
            
            # Only add if it's actual menu content (not empty and not pricing info)
            if menu_text and len(menu_text) > 5:
                # Check if it's not a duplicate (sometimes same item appears multiple times)
                is_duplicate = False
                for item in self.menu_items:
                    if item['day'] == self.current_day and item['name'] == menu_text:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    self.menu_items.append({
                        'day': self.current_day,
                        'name': menu_text,
                        'scraped_at': datetime.now().isoformat()
                    })
            
            self.current_data = []
    
    def handle_data(self, data):
        if self.in_day_heading or self.in_menu_paragraph:
            self.current_data.append(data)


class LunchMenuScraper:
    """Main scraper class for extracting lunch menu data."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the scraper with configuration.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config = self._load_config(config_path)
        self.playwright = None
        self.browser = None
        self.history_file = "menu_history.json"
        self.price_history_file = "price_history.json"

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print_success(f"Konfigurationsfil laddad: {config_path}")
            return config
        except FileNotFoundError:
            print_error(f"Konfigurationsfil '{config_path}' hittades inte.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print_error(f"Ogiltig JSON i konfigurationsfilen: {e}")
            sys.exit(1)

    def save_menu_history(self, menu_items: List[Dict]) -> None:
        """Save menu to history file."""
        try:
            # Load existing history
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add current week's data
            week_number = datetime.now().isocalendar()[1]
            year = datetime.now().year
            week_key = f"{year}-W{week_number:02d}"
            
            # Check if this week already exists
            existing_entry = None
            for entry in history:
                if entry.get('week') == week_key:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Update existing entry
                existing_entry['items'] = menu_items
                existing_entry['updated_at'] = datetime.now().isoformat()
            else:
                # Add new entry
                history.append({
                    'week': week_key,
                    'year': year,
                    'week_number': week_number,
                    'items': menu_items,
                    'scraped_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                })
            
            # Keep only last 12 weeks
            history = sorted(history, key=lambda x: x['week'], reverse=True)[:12]
            
            # Save history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            print_success(f"Menyhistorik sparad (Vecka {week_number})")
            
        except Exception as e:
            print_error(f"Kunde inte spara historik: {e}")
    
    def extract_prices(self, page: Page) -> Dict[str, int]:
        """Extract lunch prices from page."""
        prices = {}
        try:
            # Look for price information in paragraphs
            price_paragraphs = page.locator('p.has-text-align-center').all()
            
            for para in price_paragraphs:
                text = para.inner_text()
                # Find prices like "129 kr", "115 kr", etc.
                price_matches = re.findall(r'(\d+)\s*kr', text.lower())
                
                if 'lunchbuffé' in text.lower() and price_matches:
                    prices['Lunchbuffé'] = int(price_matches[0])
                elif '10-11' in text and price_matches:
                    prices['Tidig lunch (10-11)'] = int(price_matches[0])
                elif 'pensionär' in text.lower() and price_matches:
                    prices['Pensionärspris'] = int(price_matches[0])
                elif 'take away' in text.lower() and price_matches:
                    prices['Take away'] = int(price_matches[0])
            
        except Exception as e:
            print_warning(f"Kunde inte extrahera priser: {e}")
        
        return prices
    
    def save_price_history(self, prices: Dict[str, int]) -> None:
        """Save price history."""
        try:
            history = []
            if os.path.exists(self.price_history_file):
                with open(self.price_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add current prices
            history.append({
                'date': datetime.now().isoformat(),
                'prices': prices
            })
            
            # Keep only last 6 months of data
            six_months_ago = datetime.now() - timedelta(days=180)
            history = [h for h in history if datetime.fromisoformat(h['date']) > six_months_ago]
            
            with open(self.price_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            print_success("Prishistorik sparad")
            
        except Exception as e:
            print_error(f"Kunde inte spara prishistorik: {e}")
    
    def get_price_changes(self) -> List[Dict]:
        """Analyze price changes."""
        changes = []
        try:
            if not os.path.exists(self.price_history_file):
                return changes
            
            with open(self.price_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if len(history) < 2:
                return changes
            
            # Compare latest with previous
            latest = history[-1]['prices']
            previous = history[-2]['prices']
            
            for price_type, current_price in latest.items():
                if price_type in previous:
                    old_price = previous[price_type]
                    if current_price != old_price:
                        diff = current_price - old_price
                        changes.append({
                            'type': price_type,
                            'old': old_price,
                            'new': current_price,
                            'diff': diff,
                            'percent': round((diff / old_price) * 100, 1)
                        })
        
        except Exception as e:
            print_warning(f"Kunde inte analysera prisförändringar: {e}")
        
        return changes
    
    def get_all_price_history(self) -> List[Dict]:
        """Get all price history entries."""
        try:
            if not os.path.exists(self.price_history_file):
                return []
            
            with open(self.price_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            return history
            
        except Exception as e:
            print_warning(f"Kunde inte läsa prishistorik: {e}")
            return []
    
    def compare_with_previous_week(self) -> Tuple[List[str], List[str], List[str]]:
        """Compare current menu with previous week."""
        try:
            if not os.path.exists(self.history_file):
                return [], [], []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if len(history) < 2:
                return [], [], []
            
            # Get current and previous week
            current_week = history[0]['items']
            previous_week = history[1]['items']
            
            current_dishes = set(item['name'] for item in current_week)
            previous_dishes = set(item['name'] for item in previous_week)
            
            new_dishes = list(current_dishes - previous_dishes)
            removed_dishes = list(previous_dishes - current_dishes)
            common_dishes = list(current_dishes & previous_dishes)
            
            return new_dishes, removed_dishes, common_dishes
            
        except Exception as e:
            print_warning(f"Kunde inte jämföra veckor: {e}")
            return [], [], []

    def display_menu(self, menu_items: List[Dict], week_number: str = "") -> None:
        """
        Display menu in a nice formatted way.
        
        Args:
            menu_items: List of menu items to display
            week_number: Week number string (e.g., "Vecka 48")
        """
        if not menu_items:
            print_warning("Inga menyposter hittades.")
            return
        
        print_success(f"Hittade {len(menu_items)} menyposter\n")
        
        # Group by day
        days_dict = {}
        for item in menu_items:
            day = item['day']
            if day not in days_dict:
                days_dict[day] = []
            days_dict[day].append(item['name'])
        
        # Define weekday order for Swedish days
        weekday_order = {
            'MÅNDAG': 1, 'TISDAG': 2, 'ONSDAG': 3, 'TORSDAG': 4, 'FREDAG': 5,
            'LÖRDAG': 6, 'SÖNDAG': 7,
            'Måndag': 1, 'Tisdag': 2, 'Onsdag': 3, 'Torsdag': 4, 'Fredag': 5,
            'Lördag': 6, 'Söndag': 7
        }
        
        # Sort days by weekday order
        def get_day_sort_key(day_text):
            # Extract weekday name from text like "MÅNDAG 24/11"
            day_name = day_text.split()[0]
            return weekday_order.get(day_name, 99)
        
        sorted_days = sorted(days_dict.keys(), key=get_day_sort_key)
        
        print(f"{Colors.BOLD}{Colors.YELLOW}📅 Veckomeny:{Colors.ENDC}\n")
        for day in sorted_days:
            items = days_dict[day]
            print(f"{Colors.BOLD}{Colors.CYAN}  {day}{Colors.ENDC}")
            for idx, item_name in enumerate(items, 1):
                print(f"{Colors.GREEN}    🍽️  {item_name}{Colors.ENDC}")
            print()
        
        # Generate HTML file
        new_dishes, removed_dishes, common_dishes = self.compare_with_previous_week()
        price_changes = self.get_price_changes()
        price_history = self.get_all_price_history()
        self.generate_html(sorted_days, days_dict, new_dishes, removed_dishes, price_changes, price_history, week_number)
    
    def generate_html(self, sorted_days: List[str], days_dict: Dict[str, List[str]], 
                     new_dishes: List[str], removed_dishes: List[str], 
                     price_changes: List[Dict], price_history: List[Dict], week_number: str = "") -> None:
        """
        Generate HTML file with menu.
        
        Args:
            sorted_days: List of days in correct order
            days_dict: Dictionary mapping days to menu items
            week_number: Week number string (e.g., "Vecka 48")
        """
        # Use week number in title if available
        title_suffix = f" - {week_number}" if week_number else ""
        
        html_content = """<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kajen Gävle""" + title_suffix + """</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Roboto Mono', monospace;
            background: #f5f5f5;
            line-height: 1.8;
            color: #2d3748;
            padding: 20px;
            font-size: 14px;
        }
        .container {
            max-width: 680px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .header {
            padding: 32px 24px 24px;
            border-bottom: 1px solid #e5e5e5;
        }
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #1a202c;
            letter-spacing: -0.5px;
        }
        .header .subtitle {
            font-size: 14px;
            color: #718096;
            font-weight: 400;
        }
        .week-badge {
            display: inline-block;
            background: #edf2f7;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 12px;
            color: #4a5568;
            margin-top: 12px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e2e8f0;
            padding: 0 24px;
            gap: 8px;
        }
        .tab {
            padding: 12px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-family: 'Roboto Mono', monospace;
            font-size: 13px;
            color: #718096;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }
        .tab:hover {
            color: #2d3748;
        }
        .tab.active {
            color: #2d3748;
            border-bottom-color: #2d3748;
        }
        .tab-content {
            display: none;
            padding: 24px;
        }
        .tab-content.active {
            display: block;
        }
        .content {
            padding: 0;
        }
        .alert {
            padding: 12px 16px;
            margin-bottom: 16px;
            border-radius: 6px;
            font-size: 14px;
            border-left: 3px solid;
        }
        .alert-warning {
            background: #fff8e1;
            border-color: #ffa726;
            color: #e65100;
        }
        .alert-info {
            background: #e3f2fd;
            border-color: #42a5f5;
            color: #1565c0;
        }
        .stats {
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
        }
        .stat {
            flex: 1;
            padding: 16px;
            background: #fafafa;
            border-radius: 6px;
            text-align: center;
        }
        .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #2d3748;
            letter-spacing: -0.5px;
        }
        .stat-label {
            font-size: 12px;
            color: #718096;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }
        .day-section {
            margin-bottom: 32px;
        }
        .day-section h2 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 14px;
            color: #2d3748;
            letter-spacing: 0.3px;
        }
        .chart-container {
            margin: 24px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        .chart-title {
            font-size: 14px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 16px;
        }
        .price-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 24px;
        }
        .price-table th,
        .price-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            font-size: 13px;
        }
        .price-table th {
            font-weight: 600;
            color: #2d3748;
            background: #f7fafc;
        }
        .price-table td {
            color: #4a5568;
        }
        .price-change {
            font-weight: 500;
        }
        .price-change.up {
            color: #e53e3e;
        }
        .price-change.down {
            color: #38a169;
        }
        .menu-item {
            padding: 14px 0;
            border-bottom: 1px solid #e2e8f0;
            font-size: 14px;
            color: #4a5568;
            letter-spacing: 0.2px;
        }
        .menu-item:last-child {
            border-bottom: none;
        }
        .menu-item.new {
            background: #f0fdf4;
            padding: 12px;
            margin: 0 -12px 8px;
            border-radius: 4px;
            border-bottom: none;
        }
        .menu-item.new:before {
            content: "Ny ";
            background: #22c55e;
            color: white;
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 8px;
            font-weight: 600;
        }
        .footer {
            padding: 16px 24px;
            border-top: 1px solid #e5e5e5;
            font-size: 13px;
            color: #999;
            text-align: center;
        }
        @media (max-width: 600px) {
            body { padding: 12px; }
            .header h1 { font-size: 24px; }
            .stats { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kajen Gävle</h1>
            <div class="subtitle">Veckans lunchmeny</div>"""
        
        # Add week badge
        if week_number:
            html_content += f"""
            <span class="week-badge">{week_number}</span>"""
        
        html_content += """
        </div>
        <div class="tabs">
            <button class="tab active" onclick="showTab('menu')">Meny</button>
            <button class="tab" onclick="showTab('prices')">Prisutveckling</button>
        </div>
        <div class="content">
            <div id="menu-tab" class="tab-content active">
"""
        
        # Add price changes alert
        if price_changes:
            html_content += '            <div class="alert alert-warning">\n'
            html_content += '                <strong>Prisändringar</strong><br>\n'
            for change in price_changes:
                symbol = "↑" if change['diff'] > 0 else "↓"
                html_content += f'                {symbol} {change["type"]}: {change["old"]} → {change["new"]} kr<br>\n'
            html_content += '            </div>\n'
        
        # Add price history
        if price_history and len(price_history) >= 2:
            oldest = price_history[0]
            newest = price_history[-1]
            
            has_changes = False
            for price_type in newest['prices']:
                if price_type in oldest['prices'] and oldest['prices'][price_type] != newest['prices'][price_type]:
                    has_changes = True
                    break
            
            if has_changes:
                html_content += '            <div class="alert alert-info">\n'
                html_content += f'                <strong>Prisutveckling sedan {oldest["date"][:10]}</strong><br>\n'
                for price_type in newest['prices']:
                    if price_type in oldest['prices']:
                        old_price = oldest['prices'][price_type]
                        new_price = newest['prices'][price_type]
                        if old_price != new_price:
                            diff = new_price - old_price
                            percent = round((diff / old_price) * 100, 1)
                            html_content += f'                {price_type}: {old_price} → {new_price} kr ({diff:+d} kr, {percent:+.1f}%)<br>\n'
                html_content += '            </div>\n'
        
        # Add statistics
        total_dishes = sum(len(items) for items in days_dict.values())
        html_content += f"""
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(sorted_days)}</div>
                    <div class="stat-label">Dagar</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_dishes}</div>
                    <div class="stat-label">Rätter</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(new_dishes)}</div>
                    <div class="stat-label">Nya</div>
                </div>
            </div>
"""
        
        # Add menu items
        new_dishes_set = set(new_dishes)
        for day in sorted_days:
            items = days_dict[day]
            html_content += f'                <div class="day-section">\n'
            html_content += f'                    <h2>{day}</h2>\n'
            for item in items:
                if item in new_dishes_set:
                    html_content += f'                    <div class="menu-item new">{item}</div>\n'
                else:
                    html_content += f'                    <div class="menu-item">{item}</div>\n'
            html_content += '                </div>\n'
        
        # Close menu tab
        html_content += '            </div>\n'
        
        # Add prices tab
        html_content += '            <div id="prices-tab" class="tab-content">\n'
        
        # Create price chart
        if price_history and len(price_history) >= 2:
            # Prepare data for chart
            dates = [entry['date'][:10] for entry in price_history]
            
            # Get all price types
            price_types = list(price_history[0]['prices'].keys())
            
            # Create datasets for each price type
            datasets = []
            colors = ['#e53e3e', '#3182ce', '#38a169', '#d69e2e']
            
            for idx, price_type in enumerate(price_types):
                prices = [entry['prices'].get(price_type, 0) for entry in price_history]
                datasets.append({
                    'label': price_type,
                    'data': prices,
                    'color': colors[idx % len(colors)]
                })
            
            # Add chart
            html_content += '                <div class="chart-container">\n'
            html_content += '                    <div class="chart-title">Prisutveckling över tid</div>\n'
            html_content += '                    <canvas id="priceChart"></canvas>\n'
            html_content += '                </div>\n'
            
            # Add price table
            html_content += '                <table class="price-table">\n'
            html_content += '                    <thead><tr><th>Typ</th>'
            for date in dates[-5:]:  # Show last 5 dates
                html_content += f'<th>{date}</th>'
            html_content += '<th>Förändring</th></tr></thead>\n'
            html_content += '                    <tbody>\n'
            
            for price_type in price_types:
                html_content += f'                        <tr><td>{price_type}</td>'
                recent_prices = [entry['prices'].get(price_type, 0) for entry in price_history[-5:]]
                for price in recent_prices:
                    html_content += f'<td>{price} kr</td>'
                
                # Calculate change
                if len(recent_prices) >= 2:
                    first = recent_prices[0]
                    last = recent_prices[-1]
                    diff = last - first
                    percent = round((diff / first) * 100, 1) if first > 0 else 0
                    change_class = 'up' if diff > 0 else ('down' if diff < 0 else '')
                    symbol = '↑' if diff > 0 else ('↓' if diff < 0 else '→')
                    html_content += f'<td class="price-change {change_class}">{symbol} {diff:+d} kr ({percent:+.1f}%)</td>'
                else:
                    html_content += '<td>-</td>'
                
                html_content += '</tr>\n'
            
            html_content += '                    </tbody>\n'
            html_content += '                </table>\n'
        else:
            html_content += '                <p style="padding: 24px; color: #718096;">Ingen prishistorik tillgänglig än.</p>\n'
        
        html_content += '            </div>\n'
        
        # Close content and add footer
        html_content += """        </div>
        <div class="footer">
            Uppdaterad """ + datetime.now().strftime('%Y-%m-%d kl %H:%M') + """
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName + '-tab').classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
"""
        
        # Add Chart.js initialization
        if price_history and len(price_history) >= 2:
            dates = [entry['date'][:10] for entry in price_history]
            price_types = list(price_history[0]['prices'].keys())
            colors = ['#e53e3e', '#3182ce', '#38a169', '#d69e2e']
            
            html_content += """        // Initialize price chart
        const ctx = document.getElementById('priceChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: """ + str(dates) + """,
                datasets: [
"""
            
            for idx, price_type in enumerate(price_types):
                prices = [entry['prices'].get(price_type, 0) for entry in price_history]
                html_content += """                    {
                        label: '""" + price_type + """',
                        data: """ + str(prices) + """,
                        borderColor: '""" + colors[idx % len(colors)] + """',
                        backgroundColor: '""" + colors[idx % len(colors)] + """33',
                        tension: 0.3,
                        fill: false
                    }""" + ("," if idx < len(price_types) - 1 else "") + """
"""
            
            html_content += """                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            font: {
                                family: 'Roboto Mono',
                                size: 12
                            },
                            padding: 15
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return value + ' kr';
                            },
                            font: {
                                family: 'Roboto Mono',
                                size: 11
                            }
                        }
                    },
                    x: {
                        ticks: {
                            font: {
                                family: 'Roboto Mono',
                                size: 11
                            }
                        }
                    }
                }
            }
        });
"""
        
        html_content += """    </script>
</body>
</html>
"""
        
        # Save HTML file
        try:
            output_file = "menu.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print_success(f"HTML-fil skapad: {output_file}")
            
            # Open HTML file in browser
            abs_path = os.path.abspath(output_file)
            print_info(f"Öppnar {output_file} i webbläsaren...")
            webbrowser.open(f'file://{abs_path}')
            
        except Exception as e:
            print_error(f"Kunde inte skapa HTML-fil: {e}")

    def fetch_page(self, url: Optional[str] = None) -> tuple[Optional[List[Dict]], str]:
        """
        Fetch a webpage using Playwright and extract menu data.
        
        Args:
            url: URL to fetch (uses config URL if not provided)
            
        Returns:
            Tuple of (menu items list or None, week number string)
        """
        # Check if using local file
        local_file = self.config.get('local_file')
        if local_file:
            try:
                print_info(f"Läser från lokal fil: {local_file}")
                with open(local_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                print_success(f"Fil inläst ({len(html_content)} tecken)")
                
                # Parse with HTMLParser for local files
                print_info("Extraherar menydata från HTML...")
                parser = MenuHTMLParser()
                parser.feed(html_content)
                menu_items = parser.menu_items
                
                # Calculate week number from first item
                week_number = ""
                if menu_items:
                    first_day = menu_items[0]['day']
                    date_match = re.search(r'(\d{1,2})/(\d{1,2})', first_day)
                    if date_match:
                        day = int(date_match.group(1))
                        month = int(date_match.group(2))
                        year = datetime.now().year
                        date_obj = datetime(year, month, day)
                        week_num = date_obj.isocalendar()[1]
                        week_number = f"Vecka {week_num}"
                
                return menu_items, week_number
                
            except FileNotFoundError:
                print_error(f"Filen '{local_file}' hittades inte")
                return None, ""
            except Exception as e:
                print_error(f"Fel vid inläsning av fil: {e}")
                return None, ""
        
        # Otherwise fetch from web with Playwright
        target_url = url or self.config.get('target_url')
        timeout = self.config.get('timeout', 30) * 1000  # Convert to milliseconds
        headless = self.config.get('headless', True)
        use_chrome = self.config.get('use_installed_chrome', False)

        try:
            print_info(f"Hämtar sida: {Colors.UNDERLINE}{target_url}{Colors.ENDC}")
            print_info(f"Timeout: {timeout/1000}s | Headless: {headless} | Chrome: {'Systemets' if use_chrome else 'Playwright'}")
            
            with sync_playwright() as p:
                # Launch browser
                if use_chrome:
                    # Try to use system Chrome which might have proxy settings configured
                    browser = p.chromium.launch(
                        channel="chrome",
                        headless=headless
                    )
                else:
                    browser = p.chromium.launch(headless=headless)
                
                # Create context with custom user agent
                context = browser.new_context(
                    user_agent=self.config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                    bypass_csp=True,
                    ignore_https_errors=not self.config.get('verify_ssl', True)
                )
                
                # Create new page
                page = context.new_page()
                
                # Navigate to URL
                page.goto(target_url, timeout=timeout, wait_until='domcontentloaded')
                
                # Wait for menu content to load
                print_info("Väntar på att innehållet ska laddas...")
                page.wait_for_selector('h3.matochmat-wrap__day-heading', timeout=10000)
                
                print_success("Sidan laddad!")
                
                # Extract prices
                prices = self.extract_prices(page)
                if prices:
                    print_info("Priser extraherade")
                    for price_type, price in prices.items():
                        print(f"{Colors.YELLOW}    💰 {price_type}: {price} kr{Colors.ENDC}")
                    self.save_price_history(prices)
                
                # Extract menu data directly from page
                menu_items, week_number = self.extract_menu_data_from_page(page)
                
                # Close browser
                browser.close()
                
            return menu_items, week_number
            
        except PlaywrightTimeout:
            print_error(f"Timeout efter {timeout/1000} sekunder")
            print_warning("Tips: Öka 'timeout' i config.json eller använd 'local_file' för att läsa från sparad HTML")
            return None, ""
        except Exception as e:
            print_error(f"Fel vid hämtning: {e}")
            print_warning("Tips: Spara HTML-filen manuellt och använd 'local_file' i config.json")
            return None, ""

    def extract_menu_data_from_page(self, page: Page) -> tuple[List[Dict], str]:
        """
        Extract menu data directly from Playwright page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Tuple of (menu items list, week number string)
        """
        print_info("Extraherar menydata med Playwright...")
        menu_items = []
        week_number = ""
        
        try:
            # Try to extract week number from page
            try:
                # Look for week number in various possible locations
                week_heading = page.locator('h2, h3, p').filter(has_text='Vecka').first
                if week_heading:
                    week_text = week_heading.inner_text()
                    week_match = re.search(r'[Vv]ecka\s*(\d+)', week_text)
                    if week_match:
                        week_number = f"Vecka {week_match.group(1)}"
                        print_info(f"Hittade veckonummer: {week_number}")
            except:
                # If not found, calculate from first date
                pass
        except Exception as e:
            print_warning(f"Kunde inte hitta veckonummer: {e}")
        
        try:
            # Find all day headings
            day_headings = page.locator('h3.matochmat-wrap__day-heading').all()
            
            for heading in day_headings:
                day = heading.inner_text().strip()
                print_info(f"Bearbetar: {day}")
                
                # Get all paragraphs between this heading and the next heading or div
                # Start from the heading and get following siblings
                current_element = heading
                
                # Try to get next siblings that are paragraphs
                try:
                    # Get parent and then find paragraphs after this heading
                    parent = heading.locator('xpath=..')
                    all_elements = parent.locator('> *').all()
                    
                    # Find index of current heading
                    heading_found = False
                    for element in all_elements:
                        tag_name = element.evaluate('el => el.tagName.toLowerCase()')
                        
                        if not heading_found:
                            # Look for the heading
                            if tag_name == 'h3':
                                heading_text = element.inner_text().strip()
                                if heading_text == day:
                                    heading_found = True
                        else:
                            # After finding heading, collect paragraphs until next h3 or div
                            if tag_name == 'h3' or (tag_name == 'div' and 'matochmat__menu-text' in (element.get_attribute('class') or '')):
                                break
                            elif tag_name == 'p':
                                # Check if it's not a pricing paragraph
                                class_attr = element.get_attribute('class') or ''
                                if 'has-text-align-center' not in class_attr:
                                    text = element.inner_text().strip()
                                    if text and len(text) > 5:
                                        menu_items.append({
                                            'day': day,
                                            'name': text,
                                            'scraped_at': datetime.now().isoformat()
                                        })
                except Exception as e:
                    print_warning(f"Kunde inte hämta menyer för {day}: {e}")
            
            # Remove duplicates
            seen = set()
            unique_items = []
            for item in menu_items:
                key = (item['day'], item['name'])
                if key not in seen:
                    seen.add(key)
                    unique_items.append(item)
            
            menu_items = unique_items
            
            # If week number not found, calculate from first menu item
            if not week_number and menu_items:
                # Extract date from first day (e.g., "MÅNDAG 24/11")
                first_day = menu_items[0]['day']
                date_match = re.search(r'(\d{1,2})/(\d{1,2})', first_day)
                if date_match:
                    day = int(date_match.group(1))
                    month = int(date_match.group(2))
                    year = datetime.now().year
                    date_obj = datetime(year, month, day)
                    week_num = date_obj.isocalendar()[1]
                    week_number = f"Vecka {week_num}"
                    print_info(f"Beräknade veckonummer från datum: {week_number}")
            
        except Exception as e:
            print_error(f"Fel vid extrahering: {e}")
            return [], ""
        
        return menu_items, week_number

    def save_data(self, data: List[Dict], format_type: Optional[str] = None, 
                  output_file: Optional[str] = None) -> None:
        """
        Save extracted data to file.
        
        Args:
            data: List of menu items to save
            format_type: Output format ('json' or 'csv')
            output_file: Output file path (without extension)
        """
        format_type = format_type or self.config.get('output_format', 'json')
        output_file = output_file or self.config.get('output_file', 'output/menu_data')
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if format_type.lower() == 'json':
            self._save_json(data, f"{output_file}.json")
        elif format_type.lower() == 'csv':
            self._save_csv(data, f"{output_file}.csv")
        else:
            print(f"Error: Unsupported output format '{format_type}'")
            return

    def _save_json(self, data: List[Dict], filepath: str) -> None:
        """Save data as JSON."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print_success(f"Data sparad som JSON: {filepath}")
        except IOError as e:
            print_error(f"Fel vid sparande av JSON: {e}")

    def _save_csv(self, data: List[Dict], filepath: str) -> None:
        """Save data as CSV."""
        if not data:
            print_warning("Ingen data att spara")
            return
            
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print_success(f"Data sparad som CSV: {filepath}")
        except IOError as e:
            print_error(f"Fel vid sparande av CSV: {e}")

    def run(self) -> None:
        """Execute the scraping process."""
        print_header("🍽️  LUNCH MENU SCRAPER  🍽️")
        
        # Fetch the page and extract data
        menu_data, week_number = self.fetch_page()
        if not menu_data:
            print_error("Kunde inte hämta eller extrahera data. Avslutar.")
            return
        
        # Display week number if found
        if week_number:
            print()
            print(f"{Colors.BOLD}{Colors.CYAN}📅 {week_number}{Colors.ENDC}")
        
        # Display the menu
        self.display_menu(menu_data, week_number)
        
        # Save to history
        self.save_menu_history(menu_data)
        
        # Check for price changes
        price_changes = self.get_price_changes()
        
        # Also get all historical prices for display
        all_price_changes = self.get_all_price_history()
        
        if price_changes:
            print()
            print(f"{Colors.BOLD}{Colors.YELLOW}💰 PRISFÖRÄNDRINGAR SEDAN FÖRRA UPPDATERINGEN:{Colors.ENDC}")
            for change in price_changes:
                symbol = "📈" if change['diff'] > 0 else "📉"
                color = Colors.RED if change['diff'] > 0 else Colors.GREEN
                print(f"{color}  {symbol} {change['type']}: {change['old']} kr → {change['new']} kr ({change['diff']:+d} kr, {change['percent']:+.1f}%){Colors.ENDC}")
        
        if all_price_changes and len(all_price_changes) >= 2:
            print()
            print(f"{Colors.BOLD}{Colors.CYAN}📊 PRISHISTORIK:{Colors.ENDC}")
            # Show oldest vs newest (oldest is first in list, newest is last)
            oldest = all_price_changes[0]   # First entry (oldest)
            newest = all_price_changes[-1]  # Last entry (newest/today)
            
            print(f"{Colors.BOLD}  Jämförelse från {oldest['date'][:10]} till idag:{Colors.ENDC}")
            for price_type in newest['prices']:
                if price_type in oldest['prices']:
                    old_price = oldest['prices'][price_type]
                    new_price = newest['prices'][price_type]
                    if old_price != new_price:
                        diff = new_price - old_price
                        symbol = "📈" if diff > 0 else "📉"
                        color = Colors.RED if diff > 0 else Colors.GREEN
                        percent = round((diff / old_price) * 100, 1)
                        print(f"{color}  {symbol} {price_type}: {old_price} kr → {new_price} kr ({diff:+d} kr, {percent:+.1f}%){Colors.ENDC}")
        
        # Compare with previous week
        new_dishes, removed_dishes, common_dishes = self.compare_with_previous_week()
        
        if new_dishes or removed_dishes:
            print()
            print(f"{Colors.BOLD}{Colors.CYAN}📊 JÄMFÖRELSE MED FÖRRA VECKAN:{Colors.ENDC}")
            
            if new_dishes:
                print(f"\n{Colors.GREEN}  ✨ NYA RÄTTER ({len(new_dishes)}):{Colors.ENDC}")
                for dish in new_dishes[:5]:  # Show max 5
                    print(f"{Colors.GREEN}    + {dish}{Colors.ENDC}")
            
            if removed_dishes:
                print(f"\n{Colors.RED}  👋 BORTTAGNA RÄTTER ({len(removed_dishes)}):{Colors.ENDC}")
                for dish in removed_dishes[:5]:  # Show max 5
                    print(f"{Colors.RED}    - {dish}{Colors.ENDC}")
            
            if common_dishes:
                print(f"\n{Colors.YELLOW}  🔄 ÅTERKOMMANDE ({len(common_dishes)} rätter){Colors.ENDC}")
        
        # Optional: Save if configured
        if self.config.get('save_to_file', False):
            print()
            print_info(f"Sparar {len(menu_data)} menyposter...")
            self.save_data(menu_data)
        
        print()
        print_header("✅  KLART!  ✅")


def main():
    """Main entry point."""
    # Check for custom config path
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    try:
        # Create and run scraper
        scraper = LunchMenuScraper(config_path)
        scraper.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Avbruten av användaren{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Oväntat fel: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
