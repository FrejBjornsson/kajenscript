"""
Simulation script to demonstrate price tracking and weekly comparison
"""
import json
from datetime import datetime, timedelta

# Simulate price history with changes
def simulate_price_changes():
    print("📊 Simulerar prisförändringar...\n")
    
    # Create fake price history
    two_weeks_ago = (datetime.now() - timedelta(days=14)).isoformat()
    last_week = (datetime.now() - timedelta(days=7)).isoformat()
    today = datetime.now().isoformat()
    
    price_history = [
        {
            "date": two_weeks_ago,
            "prices": {
                "Lunchbuffé": 125,
                "Tidig lunch (10-11)": 110,
                "Pensionärspris": 100,
                "Take away": 95
            }
        },
        {
            "date": last_week,
            "prices": {
                "Lunchbuffé": 125,
                "Tidig lunch (10-11)": 115,
                "Pensionärspris": 105,
                "Take away": 99
            }
        },
        {
            "date": today,
            "prices": {
                "Lunchbuffé": 129,
                "Tidig lunch (10-11)": 115,
                "Pensionärspris": 105,
                "Take away": 99
            }
        }
    ]
    
    with open('price_history.json', 'w', encoding='utf-8') as f:
        json.dump(price_history, f, indent=2, ensure_ascii=False)
    
    print("✅ Prishistorik skapad med följande förändringar:")
    print(f"   📈 Lunchbuffé: 125 kr → 129 kr (+4 kr, +3.2%)")
    print(f"   📈 Tidig lunch: 110 kr → 115 kr (+5 kr, +4.5%)")
    print(f"   📈 Pensionärspris: 100 kr → 105 kr (+5 kr, +5%)")
    print(f"   📈 Take away: 95 kr → 99 kr (+4 kr, +4.2%)\n")

# Simulate menu history with changes
def simulate_menu_changes():
    print("📊 Simulerar veckojämförelse...\n")
    
    last_week_items = [
        {"day": "MÅNDAG 17/11", "name": "Köttbullar med potatismos", "scraped_at": datetime.now().isoformat()},
        {"day": "MÅNDAG 17/11", "name": "Pasta carbonara", "scraped_at": datetime.now().isoformat()},
        {"day": "MÅNDAG 17/11", "name": "Pocherad fisk med hummersås & kokt potatis", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 18/11", "name": "Raggmunk med lingon, stekt fläsk & löksås", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 18/11", "name": "Kycklinggryta med ris", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 18/11", "name": "Ångad fisk med äggsås", "scraped_at": datetime.now().isoformat()},
        {"day": "ONSDAG 19/11", "name": "Laxfilé med dillsås", "scraped_at": datetime.now().isoformat()},
        {"day": "ONSDAG 19/11", "name": "Boeuf bourguignon med potatispuré", "scraped_at": datetime.now().isoformat()},
        {"day": "TORSDAG 20/11", "name": "Pannbiff med lök", "scraped_at": datetime.now().isoformat()},
        {"day": "FREDAG 21/11", "name": "Fish and chips med remouladsås", "scraped_at": datetime.now().isoformat()},
    ]
    
    this_week_items = [
        {"day": "MÅNDAG 24/11", "name": "Honungsglaserad kotlettrad med rostad potatis & sötpotatis", "scraped_at": datetime.now().isoformat()},
        {"day": "MÅNDAG 24/11", "name": "Pasta carbonara", "scraped_at": datetime.now().isoformat()},
        {"day": "MÅNDAG 24/11", "name": "Pocherad fisk med hummersås & kokt potatis", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 25/11", "name": "Raggmunk med lingon, stekt fläsk & löksås", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 25/11", "name": "Kycklingklubba med grönsaksris & srirachamayo", "scraped_at": datetime.now().isoformat()},
        {"day": "TISDAG 25/11", "name": "Ångad fisk med äggsås", "scraped_at": datetime.now().isoformat()},
        {"day": "ONSDAG 26/11", "name": "Friterad kyckling med pommes & chilibearnaise", "scraped_at": datetime.now().isoformat()},
        {"day": "ONSDAG 26/11", "name": "Boeuf bourguignon med potatispuré", "scraped_at": datetime.now().isoformat()},
        {"day": "TORSDAG 27/11", "name": "Kryddiga köttfärsbiffar med rostade rotfrukter & rödvinssås", "scraped_at": datetime.now().isoformat()},
        {"day": "FREDAG 28/11", "name": "Fish and chips med remouladsås", "scraped_at": datetime.now().isoformat()},
    ]
    
    menu_history = [
        {
            "week": "2025-W48",
            "year": 2025,
            "week_number": 48,
            "items": this_week_items,
            "scraped_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "week": "2025-W47",
            "year": 2025,
            "week_number": 47,
            "items": last_week_items,
            "scraped_at": (datetime.now() - timedelta(days=7)).isoformat(),
            "updated_at": (datetime.now() - timedelta(days=7)).isoformat()
        }
    ]
    
    with open('menu_history.json', 'w', encoding='utf-8') as f:
        json.dump(menu_history, f, indent=2, ensure_ascii=False)
    
    # Calculate differences
    current_dishes = set(item['name'] for item in this_week_items)
    previous_dishes = set(item['name'] for item in last_week_items)
    
    new_dishes = current_dishes - previous_dishes
    removed_dishes = previous_dishes - current_dishes
    common_dishes = current_dishes & previous_dishes
    
    print("✅ Menyhistorik skapad med följande förändringar:")
    print(f"\n✨ NYA RÄTTER ({len(new_dishes)}):")
    for dish in list(new_dishes)[:5]:
        print(f"   + {dish}")
    
    print(f"\n👋 BORTTAGNA RÄTTER ({len(removed_dishes)}):")
    for dish in list(removed_dishes)[:5]:
        print(f"   - {dish}")
    
    print(f"\n🔄 ÅTERKOMMANDE RÄTTER: {len(common_dishes)} st")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("  🎭 SIMULERING AV PRICE TRACKING & WEEKLY COMPARISON")
    print("=" * 60)
    print()
    
    simulate_price_changes()
    simulate_menu_changes()
    
    print("=" * 60)
    print("✅ Simulering klar!")
    print("Kör nu: python scraper.py")
    print("=" * 60)
