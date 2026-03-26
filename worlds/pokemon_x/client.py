from typing import Set, Dict, Optional, TYPE_CHECKING
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient
from NetUtils import ClientStatus, NetworkItem

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


# ── Bag pocket base addresses (Pokémon X v1.0, ARM11 virtual / System Bus) ──
BAG_ITEMS_ADDR = 0x08C67554  # General items  (16 slots)
BAG_MEDICINE_ADDR = 0x08C67594  # Medicine        (47 slots)
BAG_TM_ADDR = 0x08C676A0  # TMs/HMs         (111 slots)
BAG_BALLS_ADDR = 0x08C6785C  # Poké Balls      (9 slots)
BAG_BATTLE_ADDR = 0x08C67880  # Battle items    (27 slots)
BAG_BERRIES_ADDR = 0x08C67660  # Berries         (13 slots)
BAG_KEY_ADDR = 0x08C67694  # Key items

POCKET_MAP = {
    # Fill this in based on item ID ranges from XY item tables
    # Example ranges (approximate):
    range(0x0001, 0x0010): (BAG_BALLS_ADDR, 16),  # Balls
    range(0x0011, 0x0036): (BAG_MEDICINE_ADDR, 47),  # Medicine
    range(0x0095, 0x00D4): (BAG_BERRIES_ADDR, 13), # Berries
    range(0x0148, 0x01A8): (BAG_TM_ADDR, 111),  # TMs 1-92 and HMs
    range(0x0087, 0x00D5): (BAG_BATTLE_ADDR, 27),  # Battle items
    range(0x026A, 0x026C): (BAG_TM_ADDR, 27), #Tms 93-95
    range(0x02B2, 0x02B6): (BAG_TM_ADDR, 27) #Tms 96-100
}


def get_pocket(item_id: int):
    """Return (base_address, max_slots) for the given item ID, or None."""
    for id_range, pocket in POCKET_MAP.items():
        if item_id in id_range:
            return pocket
    return None

# Each slot = 4 bytes: [item_id: u16 LE] [quantity: u16 LE]
SLOT_SIZE = 4
MEM_DOMAIN = "System Bus"

EXPECTED_ROM_NAME = "Pokemon X Ap patched"


class PokemonXClient(BizHawkClient):
    game = "Pokemon X"
    system = "3DS"
    patch_suffix = ".apX"

    local_checked_locations: Set[int]
    local_set_events: Dict[str, bool]
    local_found_key_items: Dict[str, bool]
    local_defeated_legendaries: Dict[str, bool]
    goal_flag: Optional[int]

    death_counter: Optional[int]
    previous_death_link: float
    ignore_next_death_link: bool


    def initialize_client(self):
        self.local_checked_locations = set()
        self.local_set_events = {}
        self.local_found_key_items = {}
        self.local_defeated_legendaries = {}
        self.goal_flag = None
        self.death_counter = None
        self.previous_death_link = 0
        self.ignore_next_death_link = False

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None or ctx.server.socket.closed or ctx.slot_data is None:
            return
        recieved_items = 0  # get from game file amount of items recieved
        await self.handle_recieved_items(ctx, recieved_items)

        game_clear = False
        local_checked_locations: set[int] = set()
        location_ids = get_location_ids()
        for location_id in location_ids:
            if location_id in ctx.server_locations:
                local_checked_locations.add(location_id)

        if local_checked_locations != self.local_checked_locations:
            self.local_checked_locations = local_checked_locations

            if local_checked_locations is not None:
                await ctx.check_locations(local_checked_locations)

        if not ctx.finished_game and game_clear:
            ctx.finished_game = True
            await ctx.send_msgs([{
                "cmd": "StatusUpdate",
                "status": ClientStatus.CLIENT_GOAL,
            }])

    async def handle_recieved_items(self, ctx: BizHawkClientContext, recieved_items: int) -> None:
        #recieved items should be pulled from inside the game here

        if recieved_items < len(ctx.items_received):
            item_id = ctx.items_received[recieved_items].item
            if item_id is not None:
                await give_item(ctx, item_id, quantity=1)
            recieved_items += 1

def launch_client():
    from worlds._bizhawk.context import BizHawkClientContext, launch as bizhawk_launch
    from CommonClient import ClientCommandProcessor

    bizhawk_launch()

def get_location_ids() -> set[int]:
    return set()


async def give_item(ctx: "BizHawkClientContext", item_id: int, quantity: int = 1):
    """
    Write an item into the first free bag slot in its pocket.
    A 'free' slot is one where item_id bytes == 0x0000.
    """
    pocket = get_pocket(item_id)
    if pocket is None:
        print(f"[PokeX] Unknown pocket for item ID 0x{item_id:04X}")
        return

    base_addr, max_slots = pocket

    # Read entire pocket to find a free or matching slot
    pocket_size = max_slots * SLOT_SIZE
    data = await bizhawk.read(ctx.bizhawk_ctx, [(base_addr, pocket_size, MEM_DOMAIN)])
    pocket_data = bytearray(data[0])

    for slot in range(max_slots):
        offset = slot * SLOT_SIZE
        slot_id = int.from_bytes(pocket_data[offset:offset + 2], "little")
        slot_qty = int.from_bytes(pocket_data[offset + 2:offset + 4], "little")

        if slot_id == item_id:
            # Stack onto existing slot
            new_qty = min(slot_qty + quantity, 999)
            new_data = item_id.to_bytes(2, "little") + new_qty.to_bytes(2, "little")
            await bizhawk.write(ctx.bizhawk_ctx, [(base_addr + offset, new_data, MEM_DOMAIN)])
            print(f"[PokeX] Stacked item 0x{item_id:04X} -> qty {new_qty} (slot {slot})")
            return

        if slot_id == 0x0000:
            # Empty slot — write here
            new_data = item_id.to_bytes(2, "little") + quantity.to_bytes(2, "little")
            await bizhawk.write(ctx.bizhawk_ctx, [(base_addr + offset, new_data, MEM_DOMAIN)])
            print(f"[PokeX] Gave item 0x{item_id:04X} x{quantity} (slot {slot})")
            return

    print(f"[PokeX] Bag pocket full for item 0x{item_id:04X}!")





