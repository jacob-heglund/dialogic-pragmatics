""" defines inquiry capabilities
"""


import random
from prettytable import PrettyTable
from utils import stage_row, first_stage_row, wrap_list
from inferential_theory import InferentialTheory, UniverseOfReasons
from stage import NextStage, \
                FirstMoveFor_RandomPremise, FirstMoveAgainst_RandomPremise, \
                ManualInitialMoveFor,ManualInitialMoveAgainst, \
                RandomFirstMoveFor, RandomFirstMoveAgainst, \
                Verdict


class Inquiry:
    def __init__(self, MSF, ListOfStages, CL_InferentialTheory, CR_InferentialTheory, CL_Strategy = None, CR_Strategy = None):
        self.MSF = MSF
        self.ListOfStages = ListOfStages
        self.Verdict = Verdict(self.ListOfStages[-1])
        self.CL_InferentialTheory = CL_InferentialTheory
        self.CR_InferentialTheory = CR_InferentialTheory
        self.ICG = InferentialCommonGround(CL_InferentialTheory = self.CL_InferentialTheory,CR_InferentialTheory = self.CR_InferentialTheory)
        self.CL_Homogeneity = (len(self.ICG.ForMove) / len(self.CL_InferentialTheory.ForMove), len(self.ICG.AgainstMove) / len(self.CL_InferentialTheory.AgainstMove))
        self.CR_Homogeneity = (len(self.ICG.ForMove) / len(self.CR_InferentialTheory.ForMove), len(self.ICG.AgainstMove) / len(self.CR_InferentialTheory.AgainstMove))
        self.CL_Strategy = CL_Strategy
        self.CR_Strategy = CR_Strategy

    def table(self, NumRow):
        '''
        This method prints the table representation of an inquiry. It's not intended to be called, but rather as a common
        ground shared by .show() and .scrutinize().
        '''
        x = PrettyTable()
        x.field_names = ['TurnNum', 'Agent', 'TargetNum', 'PragSig', 'Move', 'CL_AC', 'CL_RC', 'CL_AE', 'CL_RE',
                         'CR_AC', 'CR_RC', 'CR_AE', 'CR_RE']
        first_stage_row(x, self.ListOfStages[0])
        for i in range(1, NumRow):
            stage_row(x, self.ListOfStages[i])
        print(x)

    def show_full_table(self):
        self.table(NumRow=len(self.ListOfStages))
        print()
        if self.Verdict == 'sustain':
            print('By the end of the inquiry, CL\'s proposed conclusion is sustained.')
        else:
            print('By the end of the inquiry, CL\'s proposed conclusion is rejected.')

        final_stage = self.ListOfStages[-1]

        common_ground = frozenset.intersection(final_stage.FScoreSit.CL.AC, final_stage.FScoreSit.CR.AC)

        print('The propositional common ground is', list(common_ground))

    def viewstage(self, stage):
        '''

        :param stage:
        :return:
        '''

        self.table(NumRow=stage + 1)
        # Print all available moves
        print('By the end of this stage, next player has the following',
              str(len(self.ListOfStages[stage].AvailableMove['for'])),
              'for-moves available:')
        avail_for = list()
        for i in self.ListOfStages[stage].AvailableMove['for']:
            avail_for.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        avail_for.sort()
        print(wrap_list(avail_for, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.ListOfStages[stage].AvailableMove['for']], items_per_line=5))

        print('By the end of this stage, next player has the following',
              str(len(self.ListOfStages[stage].AvailableMove['against'])),
              'against-moves available:')
        avail_against = list()
        for i in self.ListOfStages[stage].AvailableMove['against']:
            avail_against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        avail_against.sort()
        print(wrap_list(avail_against, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.ListOfStages[stage].AvailableMove['against']], items_per_line=5))

        # Verdict at this stage
        if stage == 0:
            print('By the end of this stage, CL\'s proposed conclusion is sustained.')
        else:
            if Verdict(self.ListOfStages[stage]) == 'sustain':
                print('By the end of this stage, CL\'s proposed conclusion is sustained.')
            else:
                print('By the end of this stage, CL\'s proposed conclusion is rejected.')

    def show(self, stage = 'unspecified'):

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CL\'s inferential theory contains', len(self.CL_InferentialTheory.ForMove),
              'reasons-for and', len(self.CL_InferentialTheory.AgainstMove), 'reasons-against.')

        print()
        print('The Reasons-for in CL\'s inferential theory are as follows:')
        CL_IF_For = list()
        for i in self.CL_InferentialTheory.ForMove:
            CL_IF_For.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        CL_IF_For.sort()
        print(wrap_list(CL_IF_For, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.CL_InferentialTheory.ForMove], items_per_line=5))

        print()
        print('The Reasons-against in CL\'s inferential theory are as follows:')
        CL_IF_Against = list()
        for i in self.CL_InferentialTheory.AgainstMove:
            CL_IF_Against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        CL_IF_Against.sort()
        print(wrap_list(CL_IF_Against, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.CL_InferentialTheory.AgainstMove], items_per_line=5))

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CR\'s inferential theory contains', len(self.CR_InferentialTheory.ForMove),
              'reasons-for and', len(self.CR_InferentialTheory.AgainstMove), 'reasons-against.')

        print()
        print('The Reasons-for in CR\'s inferential theory are as follows:')
        CR_IF_For = list()
        for i in self.CR_InferentialTheory.ForMove:
            CR_IF_For.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        CR_IF_For.sort()
        print(wrap_list(CR_IF_For, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.CR_InferentialTheory.ForMove], items_per_line=5))

        print()
        print('The Reasons-against in CR\'s inferential theory are as follows:')
        CR_IF_Against = list()
        for i in self.CR_InferentialTheory.AgainstMove:
            CR_IF_Against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        CR_IF_Against.sort()
        print(wrap_list(CR_IF_Against, items_per_line=5))
