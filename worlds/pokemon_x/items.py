from typing import FrozenSet, Optional, TYPE_CHECKING, Dict

from BaseClasses import Item, ItemClassification
if TYPE_CHECKING:
    from . import PokemonXWorld
from .data import data, ItemData

# Bag pocket base addresses and sizes(Pokémon X (World)
BAG_ITEMS    = 0x074D5554, 400, 999     # General items     (400 slots?) WIP
BAG_KEY      = 0x074D5B94, 96, 1        # Key items         (96 slots?) WIP
BAG_TM       = 0x074D5D14, 106, 1       # TMs/HMs           (106 slots?) WIP
BAG_MEDICINE = 0x074D5EBC, 256, 999     # Medicine Bag      (256 slots?) correct adress?
BAG_BERRIES  = 0x074D5FBC, 102, 999     # Berries           (102 slots?) WIP

BADGE = "BADGE"

# Maps the items ids to where in the bag they belong unobtainable key items are included in this map
POCKET_MAP = {
    range(0,    16): BAG_ITEMS,         # Pokeballs
    range(17,   54): BAG_MEDICINE,      # Medicine
    range(55,   112): BAG_ITEMS,        # Items
    range(116,  119): BAG_ITEMS,        # Genesect Drives 3 unknown before 14 after
    range(134,  134): BAG_MEDICINE,     # Sweet Heart for some reason
    range(135,  148): BAG_ITEMS,        # Items (Gen 4 Orbs and Mail)
    range(149,  212): BAG_BERRIES,      # Berries
    range(213,  327): BAG_ITEMS,        # Items (Held Items mainly
    range(328,  424): BAG_TM,           # TMs 1-92 and HMs
    range(428,  484): BAG_KEY,          # Some Key Items not all of them should be obtainable
    range(485,  500): BAG_ITEMS,        # Items
    range(501,  503): BAG_KEY,
    range(504,  504): BAG_MEDICINE,     # Rage Candy Bar
    range(505,  531): BAG_ITEMS,        # Items Data Cards
    range(532,  536): BAG_KEY,          # Key Items
    range(537,  573): BAG_ITEMS,        # Items
    range(618,  620): BAG_TM,           # TMs 93-95
    # 621 - 640   Gen 5 items and assalt vest
    range(641,  643): BAG_KEY,          # Gen 6 early Key Items
    range(644,  650): BAG_ITEMS,        #
    range(651,  651): BAG_KEY,          # Poke Flute
    range(652,  685): BAG_ITEMS,        #
    range(686,  688): BAG_BERRIES,      #
    range(689,  689): BAG_KEY,          # Sprinkle Toad
    range(690,  694): BAG_TM,           # TMs 96-100
    range(695,  698): BAG_KEY,
    range(699,  699): BAG_ITEMS,        # Discount Code
    range(700,  703): BAG_KEY,
    range(704,  704): BAG_ITEMS,        # Strange Souvenier
    range(705,  707): BAG_KEY,
    range(708,  709): BAG_MEDICINE,
    range(710,  711): BAG_ITEMS,
    range(712,  714): BAG_KEY,
    range(715,  715): BAG_ITEMS,

    range(1001, 1008): BADGE,
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
