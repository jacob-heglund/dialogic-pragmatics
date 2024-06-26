"""defines the state of the environment at each time step
"""


from utils.env_utils import get_prev_stages, switch_agents
from utils.language_utils import exff_sets
from env.score import Score, ScoreSit


class Stage:
    def __init__(self, msf, turn_idx, agent, cl_inferential_theory, cr_inferential_theory, a_score_sit, target_move, prag_sig,
                 prime_move, f_score_sit, prev_stage, contro_set, suff_con):
        self.msf = msf
        self.turn_idx = turn_idx
        self.agent = agent
        self.cl_inferential_theory = cl_inferential_theory
        self.cr_inferential_theory = cr_inferential_theory
        self.a_score_sit = a_score_sit
        self.target_move = target_move
        self.prag_sig = prag_sig
        self.prime_move = prime_move
        self.f_score_sit = f_score_sit
        self.prev_stage = prev_stage
        self.contro_set = contro_set
        self.suff_con = suff_con
        self.available_moves = self._get_avail_moves(self)

    def _get_avail_moves(self, stage):
        # This function is used to compute all reasons available to the next mover at a given stage.
        avail_against_move = []
        avail_for_move = []
        st = get_prev_stages(stage)+[stage]

        #In this case, CL made a move in this stage and we should compute available moves for CR
        if stage.agent == 'CL':
            # We iterate through all against-moves (i.e. reason-againsts) in the msf of the stage.
            # Each against-move will pass a series of tests before it's added to a list.
            for m in stage.cr_inferential_theory.against_move:
                # Given,the move (type) under consideration is a reason-against, we first make sure that this move is
                # targeting something that CL (i.e. the opponent of the next mover CR) is entitled to.
                # And this move doesn't use the conclusion of the initial proposal of CL.
                if m.conc in stage.f_score_sit.cl.ae and st[0].prime_move.conc not in m.prem:
                    # We make sure that this move doesn't use anything that CR is committed to reject as premise and
                    # the target of this reason-against isn't something that CR is committed to accept.
                    if frozenset.intersection(m.prem, stage.f_score_sit.cr.rc) == frozenset() and m.conc not in stage.f_score_sit.cr.ac:
                        # We make sure that for every premise of this move, if CR has already committed to accept it by the
                        # end of the current stage (recall that we are computing what CR can do at next stage), CR is entitled
                        # to it. That is, making sure that CR isn't using any premise that he's not entitled.
                        if frozenset.intersection(m.prem, stage.f_score_sit.cr.ac).issubset(stage.f_score_sit.cr.ae):
                            # We make sure that this the union of CR's current ac and the premises of this move isn't
                            # persistently incoherent. In this way, CR will never make a move that will put her into
                            # persistently incoherent ac.
                            if not frozenset.union(stage.f_score_sit.cr.ac, m.prem) in exff_sets(stage.msf.lang, stage.msf.inc):
                                # The last test checks that CR hasn't used this reason-against in previous stages.
                                if all([m != i.prime_move for i in get_prev_stages(stage)] + [m != stage.prime_move]):
                                    # Once a move (type) passes all tests above, it's added to the list of available against
                                    # moves.
                                    avail_against_move.append(m)

            for j in stage.cr_inferential_theory.for_move: # We do the same thing for for-moves.
                if j.conc in stage.f_score_sit.cr.ac and j.conc not in stage.f_score_sit.cr.ae and st[0].prime_move.conc not in j.prem:
                    if frozenset.intersection(j.prem, stage.f_score_sit.cr.rc) == frozenset() and j.conc not in stage.f_score_sit.cr.rc:
                        if frozenset.intersection(j.prem, stage.f_score_sit.cr.ac).issubset(stage.f_score_sit.cr.ae):
                            if not frozenset.union(stage.f_score_sit.cr.ac, j.prem, frozenset([j.conc])) in exff_sets(stage.msf.lang, stage.msf.inc):
                                if all([j != i.prime_move for i in get_prev_stages(stage)] + [j != stage.prime_move]):
                                    avail_for_move.append(j)

            return {'agent': 'CR', 'for': frozenset(avail_for_move), 'against': frozenset(avail_against_move)}

        else:
            # In this case, CR made a move in this stage and we should compute available moves for CL.
            # The way it's checked is exactly the same as last case.
            for m in stage.cl_inferential_theory.against_move:
                if m.conc in stage.f_score_sit.cr.ae and st[0].prime_move.conc not in m.prem:
                    if frozenset.intersection(m.prem, stage.f_score_sit.cl.rc) == frozenset() and m.conc not in stage.f_score_sit.cl.ac:
                        if frozenset.intersection(m.prem, stage.f_score_sit.cl.ac).issubset(stage.f_score_sit.cl.ae):
                            if not frozenset.union(stage.f_score_sit.cl.ac, m.prem) in exff_sets(stage.msf.lang, stage.msf.inc):
                                if all([m != i.prime_move for i in get_prev_stages(stage)] + [m != stage.prime_move]):
                                    avail_against_move.append(m)

            for j in stage.cl_inferential_theory.for_move:
                if j.conc in stage.f_score_sit.cl.ac and j.conc not in stage.f_score_sit.cl.ae and st[0].prime_move.conc not in j.prem:
                    if frozenset.intersection(j.prem, stage.f_score_sit.cl.rc) == frozenset() and j.conc not in stage.f_score_sit.cl.rc:
                        if frozenset.intersection(j.prem, stage.f_score_sit.cl.ac).issubset(stage.f_score_sit.cl.ae):
                            if not frozenset.union(stage.f_score_sit.cl.ac, j.prem, frozenset([j.conc])) in exff_sets(stage.msf.lang, stage.msf.inc):
                                if all([j != i.prime_move for i in get_prev_stages(stage)] + [j != stage.prime_move]):
                                    avail_for_move.append(j)
            return {'agent': 'CL','for': frozenset(avail_for_move), 'against': frozenset(avail_against_move)}


