import json

# Constants
BAG_ITEMS = "BAG_ITEMS"
BAG_MEDICINE = "BAG_MEDICINE"
BAG_BERRIES = "BAG_BERRIES"
BAG_TM = "BAG_TM"
BAG_KEY = "BAG_KEY"
BADGE = "BADGE"

POCKET_MAP = {
    range(0,    17): BAG_ITEMS,
    range(17,   55): BAG_MEDICINE,
    range(55,   113): BAG_ITEMS,
    range(116,  120): BAG_ITEMS,
    range(134,  135): BAG_MEDICINE,
    range(135,  149): BAG_ITEMS,
    range(149,  213): BAG_BERRIES,
    range(213,  328): BAG_ITEMS,
    range(328,  425): BAG_TM,
    range(428,  485): BAG_KEY,
    range(485,  501): BAG_ITEMS,
    range(501,  502): BAG_KEY,
    range(504,  505): BAG_MEDICINE,
    range(505,  532): BAG_ITEMS,
    range(532,  537): BAG_KEY,
    range(537,  574): BAG_ITEMS,
    range(618,  621): BAG_TM,
    range(621,  638): BAG_KEY,
    range(638,  641): BAG_ITEMS,
    range(641,  644): BAG_KEY,
    range(644,  651): BAG_ITEMS,
    range(651,  652): BAG_KEY,
    range(652,  686): BAG_ITEMS,
    range(686,  689): BAG_BERRIES,
    range(689,  690): BAG_KEY,
    range(690,  695): BAG_TM,
    range(695,  699): BAG_KEY,
    range(699,  700): BAG_ITEMS,
    range(700,  704): BAG_KEY,
    range(704,  705): BAG_ITEMS,
    range(705,  708): BAG_KEY,
    range(708,  710): BAG_MEDICINE,
    range(710,  712): BAG_ITEMS,
    range(712,  715): BAG_KEY,
    range(715,  716): BAG_ITEMS,
    range(1001, 1008): BADGE,
}

def get_bag(ap_id: int) -> str | None:
    """Return the bag label for a given ap_id, or None if not in any range."""
    index = ap_id - 1  # ap_id is 1-based, ranges are 0-based
    for r, bag in POCKET_MAP.items():
        if index in r:
            return bag
    return None

def parse_items(data: dict) -> dict:
    """Add a 'bag' field to every item entry based on its ap_id."""
    result = {}
    for key, entry in data.items():
        new_entry = dict(entry)
        new_entry["bag"] = get_bag(entry["ap_id"])
        result[key] = new_entry
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parser.py <input.json> [output.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parsed = parse_items(data)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        print(f"Written to {output_path}")
    else:
        print(json.dumps(parsed, indent=2, ensure_ascii=False))