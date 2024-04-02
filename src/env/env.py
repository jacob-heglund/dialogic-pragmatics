""" defines agent inquiry capabilities
"""

from prettytable import PrettyTable
from utils.utils import wrap_list
from utils.env_utils import get_verdict
from agents.msf import MSF, random_msf
from agents.move import MoveType
from agents.inferential_theory import InferentialTheory
from agents.agent import Agent
from env.score import Score, ScoreSit
from env.stage import Stage, initial_next_stage_2


import pdb


class Environment:
    def __init__(self,
                language: list,
                target: str = "random",
                proposal: str = "undeclared",
                goal: str = "argue_for",
                cl_inferential_theory_name: str = "default",
                cr_inferential_theory_name: str = "default",
                cl_policy_name: str = "one_step_ahead",
                cr_policy_name: str = "minimize_ac",
                ):

        # build env goals
        self.target = target
        self.proposal = proposal
        self.goal = goal
        self._check_valid_goal()

        # build language
        self.language = language
        self.msf = None
        self._build_msf()

        # build agents
        self.cl_inferential_theory_name = cl_inferential_theory_name
        self.cr_inferential_theory_name = cr_inferential_theory_name
        self.cl_policy_name = cl_policy_name
        self.cr_policy_name = cr_policy_name
        self.cl_agent = None
        self.cr_agent = None
        self.icg = None
        self.cl_homogeneity = None
        self.cr_homogeneity = None
        self._build_agents()

        self.empty_score_cl = Score('CL', frozenset(), frozenset(), frozenset(), frozenset())
        self.empty_score_cr = Score('CR', frozenset(), frozenset(), frozenset(), frozenset())
        self.empty_score_sit = ScoreSit(self.empty_score_cl, self.empty_score_cr)


        # build stuff to track progress in the env
        self.stage_idx = None
        self.stage_list = None
        self.stage_verdict_list = None
        self.reset()

    def _build_msf(self):
        self.msf = random_msf(language=self.language)

    def _build_agents(self):
        self.cl_agent = Agent(self.msf, policy_name=self.cl_policy_name, inferential_theory_name=self.cl_inferential_theory_name, target=self.target, proposal=self.proposal, goal=self.goal)
        self.cr_agent = Agent(self.msf, policy_name=self.cr_policy_name, inferential_theory_name=self.cr_inferential_theory_name, target=self.target, proposal=self.proposal, goal=self.goal)

        self.icg = self._get_inferential_common_ground(
            cl_inferential_theory=self.cl_agent.inferential_theory,
            cr_inferential_theory=self.cr_agent.inferential_theory)

        self.cl_homogeneity = self._get_homogeneity(self.cl_agent.inferential_theory)
        self.cr_homogeneity = self._get_homogeneity(self.cr_agent.inferential_theory)

    def _check_valid_goal(self):
        valid_goals = ["argue_for", "argue_against"]
        if self.goal not in valid_goals:
            raise ValueError(f"Error: Goal must be one of {valid_goals}.")

    def _get_inferential_common_ground(self, cl_inferential_theory, cr_inferential_theory):
        for_move = frozenset.intersection(cl_inferential_theory.for_move, cr_inferential_theory.for_move)
        against_move = frozenset.intersection(cl_inferential_theory.against_move, cr_inferential_theory.against_move)
        return InferentialTheory(for_move=for_move, against_move=against_move)

    def _get_homogeneity(self, inferential_theory):
        for_move_homogeneity = len(self.icg.for_move) / len(inferential_theory.for_move)
        against_move_homogeneity = len(self.icg.against_move) / len(inferential_theory.against_move)
        return (for_move_homogeneity, against_move_homogeneity)

    def reset(self):
        """resets the environment to prepare to run a new episode
        """
        self.stage_idx = 0
        self.stage_list = []
        self.stage_verdict_list = []

    def step(self, move: MoveType = None) -> None:
        """defines a single step of the environment
        """
        if len(self.stage_list) == 0:
            next_stage = self._first_step(self.msf, move, self.cl_agent.inferential_theory,
                                          self.cr_agent.inferential_theory, self.goal)

        else:
            next_stage = self._step(prime=move)

        self.stage_list.append(next_stage)
        self.stage_verdict_list.append(self._get_verdict(next_stage))
        done = self._get_done_status()

        self.stage_idx += 1
        return next_stage, done

    def _first_step(self, frame: MSF, move: MoveType, cl_inferential_theory: InferentialTheory,
                    cr_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for") -> Stage:
        """env transition function for the first step of the environment

        Args:
            frame (MSF): material semantic frame
            move (MoveType) the move made by an agent
            cl_inferential_theory (InferentialTheory): inferential theory for the CL agent
            cr_inferential_theory (InferentialTheory): _description_
            argue_for_or_against (str, optional): _description_. Defaults to "argue_for".

        Returns:
            Stage: _description_
        """

        if argue_for_or_against == "argue_for":
            f_score = ScoreSit(Score(subject = 'CL', ac = frozenset.union(move.prem, frozenset([move.conc])),
                            rc = frozenset(), ae = frozenset.union(move.prem, frozenset([move.conc])),
                            re = frozenset()), self.empty_score_cr)
            suff_con_prefix = [('A', move.prem, 'A', move.conc)]
            move_set = cl_inferential_theory.for_move

        elif argue_for_or_against == "against":
            f_score = ScoreSit(Score('CL', move.prem, frozenset([move.conc]), move.prem, frozenset([move.conc])), self.empty_score_cr)
            suff_con_prefix = [('A', move.prem, 'R', move.conc)]
            move_set = cl_inferential_theory.against_move

        scon = []
        if move not in move_set:
            print('The given first move is not in CL\'s Inferential Theory.')
        else:
            for i in move.prem:
                scon.append(('A', move.prem, 'A', i))

            # Here it's important to have scon second, instead of first.
            suff_con = suff_con_prefix + scon

        next_stage = Stage(msf=frame, turn_idx=self.stage_idx, agent='CL', a_score_sit=self.empty_score_sit, target_move=None,
                    prag_sig='proposal', prime_move=move, f_score_sit=f_score, prev_stage=None,
                    contro_set=frozenset([move.conc]), suff_con=suff_con,
                    cl_inferential_theory=cl_inferential_theory, cr_inferential_theory=cr_inferential_theory)

        return next_stage

    def _step(self, prime):
        """env transition function for all steps other than the first in the env
        """
        prev_stage = self.stage_list[-1]
        next_stage = initial_next_stage_2(stage=prev_stage, prime=prime)

        return next_stage

    def get_curr_agent(self, prev_stage):
        if self.stage_idx == 0:
            agent = self.cl_agent
        else:
            if prev_stage.agent == 'CL':
                # CR agent takes the next action
                agent = self.cr_agent
            elif prev_stage.agent == 'CR':
                # CL agent takes the next action
                agent = self.cl_agent

        return agent

    def _get_verdict(self, stage):
        if self.stage_idx == 0:
            val = None
        else:
            val = get_verdict(stage)
        return val

    def _get_done_status(self) -> bool:
        """episode is done when both of the sets of moves are empty
        """
        if self.stage_idx == 0:
            # episode cannot be done after the first stage since only one agent has had a chance to
            # make a move
            done = False
        else:
            no_more_for_moves = self.stage_list[-1].available_moves['for'] == frozenset()
            no_more_against_moves = self.stage_list[-1].available_moves['against'] == frozenset()
            done = bool(no_more_for_moves and no_more_against_moves)

        return done

    def show_full_table(self):
        self._print_table(n_rows=len(self.stage_list))
        if self.stage_verdict_list[-1] == 'sustain':
            print('By the end of the inquiry, CL\'s proposed conclusion is sustained.')
        else:
            print('By the end of the inquiry, CL\'s proposed conclusion is rejected.')

        final_stage = self.stage_list[-1]

        common_ground = frozenset.intersection(final_stage.f_score_sit.cl.ac, final_stage.f_score_sit.cr.ac)

        print('The propositional common ground is', list(common_ground))

    def view_stage(self, stage_idx):
        '''

        :param stage:
        :return:
        '''

        self._print_table(n_rows=stage_idx + 1)
        # Print all available moves
        print('By the end of this stage, next player has the following',
              str(len(self.stage_list[stage_idx].available_moves['for'])),
              'for-moves available:')
        avail_for = []
        for i in self.stage_list[stage_idx].available_moves['for']:
            avail_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        avail_for.sort()
        print(wrap_list(avail_for, items_per_line=5))

        print('By the end of this stage, next player has the following',
              str(len(self.stage_list[stage_idx].available_moves['against'])),
              'against-moves available:')
        avail_against = []
        for i in self.stage_list[stage_idx].available_moves['against']:
            avail_against.append(str(set(i.prem)) + '#' + str(i.conc))
        avail_against.sort()
        print(wrap_list(avail_against, items_per_line=5))

        # verdict at this stage
        if stage_idx == 0:
            print('By the end of this stage, CL\'s proposed conclusion is sustained.')
        else:
            if self.stage_verdict_list[stage_idx] == 'sustain':
                print('By the end of this stage, CL\'s proposed conclusion is sustained.')
            else:
                print('By the end of this stage, CL\'s proposed conclusion is rejected.')

    def show(self, stage = 'unspecified'):

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Beginning of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CL\'s inferential theory contains', len(self.cl_agent.inferential_theory.for_move),
              'reasons-for and', len(self.cl_agent.inferential_theory.against_move), 'reasons-against.')

        print()
        print('The Reasons-for in CL\'s inferential theory are as follows:')
        cl_if_for = []
        for i in self.cl_agent.inferential_theory.for_move:
            cl_if_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        cl_if_for.sort()
        print(wrap_list(cl_if_for, items_per_line=5))

        print()
        print('The Reasons-against in CL\'s inferential theory are as follows:')
        cl_if_against = []
        for i in self.cl_agent.inferential_theory.against_move:
            cl_if_against.append(str(set(i.prem)) + '#' + str(i.conc))
        cl_if_against.sort()
        print(wrap_list(cl_if_against, items_per_line=5))

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print()

        print('In this inquiry, CR\'s inferential theory contains', len(self.cr_agent.inferential_theory.for_move),
              'reasons-for and', len(self.cr_agent.inferential_theory.against_move), 'reasons-against.')

        print()
        print('The Reasons-for in CR\'s inferential theory are as follows:')
        cr_if_for = []
        for i in self.cr_agent.inferential_theory.for_move:
            cr_if_for.append(str(set(i.prem)) + '⊨' + str(i.conc))
        cr_if_for.sort()
        print(wrap_list(cr_if_for, items_per_line=5))

        print()
        print('The Reasons-against in CR\'s inferential theory are as follows:')
        cr_if_against = []
        for i in self.cr_agent.inferential_theory.against_move:
            cr_if_against.append(str(set(i.prem)) + '#' + str(i.conc))
        cr_if_against.sort()
        print(wrap_list(cr_if_against, items_per_line=5))

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
            self.view_stage(stage_idx=stage)

        elif stage == 'all':
            for i in range(0, len(self.stage_list)):
                self.view_stage(stage_idx=i)

        else:
            print('The parameter stage can be set to \'all\' or an integer. If set to be an integer, say 7,'
                  'the method will display the inquiry up to stage 7 and provide detailed information about stage 7. '
                  'If set to \'all\', it will do that for all stages in turn. '
                  'If left unspecified, it will display the entire inquiry. ')

        print()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^End of an inquiry display^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    def _print_table(self, n_rows):
        '''
        Prints a table representation of an episode
        '''
        x = PrettyTable()
        x.field_names = ['Turn', 'Agent', 'Target Num', 'Prag. Significance', 'Move',
                        'CL_AC', 'CL_RC', 'CL_AE', 'CL_RE',
                        'CR_AC', 'CR_RC', 'CR_AE', 'CR_RE']

        for i in range(n_rows):
            self._stage_row(x, self.stage_list[i])

        print(x)

    def _stage_row(self, x, stage):
        """ Used  to display stages except the first stage. """
        row = [
            stage.turn_idx,
            stage.agent,
            None,
            stage.prag_sig,
            stage.prime_move.move_label,
            list(stage.f_score_sit.cl.ac),
            list(stage.f_score_sit.cl.rc),
            list(stage.f_score_sit.cl.ae),
            list(stage.f_score_sit.cl.re),
            list(stage.f_score_sit.cr.ac),
            list(stage.f_score_sit.cr.rc),
            list(stage.f_score_sit.cr.ae),
            list(stage.f_score_sit.cr.re)
        ]
        if stage.target_move is not None:
            row[2] = stage.target_move.turn_idx
        x.add_row(row)


def inquiry_from_stage(orig_inq, stage_num, next_stage_flag = None, cl_policy = None, cr_policy = None):
    if not cl_policy:
        cl_policy = orig_inq.cl_policy
    if not cr_policy:
        cr_policy = orig_inq.cr_policy

    stage_list = orig_inq.stage_list[:stage_num]

    if next_stage_flag:
        stage_list.append(next_stage_flag)

    stage = stage_list[-1]

    while stage.available_moves['for'] != frozenset() or stage.available_moves['against'] != frozenset():
        stage = next_stage_flag(prev_stage=stage, cl_policy=cl_policy, cr_policy=cr_policy)
        stage_list.append(stage)

    return Environment(msf = stage.msf, stage_list = stage_list, cl_inferential_theory=orig_inq.cl_inferential_theory, cr_inferential_theory = orig_inq.cr_inferential_theory, cl_policy = cl_policy, cr_policy = cr_policy)

