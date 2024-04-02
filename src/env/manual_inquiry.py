"""defines manual inquiry
"""

from agents.agent import first_move_manual_inquiry, first_move_for_random_premise, first_move_against_random_premise
from env.env import Environment
from env.stage import manual_next_stage, random_next_stage


def manual_inquiry_random_first_move(frame, val, target, cl_inferential_theory, cr_inferential_theory):
    if val == 'reason for':
        c = first_move_for_random_premise(frame=frame, conclusion=target, cl_inferential_theory = cl_inferential_theory,
                                       cr_inferential_theory = cr_inferential_theory)
    elif val == 'reason against':
        c = first_move_against_random_premise(frame=frame, target = target, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)
    else:
        print('val must be either \'reason for\' or \'reason against\'.')
    lst = [c]
    return Environment(msf = frame, stage_list = lst, cl_inferential_theory = cl_inferential_theory, cr_inferential_theory = cr_inferential_theory)


def manual_inquiry_first_move(frame, premise, val, conclusion, cl_inferential_theory, cr_inferential_theory):
    if val == 'reason for':
        argue_for_or_against = "argue_for"
    elif val == 'reason against':
        argue_for_or_against = "argue_against"
    else:
        print('input error')
    c = first_move_manual_inquiry(frame=frame, premise=premise, conclusion=conclusion, cl_inferential_theory=cl_inferential_theory,
                        cr_inferential_theory=cr_inferential_theory, argue_for_or_against=argue_for_or_against)
    lst = [c]
    return Environment(msf = frame, stage_list = lst, cl_inferential_theory = cl_inferential_theory, cr_inferential_theory = cr_inferential_theory)

def manual_inquiry_completion_single(inq, targetnum, prag_sig, proposal, val):
    last = inq.stage_list[-1]
    target = inq.stage_list[targetnum]
    s = manual_next_stage(prev_stage = last, target_stage = target, prag_sig = prag_sig, proposal = proposal,
                        val = val)
    return Environment(msf = inq.msf, stage_list = inq.stage_list + [s], cl_inferential_theory = inq.cl_inferential_theory, cr_inferential_theory = inq.cr_inferential_theory)


def inquiry_completion(inq):
    lst = inq.stage_list
    c = lst[-1]
    while c.available_moves['for'] != frozenset() or c.available_moves['against'] != frozenset():
        c = random_next_stage(c)
        lst.append(c)
    result = Environment(msf = c.msf, stage_list = lst, cl_inferential_theory = inq.cl_inferential_theory, cr_inferential_theory = inq.cr_inferential_theory)
    return result

