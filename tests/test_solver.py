from enum import StrEnum
import pytest

from murdle_solver.main import (
    solve,
    _remove_other_topics_at_owner,
    _remove_topic_from_other_owners,
    _create_combinations,
    _fix_mutually_exclusive_options,
)


def test_create_combinations():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM"])
    Locations = StrEnum("Locations", ["CASTLE", "TRACK"])

    # Should have the option for each topic as an entry
    # and all options from all other topics as suboptions
    combinations = _create_combinations([Suspects, Weapons, Locations])

    assert combinations == {
        Suspects.MARIO: [
            Weapons.GO_CART,
            Weapons.MUSHROOM,
            Locations.CASTLE,
            Locations.TRACK,
        ],
        Suspects.LUIGI: [
            Weapons.GO_CART,
            Weapons.MUSHROOM,
            Locations.CASTLE,
            Locations.TRACK,
        ],
        Weapons.GO_CART: [
            Suspects.MARIO,
            Suspects.LUIGI,
            Locations.CASTLE,
            Locations.TRACK,
        ],
        Weapons.MUSHROOM: [
            Suspects.MARIO,
            Suspects.LUIGI,
            Locations.CASTLE,
            Locations.TRACK,
        ],
        Locations.CASTLE: [
            Suspects.MARIO,
            Suspects.LUIGI,
            Weapons.GO_CART,
            Weapons.MUSHROOM,
        ],
        Locations.TRACK: [
            Suspects.MARIO,
            Suspects.LUIGI,
            Weapons.GO_CART,
            Weapons.MUSHROOM,
        ],
    }


def test_remove_other_topics_at_owner():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM"])
    combinations = _create_combinations([Suspects, Weapons])

    _remove_other_topics_at_owner(
        combinations=combinations, topic=Suspects.MARIO, option=Weapons.GO_CART
    )

    assert combinations == {
        Suspects.MARIO: [Weapons.GO_CART],
        Suspects.LUIGI: [Weapons.GO_CART, Weapons.MUSHROOM],
        Weapons.GO_CART: [Suspects.MARIO, Suspects.LUIGI],
        Weapons.MUSHROOM: [Suspects.MARIO, Suspects.LUIGI],
    }


def test_remove_other_topics_at_owner_with_unrelated_options():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM"])
    # Add another topic so we can assert that this topic is not removed.
    Locations = StrEnum("Locations", ["PIT"])
    combinations = {
        Suspects.MARIO: [Weapons.GO_CART, Weapons.MUSHROOM, Locations.PIT],
        Suspects.LUIGI: [Weapons.GO_CART, Weapons.MUSHROOM, Locations.PIT],
        Weapons.GO_CART: [Suspects.MARIO, Suspects.LUIGI, Locations.PIT],
        Weapons.MUSHROOM: [Suspects.MARIO, Suspects.LUIGI, Locations.PIT],
    }

    # Should remove all other weapons from Mario, other than go_cart (i.e. mushroom)
    _remove_other_topics_at_owner(
        combinations=combinations, topic=Suspects.MARIO, option=Weapons.GO_CART
    )

    assert combinations == {
        Suspects.MARIO: [Weapons.GO_CART, Locations.PIT],
        Suspects.LUIGI: [Weapons.GO_CART, Weapons.MUSHROOM, Locations.PIT],
        Weapons.GO_CART: [Suspects.MARIO, Suspects.LUIGI, Locations.PIT],
        Weapons.MUSHROOM: [Suspects.MARIO, Suspects.LUIGI, Locations.PIT],
    }


def test_fix_mutually_exclusive_options():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM"])
    Locations = StrEnum("Locations", ["CASTLE", "TRACK"])

    # We create a case where for mario has two options specified: GO_CART and CASTLE
    # This means that they are also mutually exclusive. For each of GO_CART and CASTLE,
    # remove the other options
    combinations = {
        Suspects.MARIO: [Weapons.GO_CART, Locations.CASTLE],
        Weapons.GO_CART: [
            Suspects.MARIO,
            Locations.CASTLE,
            Locations.TRACK,
        ],
        Locations.CASTLE: [Suspects.MARIO, Weapons.GO_CART, Weapons.MUSHROOM],
    }
    _fix_mutually_exclusive_options(combinations)

    # Ensure that GO_CART can only be at CASTLE and vice versa
    assert combinations == {
        Suspects.MARIO: [Weapons.GO_CART, Locations.CASTLE],
        Weapons.GO_CART: [
            Suspects.MARIO,
            Locations.CASTLE,
        ],
        Locations.CASTLE: [Suspects.MARIO, Weapons.GO_CART],
    }


@pytest.mark.skip(reason="unfinished test..")
def test_remove_topic_from_other_owners():
    _remove_topic_from_other_owners()


def test_solve():
    # Lets test with the first challenge of the book
    Suspects = StrEnum(
        "Suspects", ["MISS_SAFFRON", "GENERAL_COFFEE", "GRANDMASTER_ROSE"]
    )
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
        {
            Suspects.GRANDMASTER_ROSE: [
                Locations.STORAGE_ROOM,
                Locations.CONSPIRACY_ROOM,
            ]
        },
        {Weapons.MURDLE_BOOK: [Locations.STORAGE_ROOM, Locations.ROOFTOP]},
        {Suspects.MISS_SAFFRON: [Weapons.MAGNIFYING_GLASS]},
    ]

    # todo, actually assert....
    solve(TEST_INPUT, FACTS)
