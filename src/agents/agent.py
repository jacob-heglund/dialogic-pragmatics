""" define the agents and their logic for taking action in the environment
"""
import random

from utils.env_utils import get_verdict
from agents.inferential_theory import InferentialTheory, random_inferential_theory_generator
from agents.move import MoveType
from agents.msf import MSF
from env.stage import Stage, initial_next_stage_2

import pdb



class Agent():
    """
    class for an action-taking agent
    """
    def __init__(self, msf, policy_name="random", inferential_theory_name="random", target="random", proposal="undeclared", goal="argue_for") -> None:
        self.msf = msf
        self.valid_policy_names = ["random", "minimize_ac", "one_step_ahead"]
        if policy_name in self.valid_policy_names:
            self.policy_name = policy_name
        else:
            raise ValueError(f"Error: Agent policy must be one of {self.valid_policy_names}.")

        self.valid_inferential_theory_names = ["default", "random"]
        self.inferential_theory_name = inferential_theory_name
        self.inferential_theory = None
        self._build_inferential_theory()

        self.target = target
        self.proposal = proposal
        self.goal = goal

    def _build_inferential_theory(self):
        if self.inferential_theory_name == "default":
            self.inferential_theory = InferentialTheory(self.msf.for_move, self.msf.against_move)

        elif self.inferential_theory_name == "random":
            self.inferential_theory = random_inferential_theory_generator(msf=self.msf, for_move_size="random", against_move_size="random", for_move_chance=0.5, against_move_chance=0.5)

        else:
            raise ValueError(f"Error: Inferential theory must be one of {self.valid_inferential_theory_names}.")

    def get_action(self, stage=None) -> MoveType:
        if stage == None:
            action = self._get_first_action()
        else:
            action = self._get_action(stage)
        return action

    def _get_first_action(self) -> MoveType:
        # take first action in the env
        if self.target != 'random':
            move = self._first_move_random_premise(frame=self.msf, statement=self.target,
                                            cl_inferential_theory=self.inferential_theory,
                                            argue_for_or_against=self.goal)
        elif self.proposal != 'undeclared':
            (a,b) = self.proposal
            move = self._first_move_manual_move(frame=self.msf, proposal=(frozenset(a), b),
                                        cl_inferential_theory=self.inferential_theory,
                                        argue_for_or_against=self.goal)
        else:
            move = self._first_move_random_move(cl_inferential_theory=self.inferential_theory,
                                        argue_for_or_against=self.goal)

        return move

    def _first_move_random_premise(self, frame: MSF, statement: str, cl_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for"):
        """ given an input statement, selects a random valid move to make
        """
        # Input statement as a string, e.g. 'a_2'
        if argue_for_or_against == "argue_for":
            move_set = frame.for_move
        elif argue_for_or_against == "argue_against":
            move_set = cl_inferential_theory.against_move

        pool = []
        for i in move_set:
            if i.conc == frame.lang.index(statement):
                pool.append(i)

        if argue_for_or_against == "argue_for":
            move_sample_set = frozenset.intersection(frozenset(pool), cl_inferential_theory.for_move)
        elif argue_for_or_against == "argue_against":
            move_sample_set = pool

        move = random.sample(move_sample_set, 1)[0]
        return move

    def _first_move_random_move(self, cl_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for"):
        # Uniforn random sample of one for-move. For-moves may not be equally distributed
        # over all sentences, so some sentences are more likely to be defended than others by this function
        if argue_for_or_against == "argue_for":
            move_set = cl_inferential_theory.for_move
        elif argue_for_or_against == "argue_against":
            move_set = cl_inferential_theory.against_move

        move = random.sample(move_set, 1)[0]
        return move

    def _first_move_manual_move(self, frame: MSF, proposal: tuple, cl_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for"):
        if argue_for_or_against == "argue_for":
            statement = proposal
            valid_first_move_set = frame.imp
            frame_move_set = frame.for_move
            move_val = "reason for"
            agent_move_set = cl_inferential_theory.for_move

        elif argue_for_or_against == "argue_against":
            statement = proposal[0]
            valid_first_move_set = frame.exc[proposal[1]]
            frame_move_set = frame.against_move
            move_val = "reason against"
            agent_move_set = cl_inferential_theory.against_move

        if statement not in valid_first_move_set:
            print('Not an eligible first reason-for move in this semantic frame')
        else:
            for m in frame_move_set:
                if (m.prem == proposal[0]) and (m.conc == proposal[1]) and (m.val == move_val):
                    prime = m
                    break
            if prime not in agent_move_set:
                print('The proposal is not in the current agent\'s inferential theory.')
            else:
                return prime

    def _first_move_random_move_random_conclusion(self, frame: MSF, cl_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for"):
        # This function first randomly draws a statement to argue for or against (depending on argue_for_or_against), then defend it with a randomly drawn move.
        # All sentences are equally likely to be defended by this function.
        conclusion = random.sample(frame.lang, 1)[0]
        return self._first_move_random_premise(frame=frame, statement=conclusion, cl_inferential_theory=cl_inferential_theory,
                                        argue_for_or_against=argue_for_or_against)

    def first_move_manual_inquiry(self, frame: MSF, premise, conclusion, cl_inferential_theory: InferentialTheory, argue_for_or_against: str ="argue_for"):
        proposal = (frozenset([frame.lang.index(s) for s in premise]), frame.lang.index(conclusion))
        return self._first_move_manual_move(frame=frame, proposal = proposal, cl_inferential_theory=cl_inferential_theory,
                                    argue_for_or_against=argue_for_or_against)

    def _get_action(self, prev_stage: Stage) -> MoveType:
        if self.policy_name == 'random':
            move = self._random_next_stage(stage=prev_stage)
        elif self.policy_name == 'minimize_ac':
            move = self._minimize_ac_next_stage(stage=prev_stage)
        elif self.policy_name == 'one_step_ahead':
            move = self._one_step_ahead_next_stage(stage=prev_stage)
        else:
            print('Error: Currently, CL and CR have only three strategies: \'random\', \'minimize_ac\' and \'one_step_ahead\'.')

        return move

    def _random_next_stage(self, stage):
        moves = frozenset.union(stage.available_moves['for'], stage.available_moves['against'])
        prime = random.sample(moves, 1)[0]
        return prime

    def _minimize_ac_next_stage(self, stage):
        moves = frozenset.union(stage.available_moves['for'], stage.available_moves['against'])
        lst_new_ac_length = set()
        pool = []
        for i in moves:
            lst_new_ac_length.add(len(self._get_new_commitment(i, stage)[0]))
        min_new_ac_length = min(lst_new_ac_length)
        for i in moves:
            if len(self._get_new_commitment(i,stage)[0]) == min_new_ac_length:
                pool.append(i)

        prime = random.sample(frozenset(pool), 1)[0]
        return prime

    def _get_new_commitment(self, move, prev_stage):
        # Computing what the move is grossly adding.
        if move.val == 'reason for':
            gross_new_ac = frozenset.union(move.prem, frozenset([move.conc]))
            gross_new_rc = frozenset()
        if move.val == 'reason against':
            gross_new_ac = move.prem
            gross_new_rc = frozenset([move.conc])

        # Computing the move's net new commitments.
        if prev_stage.agent == 'CL':
            new_ac = gross_new_ac - prev_stage.f_score_sit.cr.ac
            new_rc = gross_new_rc - prev_stage.f_score_sit.cr.rc

        if prev_stage.agent == 'CR':
            new_ac = gross_new_ac - prev_stage.f_score_sit.cl.ac
            new_rc = gross_new_rc - prev_stage.f_score_sit.cl.rc

        return (new_ac, new_rc)

    def _one_step_ahead_next_stage(self, stage):
        moves = frozenset.union(stage.available_moves['for'], stage.available_moves['against'])
        pool = []

        for i in moves:
            #Case for CL
            if stage.agent == 'CL':
                if get_verdict(initial_next_stage_2(stage = stage, prime = i)) == 'fail':
                    pool.append(i)
            #Case for CR
            else:
                if get_verdict(initial_next_stage_2(stage = stage, prime = i)) == 'sustain':
                    pool.append(i)

        if len(pool) != 0:
            prime = random.sample(frozenset(pool), 1)[0]
        else:
            prime = random.sample(frozenset(moves), 1)[0]
        return prime



