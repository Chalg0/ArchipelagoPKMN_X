from typing import TYPE_CHECKING

from rule_builder.options import OptionFilter
from rule_builder.rules import Has, HasAll, Rule

from .data import data


def set_rules(world: "Pokemon X") -> None:

    def get_entrance(entrance: str):
        return world.multiworld.get_entrance(entrance, world.player)

    world.set_rule(
        get_entrance("REGION_AQUACORDE_TOWN_UPPER -> REGION_AQUACORDE_TOWN_MAIN"),
        Has("EVENT_OBTAIN_STARTER"),
    ),

    world.set_rule(
        get_entrance("REGION_VANIVILLE_TOWN_MAIN -> REGION_VANIVILLE_TOWN_PROTAGONIST_HOUSE_PROF_LETTER"),
        Has("Prof's Letter"),
    ),

    world.set_rule(
        get_entrance("REGION_AQUACORDE_TOWN_MAIN -> REGION_ROUTE_2"),
        Has("EVENT_GOODBYE_FROM_MOM"),
    ),

    world.set_rule(
        get_entrance("REGION_SANTALUNE_CITY_MAIN -> REGION_SANTALUNE_CITY_POST_GYM"),
        Has("EVENT_DEFEAT_VIOLA")
    )