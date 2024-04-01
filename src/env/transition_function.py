""" define the outcomes of actions by agents at each time step in the environment
"""
import random
from env.score import Score, ScoreSit
from env.stage import Stage


EmptyScore_CL = Score('CL', frozenset(), frozenset(), frozenset(), frozenset())

EmptyScore_CR = Score('CR', frozenset(), frozenset(), frozenset(), frozenset())

Emptyscore_sit = ScoreSit(EmptyScore_CL, EmptyScore_CR)


##################
# actions arguing for a position
#################
def initial_move_for(frame, move, cl_inferential_theory, cr_inferential_theory):
    f_score = ScoreSit(Score(subject = 'CL', ac = frozenset.union(move.prem, frozenset([move.conc])),
                            rc = frozenset(), ae = frozenset.union(move.prem, frozenset([move.conc])),
                            re = frozenset()), EmptyScore_CR)
    scon = []
    if move not in cl_inferential_theory.for_move:
        print('The given first move is not in CL\'s Inferential Theory.')
    else:
        for i in move.prem:
            scon.append(('A', None, 'A', i))
        suff_con = [('A', move.prem, 'A', move.conc)] + scon
    # Here it's important to have scon second, instead of first.
        return Stage(msf = frame, turn_idx = 0, agent = 'CL', a_score_sit = Emptyscore_sit, target_move = None,
                     prag_sig = 'proposal', prime_move = move, f_score_sit = f_score, last_stage = None,
                     contro_set = frozenset([move.conc]), suff_con = suff_con, cl_inferential_theory = cl_inferential_theory,
                     cr_inferential_theory = cr_inferential_theory)


def manual_initial_move_for(frame, proposal, cl_inferential_theory, cr_inferential_theory):
    if proposal not in frame.imp:
        print('Not an eligible first reason-for move in this semantic frame')
    else:
        for m in frame.for_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason for':
                prime = m
                break
        if prime not in cl_inferential_theory.for_move:
            print('The proposal is not in the player\'s inferential theory.')
        else:
            return initial_move_for(frame = frame, move = prime, cl_inferential_theory = cl_inferential_theory,
                                  cr_inferential_theory = cr_inferential_theory)


def first_move_for(frame, premise, conclusion, cl_inferential_theory, cr_inferential_theory):
    proposal = (frozenset([frame.lang.index(s) for s in premise]), frame.lang.index(conclusion))
    return manual_initial_move_for(frame = frame, proposal = proposal, cl_inferential_theory = cl_inferential_theory,
                                  cr_inferential_theory = cr_inferential_theory)


def first_move_for_random_premise(frame, conclusion, cl_inferential_theory, cr_inferential_theory):
    # Input conclusion as a string, e.g. 'a_2'
    pool = []
    for i in frame.for_move:
        if i.conc == frame.lang.index(conclusion):
            pool.append(i)
    move = random.sample(frozenset.intersection(frozenset(pool), cl_inferential_theory.for_move), 1)[0]
    return initial_move_for(frame = frame, move = move, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def random_first_move_for(frame, cl_inferential_theory, cr_inferential_theory):
    # This function draws one move out of all for-moves arbitrarily. Notice for-moves may not be equally distributed
    # over all sentences. So some sentence is more likely to be defended than others by this function
    m = random.sample(cl_inferential_theory.for_move, 1)[0]
    return initial_move_for(frame = frame, move = m, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def random_first_move_for_random_conclusion(frame, cl_inferential_theory, cr_inferential_theory):
    # This function first randomly draws a conclusion to defend and then defend it with a randomly drawn move.
    # All sentences are equally likely to be defended by this function.
    conclusion = random.sample(frame.lang, 1)[0]
    return first_move_for_random_premise(frame = frame, conclusion = conclusion, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


##################
# actions arguing against a position
#################
def initial_move_against(frame, move, cl_inferential_theory, cr_inferential_theory):
    f_score = ScoreSit(Score('CL', move.prem, frozenset([move.conc]), move.prem, frozenset([move.conc])), EmptyScore_CR)
    scon = []
    if move not in cl_inferential_theory.against_move:
        print('The given first move is not in CL\'s Inferential Theory.')
    else:
        for i in move.prem:
            scon.append(('A', None, 'A', i))
        suff_con = [('A', move.prem, 'R', move.conc)] + scon
        return Stage(msf = frame, turn_idx = 0, agent = 'CL', cl_inferential_theory = cl_inferential_theory,
                     cr_inferential_theory = cr_inferential_theory, a_score_sit = Emptyscore_sit, target_move = None,
                     prag_sig = 'proposal', prime_move = move, f_score_sit = f_score, last_stage= None,
                     contro_set = frozenset([move.conc]), suff_con = suff_con)


def manual_initial_move_against(frame, proposal, cl_inferential_theory, cr_inferential_theory):
    if proposal[0] not in frame.EXC[proposal[1]]:
        print('Not an eligible first reason-against move in this semantic frame')
    else:
        for m in frame.against_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason against':
                prime = m
                break
        if prime not in cl_inferential_theory.against_move:
            print('The given first move is not in CL\'s Inferential Theory.')
        else:
            return initial_move_against(frame = frame, move = prime, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def first_move_against(frame, premise, target, cl_inferential_theory, cr_inferential_theory):
    proposal = (frozenset([frame.lang.index(s) for s in premise]), frame.lang.index(target))
    return manual_initial_move_against(frame = frame, proposal = proposal, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def first_move_against_random_premise(frame, target, cl_inferential_theory, cr_inferential_theory):
    pool = []
    for i in cl_inferential_theory.against_move:
        if i.conc == frame.lang.index(target):
            pool.append(i)
    move = random.sample(pool, 1)[0]
    return initial_move_against(frame = frame, move = move, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def random_first_move_against(frame, cl_inferential_theory, cr_inferential_theory):
    # This function draws one move out of all for-moves arbitrarily. Notice for-moves may not be equally distributed
    # over all sentences. So some sentence is more likely to be defended than others by this function
    m = random.sample(cl_inferential_theory.against_move, 1)[0]
    return initial_move_against(frame = frame, move = m, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)


def random_first_move_against_random_target(frame, cl_inferential_theory, cr_inferential_theory):
    # This function first randomly draws a target to argue against and then defend it with a randomly drawn move.
    # All sentences are equally likely to be defended by this function.
    target = random.sample(frame.lang, 1)[0]
    return first_move_against_random_premise(frame = frame, target = target, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)