def initial_next_stage(prev_stage, target_stage, prag_sig, move):
    """
    Return next stage, which is equivalent to making a move, requiring specification of the current stage and what move
    is to be made. This is perhaps the most important function in this program.
    This function is not intended to be called manually. It requires objects of class Stage and objects of class MoveType
    as inputs, which makes it almost impossible to run manually. Instead, this function does the hardwork of making moves.
    Other functions intending to be called, requiring less demanding inputs, are defined using this function.

    Notice, since we build prev_stage as an attribute of a stage. When we know what the last stage of a stage is, we
    actually have access to all previous stages. This feature is important for the operation of this function.

    This function requires inputs of what the last stage is, what the target stage is, what the pragmatic
    significance of the (move of the) next stage is, and what move is made.

    Parameters
    ----------
    prev_stage : Stage
        An object of class Stage, namely the stage right before the one to be generated by this function.
    target_stage : Stage
        An object of class Stage, namely the stage targeted by the move being made.
    prag_sig : str
        The pragmatic significance of the move being made.
    move : MoveType
        The move is being made.

    Returns
    -------
    Stage
        The next stage in which the move specified in the input is made.
    """
    if prev_stage.agent == 'CL' and move not in prev_stage.cr_inferential_theory.for_move and move not in prev_stage.cr_inferential_theory.against_move:
        print('Error: Attempted move is not in CL\'s Inferential Theory.')
    if prev_stage.agent == 'CR' and move not in prev_stage.cl_inferential_theory.for_move and move not in prev_stage.cl_inferential_theory.against_move:
        print('Error: Attempted move is not in CR\'s Inferential Theory.')

    frame = prev_stage.msf
    a = switch_agents(prev_stage.agent)
    if move.val == 'reason against': # For the case where the valence of next move is reason-against.
        # To simplify the scoring process, I keep a list of controversial sentences.
        # This step updates the set of controversial claims.
        controv = frozenset.union(prev_stage.contro_set, frozenset([move.conc]))
        # The next four lines update the sufficient conditions for scoring.
        scon = []
        for i in move.prem:
            scon.append(('A', None, 'A', i))
        suff_con = prev_stage.suff_con + [('A', move.prem, 'R', move.conc)] + scon

    else:   # This is for the case where the valence of next move is reason-for.
        controv = frozenset.union(prev_stage.contro_set, frozenset([move.conc]))
        scon = []
        for i in move.prem:
            scon.append(('A', None, 'A', i))
        suff_con = prev_stage.suff_con + [('A', move.prem, 'A', move.conc)] + scon

    # The following block updates the commitments of CL and CR in different cases.
    # Updating commitments is a very simple process that has nothing to do with entitlements.
    if a == 'CL':
        if move.val == 'reason against':
            cl_ac = frozenset.union(prev_stage.f_score_sit.cl.ac, move.prem)
            cl_rc = frozenset.union(prev_stage.f_score_sit.cl.rc, frozenset([move.conc]))
        else:
            cl_ac = frozenset.union(prev_stage.f_score_sit.cl.ac, move.prem, frozenset([move.conc]))
            cl_rc = prev_stage.f_score_sit.cl.rc
        cr_ac = prev_stage.f_score_sit.cr.ac
        cr_rc = prev_stage.f_score_sit.cr.rc
    else:
        if move.val == 'reason against':
            cr_ac = frozenset.union(prev_stage.f_score_sit.cr.ac, move.prem)
            cr_rc = frozenset.union(prev_stage.f_score_sit.cr.rc, frozenset([move.conc]))
        else:
            cr_ac = frozenset.union(prev_stage.f_score_sit.cr.ac, move.prem, frozenset([move.conc]))
            cr_rc = prev_stage.f_score_sit.cr.rc
        cl_ac = prev_stage.f_score_sit.cl.ac
        cl_rc = prev_stage.f_score_sit.cl.rc

        #Now we are done with commitments, sufficient conditions and controversial statements. Time for entitlements!

    # We first initiate lists of potential entitlements of CL and CR. E.g. p_cl_ae intended to be the set of sentences that
    # the CL is potentially entitled to accept. It starts as the set of sentences CL is committed to accept.
    p_cl_ae = cl_ac
    p_cl_re = cl_rc
    p_cr_ae = cr_ac
    p_cr_re = cr_rc
    cl_ae = []
    cl_re = []
    cr_ae = []
    cr_re = []

    # First Step: make agents entitled to accept all noncontroversial sentences that they are committed to accept.
    # A sentence is not controversial if it has never appeared on the right of a turntile. This is just to simplify
    # the process of keeping track of entitlement. The tracking process still works without it, albeit slower.
    for i in cl_ac:
        if i not in controv:
            cl_ae.append(i)
    for i in cr_ac:
        if i not in controv:
            cr_ae.append(i)

    # Second Step: Iterate through all sufficient conditions accumulated so far from the latest to earliest.
    # Basically, we iterate until we find a sufficient condition, whose premises are met and conclusion has yet been
    # actualized. We then actualize it and redo the interation from the beginning. We do so until there is no further
    # sufficient condition to be actualized, i.e. for each suff_con, either its premises are not met, or its conclusion
    # has already been actualized.
    n = 0
    while n < len(suff_con):
        n = 0
        for i in reversed(suff_con):
            if i[2] == 'A':  # The case of A -> A condition
                if i[1] is None:  # The case of automatic satisfication
                    if i[3] in p_cl_ae and i[3] not in cl_ae:  # Case of CL
                        cl_ae.append(i[3])
                        p_cr_re = p_cr_re - frozenset([i[3]])
                        break
                    if i[3] in p_cr_ae and i[3] not in cr_ae:  # Case of CR
                        cr_ae.append(i[3])
                        p_cl_re = p_cl_re - frozenset([i[3]])
                        break
                elif i[1] is not None:  # The case of conditional satisfication
                    if i[1].issubset(frozenset(cl_ae)) and i[3] in p_cl_ae and i[3] not in cl_ae:  # Case of CL
                        cl_ae.append(i[3])
                        p_cr_re = p_cr_re - frozenset([i[3]])
                        break
                    if i[1].issubset(frozenset(cr_ae)) and i[3] in p_cr_ae and i[3] not in cr_ae:  # Case of CR
                        cr_ae.append(i[3])
                        p_cl_re = p_cl_re - frozenset([i[3]])
                        break
            elif i[2] == 'R':  # The case of A -> R condition
                if i[1].issubset(frozenset(cl_ae)) and i[3] in p_cl_re and i[3] not in cl_re:
                    cl_re.append(i[3])
                    p_cr_ae = p_cr_ae - frozenset([i[3]])
                    break
                if i[1].issubset(frozenset(cr_ae)) and i[3] in p_cr_re and i[3] not in cr_re:
                    cr_re.append(i[3])
                    p_cl_ae = p_cl_ae - frozenset([i[3]])
                    break
            n = n + 1

    # We initiated cl_ae, cl_re, cr_ae, cr_re as lists for convenience. Now we convert them back to frozensets.
    cl_ae = frozenset(cl_ae)
    cl_re = frozenset(cl_re)
    cr_ae = frozenset(cr_ae)
    cr_re = frozenset(cr_re)

    # Creating scores for CL and CR.
    cl = Score('CL', ac = cl_ac, ae = cl_ae, rc = cl_rc, re = cl_re)
    cr = Score('CR', ac = cr_ac, ae = cr_ae, rc = cr_rc, re = cr_re)

    # Creating final score
    finalscore = ScoreSit(cl_score = cl, cr_score = cr)

    next_stage = Stage(msf = frame, turn_idx = prev_stage.turn_idx + 1, agent = a, cl_inferential_theory = prev_stage.cl_inferential_theory,
                 cr_inferential_theory = prev_stage.cr_inferential_theory, a_score_sit = prev_stage.f_score_sit,
                 target_move = target_stage, prag_sig = prag_sig, prime_move=move, f_score_sit = finalscore,
                 prev_stage=prev_stage, contro_set = controv, suff_con = suff_con)

    return next_stage


