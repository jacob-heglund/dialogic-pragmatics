""" defines the CM closure operations
"""

from msf import MSF, exff_closure


def cm_imp_closure_once(input_imp):
    """
    Close the input_imp under CM once.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.

    Parameters
    ----------
    input_imp : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    Returns
    -------
    frozenset
        A frozenset set of implications. Namely, the one obtained by closing the input_imp under CM once.
    """

    imp_unsorted = []
    # We first change the format of the input IMP to make it earsier to sort
    for p in input_imp:
        imp_unsorted.append(( list(p[0]), p[1] ))
    # We sort the input IMP in its new format. The point of changing format is completely for this sorting. In the old
    # format, the input_imp will be sorted into undesired order. In the new format, all implications with the same premises
    # on the left will be sorted together.
    imp = sorted(imp_unsorted)
    i = 0
    j = 0
    # i and j are two indices we use to enumerate through imp. After the sorting, the input_imp are in the order such that
    # implications with the same premises are adjacent. This allows us to see the input_imp as partitioned into chunks.
    # Each chunk contains implications with the same premises. The idea is that i will be pointing to the first implication
    # in each chunk at a time and j will go through all elements in that chunk.

    # I call such a chunk "op_group", standing for "operating group", i.e. the group of implications we operate on
    # For example, if the premise set \Gamma = [1,3,5] implies and only implies 2 and 4 in the input_imp.
    # [([1,3,5], 2), ([1,3,5], 4)] would be an op_group and for this group, op_group_rhs would be [2,4] while op_group_lhs
    # would be [1,3,5].
    # To close an IMP under CM once, we only have to, for each op_group, for any m in op_group_rhs and any k in op_group_rhs,
    # we add the implication (op_group_lhs + [m], k).
    # This procedure will generate some implications that are already in the input_imp. But that's okay.
    op_group_rhs = []
    new_imps = []
    while i in range(len(imp)):
        # in each chunk at a time and j will go through all elements in that chunk.
        op_group_lhs = imp[i][0]
        while imp[i][0] == imp[j][0]:
            op_group_rhs.append(imp[j][1])
            j = j + 1
            if j not in range(len(imp)):
                break
        for k in op_group_rhs:
            for m in op_group_rhs:
                new_imps.append((frozenset.union(frozenset(op_group_lhs), frozenset([k])), m))
        op_group_rhs = []
        i = j
    return frozenset.union(input_imp, frozenset(new_imps))


def cm_imp_closure(input_imp):
    """
    Close the input_imp under CM until the fixed point is reached.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.

    Parameters
    ----------
    input_imp : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    Returns
    -------
    frozenset
        A frozenset set of implications. Namely, the one obtained by closing the input_imp under CM until the fixed point
        is reached.
    """
    result = cm_imp_closure_once(input_imp)
    while len(result) != len(cm_imp_closure_once(result)):
        result = cm_imp_closure_once(result)
    return result


def cm_inc_closure_once(input_imp, input_inc):
    """
    Close the input_inc under CM, with respect to the input_imp once.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.
    Let B be \bot.
    Then this means that if \Gamma implies A and \Gamma is incoherent, then \Gamma, A is incoherent.

    Parameters
    ----------
    input_imp : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    input_inc : frozenset
        A frozenset of incoherent frozensets, where each incoherent frozenset contains a bunch of indexes of jointly incoherent sentences.

    Returns
    -------
    frozenset
        A frozenset set of incoherent. Namely, the one obtained by closing the input_inc under CM with respect to the
        input_imp once.
    """

    new_inc = []
    for i in input_inc:
        for j in input_imp:
            if j[0] == i:
                new_inc.append(frozenset.union(i , frozenset([j[1]])))
    result = frozenset.union(input_inc, frozenset(new_inc))
    return result


def cm_inc_closure(input_imp, input_inc):
    """
    Close the input_inc under CM, with respect to the input_imp until a fixed point is reached.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.
    Let B be \bot.
    Then this means that if \Gamma implies A and \Gamma is incoherent, then \Gamma, A is incoherent.

    Parameters
    ----------
    input_imp : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    input_inc : frozenset
        A frozenset of incoherent frozensets, where each incoherent frozenset contains a bunch of indexes of jointly incoherent sentences.

    Returns
    -------
    frozenset
        A frozenset set of incoherent. Namely, the one obtained by closing the input_inc under CM with respect to the
        input_imp until a fixed point is reached.
    """
    result = cm_inc_closure_once(input_imp, input_inc)
    while len(result) != len(cm_inc_closure_once(input_imp, result)):
        result = cm_inc_closure_once(input_imp, result)
    return result


def msf_cm_full_closure_once(frame):
    cm_imp_first_time = cm_imp_closure(frame.imp)
    cm_inc_first_time = cm_inc_closure_once(cm_imp_first_time, frame.inc)
    exff_imp_first_time = exff_closure(language= frame.L, imp= cm_imp_first_time, inc= cm_inc_first_time)
    # Notice closing the INC under CM creates more incoherent sets and hence more exff sets, which in turn create more
    # implications via exff. So we have to close the IMP under exff after we generate more incoherent sets.
    # We consider closing under cm_imp, cm_inc, exff in turn as closing under cm once. Strictly speaking, it doesn't
    # make too much sense of closing once, since, e.g., exff apparently creates more implications that will produce more
    # imcoherent sets under CM.
    return MSF(lang = frame.L, imp = exff_imp_first_time, INC = cm_inc_first_time)


def msf_cm_full_closure(frame):
    result = msf_cm_full_closure_once(frame)
    while len(result.imp) != len(msf_cm_full_closure_once(result).imp) or len(result.inc) != len(msf_cm_full_closure_once(result).inc):
        result = msf_cm_full_closure_once(result)
    return result

