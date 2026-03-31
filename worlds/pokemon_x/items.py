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
    range(0,    17): BAG_ITEMS,         # Pokeballs
    range(17,   55): BAG_MEDICINE,      # Medicine
    range(55,   113): BAG_ITEMS,        # Items
    range(116,  120): BAG_ITEMS,        # Genesect Drives 3 unknown before 14 after
    range(134,  135): BAG_MEDICINE,     # Sweet Heart for some reason
    range(135,  149): BAG_ITEMS,        # Items (Gen 4 Orbs and Mail)
    range(149,  213): BAG_BERRIES,      # Berries
    range(213,  328): BAG_ITEMS,        # Items (Held Items mainly
    range(328,  425): BAG_TM,           # TMs 1-92 and HMs
    range(428,  485): BAG_KEY,          # Some Key Items not all of them should be obtainable
    range(485,  501): BAG_ITEMS,        # Items
    range(501,  502): BAG_KEY,
    range(504,  505): BAG_MEDICINE,     # Rage Candy Bar
    range(505,  532): BAG_ITEMS,        # Items Data Cards
    range(532,  537): BAG_KEY,          # Key Items
    range(537,  574): BAG_ITEMS,        # Items
    range(618,  621): BAG_TM,           # TMs 93-95
    range(621,  638): BAG_KEY,
    range(638,  641): BAG_ITEMS,
    range(641,  644): BAG_KEY,          # Gen 6 early Key Items
    range(644,  651): BAG_ITEMS,        #
    range(651,  652): BAG_KEY,          # Poke Flute
    range(652,  686): BAG_ITEMS,        #
    range(686,  689): BAG_BERRIES,      #
    range(689,  690): BAG_KEY,          # Sprinkle Toad
    range(690,  695): BAG_TM,           # TMs 96-100
    range(695,  699): BAG_KEY,
    range(699,  700): BAG_ITEMS,        # Discount Code
    range(700,  704): BAG_KEY,
    range(704,  705): BAG_ITEMS,        # Strange Souvenier
    range(705,  708): BAG_KEY,
    range(708,  710): BAG_MEDICINE,
    range(710,  712): BAG_ITEMS,
    range(712,  715): BAG_KEY,
    range(715,  716): BAG_ITEMS,

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
