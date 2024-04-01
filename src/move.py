""" basic movement options in the dialogue
"""


class MoveType:
    """
    A class used to represent a move-type.
    It only records the premises, the conclusions, both as numbers, the valence (reason for or reason against)
    and the label of a move. Labels are of form: a_1, a_2, a_3 entails/excludes a_4.

    Attributes
    ----------
    prem : frozenset
        a frozenset of numbers, each number is the index of a sentence in the list for the enumerated language
        for example, a prem of a MoveType can be frozenset([1, 2, 4]), meaning the premise of the move is the sentences
        indexed by 1, 2, 4 in the enumerated language.
    val : str
        it's either 'reason for' or 'reason against'
    conc : int
        the index of a sentence in the enumerated language, as an integer
    move_label : str
        a str for the name of this move-type, e.g. 'a_1, a_2, a_3 entails a_4', or 'a_2, a_5 excludes a_1'
    """
    def __init__(self, prem, val, conc, move_label):
        self.prem = prem
        self.val = val
        self.conc = conc
        self.move_label = label_maker(move_label, self.prem, self.val, self.conc)
        self.short_label = short_label_maker(prem = self.prem, val = self.val, conc = self.conc)

    def show(self):
        print(self.move_label)

    def to_text(self):
        if self.val == 'reason for':
            text = str(set(self.prem)) + '⊨' + str(self.conc)
        else:
            text = str(set(self.prem)) + '#' + str(self.conc)
        return text


def label_maker(label, prem, val, conc):
    if label:
        pass
    else:
        label = 'a_'
        for p in prem:
            label += str(p) + ', a_'
        label = label[0:-4] # strip trailing ', a_'
        if val == 'reason for':
            label += ' entails '
        else:
            label += ' excludes '
        label += 'a_' + str(conc)

    return label


def short_label_maker(prem, val, conc):
    shortlable = str()
    for p in list(prem):
        shortlable = shortlable + str(p)
    if val == 'reason for':
        shortlable = shortlable + 'F'
    if val == 'reason against':
        shortlable = shortlable + 'A'
    shortlable = shortlable + str(conc)
    return shortlable


def same_move_type(movetype_1, movetype_2):
    if movetype_1.prem == movetype_2.prem and movetype_1.val == movetype_2.val and movetype_1.conc == movetype_2.conc:
        val = True
    else:
        val = False

    return val

def flip_val(sequent: MoveType) -> MoveType:
    if sequent.val == 'reason for':
        move = MoveType(sequent.prem, 'reason against', sequent.conc,
                                    sequent.move_label.replace('entails', 'excludes'))
    else:
        move = MoveType(sequent.prem, 'reason for', sequent.conc,
                                    sequent.move_label.replace('excludes', 'entails'))
    return move