#        print(wrap_list([i.MoveLabel for i in self.CR_InferentialTheory.AgainstMove], items_per_line=5))

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, the inferential common ground contains', len(self.ICG.ForMove),
              'reasons-for and', len(self.ICG.AgainstMove), 'reasons-against.')

        print()
        print('The Reasons-for in the inferential common ground are as follows:')
        ICG_IF_For = list()
        for i in self.ICG.ForMove:
            ICG_IF_For.append(str(set(i.Prem)) + '⊨' + str(i.Conc))
        ICG_IF_For.sort()
        print(wrap_list(ICG_IF_For, items_per_line=5))

        print()
        print('The Reasons-against in the inferential common ground are as follows:')
        ICG_IF_Against = list()
        for i in self.ICG.AgainstMove:
            ICG_IF_Against.append(str(set(i.Prem)) + '#' + str(i.Conc))
        ICG_IF_Against.sort()
        print(wrap_list(ICG_IF_Against, items_per_line=5))

        print()

        cl_for_perc = str(round(self.CL_Homogeneity[0] * 100, 2))
        cl_agn_perc = str(round(self.CL_Homogeneity[1] * 100, 2))
        cr_for_perc = str(round(self.CR_Homogeneity[0] * 100, 2))
        cr_agn_perc = str(round(self.CR_Homogeneity[1] * 100, 2))

        print(cl_for_perc + "% of CL's reasons-for are common ground.", cl_agn_perc + "% of CL's reasons-against are common ground.")
        print(cr_for_perc + "% of CR's reasons-for are common ground.", cr_agn_perc + "% of CR's reasons-against are common ground.")

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        if stage == 'unspecified':
            self.show_full_table()

        elif isinstance(stage, int):
            self.viewstage(stage = stage)

        elif stage == 'all':
            for i in range(0, len(self.ListOfStages)):
                self.viewstage(stage = i)

        else:
            print('The parameter stage can be set to \'all\' or an integer. If set to be an integer, say 7,'
                  'the method will display the inquiry up to stage 7 and provide detailed information about stage 7. '
                  'If set to \'all\', it will do that for all stages in turn. '
                  'If left unspecified, it will display the entire inquiry. ')

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")



def InferentialCommonGround(CL_InferentialTheory, CR_InferentialTheory):
    return InferentialTheory(ForMove = frozenset.intersection(CL_InferentialTheory.ForMove, CR_InferentialTheory.ForMove),
                             AgainstMove = frozenset.intersection(CL_InferentialTheory.AgainstMove, CR_InferentialTheory.AgainstMove))


