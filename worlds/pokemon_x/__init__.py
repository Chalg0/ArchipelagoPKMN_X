import os
from typing import ClassVar, List

import settings
from worlds.AutoWorld import WebWorld, World

from .rules import set_rules
from .locations import create_locations, PokemonXLocation, create_location_label_to_id_map
from .regions import create_regions
from .items import PokemonXItem, find_item_data, create_item_label_to_id_map
from .client import PokemonXClient
from .options import PokemonXOptions
from .rom import PokemonXPatch


class PokemonXWebWorld(WebWorld):
    theme = "grass"
    tutorials = []

class PokemonXSettings(settings.Group):
    class PokemonXRomFile(settings.UserFilePath):
        description = "Pokemon X ROM File"
        copy_to = "Pokemon X.cci"
        md5s = []
        required = False

    rom_file: PokemonXRomFile = PokemonXRomFile(PokemonXRomFile.copy_to)


class PokemonXWorld(World):
    game = "Pokemon X"
    web = PokemonXWebWorld()

    settings_key = "pokemon_x_settings"
    settings: ClassVar[PokemonXSettings]

    options_dataclass = PokemonXOptions
    options: PokemonXOptions

    item_name_to_id = create_item_label_to_id_map()
    location_name_to_id = create_location_label_to_id_map()

    def create_regions(self):
        all_regions = create_regions(self)
        self.multiworld.regions.extend(all_regions.values())

        create_locations(self, all_regions)

    def create_items(self):
        item_locations: List[PokemonXLocation] = [
            location
            for location in self.multiworld.get_locations(self.player)
            if location.address is not None
        ]

        item_locations = [location for location in item_locations]
        itempool: List[PokemonXItem] = []

        for location in item_locations:
            item_data = find_item_data(location.default_item)
            if item_data is None:
                continue
            new_item = PokemonXItem(
                item_data.label,
                item_data.classification,
                item_data.ap_id,
                self.player,
                item_data.tags,
            )
            itempool.append(new_item)

        self.multiworld.itempool += itempool

    def set_rules(self):
        set_rules(self)

    def generate_output(self, output_directory: str) -> None:
        patch = PokemonXPatch(player=self.player, player_name=self.player_name)
        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{PokemonXPatch.patch_file_ending}"))
