""" helper functions for violations
"""

from utils import powerset_


def find_violations(imps: frozenset) -> dict:

    prems_to_concs = dict()
    gammadelta_to_viols = dict() # result

    for i in imps: # build a dict of premise sets to sets of conclusions implied by them

        if i[0] not in prems_to_concs:
            prems_to_concs[i[0]] = frozenset({i[1]})
        else:
            prems_to_concs[i[0]] = frozenset.union(prems_to_concs[i[0]], frozenset({i[1]}))

    for gamma, c_gamma in prems_to_concs.items(): # for all premise sets gamma in IMP

        non_CO_c_gamma = frozenset.difference(c_gamma, gamma) # non-CO consequences of gamma

        for delta in powerset_(non_CO_c_gamma): # for all non-empty subsets of non-CO consequences of gamma delta

            c_gammaUdelta = prems_to_concs[frozenset.union(gamma, delta)]

            cm_viols = frozenset.difference(c_gamma, c_gammaUdelta) # CM viols are difference between C(gamma) and C(gamma U delta), the consequences lost by explicitating delta
            ct_viols = frozenset.difference(c_gammaUdelta, c_gamma) # CT viols are difference between C(gamma U delta) and C(gamma), the consequences gained by explicitating delta

            gammadelta_to_viols[(gamma, delta)] = (cm_viols, ct_viols) # ordered pair (gamma, delta) maps to ordered pair (cm_viols, ct_viols)

    return gammadelta_to_viols


def show_violations(imps: frozenset, longform : bool = True):

    gammadelta_to_viols = find_violations(imps)

    CM_viols_count = 0
    CT_viols_count = 0

    CM_violator_count = 0
    CT_violator_count = 0

    for gammadelta, viols in gammadelta_to_viols.items():

        gamma = gammadelta[0]
        delta = gammadelta[1]
        union = frozenset.union(gamma, delta)
        cm_viols = viols[0]
        ct_viols = viols[1]

        if len(cm_viols) != 0:
            CM_viols_count += len(cm_viols)
            CM_violator_count += 1
            if longform:
                for viol in cm_viols:
                    print('CM violation: ' + str(set(gamma)) + '⊨' + str(viol) + ' and ' + str(set(gamma)) + '⊨' + str(set(delta)) + ', but not ' + str(set(union)) + '⊨' + str(viol))
                    print('\n')

        if len(ct_viols) != 0:
            CT_viols_count += len(ct_viols)
            CT_violator_count += 1
            if longform:
                for viol in ct_viols:
                    print('CT violation: ' + str(set(gamma)) + '⊨' + str(set(delta)) + ' and ' + str(set(union)) + '⊨' + str(viol) + ', but not ' + str(set(gamma)) + '⊨' + str(viol))
                    print('\n')

    if longform:
        print(str(CM_violator_count) + ' premise sets had CM violations. There were ' + str(CM_viols_count) + ' total CM violations.')
        print(str(CT_violator_count) + ' premise sets had CT violations. There were ' + str(CT_viols_count) + ' total CT violations.')
    else:
        print(str(CM_violator_count) + ',' + str(CM_viols_count) + ',' + str(CT_violator_count) + ',' + str(CT_viols_count))

