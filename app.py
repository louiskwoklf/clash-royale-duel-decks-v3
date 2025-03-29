from flask import Flask, render_template, request
import os
import requests
from bs4 import BeautifulSoup
from itertools import product

app = Flask(__name__)

CARDS_FILE = os.path.join(app.static_folder, 'cards.txt')
IMAGES_FOLDER = os.path.join(app.static_folder, 'images')

rarity_order = {
    "common": 0,
    "rare": 1,
    "epic": 2,
    "legendary": 3,
    "champion": 4
}

def parse_card_line(line):
    line = line.strip()
    if line.startswith("{") and line.endswith("}"):
        line = line[1:-1]
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 3:
        return None
    card_name, rarity, cost = parts
    try:
        cost = int(cost)
    except ValueError:
        cost = 0
    return {"name": card_name, "rarity": rarity.lower(), "cost": cost}

def load_cards():
    cards = []
    if os.path.exists(CARDS_FILE):
        with open(CARDS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    card = parse_card_line(line)
                    if card:
                        cards.append(card)
    return cards

def ensure_image(card_name):
    filename = os.path.join(IMAGES_FOLDER, f"{card_name}.png")
    if not os.path.exists(filename):
        url = (
            "https://cdns3.royaleapi.com/cdn-cgi/image/"
            f"w=75,h=90,format=auto,q=80/static/img/cards/v4-aba2f5ae/{card_name}.png"
        )
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                os.makedirs(IMAGES_FOLDER, exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded image for {card_name}")
            else:
                print(f"Failed to download image for {card_name}: status {response.status_code}")
        except Exception as e:
            print(f"Error downloading image for {card_name}: {e}")

def fetch_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    print(f"Error fetching page: {response.status_code}")
    return None

def extract_decks(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    deck_segments = soup.find_all('div', class_='ui attached segment deck_segment')
    decks = []
    unique_deck_cards = set()
    for deck_segment in deck_segments:
        deck_name_tag = deck_segment.find('h4', class_='deck_human_name-mobile')
        deck_name = deck_name_tag.get_text(strip=True) if deck_name_tag else 'Unknown Deck Name'
        card_names = []
        for img_tag in deck_segment.find_all('img', class_='deck_card'):
            card_key = img_tag.get('data-card-key')
            if card_key:
                card_names.append(card_key)
            else:
                card_alt = img_tag.get('alt')
                if card_alt:
                    card_names.append(card_alt.lower().replace(' ', '-'))
        rep = tuple(sorted(card_names))
        if rep not in unique_deck_cards:
            unique_deck_cards.add(rep)
            decks.append({'deck_name': deck_name, 'cards': card_names})
        else:
            print(f"Duplicate deck skipped: {deck_name}")
    return decks

def query_deck(deck, duration):
    base_url = "https://royaleapi.com/decks/popular"
    params = {
        "time": duration,
        "sort": "rating",
        "size": "30",
        "players": "PvP",
        "min_ranked_trophies": "0",
        "max_ranked_trophies": "4000",
        "min_elixir": "1",
        "max_elixir": "9",
        "evo": "2",
        "min_cycle_elixir": "4",
        "max_cycle_elixir": "28",
        "mode": "detail",
        "type": "TopRanked",
        "global_exclude": "false",
    }
    cards_included = deck[:] if deck else []
    if "tower-princess" not in cards_included:
        cards_included.append("tower-princess")
    params["inc"] = cards_included
    req = requests.Request('GET', base_url, params=params)
    return req.prepare().url

def is_valid_duel(combo):
    all_cards = []
    for deck in combo:
        all_cards.extend(deck.get("cards", []))
    return len(all_cards) == len(set(all_cards))

def build_duel_decks(potential_decks, limit=1000):
    duel_decks = []
    seen = set()
    total_unique = 0
    for combo in product(
        potential_decks.get('deck1', []),
        potential_decks.get('deck2', []),
        potential_decks.get('deck3', []),
        potential_decks.get('deck4', [])
    ):
        if is_valid_duel(combo):
            rep = tuple(sorted(tuple(sorted(deck['cards'])) for deck in combo))
            if rep not in seen:
                seen.add(rep)
                total_unique += 1
                if len(duel_decks) < limit:
                    duel_decks.append(combo)
    return duel_decks, total_unique

@app.route("/", methods=["GET", "POST"])
def index():
    cards = load_cards()
    for card in cards:
        ensure_image(card["name"])
    selected_duration = "1d"
    deck_output = deck_results = None
    duel_decks, total_duel_decks = None, 0

    if request.method == "POST":
        selected_duration = request.form.get("duration", "1d")
        deck_output = {
            "deck1": [c.strip() for c in request.form.get("deck0", "").split(",") if c.strip()],
            "deck2": [c.strip() for c in request.form.get("deck1", "").split(",") if c.strip()],
            "deck3": [c.strip() for c in request.form.get("deck2", "").split(",") if c.strip()],
            "deck4": [c.strip() for c in request.form.get("deck3", "").split(",") if c.strip()]
        }
        deck_results = {}
        deck_debug_info = {}
        for key, deck in deck_output.items():
            url = query_deck(deck, selected_duration)
            deck_results[key] = url
            html_content = fetch_html(url)
            extracted = extract_decks(html_content) if html_content else []
            deck_debug_info[key] = {"url": url, "extracted": extracted}
        potential_decks = {key: deck_debug_info[key]['extracted'] for key in deck_debug_info}
        duel_decks, total_duel_decks = build_duel_decks(potential_decks)
    return render_template("index.html", cards=cards, deck_output=deck_output,
                           deck_results=deck_results, duel_decks=duel_decks,
                           total_duel_decks=total_duel_decks, selected_duration=selected_duration)

if __name__ == "__main__":
    app.run(debug=True)