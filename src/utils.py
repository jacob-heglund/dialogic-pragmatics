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


def agentswitch(x):
    """ This flips the agents: sending 'CL' to 'CR' and 'CR' to 'CL' """
    if x == 'CL':
        return 'CR'
    else:
        return 'CL'


def wrap_list(lst, items_per_line=5):
    """ This is used to display long lists. By default, it presents five elements on each line. """
    lines = list()
    for i in range(0, len(lst), items_per_line):
        chunk = lst[i:i + items_per_line]
        line = ", ".join("{!r}".format(x) for x in chunk)
        lines.append(line)
    return ",\n ".join(lines)


def stage_row(x, stage):
    """ This is used in the .show() method for MSF and inquiry, to display stages except the first stage. """
    if stage.TargetMove == None:
        x.add_row([stage.TurnNum,
               stage.Agent,
               None,
               stage.PragSig,
               stage.PrimeMove.MoveLabel,
               list(stage.FScoreSit.CL.AC),
               list(stage.FScoreSit.CL.RC),
               list(stage.FScoreSit.CL.AE),
               list(stage.FScoreSit.CL.RE),
               list(stage.FScoreSit.CR.AC),
               list(stage.FScoreSit.CR.RC),
               list(stage.FScoreSit.CR.AE),
               list(stage.FScoreSit.CR.RE)
               ])
    else:
        x.add_row([stage.TurnNum,
               stage.Agent,
               stage.TargetMove.TurnNum,
               stage.PragSig,
               stage.PrimeMove.MoveLabel,
               list(stage.FScoreSit.CL.AC),
               list(stage.FScoreSit.CL.RC),
               list(stage.FScoreSit.CL.AE),
               list(stage.FScoreSit.CL.RE),
               list(stage.FScoreSit.CR.AC),
               list(stage.FScoreSit.CR.RC),
               list(stage.FScoreSit.CR.AE),
               list(stage.FScoreSit.CR.RE)
               ])


def first_stage_row(x, stage):
    """ This is used in the .show() method for MSF and inquiry, to display the first stage """
    x.add_row([stage.TurnNum,
               stage.Agent,
               None,
               stage.PragSig,
               stage.PrimeMove.MoveLabel,
               list(stage.FScoreSit.CL.AC),
               list(stage.FScoreSit.CL.RC),
               list(stage.FScoreSit.CL.AE),
               list(stage.FScoreSit.CL.RE),
               list(stage.FScoreSit.CR.AC),
               list(stage.FScoreSit.CR.RC),
               list(stage.FScoreSit.CR.AE),
               list(stage.FScoreSit.CR.RE)
               ])

