""" defines output for Dialogic Pragmatics 2 (DP2)
"""

from msf import msf_closure


def inquiry_to_msf(inquiry):
    imp = []
    inc = []
    for i in inquiry.AcceptedFor:
        imp.append((frozenset(i[0]), i[1]))
    for i in inquiry.AcceptedAgainst:
        inc.append(frozenset.union(frozenset(i[0]), frozenset([i[1]])))
    return msf_closure(inquiry.Language, frozenset(imp), frozenset(inc))
