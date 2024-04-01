""" basic movement options in the dialogue
"""


class MoveType:
    """
    A class used to represent a move-type.
    It only records the premises, the conclusions, both as numbers, the valence (reason for or reason against)
    and the label of a move. Labels are of form: a_1, a_2, a_3 entails/excludes a_4.

    Attributes
    ----------
    Prem : frozenset
        a frozenset of numbers, each number is the index of a sentence in the list for the enumerated language
        for example, a Prem of a MoveType can be frozenset([1, 2, 4]), meaning the premise of the move is the sentences
        indexed by 1, 2, 4 in the enumerated language.
    Val : str
        it's either 'reason for' or 'reason against'
    Conc : int
        the index of a sentence in the enumerated language, as an integer
    MoveLabel : str
        a str for the name of this move-type, e.g. 'a_1, a_2, a_3 entails a_4', or 'a_2, a_5 excludes a_1'
    """
    def __init__(self, Prem, Val, Conc, MoveLabel):
        self.Prem = Prem
        self.Val = Val
        self.Conc = Conc
        self.MoveLabel = LabelMaker(MoveLabel, self.Prem, self.Val, self.Conc)
        self.ShortLabel = ShortLabelMaker(Prem = self.Prem, Val = self.Val, Conc = self.Conc)

    def show(self):
        print(self.MoveLabel)

    def to_text(self):
        if self.Val == 'reason for':
            text = str(set(self.Prem)) + '⊨' + str(self.Conc)
        else:
            text = str(set(self.Prem)) + '#' + str(self.Conc)
        return text


def LabelMaker(label, prem, val, conc):
    if label:
        return label
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


def ShortLabelMaker(Prem, Val, Conc):
    shortlable = str()
    for p in list(Prem):
        shortlable = shortlable + str(p)
    if Val == 'reason for':
        shortlable = shortlable + 'F'
    if Val == 'reason against':
        shortlable = shortlable + 'A'
    shortlable = shortlable + str(Conc)
    return shortlable


def SameMoveType(movetype_1, movetype_2):
    if movetype_1.Prem == movetype_2.Prem and movetype_1.Val == movetype_2.Val and movetype_1.Conc == movetype_2.Conc:
        return True
    else:
        return False


def flip_val(sequent: MoveType) -> MoveType:
    if sequent.Val == 'reason for':
        return MoveType(sequent.Prem, 'reason against', sequent.Conc,
                                    sequent.MoveLabel.replace('entails', 'excludes'))
    else:
        return MoveType(sequent.Prem, 'reason for', sequent.Conc,
                                    sequent.MoveLabel.replace('excludes', 'entails'))

