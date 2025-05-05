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

    # fmt: off
    assert combinations == {
        Suspects.MARIO: [Weapons.GO_CART, Weapons.MUSHROOM, Locations.CASTLE, Locations.TRACK],
        Suspects.LUIGI: [Weapons.GO_CART, Weapons.MUSHROOM, Locations.CASTLE, Locations.TRACK],
        Weapons.GO_CART: [Suspects.MARIO, Suspects.LUIGI, Locations.CASTLE, Locations.TRACK],
        Weapons.MUSHROOM: [Suspects.MARIO, Suspects.LUIGI, Locations.CASTLE, Locations.TRACK],
        Locations.CASTLE: [Suspects.MARIO,Suspects.LUIGI,Weapons.GO_CART,Weapons.MUSHROOM],
        Locations.TRACK: [Suspects.MARIO,Suspects.LUIGI,Weapons.GO_CART,Weapons.MUSHROOM],
    }
    # fmt: on


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


def test_remove_topic_from_other_owners():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI", "BOWSER"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM", "HAMMER"])
    Locations = StrEnum("Locations", ["CASTLE", "TRACK", "PIT"])

    # fmt: off
    combinations = {
        Suspects.MARIO: [Weapons.GO_CART, Locations.CASTLE, Locations.TRACK, Locations.PIT],
        Suspects.LUIGI: [Weapons.GO_CART, Weapons.MUSHROOM, Weapons.HAMMER, Locations.CASTLE, Locations.TRACK, Locations.PIT],
        Suspects.BOWSER: [Weapons.GO_CART, Weapons.MUSHROOM, Weapons.HAMMER, Locations.CASTLE, Locations.TRACK, Locations.PIT],
    }
    # fmt: on
    _remove_topic_from_other_owners(combinations, Suspects.MARIO, Weapons.GO_CART)

    # Ensure that GO_CART has been removed from the other suspects
    # fmt: off
    assert combinations == {
        Suspects.MARIO: [Weapons.GO_CART, Locations.CASTLE, Locations.TRACK, Locations.PIT],
        Suspects.LUIGI: [Weapons.MUSHROOM, Weapons.HAMMER, Locations.CASTLE, Locations.TRACK, Locations.PIT],
        Suspects.BOWSER: [Weapons.MUSHROOM, Weapons.HAMMER, Locations.CASTLE, Locations.TRACK, Locations.PIT],
    }
    # fmt: on


def test_first_challenge():
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
    TEST_INPUT = [Suspects, Weapons, Locations]
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
    should_contain = {
        Suspects.GRANDMASTER_ROSE: [Weapons.RED_HERRING, Locations.CONSPIRACY_ROOM],
        Suspects.GENERAL_COFFEE: [Weapons.MURDLE_BOOK, Locations.STORAGE_ROOM],
        Suspects.MISS_SAFFRON: [Weapons.MAGNIFYING_GLASS, Locations.ROOFTOP],
    }

    result = solve(TEST_INPUT, FACTS)
    for key, value in should_contain.items():
        assert result[key] == value


def test_fix_mutually_exclusive_options_4groups():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI", "BOWSER", "LEIA"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM", "HAMMER", "SPEAR"])
    Locations = StrEnum("Locations", ["CASTLE", "TRACK", "PIT", "FARM"])
    Fixation = StrEnum("Fixation", ["FLOWERS", "FIRE", "CARS", "PANCAKES"])

    # fmt: off
    combinations = {
        Suspects.BOWSER: [Weapons.SPEAR, Locations.TRACK, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES],
        Weapons.SPEAR: [Suspects.BOWSER, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK],
        Locations.TRACK: [Suspects.BOWSER, Fixation.FIRE, Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR],
        Fixation.FIRE: [Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR, Suspects.BOWSER, Suspects.LEIA, Suspects.LUIGI, Suspects.MARIO, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK]
    }
    # fmt: on
    _remove_topic_from_other_owners(combinations, Suspects.MARIO, Weapons.GO_CART)

    # Ensure that fixation FIRE has been selected for weapon spear
    # fmt: off
    assert combinations == {
        Suspects.BOWSER: [Weapons.SPEAR, Locations.TRACK, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES],
        Weapons.SPEAR: [Suspects.BOWSER, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK],
        Locations.TRACK: [Suspects.BOWSER, Fixation.FIRE, Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR],
        Fixation.FIRE: [Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR, Suspects.BOWSER, Suspects.LEIA, Suspects.LUIGI, Suspects.MARIO, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK]
    }
    # fmt: on


