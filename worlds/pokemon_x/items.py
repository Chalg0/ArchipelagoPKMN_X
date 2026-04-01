from typing import FrozenSet, Optional, Dict

from BaseClasses import Item, ItemClassification
from .data import data, ItemData

# Bag pocket base addresses and sizes(Pokémon X (World)
BAG_ITEMS    = 0x074D5554, 400, 999     # General items     (400 slots?) WIP
BAG_KEY      = 0x074D5B94, 96,  1       # Key items        (96 slots?) WIP
BAG_TM       = 0x074D5D14, 106, 1       # TMs/HMs           (106 slots?) WIP
BAG_MEDICINE = 0x074D5EBC, 256, 999     # Medicine Bag      (256 slots?) correct adress?
BAG_BERRIES  = 0x074D5FBC, 102, 999     # Berries           (102 slots?) WIP

BADGE = "BADGE"


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

def get_item_name_from_id(item_id) -> str | None:
    for item_data in data.items.values():
        if item_data.ap_id == item_id:
            return item_data.label
    return None


def create_item_label_to_id_map() -> Dict[str, int]:
    """
    Creates a map from item labels to their AP item id (code)
    """
    label_to_code_map: Dict[str, int] = {}
    for item_value, attributes in data.items.items():
        label_to_code_map[attributes.label] = attributes.ap_id

    return label_to_code_map

def get_pocket(item_id):
    for item_data in data.items.values():
        if item_data.ap_id == item_id:
            bag = item_data.bag
            if bag == "BAG_ITEMS":
                return BAG_ITEMS
            elif bag == "BAG_TM":
                return BAG_TM
            elif bag == "BAG_KEY":
                return BAG_KEY
            elif bag == "BAG_MEDICINE":
                return BAG_MEDICINE
            elif bag == "BAG_BERRIES":
                return BAG_BERRIES
            elif bag == "BADGE":
                return BADGE
    return None