def initial_next_stage_2(stage, prime):
    # This is the second part of initial_next_stage. Most parameters required by initial_next_stage can be inferred from the
    # move to be take. Thus this function does the inferring and reduces the number of parameters required by initial_next_stage.
    if prime.val == 'reason for':
        for i in reversed(get_prev_stages(stage)+[stage]):
            if i.prag_sig == 'proposal' and i.prime_move.conc == prime.conc and i.agent != stage.agent:
                target_stage = None
                prag_sig = 'proposal'
                break
            elif i.prime_move.val == 'reason against' and i.prime_move.conc == prime.conc and i.agent == stage.agent:
                target_stage = i
                prag_sig = 'conclusion challenge'
                break
            else:
                target_stage = None
                prag_sig = None
    elif prime.val == 'reason against':
        for i in reversed(get_prev_stages(stage) + [stage]):
            if i.prag_sig == 'proposal' and i.prime_move.conc == prime.conc and i.agent != stage.agent:
                target_stage = None
                prag_sig = 'proposal'
                break
            elif i.prime_move.val == 'reason against' and i.agent == stage.agent:
                if prime.conc in i.prime_move.prem:
                    target_stage = i
                    prag_sig = 'premise challenge'
                    break
            elif i.prime_move.val == 'reason for' and i.agent == stage.agent:
                if prime.conc in i.prime_move.prem:
                    target_stage = i
                    prag_sig = 'premise challenge'
                    break
                elif prime.conc == i.prime_move.conc:
                    target_stage = i
                    prag_sig = 'conclusion challenge'
                    break
            else:
                target_stage = None
                prag_sig = None

    return initial_next_stage(prev_stage = stage, target_stage = target_stage, prag_sig = prag_sig, move = prime)


