""" defines agent inferential theories based on an MSF
"""

import random
import numpy as np
from utils.utils import wrap_list


class InferentialTheory:
    def __init__(self, for_move, against_move):
        # frozensets of all for- and against-moves to be used by an agent with this InferentialTheory. All members of this frozenset are objects of class MoveType.
        self.for_move = for_move
        self.against_move = against_move
        self.arg = self._arg_generator(for_move = self.for_move, against_move = self.against_move)
        self.att = self._att_generator(for_move = self.for_move, against_move = self.against_move)

    def export(self, filename):   #method for exporting an Inferential Theory as an argumentation frame in Aspartix format as a .txt file. You will have to manually change the extension of the txt file to .dl, for now.
        f = open(filename, 'w')
        f.write("% arguments\n")
        for arg in self.arg:
            f.write('arg(' + arg + ').\n')
        f.write("\n% attack relations\n")
        for att in self.att:
            f.write('att(' + att[0] + ',' + att[1] + ').\n')
        f.close()

    def show(self):
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of an InferentialTheory display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('This inferential theory contains', len(self.for_move), 'reasons-for, as follows:')
        reasons_for = []
        for i in self.for_move:
            reasons_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        reasons_for.sort()
        print(wrap_list(reasons_for, items_per_line=5))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('This inferential theory contains', len(self.against_move), 'reasons-against, as follows:')
        reasons_against = []
        for i in self.against_move:
            reasons_against.append(str(set(i.prem)) + '#' + str(i.conc))
        reasons_against.sort()
        print(wrap_list(reasons_against, items_per_line=5))
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of an InferentialTheory display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

    def _arg_generator(self, for_move, against_move):
        for_nodes = []
        against_nodes = []

        for move in for_move:
            for_nodes.append(move.short_label)
        for_nodes.sort()

        for move in against_move:
            against_nodes.append(move.short_label)
        against_nodes.sort()

        nodes = for_nodes + against_nodes
        return nodes # Notice return is a list of strings, with for_nodes first and then against_nodes

    def _att_generator(self, for_move, against_move):
        attfromformove = []
        attfromagainstmove = []

        for formove in for_move:
            for againstmove in against_move:
                if formove.conc == againstmove.conc:
                    attfromformove.append((formove.short_label, againstmove.short_label))

        for againstmove in against_move:
            for formove in for_move:
                if againstmove.conc in formove.prem:
                    attfromagainstmove.append((againstmove.short_label, formove.short_label))
                elif againstmove.conc == formove.conc:
                    attfromagainstmove.append((againstmove.short_label, formove.short_label))
            for otheragainstmove in against_move:
                if againstmove.conc in otheragainstmove.prem:
                    attfromagainstmove.append((againstmove.short_label, otheragainstmove.short_label))

        allatt = attfromformove + attfromagainstmove
        allatt.sort()
        return allatt


def random_inferential_theory_generator(msf, for_move_size = 'random', against_move_size = 'random', for_move_chance = 0.5, against_move_chance = 0.5):

    # Part for for_move
    if for_move_size != 'random':
        if for_move_size > len(msf.for_move):
            print('Warning: the declared for_move_size is larger than the size of all for-moves in the universe of reasons.')
        selected_for_move = frozenset(random.sample(msf.for_move, for_move_size))
    else:
        k = np.random.binomial(len(msf.for_move), for_move_chance)
        selected_for_move = frozenset(random.sample(msf.for_move, k))

    # Part for against_move
    if against_move_size != 'random':
        if against_move_size > len(msf.against_move):
            print('Warning: the declared against_move_size is larger than the size of all against-moves in the universe of reasons.')
        selected_against_move = frozenset(random.sample(msf.against_move, against_move_size))
    else:
        k = np.random.binomial(len(msf.against_move), against_move_chance)
        selected_against_move = frozenset(random.sample(msf.against_move, k))

    return InferentialTheory(for_move = selected_for_move, against_move = selected_against_move)

