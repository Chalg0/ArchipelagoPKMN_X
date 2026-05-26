"""
Classes and functions related to creating a ROM patch for Pokemon X
"""
from typing import TYPE_CHECKING

import settings as ap_settings
from worlds.Files import APProcedurePatch

if TYPE_CHECKING:
    pass


class PokemonXPatch(APProcedurePatch):
    game = "Pokemon X"
    patch_file_ending = ".apX"
    result_file_ending = ".3ds"
    hash = None  # No MD5 verification
    procedure = []  # placeholder; no ROM modifications implemented yet

    @classmethod
    def get_source_data(cls) -> bytes:
        settings_obj = ap_settings.get_settings()
        rom_path = str(settings_obj["pokemon_x_settings"]["rom_file"])
        with open(rom_path, "rb") as f:
            return f.read()