def manual_next_stage(prev_stage, target_stage, prag_sig, proposal, val):
    '''
    Generate next stage with more friendly, albeit still not friendly enough, inputs. Instead of inputting an object of
    class MoveType, you only need to put in a proposal and its valence.

    Parameters
    ----------
    prev_stage : Stage
        An object of class Stage, namely the stage right before the one to be generated by this function.
    target_stage : Stage
        An object of class Stage, namely the stage targeted by the move being made.
    prag_sig : str
        The pragmatic significance of the move being made.
    proposal : tuple
        A 2-tuple whose first element is the frozenset of indexes of premises and the second element is an int, namely
        the index of the conlcusion. Throughout the program, we use kind of meta-typing. When a function expects a proposal
        as input, it's expecting such a tuple.
    val: str
        The valence of the move to be made. Notice proposal doesn't distinguish reason for from reason against, but only
        records premises and conclusion. This is why we need valence as a separate input. val is either 'reason for' or
        'reason against'.


    Returns
    -------
    Stage
        The next stage in which the move specified in the input is made.
    '''
    agent = switch_agents(prev_stage.agent)
    prime = None
    if val == 'reason against':
        for m in prev_stage.msf.against_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason against':
                prime = m
                break
    else:
        for m in prev_stage.msf.for_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason for':
                prime = m
                break
    if prime is None:
        print('The proposed next move is not in the given MSF.')
    elif agent == 'CL' and prime not in prev_stage.cl_inferential_theory.for_move and prime not in prev_stage.cl_inferential_theory.against_move:
        print('The proposed next move is not in the InferentialTheory of CL, who is the next agent to make a move.')
    elif agent == 'CR' and prime not in prev_stage.cr_inferential_theory.for_move and prime not in prev_stage.cr_inferential_theory.against_move:
        print('The proposed next move is not in the InferentialTheory of CR, who is the next agent to make a move.')
    else:
        return initial_next_stage(prev_stage, target_stage, prag_sig, prime)


def manual_next_stage_2(prev_stage, target_stage, prag_sig, premise, val, conclusion):
    frame = prev_stage.msf
    proposal = (frozenset([frame.lang.index(s) for s in premise]), frame.lang.index(conclusion))
    return manual_next_stage(prev_stage = prev_stage, target_stage = target_stage, prag_sig = prag_sig, proposal = proposal,
                           val = val)


def manual_next_stage_infer(prev_stage, proposal, val):
    agent = switch_agents(prev_stage.agent)
    prime = None
    if val == 'reason against':
        for m in prev_stage.msf.against_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason against':
                prime = m
                break
    else:
        for m in prev_stage.msf.for_move:
            if m.prem == proposal[0] and m.conc == proposal[1] and m.val == 'reason for':
                prime = m
                break
    if prime is None:
        print('The proposed next move is not in the given MSF.')
    elif agent == 'CL' and prime not in prev_stage.cl_inferential_theory.for_move and prime not in prev_stage.cl_inferential_theory.against_move:
        print('The proposed next move is not in the InferentialTheory of CL, who is the next agent to make a move.')
    elif agent == 'CR' and prime not in prev_stage.cr_inferential_theory.for_move and prime not in prev_stage.cr_inferential_theory.against_move:
        print('The proposed next move is not in the InferentialTheory of CR, who is the next agent to make a move.')
    else:
        return initial_next_stage_2(prev_stage, prime)


