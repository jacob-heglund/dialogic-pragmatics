""" defines an episode of an inquiry environment
"""


from prettytable import PrettyTable
from utils.utils import stage_row, first_stage_row, wrap_list
from agents.inferential_theory import InferentialTheory
from env.stage import verdict


class Inquiry:
    """ defines an inquiry environment where two agents ask for and give reasons against different sentences in a language
    """
    def __init__(self, msf, list_of_stages, cl_inferential_theory, cr_inferential_theory, cl_strategy = None, cr_strategy = None):
        self.msf = msf
        self.list_of_stages = list_of_stages
        self.verdict = verdict(self.list_of_stages[-1])
        self.cl_inferential_theory = cl_inferential_theory
        self.cr_inferential_theory = cr_inferential_theory
        self.icg = self._get_inferential_common_ground(cl_inferential_theory = self.cl_inferential_theory,cr_inferential_theory = self.cr_inferential_theory)
        self.cl_homogeneity = (len(self.icg.for_move) / len(self.cl_inferential_theory.for_move), len(self.icg.against_move) / len(self.cl_inferential_theory.against_move))
        self.cr_homogeneity = (len(self.icg.for_move) / len(self.cr_inferential_theory.for_move), len(self.icg.against_move) / len(self.cr_inferential_theory.against_move))
        self.cl_strategy = cl_strategy
        self.cr_strategy = cr_strategy

    def table(self, n_rows):
        '''
        This method prints the table representation of an inquiry. It's not intended to be called, but rather as a common
        ground shared by .show() and .scrutinize().
        '''
        x = PrettyTable()
        x.field_names = ['Turn', 'Agent', 'Target Num,', 'Prag. Significance', 'Move', 'CL_AC', 'CL_RC', 'CL_AE', 'CL_RE',
                         'CR_AC', 'CR_RC', 'CR_AE', 'CR_RE']
        first_stage_row(x, self.list_of_stages[0])
        for i in range(1, n_rows):
            stage_row(x, self.list_of_stages[i])
        print(x)

    def show_full_table(self):
        self.table(n_rows=len(self.list_of_stages))
        print()
        if self.verdict == 'sustain':
            print('By the end of the inquiry, CL\'s proposed conclusion is sustained.')
        else:
            print('By the end of the inquiry, CL\'s proposed conclusion is rejected.')

        final_stage = self.list_of_stages[-1]

        common_ground = frozenset.intersection(final_stage.f_score_sit.cl.ac, final_stage.f_score_sit.cr.ac)

        print('The propositional common ground is', list(common_ground))

    def view_stage(self, stage):
        '''

        :param stage:
        :return:
        '''

        self.table(n_rows=stage + 1)
        # Print all available moves
        print('By the end of this stage, next player has the following',
              str(len(self.list_of_stages[stage].available_moves['for'])),
              'for-moves available:')
        avail_for = []
        for i in self.list_of_stages[stage].available_moves['for']:
            avail_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        avail_for.sort()
        print(wrap_list(avail_for, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.list_of_stages[stage].available_moves['for']], items_per_line=5))

        print('By the end of this stage, next player has the following',
              str(len(self.list_of_stages[stage].available_moves['against'])),
              'against-moves available:')
        avail_against = []
        for i in self.list_of_stages[stage].available_moves['against']:
            avail_against.append(str(set(i.prem)) + '#' + str(i.conc))
        avail_against.sort()
        print(wrap_list(avail_against, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.list_of_stages[stage].available_moves['against']], items_per_line=5))

        # verdict at this stage
        if stage == 0:
            print('By the end of this stage, CL\'s proposed conclusion is sustained.')
        else:
            if verdict(self.list_of_stages[stage]) == 'sustain':
                print('By the end of this stage, CL\'s proposed conclusion is sustained.')
            else:
                print('By the end of this stage, CL\'s proposed conclusion is rejected.')

    def show(self, stage = 'unspecified'):

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CL\'s inferential theory contains', len(self.cl_inferential_theory.for_move),
              'reasons-for and', len(self.cl_inferential_theory.against_move), 'reasons-against.')

        print()
        print('The Reasons-for in CL\'s inferential theory are as follows:')
        cl_if_for = []
        for i in self.cl_inferential_theory.for_move:
            cl_if_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        cl_if_for.sort()
        print(wrap_list(cl_if_for, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.cl_inferential_theory.for_move], items_per_line=5))

        print()
        print('The Reasons-against in CL\'s inferential theory are as follows:')
        cl_if_against = []
        for i in self.cl_inferential_theory.against_move:
            cl_if_against.append(str(set(i.prem)) + '#' + str(i.conc))
        cl_if_against.sort()
        print(wrap_list(cl_if_against, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.cl_inferential_theory.against_move], items_per_line=5))

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CR\'s inferential theory contains', len(self.cr_inferential_theory.for_move),
              'reasons-for and', len(self.cr_inferential_theory.against_move), 'reasons-against.')

        print()
        print('The Reasons-for in CR\'s inferential theory are as follows:')
        cr_if_for = []
        for i in self.cr_inferential_theory.for_move:
            cr_if_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        cr_if_for.sort()
        print(wrap_list(cr_if_for, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.cr_inferential_theory.for_move], items_per_line=5))

        print()
        print('The Reasons-against in CR\'s inferential theory are as follows:')
        cr_if_against = []
        for i in self.cr_inferential_theory.against_move:
            cr_if_against.append(str(set(i.prem)) + '#' + str(i.conc))
        cr_if_against.sort()
        print(wrap_list(cr_if_against, items_per_line=5))
        # print(wrap_list([i.move_label for i in self.cr_inferential_theory.against_move], items_per_line=5))

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, the inferential common ground contains', len(self.icg.for_move),
              'reasons-for and', len(self.icg.against_move), 'reasons-against.')

        print()
        print('The Reasons-for in the inferential common ground are as follows:')
        icg_if_for = []
        for i in self.icg.for_move:
            icg_if_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        icg_if_for.sort()
        print(wrap_list(icg_if_for, items_per_line=5))

        print()
        print('The Reasons-against in the inferential common ground are as follows:')
        icg_if_against = []
        for i in self.icg.against_move:
            icg_if_against.append(str(set(i.prem)) + '#' + str(i.conc))
        icg_if_against.sort()
        print(wrap_list(icg_if_against, items_per_line=5))

        print()

        cl_for_perc = str(round(self.cl_homogeneity[0] * 100, 2))
        cl_agn_perc = str(round(self.cl_homogeneity[1] * 100, 2))
        cr_for_perc = str(round(self.cr_homogeneity[0] * 100, 2))
        cr_agn_perc = str(round(self.cr_homogeneity[1] * 100, 2))

        print(cl_for_perc + "% of CL's reasons-for are common ground.", cl_agn_perc + "% of CL's reasons-against are common ground.")
        print(cr_for_perc + "% of CR's reasons-for are common ground.", cr_agn_perc + "% of CR's reasons-against are common ground.")

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        if stage == 'unspecified':
            self.show_full_table()

        elif isinstance(stage, int):
            self.view_stage(stage = stage)

        elif stage == 'all':
            for i in range(0, len(self.list_of_stages)):
                self.view_stage(stage = i)

        else:
            print('The parameter stage can be set to \'all\' or an integer. If set to be an integer, say 7,'
                  'the method will display the inquiry up to stage 7 and provide detailed information about stage 7. '
                  'If set to \'all\', it will do that for all stages in turn. '
                  'If left unspecified, it will display the entire inquiry. ')

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    def _get_inferential_common_ground(self, cl_inferential_theory, cr_inferential_theory):
        return InferentialTheory(for_move = frozenset.intersection(cl_inferential_theory.for_move, cr_inferential_theory.for_move), against_move = frozenset.intersection(cl_inferential_theory.against_move, cr_inferential_theory.against_move))
