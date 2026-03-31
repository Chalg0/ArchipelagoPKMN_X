from typing import FrozenSet, Optional, TYPE_CHECKING, Dict

from BaseClasses import Item, ItemClassification
if TYPE_CHECKING:
    from . import PokemonXWorld
from .data import data, ItemData

# Bag pocket base addresses and sizes(Pokémon X (World)
BAG_ITEMS    = 0x074D5554, 400, 999 # General items     (400 slots?) WIP
BAG_KEY      = 0x074D5B94, 96, 1  # Key items         (96 slots?) WIP
BAG_TM       = 0x074D5D14, 106, 1  # TMs/HMs           (106 slots?) WIP
BAG_MEDICINE = 0x074D5EBC, 256, 999  # Medicine Bag      (256 slots?) correct adress?
BAG_BERRIES  = 0x074D5FBC, 102, 999# Berries           (102 slots?) WIP

BADGE = "BADGE"

# Maps the items ids to where in the bag they belong
POCKET_MAP = {
    range(0x0000, 0x0010): BAG_ITEMS,      # Pokeballs
    range(0x0011, 0x0036): BAG_MEDICINE,   # Medicine
    range(0x0037, 0x0070): BAG_ITEMS,      # Items
    range(0x0074, 0x0077): BAG_ITEMS,      # Genesect Drives 3 unknown before 14 after
    range(0x0086, 0x0086): BAG_MEDICINE,   # Sweet Heart for some reason
    range(0x0087, 0x0094): BAG_ITEMS,      # Items (Gen 4 Orbs and Mail)
    range(0x0095, 0x00D4): BAG_BERRIES,    # Berries
    range(0x00D5, 0x0147): BAG_ITEMS,      # Items (Held Items mainly
    range(0x0148, 0x01A8): BAG_TM,         # TMs 1-92 and HMs
    range(0x01AC, 0x01E4): BAG_KEY,        # Some Key Items not all of them should be obtainable
    range(0x026A, 0x026C): BAG_TM,         # TMs 93-95
    range(0x02B2, 0x02B6): BAG_TM,         # TMs 96-100
    range(1001, 10008): BADGE,
}

class PokemonXItem(Item):
    game: str = "Pokemon X"
    tags: FrozenSet[str]

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int, tags: FrozenSet[str]) -> None:
        super().__init__(name, classification, code, player)
        self.tags = tags


def find_item_data(item_name) -> ItemData | None:
    for item_data in data.items.values():
        if item_data.label == item_name:
            return item_data
    return None


def create_item_label_to_id_map() -> Dict[str, int]:
    """
    Creates a map from item labels to their AP item id (code)
    """
    label_to_code_map: Dict[str, int] = {}
    for item_value, attributes in data.items.items():
        label_to_code_map[attributes.label] = attributes.ap_id

    return label_to_code_map
