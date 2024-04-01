""" defines agents' inferential theories
"""

import random
import numpy as np
from utils import wrap_list


class InferentialTheory:
    def __init__(self, ForMove, AgainstMove):
        self.ForMove = ForMove  # the frozenset of all formoves to be used by a player with this InferentialTheory, that is all members of this frozenset are objects of class MoveType
        self.AgainstMove = AgainstMove  # the frozenset of all formoves to be used by a player with this InferentialTheory, that is all members of this frozenset are objects of class MoveType
        self.Arg = ArgGenerator(ForMove = self.ForMove, AgainstMove = self.AgainstMove)
        self.Att = AttGenerator(ForMove = self.ForMove, AgainstMove = self.AgainstMove)

    def export(self, filename):   #method for exporting an Inferential Theory as an argumentation frame in Aspartix format as a .txt file. You will have to manually change the extension of the txt file to .dl, for now.
        f = open(filename, 'w')
        f.write("% arguments\n")
        for arg in self.Arg:
            f.write('arg(' + arg + ').\n')
        f.write("\n% attack relations\n")
        for att in self.Att:
            f.write('att(' + att[0] + ',' + att[1] + ').\n')
        f.close()
    def show(self):
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of an InferentialTheory display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('This inferential theory contains', len(self.ForMove), 'reasons-for, as follows:')
        reasons_for = list()
        for i in self.ForMove:
            reasons_for.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        reasons_for.sort()
        print(wrap_list(reasons_for, items_per_line=5))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('This inferential theory contains', len(self.AgainstMove), 'reasons-against, as follows:')
        reasons_against = list()
        for i in self.AgainstMove:
            reasons_against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        reasons_against.sort()
        print(wrap_list(reasons_against, items_per_line=5))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of an InferentialTheory display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')


def UniverseOfReasons(msf):
    return InferentialTheory(ForMove = msf.ForMove, AgainstMove = msf.AgainstMove)


def ArgGenerator(ForMove, AgainstMove):
    fornodes = list()
    againstnodes = list()

    for move in ForMove:
        fornodes.append(move.ShortLabel)
    fornodes.sort()

    for move in AgainstMove:
        againstnodes.append(move.ShortLabel)
    againstnodes.sort()

    nodes = fornodes + againstnodes
    return nodes # Notice return is a list of strings, with fornodes first and then againstnodes


def AttGenerator(ForMove, AgainstMove):
    attfromformove = list()
    attfromagainstmove = list()

    for formove in ForMove:
        for againstmove in AgainstMove:
            if formove.Conc == againstmove.Conc:
                attfromformove.append((formove.ShortLabel, againstmove.ShortLabel))

    for againstmove in AgainstMove:
        for formove in ForMove:
            if againstmove.Conc in formove.Prem:
                attfromagainstmove.append((againstmove.ShortLabel, formove.ShortLabel))
            elif againstmove.Conc == formove.Conc:
                attfromagainstmove.append((againstmove.ShortLabel, formove.ShortLabel))
        for otheragainstmove in AgainstMove:
            if againstmove.Conc in otheragainstmove.Prem:
                attfromagainstmove.append((againstmove.ShortLabel, otheragainstmove.ShortLabel))

    allatt = attfromformove + attfromagainstmove
    allatt.sort()
    return allatt


def RandomInferentialTheoryGenerator(msf, for_move_size = 'random', against_move_size = 'random', for_move_chance = 1/2, against_move_chance = 1/2):

    # Part for ForMove
    if for_move_size != 'random':
        if for_move_size > len(msf.ForMove):
            print('Warning: the declared for_move_size is larger than the size of all for-moves in the universe of reasons.')
        SelectedForMove = frozenset(random.sample(msf.ForMove, for_move_size))
    else:
        k = np.random.binomial(len(msf.ForMove), for_move_chance)
        SelectedForMove = frozenset(random.sample(msf.ForMove, k))

    # Part for AgainstMove
    if against_move_size != 'random':
        if against_move_size > len(msf.AgainstMove):
            print('Warning: the declared against_move_size is larger than the size of all against-moves in the universe of reasons.')
        SelectedAgainstMove = frozenset(random.sample(msf.AgainstMove, against_move_size))
    else:
        k = np.random.binomial(len(msf.AgainstMove), against_move_chance)
        SelectedAgainstMove = frozenset(random.sample(msf.AgainstMove, k))

    return InferentialTheory(ForMove = SelectedForMove, AgainstMove = SelectedAgainstMove)