def InquiryFor(frame, target = 'random', proposal = 'undeclared', CL_strategy = 'random', CR_strategy = 'random',
               CL_InferentialTheory = 'undeclared', CR_InferentialTheory = 'undeclared'):
    if CL_InferentialTheory == 'undeclared':
        CL_InferentialTheory = UniverseOfReasons(frame)
    if CR_InferentialTheory == 'undeclared':
        CR_InferentialTheory = UniverseOfReasons(frame)
    # input conclusion as a string, e.g. 'a_2'
    if proposal != 'undeclared' and target != 'random':
        print('You can either specify proposal, of form ([1,2,3],4), or target, of form \'a_2\', but not both.')
    elif target != 'random':
        c = FirstMoveFor_RandomPremise(frame = frame, conclusion = target, CL_InferentialTheory = CL_InferentialTheory,
                                       CR_InferentialTheory = CR_InferentialTheory)
    elif proposal != 'undeclared':
        (a,b) = proposal
        c = ManualInitialMoveFor(frame = frame, proposal = (frozenset(a), b), CL_InferentialTheory = CL_InferentialTheory,
                                       CR_InferentialTheory = CR_InferentialTheory)
    else:
        c = RandomFirstMoveFor(frame = frame, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory)

    lst = [c]
    while c.AvailableMove['for'] != frozenset() or c.AvailableMove['against'] != frozenset():
        c = NextStage(laststage = c, CL_strategy = CL_strategy, CR_strategy = CR_strategy)
        lst.append(c)
    result = Inquiry(MSF = c.MSF, ListOfStages = lst, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory, CL_Strategy = CL_strategy, CR_Strategy = CR_strategy)
    return result


def InquiryAgainst(frame, target = 'random', proposal = 'undeclared', CL_strategy = 'random', CR_strategy = 'random',
               CL_InferentialTheory = 'undeclared', CR_InferentialTheory = 'undeclared'):
    if CL_InferentialTheory == 'undeclared':
        CL_InferentialTheory = UniverseOfReasons(frame)
    if CR_InferentialTheory == 'undeclared':
        CR_InferentialTheory = UniverseOfReasons(frame)
    # input conclusion as a string, e.g. 'a_2'
    if proposal != 'undeclared' and target != 'random':
        print('You can either specify proposal, of form ([1,2,3],4), or target, of form \'a_2\', but not both.')
    elif target != 'random':
        c = FirstMoveAgainst_RandomPremise(frame = frame, target = target, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)
    elif proposal != 'undeclared':
        (a,b) = proposal
        c = ManualInitialMoveAgainst(frame = frame, proposal = (frozenset(a), b), CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)
    else:
        c = RandomFirstMoveAgainst(frame = frame, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory)

    lst = [c]
    while c.AvailableMove['for'] != frozenset() or c.AvailableMove['against'] != frozenset():
        c = NextStage(laststage = c, CL_strategy = CL_strategy, CR_strategy = CR_strategy)
        lst.append(c)
    result = Inquiry(MSF = c.MSF, ListOfStages = lst, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory, CL_Strategy = CL_strategy, CR_Strategy = CR_strategy)
    return result


def InquiryFromStage(orig_inq, stage_num, next_stage = None, CL_strategy = None, CR_strategy = None):
    if not CL_strategy:
        CL_strategy = orig_inq.CL_Strategy
    if not CR_strategy:
        CR_strategy = orig_inq.CR_Strategy

    stage_list = orig_inq.ListOfStages[:stage_num]

    if next_stage:
        stage_list.append(next_stage)

    stage = stage_list[-1]

    while stage.AvailableMove['for'] != frozenset() or stage.AvailableMove['against'] != frozenset():
        stage = NextStage(laststage=stage, CL_strategy=CL_strategy, CR_strategy=CR_strategy)
        stage_list.append(stage)

    return Inquiry(MSF = stage.MSF, ListOfStages = stage_list, CL_InferentialTheory=orig_inq.CL_InferentialTheory, CR_InferentialTheory = orig_inq.CR_InferentialTheory, CL_Strategy = CL_strategy, CR_Strategy = CR_strategy)


