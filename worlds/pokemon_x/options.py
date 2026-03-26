from dataclasses import dataclass
from Options import Toggle

class RandomizeStarters(Toggle):
    display_name = "Randomize Starters"

@dataclass
class PokemonXOptions:
    randomize_starters: RandomizeStarters