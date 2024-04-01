""" defines the CT closure operations
"""

from msf import ExFF_closure, MSF
from cm_closure import CM_IMP_closure, CM_IMP_closure_once, CM_INC_closure, CM_INC_closure_once, msf_CM_full_closure, msf_CM_full_closure_once

def CT_IMP_closure_once(input_IMP):
    new_imp = list()
    for i in input_IMP:
        for j in input_IMP:
            if j[0] == frozenset.union(i[0], frozenset([i[1]])):
                new_imp.append((i[0], j[1]))
    output_IMP = frozenset.union(input_IMP, frozenset(new_imp))
    return output_IMP


def CT_IMP_closure(input_IMP):
    result = CT_IMP_closure_once(input_IMP)
    while len(result) != len(CT_IMP_closure_once(result)):
        result = CT_IMP_closure_once(result)
    return result


def CT_INC_closure_once(input_IMP, input_INC):
    new_inc = list()
    for i in input_IMP:
        if frozenset.union(i[0], frozenset([i[1]])) in input_INC:
            new_inc.append(i[0])
    output_INC = frozenset.union(input_INC, frozenset(new_inc))
    return output_INC


def CT_INC_closure(input_IMP, input_INC):
    result = CT_INC_closure_once(input_IMP, input_INC)
    while len(result) != len(CT_INC_closure_once(input_IMP, result)):
        result = CT_INC_closure_once(input_IMP, result)
    return result


def msf_CT_full_closure_once(frame):
    ct_imp_first_time = CT_IMP_closure(frame.IMP)
    ct_inc_first_time = CT_INC_closure_once(ct_imp_first_time, frame.INC)
    exff_imp_first_time = ExFF_closure(language= frame.L, imp= ct_imp_first_time, inc= ct_inc_first_time)
    return MSF(L = frame.L, IMP = exff_imp_first_time, INC = ct_inc_first_time)


def msf_CT_full_closure(frame):
    result = msf_CT_full_closure_once(frame)
    while len(result.IMP) != len(msf_CT_full_closure_once(result).IMP) or len(result.INC) != len(msf_CT_full_closure_once(result).INC):
        result = msf_CT_full_closure_once(result)
    return result


def UNUSED_MSF_closure(frame, close_under, times = 1):
    '''

    :param frame:
    :param close_under:
    :param times:
    :return:
    '''
    if times == 'full':
        if close_under == 'cm_imp':
            return MSF(L = frame.L, IMP = CM_IMP_closure(frame.IMP), INC = frame.INC)
        elif close_under == 'cm_inc':
            return MSF(L = frame.L, IMP = frame.IMP, INC = CM_INC_closure(frame.IMP, frame.INC))
        elif close_under == 'cm':
            return msf_CM_full_closure(frame)
        elif close_under == 'ct_imp':
            return MSF(L = frame.L, IMP = CT_IMP_closure(frame.IMP), INC = frame.INC)
        elif close_under == 'ct_inc':
            return MSF(L = frame.L, IMP = frame.IMP, INC = CT_INC_closure(frame.IMP, frame.INC))
        elif close_under == 'ct':
            return msf_CT_full_closure(frame)
        elif close_under == 'cm and ct':
            result = msf_CT_full_closure(msf_CM_full_closure(frame))
            while len(result.IMP) != len(msf_CT_full_closure(msf_CM_full_closure(result)).IMP) or len(result.INC) != len(msf_CT_full_closure(msf_CM_full_closure(result)).INC):
                result = msf_CT_full_closure(msf_CM_full_closure(result))
            return result
        else:
            print('This function requires a parameter close_under, which can take value from the following strings: '
                  '\'cm_imp\', \'cm_inc\', \'cm\', \'ct_imp\', \'ct_inc\', \'ct\', \'cm and ct\'.'
                  'By default, this function closes the input msf under the specified rule once. You can ask the function'
                  'to close multiple times by changing the parameter times, which can be any positive integer or \'full\'. If times is'
                  '\'full\', the function will close the input msf under the specified rule until a fixed point.')

    elif isinstance(times, int) and times > 0:
        if close_under == 'cm_imp':
            result = CM_IMP_closure_once(frame.IMP)
            for i in range(times - 1):
                result = CM_IMP_closure_once(result)
            return MSF(L = frame.L, IMP = result, INC = frame.INC)
        elif close_under == 'cm_inc':
            result = CM_INC_closure_once(frame.IMP, frame.INC)
            for i in range(times - 1):
                result = CM_INC_closure_once(frame.IMP, result)
            return MSF(L = frame.L, IMP = frame.IMP, INC = result)
        elif close_under == 'cm':
            result = msf_CM_full_closure_once(frame)
            for i in range(times - 1):
                result = msf_CM_full_closure_once(result)
            return result
        elif close_under == 'ct_imp':
            result = CT_IMP_closure(frame.IMP)
            for i in range(times - 1):
                result = CT_IMP_closure(result)
            return MSF(L = frame.L, IMP = result, INC = frame.INC)
        elif close_under == 'ct_inc':
            result = CT_INC_closure(frame.IMP, frame.INC)
            for i in range(times - 1):
                result = CT_INC_closure(frame.IMP, result)
            return MSF(L = frame.L, IMP = frame.IMP, INC = result)
        elif close_under == 'ct':
            result = msf_CT_full_closure_once(frame)
            for i in range(times - 1):
                result = msf_CT_full_closure_once(result)
            return result
        elif close_under == 'cm and ct':
            result = msf_CT_full_closure(msf_CM_full_closure(frame))
            for i in range(times - 1):
                result = msf_CT_full_closure(msf_CM_full_closure(result))
            return result
        else: print('This function requires a parameter close_under, which can take value from the following strings: '
                    '\'cm_imp\', \'cm_inc\', \'cm\', \'ct_imp\', \'ct_inc\', \'ct\', \'cm and ct\'.'
                    'By default, this function closes the input msf under the specified rule once. You can ask the function'
                    'to close multiple times by changing the parameter times, which can be any positive integer or \'full\'. If times is'
                    '\'full\', the function will close the input msf under the specified rule until a fixed point.')
    else: print('The parameter times specifies how many times you want the input msf closed under the rule you specified.'
                'It can either be positive integers, e.g. 1, 2, ... or string \'full\'. If it\'s set to be \'full\', it will'
                'close the input msf under the rule you specified until a fixed point.')

