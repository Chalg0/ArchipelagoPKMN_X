from typing import Dict, Optional
from BaseClasses import Location, Region
from .data import data

class PokemonXLocation(Location):
    game = "Pokemon X"
    key: Optional[str]
    default_item_value: str #todo

    def __init__(
            self,
            player: int,
            name: str,
            address: Optional[int],
            parent: Optional[Region] = None,
            key: Optional[str] = None,
            default_item_value: str = None) -> None:
        super().__init__(player, name, address, parent)
        self.key = key
        self.default_item = default_item_value


def create_locations(world, regions: Dict[str, Region]) -> None:
    for region_name, region_data in data.regions.items():
        region = regions[region_name]

        for location_name in region_data.locations:
            location_data = data.locations[location_name]

            location = PokemonXLocation(
                world.player,
                location_data.label,
                location_data.ap_id,
                region,
                location_name,
                location_data.default_item
            )
            region.locations.append(location)

def create_location_label_to_id_map() -> Dict[str, int]:
    """
    Creates a map from location labels to their AP location id (address)
    """
    label_to_id_map: Dict[str, int] = {}
    for region_data in data.regions.values():
        for location_name in region_data.locations:
            location_data = data.locations[location_name]
            label_to_id_map[location_data.label] = location_data.ap_id

    return label_to_id_map
