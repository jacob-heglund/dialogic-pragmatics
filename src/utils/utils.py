"""basic utility functions for the reasoning system
"""


def list_powerset_list(lst: list) -> list:
    """ This gives the power set of a given list as a list of frozensets """
    result = [frozenset()]
    for x in lst:
        result.extend([frozenset.union(subset, frozenset([x])) for subset in result])
    return result


def list_powerset(lst: list) -> frozenset:
    """ This gives the power set of a given list as a frozenset of frozensets """
    return frozenset(list_powerset_list(lst))


def list_powerset_(lst: list) -> frozenset:
    """ This gives the power set of a given list with the empty set removed, as a frozenset of frozensets """
    result = list_powerset_list(lst)
    del result[0]
    return frozenset(result)


def powerset(m: frozenset) -> frozenset:
    """ This gives the power set of a given frozenset as a frozenset of frozensets """
    return list_powerset(list(m))


def powerset_(m: frozenset) -> frozenset:
    """ This gives the power set of a given frozenset, with the empty set removed, as a frozenset of frozensets """
    return list_powerset_(list(m))


def wrap_list(lst, items_per_line=5):
    """ This is used to display long lists. By default, it presents five elements on each line. """
    lines = []
    for i in range(0, len(lst), items_per_line):
        chunk = lst[i:i + items_per_line]
        line = ", ".join("{!r}".format(x) for x in chunk)
        lines.append(line)
    return ",\n ".join(lines)

