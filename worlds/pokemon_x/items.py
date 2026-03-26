from typing import FrozenSet, Optional, TYPE_CHECKING, Dict

from BaseClasses import Item, ItemClassification
if TYPE_CHECKING:
    from . import PokemonXWorld
from .data import data, ItemData


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
