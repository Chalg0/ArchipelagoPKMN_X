from BaseClasses import Item, ItemClassification

import orjson
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Tuple, Any, Union
from importlib import resources

class ItemData(NamedTuple):
    name: str
    label: str
    ap_id: int
    classification: ItemClassification
    tags: FrozenSet[str]

class LocationData(NamedTuple):
    name: str
    label: str
    parent_region: str
    default_item: int
    ap_id: Union[int, List[int]]
    flag: int
    tags: FrozenSet[str]

class EventData(NamedTuple):
    name: str
    parent_region: str

class RegionData:
    name: str
    has_grass: bool
    has_water: bool
    has_fishing: bool
    exits: List[str]
    warps: List[str]
    locations: List[str]
    events: List[EventData]

    def __init__(self, name: str, has_grass: bool, has_water: bool, has_fishing: bool):
        self.name = name
        self.has_grass = has_grass
        self.has_water = has_water
        self.has_fishing = has_fishing
        self.exits = []
        self.warps = []
        self.locations = []
        self.events = []


class PokemonXData:
    locations: Dict[str, LocationData]
    items: Dict[int, ItemData]
    regions: Dict[str, RegionData]

    def __init__(self) -> None:
        self.locations = {}
        self.items = {}
        self.regions = {}


def _init() -> None:
    _init_region()
    _init_items()


def _init_region() -> None:
    # Load/merge region json files
    region_json_list = []

    regions_path = resources.files(__package__) / "data" / "regions"

    for file in regions_path.iterdir():
        if file.is_file():
            region_json_list.append(load_json_data(f"regions/{file.name}"))

    regions_json = {}
    for region_subset in region_json_list:
        for region_name, region_json in region_subset.items():
            if region_name in regions_json:
                raise AssertionError(f"Region [{region_name}] was defined multiple times")
            regions_json[region_name] = region_json

    #Create Region data
    location_attributes_json = load_json_data("locations.json")
    claimed_locations: Set[str] = set()
    data.regions = {}
    for region_name, region_json in regions_json.items():
        new_region = RegionData(
            region_name,
            region_json["has_grass"],
            region_json["has_water"],
            region_json["has_fishing"]
        )

        for location_name in region_json["locations"]:
            if location_name in claimed_locations:
                raise AssertionError(f"Location [{location_name}] was claimed by multiple regions")
            new_location = LocationData(
                location_name,
                location_attributes_json[location_name]["label"],
                region_name,
                location_attributes_json[location_name]["default_item"],
                location_attributes_json[location_name]["ap_id"],
                location_attributes_json[location_name]["flag"],
                frozenset(location_attributes_json[location_name]["tags"])
                )
            new_region.locations.append(location_name)
            data.locations[location_name] = new_location
            claimed_locations.add(location_name)

        new_region.locations.sort()

        # Events
        for event in region_json["events"]:
            new_region.events.append(EventData(event, region_name))

        # Exits
        for region_exit in region_json["exits"]:
            new_region.exits.append(region_exit)

        data.regions[region_name] = new_region

def _init_items() -> None:
    items_json = load_json_data("itemsX.json")

    data.items = {}
    for item_name, attributes in items_json.items():
        item_classification = None
        if attributes["classification"] == "PROGRESSION":
            item_classification = ItemClassification.progression
        elif attributes["classification"] == "USEFUL":
            item_classification = ItemClassification.useful
        elif attributes["classification"] == "FILLER":
            item_classification = ItemClassification.filler
        elif attributes["classification"] == "TRAP":
            item_classification = ItemClassification.trap
        else:
            raise ValueError(f"Unknown classification {attributes['classification']} for item {item_name}")

        data.items[attributes["ap_id"]] = ItemData(
            item_name,
            attributes["label"],
            attributes["ap_id"],
            item_classification,
            frozenset(attributes["tags"])
        )

def load_json_data(data_name: str) -> Union[List[Any], Dict[str, Any]]:
    data_path = resources.files(__package__) / "data" / data_name
    return orjson.loads(data_path.read_bytes().decode("utf-8-sig"))

data = PokemonXData()
_init()
