from typing import Set, Dict, Optional, TYPE_CHECKING

import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from NetUtils import ClientStatus, NetworkItem
from .items import get_item_name_from_id, get_pocket

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

EXPECTED_ROM_NAME = "Pokemon X (USA) (En,Ja,Fr,De,Es,It,Ko) AP v0.1"
MEM_DOMAIN = "FCRAM"

MONEY_ADDRESS = 0x074D869C
BADGE_ADDRESS = 0x074D86A0
BADGE_ID_FIRST = 1001
BADGE_ID_LAST = 1008
# ── How many items the game has processed, stored in save RAM ──
# You need to find/allocate a free u16 in your save block for this counter.
# This address is a PLACEHOLDER — replace with a real free address in your save.
RECEIVED_ITEMS_COUNT_ADDR = 0x08C9FFFF  # <-- REPLACE with real address

BAG_SLOT_SIZE  = 4          # 2 Byte Item_Id + 2 Byte Quantity


async def handle_badges(ctx: "BizHawkClientContext") -> bool:
    new_badges = 0
    # For every badge the player has gotten 1 is shifted into the position and logically ored with the result
    # Using or to prevent badges being in items recieved multiple times messing things up
    for item_id in ctx.items_received:
        if BADGE_ID_FIRST <= item_id.item <= BADGE_ID_LAST:
            shifted = 1 << item_id.item - BADGE_ID_FIRST
            new_badges = new_badges | shifted
    try:
        await bizhawk.write(ctx.bizhawk_ctx, [(BADGE_ADDRESS, new_badges.to_bytes(1, "little"), MEM_DOMAIN)])
    except Exception as e:
        print(f"[PokeX] Failed to write new item: {e}")
        return False
    return True


class PokemonXClient(BizHawkClient):
    game         = "Pokemon X"
    system       = "3DS"
    patch_suffix = ".apX"

    local_checked_locations: Set[int]

    def __init__(self):
        super().__init__()
        self.local_checked_locations = set()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        # TODO refuse connection if the wrong ROM/AP patch is loaded

        ctx.game = self.game  # sets "Pokemon X"
        ctx.items_handling = 0b111  # receive items from anywhere
        ctx.watcher_timeout = 0.125
        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None:
            return

        await handle_badges(ctx)
        await self.handle_received_items(ctx)
        await self.handle_checked_locations(ctx)

        # TODO: set game_clear
        game_clear = False
        if not ctx.finished_game and game_clear:
            ctx.finished_game = True
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

    async def handle_received_items(self, ctx: "BizHawkClientContext") -> None:
        #TODO read how many items the client has already recieved
        try:
            raw = await bizhawk.read(
                ctx.bizhawk_ctx,
                [(RECEIVED_ITEMS_COUNT_ADDR, 2, MEM_DOMAIN)]
            )
        except Exception as e:
            print(f"[PokeX] Could not read received-items counter: {e}")
            return

        game_received_count = int.from_bytes(raw[0], "little")

        # adding the next unrecieved item each method call
        if game_received_count < len(ctx.items_received):
            network_item: NetworkItem = ctx.items_received[game_received_count]
            success = await give_item(ctx, network_item.item, quantity=1)
            if not success:
                print(f"[PokeX] Could not give item 0x{network_item.item:04X} at index {game_received_count}")
                return

            game_received_count += 1
            counter_bytes = game_received_count.to_bytes(2, "little")
            try:
                await bizhawk.write(
                    ctx.bizhawk_ctx,[(RECEIVED_ITEMS_COUNT_ADDR, counter_bytes, MEM_DOMAIN)]
                )
            except Exception as e:
                print(f"[PokeX] Could not write received-items counter: {e}")

    # ------------------------------------------------------------------ #
    #  Location checking                                                 #
    # ------------------------------------------------------------------ #
    async def handle_checked_locations(self, ctx: "BizHawkClientContext") -> None:
        """
        Reads which locations are complete from the game and reports them
        to the server.  Replace get_location_ids() with real memory reads.
        """
        local_checked: Set[int] = set()

        for location_id in get_location_ids():
            if location_id in ctx.server_locations:
                local_checked.add(location_id)

        if local_checked != self.local_checked_locations:
            self.local_checked_locations = local_checked
            if local_checked:
                await ctx.check_locations(local_checked)


# ------------------------------------------------------------------ #
#  Bag helpers                                                         #
# ------------------------------------------------------------------ #
async def give_item(ctx: "BizHawkClientContext", item_id: int, quantity: int = 1) -> bool:
    """
    Write an item into the first free (or matching) bag slot in its pocket.
    Returns True on success, False if the pocket is full or the pocket is unknown.
    """
    item_name = get_item_name_from_id(item_id)
    pocket = get_pocket(item_id)
    print(f"[PokeX] give_item called: {item_name} x{quantity}")  # add this
    if pocket is None:
        print(f"[PokeX] Unknown pocket for item ID 0x{item_id:04X}")
        return False
    # Badges are handel in handle_badges so they are not written here
    if pocket == "BADGE":
        return True

    await bizhawk.display_message(ctx.bizhawk_ctx, f"Giving item {item_name} x{quantity}")

    base_addr, max_slots, max_items = pocket
    pocket_size = max_slots * BAG_SLOT_SIZE

    try:
        data = await bizhawk.read(ctx.bizhawk_ctx, [(base_addr, pocket_size, MEM_DOMAIN)])
    except Exception as e:
        print(f"[PokeX] Failed to read bag pocket: {e}")
        return False

    pocket_data = bytearray(data[0])

    for slot in range(max_slots):
        offset   = slot * BAG_SLOT_SIZE
        slot_id  = int.from_bytes(pocket_data[offset    : offset + 2], "little")
        slot_qty = int.from_bytes(pocket_data[offset + 2: offset + 4], "little")

        if slot_id == item_id:
            # Stack onto existing slot (cap at 1 for key/TM and 999 for rest)
            new_qty  = min(slot_qty + quantity, max_items)
            new_data = item_id.to_bytes(2, "little") + new_qty.to_bytes(2, "little")
            try:
                await bizhawk.write(ctx.bizhawk_ctx, [(base_addr + offset, new_data, MEM_DOMAIN)])
            except Exception as e:
                print(f"[PokeX] Failed to write item stack: {e}")
                return False
            print(f"[PokeX] Stacked item {item_name} → qty {new_qty} (slot {slot})")
            return True

        if slot_id == 0x0000:
            # Empty slot — write here
            new_data = item_id.to_bytes(2, "little") + quantity.to_bytes(2, "little")
            try:
                await bizhawk.write(ctx.bizhawk_ctx, [(base_addr + offset, new_data, MEM_DOMAIN)])
            except Exception as e:
                print(f"[PokeX] Failed to write new item: {e}")
                return False
            print(f"[PokeX] Gave item {item_name} x{quantity} (slot {slot})")
            return True

    print(f"[PokeX] Couldnt place item {item_name}!")
    return False


# ------------------------------------------------------------------ #
#  Stub — replace with real memory reads                             #
# ------------------------------------------------------------------ #
def get_location_ids() -> Set[int]:
    """
    TODO: read flags/event bytes from game memory and return the set of Archipelago location IDs that are currently checked in-game.
    kinda difficult
    """
    return set()
