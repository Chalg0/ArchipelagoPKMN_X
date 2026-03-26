from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple, FrozenSet
from BaseClasses import Region, ItemClassification
from .data import data
from .items import PokemonXItem
from .locations import PokemonXLocation


def create_regions(world) -> Dict[str, Region]:
    return add_regions(world)

def add_regions(world) -> Dict[str, Region]:
    regions: Dict[str, Region] = {}
    connections: List[Tuple[str, str, str]] = []

    for region_name, region_data in data.regions.items():
        new_region = Region(region_name, world.player, world.multiworld)

        for event_data in region_data.events:
            event = PokemonXLocation(world.player, event_data.name, None, new_region)
            event.place_locked_item(PokemonXItem(event_data.name, ItemClassification.progression, None, world.player, frozenset("event")))
            new_region.locations.append(event)

        for region_exit in region_data.exits:
            connections.append((f"{region_name} -> {region_exit}", region_name, region_exit))

        regions[region_name] = new_region

    for name, source, dest in connections:
        regions[source].connect(regions[dest], name)

    regions["Menu"] = Region("Menu", world.player, world.multiworld)
    regions["Menu"].connect(regions["REGION_VANIVILLE_TOWN_PROTAGONIST_HOUSE_F2"], "Start Game")

    return regions