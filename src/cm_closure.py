""" defines the CM closure operations
"""

from msf import MSF, ExFF_closure


def CM_IMP_closure_once(input_IMP):
    """
    Close the input_IMP under CM once.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.

    Parameters
    ----------
    input_IMP : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    Returns
    -------
    frozenset
        A frozenset set of implications. Namely, the one obtained by closing the input_IMP under CM once.
    """

    imp_unsorted = list()
    # We first change the format of the input IMP to make it earsier to sort
    for p in input_IMP:
        imp_unsorted.append(( list(p[0]), p[1] ))
    # We sort the input IMP in its new format. The point of changing format is completely for this sorting. In the old
    # format, the input_IMP will be sorted into undesired order. In the new format, all implications with the same premises
    # on the left will be sorted together.
    imp = sorted(imp_unsorted)
    i = 0
    j = 0
    # i and j are two indices we use to enumerate through imp. After the sorting, the input_IMP are in the order such that
    # implications with the same premises are adjacent. This allows us to see the input_IMP as partitioned into chunks.
    # Each chunk contains implications with the same premises. The idea is that i will be pointing to the first implication
    # in each chunk at a time and j will go through all elements in that chunk.

    # I call such a chunk "op_group", standing for "operating group", i.e. the group of implications we operate on
    # For example, if the premise set \Gamma = [1,3,5] implies and only implies 2 and 4 in the input_IMP.
    # [([1,3,5], 2), ([1,3,5], 4)] would be an op_group and for this group, op_group_rhs would be [2,4] while op_group_lhs
    # would be [1,3,5].
    # To close an IMP under CM once, we only have to, for each op_group, for any m in op_group_rhs and any k in op_group_rhs,
    # we add the implication (op_group_lhs + [m], k).
    # This procedure will generate some implications that are already in the input_IMP. But that's okay.
    op_group_rhs = list()
    new_imps = list()
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
        op_group_rhs = list()
        i = j
    return frozenset.union(input_IMP, frozenset(new_imps))


def CM_IMP_closure(input_IMP):
    """
    Close the input_IMP under CM until the fixed point is reached.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.

    Parameters
    ----------
    input_IMP : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    Returns
    -------
    frozenset
        A frozenset set of implications. Namely, the one obtained by closing the input_IMP under CM until the fixed point
        is reached.
    """
    result = CM_IMP_closure_once(input_IMP)
    while len(result) != len(CM_IMP_closure_once(result)):
        result = CM_IMP_closure_once(result)
    return result


def CM_INC_closure_once(input_IMP, input_INC):
    """
    Close the input_INC under CM, with respect to the input_IMP once.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.
    Let B be \bot.
    Then this means that if \Gamma implies A and \Gamma is incoherent, then \Gamma, A is incoherent.

    Parameters
    ----------
    input_IMP : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    input_INC : frozenset
        A frozenset of incoherent frozensets, where each incoherent frozenset contains a bunch of indexes of jointly incoherent sentences.

    Returns
    -------
    frozenset
        A frozenset set of incoherent. Namely, the one obtained by closing the input_INC under CM with respect to the
        input_IMP once.
    """

    new_inc = list()
    for i in input_INC:
        for j in input_IMP:
            if j[0] == i:
                new_inc.append(frozenset.union(i , frozenset([j[1]])))
    result = frozenset.union(input_INC, frozenset(new_inc))
    return result


def CM_INC_closure(input_IMP, input_INC):
    """
    Close the input_INC under CM, with respect to the input_IMP until a fixed point is reached.
    CM: if \Gamma implies A and \Gamma implies B, then \Gamma, A implies B.
    Let B be \bot.
    Then this means that if \Gamma implies A and \Gamma is incoherent, then \Gamma, A is incoherent.

    Parameters
    ----------
    input_IMP : frozenset
        A frozenset of implications, where each implication is a tuple, whose first element is a frozenset of indexes of
        sentences and second element is an index of a sentence.
    input_INC : frozenset
        A frozenset of incoherent frozensets, where each incoherent frozenset contains a bunch of indexes of jointly incoherent sentences.

    Returns
    -------
    frozenset
        A frozenset set of incoherent. Namely, the one obtained by closing the input_INC under CM with respect to the
        input_IMP until a fixed point is reached.
    """
    result = CM_INC_closure_once(input_IMP, input_INC)
    while len(result) != len(CM_INC_closure_once(input_IMP, result)):
        result = CM_INC_closure_once(input_IMP, result)
    return result


def msf_CM_full_closure_once(frame):
    cm_imp_first_time = CM_IMP_closure(frame.IMP)
    cm_inc_first_time = CM_INC_closure_once(cm_imp_first_time, frame.INC)
    exff_imp_first_time = ExFF_closure(language= frame.L, imp= cm_imp_first_time, inc= cm_inc_first_time)
    # Notice closing the INC under CM creates more incoherent sets and hence more ExFF sets, which in turn create more
    # implications via ExFF. So we have to close the IMP under ExFF after we generate more incoherent sets.
    # We consider closing under cm_imp, cm_inc, exff in turn as closing under cm once. Strictly speaking, it doesn't
    # make too much sense of closing once, since, e.g., exff apparently creates more implications that will produce more
    # imcoherent sets under CM.
    return MSF(L = frame.L, IMP = exff_imp_first_time, INC = cm_inc_first_time)


def msf_CM_full_closure(frame):
    result = msf_CM_full_closure_once(frame)
    while len(result.IMP) != len(msf_CM_full_closure_once(result).IMP) or len(result.INC) != len(msf_CM_full_closure_once(result).INC):
        result = msf_CM_full_closure_once(result)
    return result