@pytest.mark.xfail
def test_fix_mutually_exclusive_options_4groups_exclude():
    Suspects = StrEnum("Suspects", ["MARIO", "LUIGI", "BOWSER", "LEIA"])
    Weapons = StrEnum("Weapons", ["GO_CART", "MUSHROOM", "HAMMER", "SPEAR"])
    Locations = StrEnum("Locations", ["CASTLE", "TRACK", "PIT", "FARM"])
    Fixation = StrEnum("Fixation", ["FLOWERS", "FIRE", "CARS", "PANCAKES"])

    # fmt: off
    combinations = {
        Suspects.BOWSER: [Weapons.SPEAR, Locations.TRACK, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES],
        Weapons.SPEAR: [Suspects.BOWSER, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK],
        Locations.TRACK: [Suspects.LEIA, Suspects.LUIGI, Suspects.MARIO, Fixation.FIRE, Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR],
        Fixation.FIRE: [Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR, Suspects.BOWSER, Suspects.LEIA, Suspects.LUIGI, Suspects.MARIO, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK]
    }
    # fmt: on
    _remove_topic_from_other_owners(combinations, Suspects.MARIO, Weapons.GO_CART)

    # Ensure that fixation FIRE has been removed for weapon spear
    # fmt: off
    assert combinations == {
        Suspects.BOWSER: [Weapons.SPEAR, Locations.TRACK, Fixation.CARS, Fixation.FIRE, Fixation.FLOWERS, Fixation.PANCAKES],
        Weapons.SPEAR: [Suspects.BOWSER, Fixation.CARS, Fixation.FLOWERS, Fixation.PANCAKES, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK],
        Locations.TRACK: [Suspects.BOWSER, Fixation.FIRE, Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR],
        Fixation.FIRE: [Weapons.GO_CART, Weapons.HAMMER, Weapons.MUSHROOM, Weapons.SPEAR, Suspects.BOWSER, Suspects.LEIA, Suspects.LUIGI, Suspects.MARIO, Locations.CASTLE, Locations.FARM, Locations.PIT, Locations.TRACK]
    }
    # fmt: on


@pytest.mark.xfail
def test_solve_four_groups():
    # Add a test that solves when the fourth group is added.
    # Challenge 51
    Suspects = StrEnum(
        "Suspects",
        ["CRYSTAL_GODDESS", "SEASHELL_DDS", "HERBALIST_ONYX", "SUPREME_MASTER_COBALT"],
    )
    Locations = StrEnum(
        "Locations",
        [
            "THE_ROOF",
            "THE_GROUNDS",
            "ISOLATION_CHAMBER",
            "ACTUAL_LABORATORY",
        ],
    )
    Weapons = StrEnum(
        "Weapons",
        [
            "CHANNELED_TEXT",
            "DOWSING_ROD",
            "PSEUDO_SCIENTIFIC_APPARATUS",
            "HYPNOTIC_WATCH",
        ],
    )
    Experiments = StrEnum(
        "Experiments",
        ["TELEKINESIS", "AURA_READING", "CONTROL_GROUP", "FORTUNE_TELLING"],
    )

    TEST_INPUT = [Suspects, Weapons, Locations, Experiments]

    # fmt: off
    FACTS = [
        {Suspects.SUPREME_MASTER_COBALT:[Locations.ACTUAL_LABORATORY]},
        {Suspects.CRYSTAL_GODDESS: [Weapons.PSEUDO_SCIENTIFIC_APPARATUS]},
        {Suspects.HERBALIST_ONYX: [Weapons.CHANNELED_TEXT]},
        {Weapons.DOWSING_ROD: [Experiments.AURA_READING, Experiments.FORTUNE_TELLING, Experiments.TELEKINESIS]},
        {Experiments.FORTUNE_TELLING: [Locations.ISOLATION_CHAMBER]},
        {Weapons.PSEUDO_SCIENTIFIC_APPARATUS: [Experiments.TELEKINESIS]},
        {Weapons.HYPNOTIC_WATCH: [Suspects.CRYSTAL_GODDESS, Suspects.SUPREME_MASTER_COBALT]},
        {Suspects.SEASHELL_DDS: [Locations.THE_GROUNDS]},
    ]
    should_contain = {
        Suspects.CRYSTAL_GODDESS: [Weapons.PSEUDO_SCIENTIFIC_APPARATUS, Locations.THE_ROOF, Experiments.TELEKINESIS],
        Suspects.SEASHELL_DDS: [Weapons.DOWSING_ROD, Locations.THE_GROUNDS, Experiments.AURA_READING],
        Suspects.HERBALIST_ONYX: [Weapons.CHANNELED_TEXT, Locations.ISOLATION_CHAMBER, Experiments.FORTUNE_TELLING],
        Suspects.SUPREME_MASTER_COBALT:[Weapons.HYPNOTIC_WATCH, Locations.ACTUAL_LABORATORY, Experiments.CONTROL_GROUP],
    }
    # fmt: on

    result = solve(TEST_INPUT, FACTS)
    for key, value in should_contain.items():
        assert result[key] == value
