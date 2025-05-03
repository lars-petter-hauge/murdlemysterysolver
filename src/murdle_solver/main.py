from itertools import chain, permutations
import pprint
from enum import StrEnum
from collections import Counter
from typing import Any

flatten = chain.from_iterable


def _remove_topic_from_other_owners(combinations, topic, option):
    similar_topic_owners = [
        t for t in combinations.keys() if topic in type(t) and t != topic
    ]
    for sim_top_own in similar_topic_owners:
        combinations[sim_top_own] = [
            opt for opt in combinations[sim_top_own] if opt != option
        ]


def _remove_other_topics_at_owner(combinations, topic, option):
    combinations[topic] = [
        opt for opt in combinations[topic] if opt not in type(option) or opt == option
    ]


def _options_with_common_set_owner(combinations):
    for topic_owner, options in combinations.items():
        topic_counter = Counter([type(opt) for opt in options])
        single_owner_options_type = [
            opt for opt, count in topic_counter.items() if count == 1
        ]
        single_owner_options = [
            opt for opt in options if any(opt in t for t in single_owner_options_type)
        ]
        yield single_owner_options, topic_owner


def solver(combinations):
    i = 1
    n_values = sum([len(val) for val in combinations.values()])
    # n_unique_types = len(set([type(x) for x in flatten(combinations.values())]))
    old_n_values = n_values + 1  # We want to enforce at least a single run
    while n_values < old_n_values:
        old_n_values = n_values
        print(f"iteration {i}, n_values: {n_values}")
        for topic_owner, options in combinations.items():
            topics = set([type(opt) for opt in options])
            for topic in topics:
                opt_at_topic = [opt for opt in options if opt in topic]
                if len(opt_at_topic) == 1:
                    opt_at_topic = opt_at_topic[0]
                    print(
                        f"single owner for {opt_at_topic} namely {topic_owner}. Removing option from other owners"
                    )
                    # We have a topic with a single option, hence only this owner can have the option
                    _remove_topic_from_other_owners(
                        combinations, topic=topic_owner, option=opt_at_topic
                    )
                    # We can mirror as well
                    _remove_topic_from_other_owners(
                        combinations, topic=opt_at_topic, option=topic_owner
                    )
                    # We can remove all other topics at the opposing owner
                    _remove_other_topics_at_owner(
                        combinations, topic=opt_at_topic, option=topic_owner
                    )
        # For any options where there is at least two common owners, we can set them as mutually exclusive
        pprint.pp(combinations)
        something = _options_with_common_set_owner(combinations)
        something = [(t, o) for (t, o) in something if len(t) > 1]
        for opts, _ in something:
            for x, y in permutations(opts):
                _remove_other_topics_at_owner(combinations, topic=x, option=y)

        pprint.pp(combinations)
        n_values = sum([len(val) for val in combinations.values()])
        i += 1


def solve(topics: list[StrEnum], facts: list[dict[StrEnum, list[StrEnum]]]) -> Any:
    combinations = {}
    for topic in topics:
        for option in topic:
            combinations[option] = list(flatten([t for t in topics if t != topic]))

    print("Solving for:")
    pprint.pp(combinations)
    for fact in facts:
        for option, suboptions in fact.items():
            chosen_topic = [t for t in topics if suboptions[0] in t][0]
            invalid_suboptions = [opt for opt in chosen_topic if opt not in suboptions]
            for opt in invalid_suboptions:
                combinations[option].remove(opt)

    print("After clearing facts:")
    pprint.pp(combinations)
    solver(combinations)

    return combinations
