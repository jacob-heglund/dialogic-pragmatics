""" defines the ct closure operations
"""

from msf import exff_closure, MSF
from cm_closure import cm_imp_closure, cm_imp_closure_once, cm_inc_closure, cm_inc_closure_once, msf_cm_full_closure, msf_cm_full_closure_once


def ct_imp_closure_once(input_imp):
    new_imp = []
    for i in input_imp:
        for j in input_imp:
            if j[0] == frozenset.union(i[0], frozenset([i[1]])):
                new_imp.append((i[0], j[1]))
    output_imp = frozenset.union(input_imp, frozenset(new_imp))
    return output_imp


def ct_imp_closure(input_imp):
    result = ct_imp_closure_once(input_imp)
    while len(result) != len(ct_imp_closure_once(result)):
        result = ct_imp_closure_once(result)
    return result


def ct_inc_closure_once(input_imp, input_inc):
    new_inc = []
    for i in input_imp:
        if frozenset.union(i[0], frozenset([i[1]])) in input_inc:
            new_inc.append(i[0])
    output_inc = frozenset.union(input_inc, frozenset(new_inc))
    return output_inc


def ct_inc_closure(input_imp, input_inc):
    result = ct_inc_closure_once(input_imp, input_inc)
    while len(result) != len(ct_inc_closure_once(input_imp, result)):
        result = ct_inc_closure_once(input_imp, result)
    return result


def msf_ct_full_closure_once(frame):
    ct_imp_first_time = ct_imp_closure(frame.imp)
    ct_inc_first_time = ct_inc_closure_once(ct_imp_first_time, frame.inc)
    exff_imp_first_time = exff_closure(language= frame.L, imp= ct_imp_first_time, inc= ct_inc_first_time)
    return MSF(lang = frame.L, imp = exff_imp_first_time, inc =  ct_inc_first_time)


def msf_ct_full_closure(frame):
    result = msf_ct_full_closure_once(frame)
    while len(result.imp) != len(msf_ct_full_closure_once(result).imp) or len(result.inc) != len(msf_ct_full_closure_once(result).inc):
        result = msf_ct_full_closure_once(result)
    return result


def unused_msf_closure(frame, close_under, times = 1):
    '''

    :param frame:
    :param close_under:
    :param times:
    :return:
    '''
    if times == 'full':
        if close_under == 'cm_imp':
            return MSF(lang = frame.L, imp = cm_imp_closure(frame.imp), inc =  frame.inc)
        elif close_under == 'cm_inc':
            return MSF(lang = frame.L, imp = frame.imp, inc =  cm_inc_closure(frame.imp, frame.inc))
        elif close_under == 'cm':
            return msf_cm_full_closure(frame)
        elif close_under == 'ct_imp':
            return MSF(lang = frame.L, imp = ct_imp_closure(frame.imp), inc =  frame.inc)
        elif close_under == 'ct_inc':
            return MSF(lang = frame.L, imp = frame.imp, inc =  ct_inc_closure(frame.imp, frame.inc))
        elif close_under == 'ct':
            return msf_ct_full_closure(frame)
        elif close_under == 'cm and ct':
            result = msf_ct_full_closure(msf_cm_full_closure(frame))
            while len(result.imp) != len(msf_ct_full_closure(msf_cm_full_closure(result)).imp) or len(result.inc) != len(msf_ct_full_closure(msf_cm_full_closure(result)).inc):
                result = msf_ct_full_closure(msf_cm_full_closure(result))
            return result
        else:
            print('This function requires a parameter close_under, which can take value from the following strings: '
                  '\'cm_imp\', \'cm_inc\', \'cm\', \'ct_imp\', \'ct_inc\', \'ct\', \'cm and ct\'.'
                  'By default, this function closes the input msf under the specified rule once. You can ask the function'
                  'to close multiple times by changing the parameter times, which can be any positive integer or \'full\'. If times is'
                  '\'full\', the function will close the input msf under the specified rule until a fixed point.')

    elif isinstance(times, int) and times > 0:
        if close_under == 'cm_imp':
            result = cm_imp_closure_once(frame.imp)
            for i in range(times - 1):
                result = cm_imp_closure_once(result)
            return MSF(lang = frame.L, imp = result, inc =  frame.inc)
        elif close_under == 'cm_inc':
            result = cm_inc_closure_once(frame.imp, frame.inc)
            for i in range(times - 1):
                result = cm_inc_closure_once(frame.imp, result)
            return MSF(lang = frame.L, imp = frame.imp, inc =  result)
        elif close_under == 'cm':
            result = msf_cm_full_closure_once(frame)
            for i in range(times - 1):
                result = msf_cm_full_closure_once(result)
            return result
        elif close_under == 'ct_imp':
            result = ct_imp_closure(frame.imp)
            for i in range(times - 1):
                result = ct_imp_closure(result)
            return MSF(lang = frame.L, imp = result, inc =  frame.inc)
        elif close_under == 'ct_inc':
            result = ct_inc_closure(frame.imp, frame.inc)
            for i in range(times - 1):
                result = ct_inc_closure(frame.imp, result)
            return MSF(lang = frame.L, imp = frame.imp, inc =  result)
        elif close_under == 'ct':
            result = msf_ct_full_closure_once(frame)
            for i in range(times - 1):
                result = msf_ct_full_closure_once(result)
            return result
        elif close_under == 'cm and ct':
            result = msf_ct_full_closure(msf_cm_full_closure(frame))
            for i in range(times - 1):
                result = msf_ct_full_closure(msf_cm_full_closure(result))
            return result
        else: print('This function requires a parameter close_under, which can take value from the following strings: '
                    '\'cm_imp\', \'cm_inc\', \'cm\', \'ct_imp\', \'ct_inc\', \'ct\', \'cm and ct\'.'
                    'By default, this function closes the input msf under the specified rule once. You can ask the function'
                    'to close multiple times by changing the parameter times, which can be any positive integer or \'full\'. If times is'
                    '\'full\', the function will close the input msf under the specified rule until a fixed point.')
    else: print('The parameter times specifies how many times you want the input msf closed under the rule you specified.'
                'It can either be positive integers, e.g. 1, 2, ... or string \'full\'. If it\'s set to be \'full\', it will'
                'close the input msf under the rule you specified until a fixed point.')
