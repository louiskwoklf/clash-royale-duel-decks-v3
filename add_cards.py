import os

# Define the order for rarity sorting.
rarity_order = {
    "common": 0,
    "rare": 1,
    "epic": 2,
    "legendary": 3,
    "champion": 4
}

# Mapping for shorthand and full rarity names.
rarity_mapping = {
    "c": "common",
    "common": "common",
    "r": "rare",
    "rare": "rare",
    "e": "epic",
    "epic": "epic",
    "l": "legendary",
    "legendary": "legendary",
    "ch": "champion",
    "champion": "champion"
}

def parse_line(line):
    """
    Parse a line from cards.txt formatted as:
    {card_name, rarity, cost}
    """
    line = line.strip()
    if line.startswith("{") and line.endswith("}"):
        line = line[1:-1]
    parts = [x.strip() for x in line.split(",")]
    if len(parts) == 3:
        card_name, rarity, cost = parts
        try:
            cost = int(cost)
        except ValueError:
            cost = 0
        return (card_name, rarity, cost)
    return None

def format_entry(entry):
    """
    Format an entry tuple into the text file format.
    """
    card_name, rarity, cost = entry
    return f"{{{card_name}, {rarity}, {cost}}}"

def sort_key(entry):
    """
    Returns a tuple that defines the sort order:
      1. Card name suffix priority: cards ending in '-hero' first, then '-ev1', then others.
      2. Rarity order as defined in rarity_order.
      3. Cost (numerical order).
      4. Card name (alphabetical order) as a default case.
    """
    card_name, rarity, cost = entry
    if card_name.endswith("-hero"):
        suffix_flag = 0
    elif card_name.endswith("-ev1"):
        suffix_flag = 1
    else:
        suffix_flag = 2
    rarity_value = rarity_order.get(rarity.lower(), 100)  # Unknown rarities sort last.
    return (suffix_flag, rarity_value, cost, card_name.lower())

def main():
    filename = "static/cards.txt"
    entries = []
    
    # Read the existing entries from cards.txt if it exists.
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    entry = parse_line(line)
                    if entry:
                        entries.append(entry)
    
    print("Current entries:")
    for entry in entries:
        print(entry)
    
    print("\nEnter new cards. When finished, type 'done' as the card name.")
    while True:
        card_name = input("Enter card name (or 'done' to finish): ").strip()
        if card_name.lower() == "done":
            break
        rarity_input = input("Enter card rarity (common [c], rare [r], epic [e], legendary [l], champion [ch]): ").strip().lower()
        rarity = rarity_mapping.get(rarity_input)
        if rarity is None:
            print("Invalid rarity entered; defaulting to common.")
            rarity = "common"
        cost_str = input("Enter card cost (number): ").strip()
        try:
            cost = int(cost_str)
        except ValueError:
            print("Invalid cost entered; defaulting to 0.")
            cost = 0
        entries.append((card_name, rarity, cost))
    
    # Sort the combined list.
    entries.sort(key=sort_key)
    
    # Write the sorted entries back to cards.txt.
    with open(filename, "w") as f:
        for entry in entries:
            f.write(format_entry(entry) + "\n")
    
    print("\nUpdated and sorted entries:")
    for entry in entries:
        print(entry)

if __name__ == "__main__":
    main()