from enum import StrEnum
from murdle_solver.main import solve


Suspects = StrEnum("Suspects", ["MISS_SAFFRON", "GENERAL_COFFEE", "GRANDMASTER_ROSE"])
Locations = StrEnum(
    "Locations",
    [
        ("STORAGE_ROOM", "the detective kit storage room"),
        ("ROOFTOP", "the rooftop lookout"),
        ("CONSPIRACY_ROOM", "the conspiracy room"),
    ],
)
Weapons = StrEnum(
    "Weapons",
    [
        ("MURDLE_BOOK", "the first murdle book"),
        ("MAGNIFYING_GLASS", "a magnifying glass"),
        ("RED_HERRING", "a red herring"),
    ],
)
TEST_INPUT = [Suspects, Locations, Weapons]
FACTS = [
    {Suspects.GENERAL_COFFEE: [Locations.STORAGE_ROOM]},
    {Suspects.GRANDMASTER_ROSE: [Locations.STORAGE_ROOM, Locations.CONSPIRACY_ROOM]},
    {Weapons.MURDLE_BOOK: [Locations.STORAGE_ROOM, Locations.ROOFTOP]},
    {Suspects.MISS_SAFFRON: [Weapons.MAGNIFYING_GLASS]},
]


def test_solve():
    solve(TEST_INPUT, FACTS)
