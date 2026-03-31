from dataclasses import dataclass
from Options import Toggle, PerGameCommonOptions


class RandomizeStarters(Toggle):
    display_name = "Randomize Starters"

@dataclass
class PokemonXOptions(PerGameCommonOptions):
    randomize_starters: RandomizeStarters