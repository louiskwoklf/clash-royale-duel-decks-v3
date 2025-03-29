from flask import Flask, render_template, request, url_for
import os
import requests

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

@app.route("/", methods=["GET", "POST"])
def index():
    cards = load_cards()
    for card in cards:
        ensure_image(card["name"])
    selected_duration = "1d"
    deck_output = None
    if request.method == "POST":
        selected_duration = request.form.get("duration", "1d")
        deck0 = request.form.get("deck0", "")
        deck1 = request.form.get("deck1", "")
        deck2 = request.form.get("deck2", "")
        deck3 = request.form.get("deck3", "")
        deck_output = {
            "deck1": deck0.split(",") if deck0 else [],
            "deck2": deck1.split(",") if deck1 else [],
            "deck3": deck2.split(",") if deck2 else [],
            "deck4": deck3.split(",") if deck3 else []
        }
    return render_template("index.html", cards=cards, deck_output=deck_output, selected_duration=selected_duration)

if __name__ == "__main__":
    app.run(debug=True)