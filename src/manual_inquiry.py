"""defines manual inquiry
"""

from stage import FirstMoveFor_RandomPremise, FirstMoveAgainst_RandomPremise, FirstMoveFor, FirstMoveAgainst, ManualNextStage, RandomNextStage
from inquiry import Inquiry



def ManualInquiry_RandomFirstMove(frame, val, target, CL_InferentialTheory, CR_InferentialTheory):
    if val == 'reason for':
        c = FirstMoveFor_RandomPremise(frame = frame, conclusion = target, CL_InferentialTheory = CL_InferentialTheory,
                                       CR_InferentialTheory = CR_InferentialTheory)
    elif val == 'reason against':
        c = FirstMoveAgainst_RandomPremise(frame = frame, target = target, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)
    else:
        print('val must be either \'reason for\' or \'reason against\'.')
    lst = [c]
    return Inquiry(MSF = frame, ListOfStages = lst, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory)


def ManualInquiry_FirstMove(frame, premise, val, conclusion, CL_InferentialTheory, CR_InferentialTheory):
    if val == 'reason for':
        c = FirstMoveFor(frame = frame, premise = premise, conclusion = conclusion, CL_InferentialTheory = CL_InferentialTheory,
                         CR_InferentialTheory = CR_InferentialTheory)
    elif val == 'reason against':
        c = FirstMoveAgainst(frame = frame, premise = premise, target = conclusion, CL_InferentialTheory = CL_InferentialTheory,
                         CR_InferentialTheory = CR_InferentialTheory)
    else:
        print('input error')
    lst = [c]
    return Inquiry(MSF = frame, ListOfStages = lst, CL_InferentialTheory = CL_InferentialTheory, CR_InferentialTheory = CR_InferentialTheory)

def ManualInquiry_Completion_Single(inq, targetnum, pragsig, proposal, val):
    last = inq.ListOfStages[-1]
    target = inq.ListOfStages[targetnum]
    s = ManualNextStage(last_stage = last, targetstage = target, pragsig = pragsig, proposal = proposal,
                        val = val)
    return Inquiry(MSF = inq.MSF, ListOfStages = inq.ListOfStages + [s], CL_InferentialTheory = inq.CL_InferentialTheory, CR_InferentialTheory = inq.CR_InferentialTheory)


def Inquiry_Completion(inq):
    lst = inq.ListOfStages
    c = lst[-1]
    while c.AvailableMove['for'] != frozenset() or c.AvailableMove['against'] != frozenset():
        c = RandomNextStage(c)
        lst.append(c)
    result = Inquiry(MSF = c.MSF, ListOfStages = lst, CL_InferentialTheory = inq.CL_InferentialTheory, CR_InferentialTheory = inq.CR_InferentialTheory)
    return result

