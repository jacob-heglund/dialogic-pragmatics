"""defines manual inquiry
"""

from stage import first_move_for_random_premise, first_move_against_random_premise, first_move_for, first_move_against, manual_next_stage, random_next_stage
from inquiry import Inquiry



def manual_inquiry_random_first_move(frame, val, target, cl_inferential_theory, cr_inferential_theory):
    if val == 'reason for':
        c = first_move_for_random_premise(frame = frame, conclusion = target, cl_inferential_theory = cl_inferential_theory,
                                       cr_inferential_theory = cr_inferential_theory)
    elif val == 'reason against':
        c = first_move_against_random_premise(frame = frame, target = target, cl_inferential_theory = cl_inferential_theory,
                          cr_inferential_theory = cr_inferential_theory)
    else:
        print('val must be either \'reason for\' or \'reason against\'.')
    lst = [c]
    return Inquiry(msf = frame, list_of_stages = lst, cl_inferential_theory = cl_inferential_theory, cr_inferential_theory = cr_inferential_theory)


def manual_inquiry_first_move(frame, premise, val, conclusion, cl_inferential_theory, cr_inferential_theory):
    if val == 'reason for':
        c = first_move_for(frame = frame, premise = premise, conclusion = conclusion, cl_inferential_theory = cl_inferential_theory,
                         cr_inferential_theory = cr_inferential_theory)
    elif val == 'reason against':
        c = first_move_against(frame = frame, premise = premise, target = conclusion, cl_inferential_theory = cl_inferential_theory,
                         cr_inferential_theory = cr_inferential_theory)
    else:
        print('input error')
    lst = [c]
    return Inquiry(msf = frame, list_of_stages = lst, cl_inferential_theory = cl_inferential_theory, cr_inferential_theory = cr_inferential_theory)

def manual_inquiry_completion_single(inq, targetnum, pragsig, proposal, val):
    last = inq.list_of_stages[-1]
    target = inq.list_of_stages[targetnum]
    s = manual_next_stage(last_stage = last, targetstage = target, pragsig = pragsig, proposal = proposal,
                        val = val)
    return Inquiry(msf = inq.msf, list_of_stages = inq.list_of_stages + [s], cl_inferential_theory = inq.cl_inferential_theory, cr_inferential_theory = inq.cr_inferential_theory)


def inquiry_completion(inq):
    lst = inq.list_of_stages
    c = lst[-1]
    while c.available_moves['for'] != frozenset() or c.available_moves['against'] != frozenset():
        c = random_next_stage(c)
        lst.append(c)
    result = Inquiry(msf = c.msf, list_of_stages = lst, cl_inferential_theory = inq.cl_inferential_theory, cr_inferential_theory = inq.cr_inferential_theory)
    return result

