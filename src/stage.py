"""defines the dialogic environment as a set of stages
"""

import random
from prettytable import PrettyTable

from utils import stage_row, first_stage_row, agentswitch
from msf import ExFF_sets
from score import Score, ScoreSit


EmptyScore_CL = Score('CL', frozenset(), frozenset(), frozenset(), frozenset())

EmptyScore_CR = Score('CR', frozenset(), frozenset(), frozenset(), frozenset())

EmptyScoreSit = ScoreSit(EmptyScore_CL, EmptyScore_CR)


class Stage:
    def __init__(self, MSF, TurnNum, Agent, CL_InferentialTheory, CR_InferentialTheory, AScoreSit, TargetMove, PragSig,
                 PrimeMove, FScoreSit, LastStage, ControSet, SuffCon):
        self.MSF = MSF
        self.TurnNum = TurnNum
        self.Agent = Agent
        self.CL_InferentialTheory = CL_InferentialTheory
        self.CR_InferentialTheory = CR_InferentialTheory
        self.AScoreSit = AScoreSit
        self.TargetMove = TargetMove
        self.PragSig = PragSig
        self.PrimeMove = PrimeMove
        self.FScoreSit = FScoreSit
        self.LastStage = LastStage
        self.ControSet = ControSet
        self.SuffCon = SuffCon
        self.AvailableMove = AvailMove(self)


    def show(self):
        if self.TurnNum == 0:
            x = PrettyTable()
            x.field_names = ['TurnNum', 'Agent', 'TargetNum', 'PragSig', 'Move', 'CL_AC', 'CL_RC', 'CL_AE', 'CL_RE',
                             'CR_AC', 'CR_RC', 'CR_AE', 'CR_RE']
            first_stage_row(x,self)
            print(x)
        else:
            x = PrettyTable()
            x.field_names = ['TurnNum', 'Agent', 'TargetNum', 'PragSig', 'Move', 'CL_AC', 'CL_RC', 'CL_AE', 'CL_RE',
                             'CR_AC', 'CR_RC', 'CR_AE', 'CR_RE']
            stage_row(x,self)
            print(x)


def PrevStages(stage):
    # This gives the list of all previous stages, given a stage, in increasing order of TurnNum, i.e. the initial stage
    # has index 0, and so on.
    prevstages = list()
    s = stage
    while s.LastStage != None:
        prevstages.append(s.LastStage)
        s = s.LastStage
    prevstages.reverse()
    return prevstages


def AvailMove(stage):
    #This function is used to compute all reasons available to the next mover at a given stage.
    avail_against_move = list()
    avail_for_move = list()
    st = PrevStages(stage)+[stage]
    if stage.Agent == 'CL': #In this case, CL made a move in this stage and we should compute available moves for CR
        # We iterate through all against-moves (i.e. reason-againsts) in the msf of the stage.
        # Each against-move will pass a series of tests before it's added to a list.
        for m in stage.CR_InferentialTheory.AgainstMove:
            # Given,the move (type) under consideration is a reason-against, we first make sure that this move is
            # targeting something that CL (i.e. the opponent of the next mover CR) is entitled to.
            # And this move doesn't use the conclusion of the initial proposal of CL.
            if m.Conc in stage.FScoreSit.CL.AE and st[0].PrimeMove.Conc not in m.Prem:
                # We make sure that this move doesn't use anything that CR is committed to reject as premise and
                # the target of this reason-against isn't something that CR is committed to accept.
                if frozenset.intersection(m.Prem, stage.FScoreSit.CR.RC) == frozenset() and m.Conc not in stage.FScoreSit.CR.AC:
                    # We make sure that for every premise of this move, if CR has already committed to accept it by the
                    # end of the current stage (recall that we are computing what CR can do at next stage), CR is entitled
                    # to it. That is, making sure that CR isn't using any premise that he's not entitled.
                    if frozenset.intersection(m.Prem, stage.FScoreSit.CR.AC).issubset(stage.FScoreSit.CR.AE):
                        # We make sure that this the union of CR's current AC and the premises of this move isn't
                        # persistently incoherent. In this way, CR will never make a move that will put her into
                        # persistently incoherent AC.
                        if not frozenset.union(stage.FScoreSit.CR.AC, m.Prem) in ExFF_sets(stage.MSF.L, stage.MSF.INC):
                            # The last test checks that CR hasn't used this reason-against in previous stages.
                            if all([m != i.PrimeMove for i in PrevStages(stage)] + [m != stage.PrimeMove]):
                                # Once a move (type) passes all tests above, it's added to the list of available against
                                # moves.
                                avail_against_move.append(m)
        for j in stage.CR_InferentialTheory.ForMove: # We do the same thing for for-moves.
            if j.Conc in stage.FScoreSit.CR.AC and j.Conc not in stage.FScoreSit.CR.AE and st[0].PrimeMove.Conc not in j.Prem:
                if frozenset.intersection(j.Prem, stage.FScoreSit.CR.RC) == frozenset() and j.Conc not in stage.FScoreSit.CR.RC:
                    if frozenset.intersection(j.Prem, stage.FScoreSit.CR.AC).issubset(stage.FScoreSit.CR.AE):
                        if not frozenset.union(stage.FScoreSit.CR.AC, j.Prem, frozenset([j.Conc])) in ExFF_sets(stage.MSF.L, stage.MSF.INC):
                            if all([j != i.PrimeMove for i in PrevStages(stage)] + [j != stage.PrimeMove]):
                                avail_for_move.append(j)
        return {'agent': 'CR', 'for': frozenset(avail_for_move), 'against': frozenset(avail_against_move)}
    else:
        # In this case, CR made a move in this stage and we should compute available moves for CL.
        # The way it's checked is exactly the same as last case.
        for m in stage.CL_InferentialTheory.AgainstMove:
            if m.Conc in stage.FScoreSit.CR.AE and st[0].PrimeMove.Conc not in m.Prem:
                if frozenset.intersection(m.Prem, stage.FScoreSit.CL.RC) == frozenset() and m.Conc not in stage.FScoreSit.CL.AC:
                    if frozenset.intersection(m.Prem, stage.FScoreSit.CL.AC).issubset(stage.FScoreSit.CL.AE):
                        if not frozenset.union(stage.FScoreSit.CL.AC, m.Prem) in ExFF_sets(stage.MSF.L, stage.MSF.INC):
                            if all([m != i.PrimeMove for i in PrevStages(stage)] + [m != stage.PrimeMove]):
                                avail_against_move.append(m)
        for j in stage.CL_InferentialTheory.ForMove:
            if j.Conc in stage.FScoreSit.CL.AC and j.Conc not in stage.FScoreSit.CL.AE and st[0].PrimeMove.Conc not in j.Prem:
                if frozenset.intersection(j.Prem, stage.FScoreSit.CL.RC) == frozenset() and j.Conc not in stage.FScoreSit.CL.RC:
                    if frozenset.intersection(j.Prem, stage.FScoreSit.CL.AC).issubset(stage.FScoreSit.CL.AE):
                        if not frozenset.union(stage.FScoreSit.CL.AC, j.Prem, frozenset([j.Conc])) in ExFF_sets(stage.MSF.L, stage.MSF.INC):
                            if all([j != i.PrimeMove for i in PrevStages(stage)] + [j != stage.PrimeMove]):
                                avail_for_move.append(j)
        return {'agent': 'CL','for': frozenset(avail_for_move), 'against': frozenset(avail_against_move)}


# Make Moves as generating stages


def InitialMoveFor(frame, move, CL_InferentialTheory, CR_InferentialTheory):
    fscore = ScoreSit(Score(Subject = 'CL', AC = frozenset.union(move.Prem, frozenset([move.Conc])),
                            RC = frozenset(), AE = frozenset.union(move.Prem, frozenset([move.Conc])),
                            RE = frozenset()), EmptyScore_CR)
    scon = list()
    if move not in CL_InferentialTheory.ForMove:
        print('The given first move is not in CL\'s Inferential Theory.')
    else:
        for i in move.Prem:
            scon.append(('A', None, 'A', i))
        suffcon = [('A', move.Prem, 'A', move.Conc)] + scon
    # Here it's important to have scon second, instead of first.
        return Stage(MSF = frame, TurnNum = 0, Agent = 'CL', AScoreSit = EmptyScoreSit, TargetMove = None,
                     PragSig = 'proposal', PrimeMove = move, FScoreSit = fscore, LastStage = None,
                     ControSet = frozenset([move.Conc]), SuffCon = suffcon, CL_InferentialTheory = CL_InferentialTheory,
                     CR_InferentialTheory = CR_InferentialTheory)


def ManualInitialMoveFor(frame, proposal, CL_InferentialTheory, CR_InferentialTheory):
    if proposal not in frame.IMP:
        print('Not an eligible first reason-for move in this semantic frame')
    else:
        for m in frame.ForMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason for':
                prime = m
                break
        if prime not in CL_InferentialTheory.ForMove:
            print('The proposal is not in the player\'s inferential theory.')
        else:
            return InitialMoveFor(frame = frame, move = prime, CL_InferentialTheory = CL_InferentialTheory,
                                  CR_InferentialTheory = CR_InferentialTheory)


def FirstMoveFor(frame, premise, conclusion, CL_InferentialTheory, CR_InferentialTheory):
    proposal = (frozenset([frame.L.index(s) for s in premise]), frame.L.index(conclusion))
    return ManualInitialMoveFor(frame = frame, proposal = proposal, CL_InferentialTheory = CL_InferentialTheory,
                                  CR_InferentialTheory = CR_InferentialTheory)

def FirstMoveFor_RandomPremise(frame, conclusion, CL_InferentialTheory, CR_InferentialTheory):
    # Input conclusion as a string, e.g. 'a_2'
    pool = list()
    for i in frame.ForMove:
        if i.Conc == frame.L.index(conclusion):
            pool.append(i)
    move = random.sample(frozenset.intersection(frozenset(pool), CL_InferentialTheory.ForMove), 1)[0]
    return InitialMoveFor(frame = frame, move = move, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)


def RandomFirstMoveFor(frame, CL_InferentialTheory, CR_InferentialTheory):
    # This function draws one move out of all for-moves arbitrarily. Notice for-moves may not be equally distributed
    # over all sentences. So some sentence is more likely to be defended than others by this function
    m = random.sample(CL_InferentialTheory.ForMove, 1)[0]
    return InitialMoveFor(frame = frame, move = m, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)

def RandomFirstMoveFor_RandomConclusion(frame, CL_InferentialTheory, CR_InferentialTheory):
    # This function first randomly draws a conclusion to defend and then defend it with a randomly drawn move.
    # All sentences are equally likely to be defended by this function.
    conclusion = random.sample(frame.L, 1)[0]
    return FirstMoveFor_RandomPremise(frame = frame, conclusion = conclusion, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)



def InitialMoveAgainst(frame, move, CL_InferentialTheory, CR_InferentialTheory):
    fscore = ScoreSit(Score('CL', move.Prem, frozenset([move.Conc]), move.Prem, frozenset([move.Conc])), EmptyScore_CR)
    scon = list()
    if move not in CL_InferentialTheory.AgainstMove:
        print('The given first move is not in CL\'s Inferential Theory.')
    else:
        for i in move.Prem:
            scon.append(('A', None, 'A', i))
        suffcon = [('A', move.Prem, 'R', move.Conc)] + scon
        return Stage(MSF = frame, TurnNum = 0, Agent = 'CL', CL_InferentialTheory = CL_InferentialTheory,
                     CR_InferentialTheory = CR_InferentialTheory, AScoreSit = EmptyScoreSit, TargetMove = None,
                     PragSig = 'proposal', PrimeMove = move, FScoreSit = fscore, LastStage= None,
                     ControSet = frozenset([move.Conc]), SuffCon = suffcon)


def ManualInitialMoveAgainst(frame, proposal, CL_InferentialTheory, CR_InferentialTheory):
    if proposal[0] not in frame.EXC[proposal[1]]:
        print('Not an eligible first reason-against move in this semantic frame')
    else:
        for m in frame.AgainstMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason against':
                prime = m
                break
        if prime not in CL_InferentialTheory.AgainstMove:
            print('The given first move is not in CL\'s Inferential Theory.')
        else:
            return InitialMoveAgainst(frame = frame, move = prime, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)

def FirstMoveAgainst(frame, premise, target, CL_InferentialTheory, CR_InferentialTheory):
    proposal = (frozenset([frame.L.index(s) for s in premise]), frame.L.index(target))
    return ManualInitialMoveAgainst(frame = frame, proposal = proposal, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)

def FirstMoveAgainst_RandomPremise(frame, target, CL_InferentialTheory, CR_InferentialTheory):
    pool = list()
    for i in CL_InferentialTheory.AgainstMove:
        if i.Conc == frame.L.index(target):
            pool.append(i)
    move = random.sample(pool, 1)[0]
    return InitialMoveAgainst(frame = frame, move = move, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)


def RandomFirstMoveAgainst(frame, CL_InferentialTheory, CR_InferentialTheory):
    # This function draws one move out of all for-moves arbitrarily. Notice for-moves may not be equally distributed
    # over all sentences. So some sentence is more likely to be defended than others by this function
    m = random.sample(CL_InferentialTheory.AgainstMove, 1)[0]
    return InitialMoveAgainst(frame = frame, move = m, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)

def RandomFirstMoveAgainst_RandomTarget(frame, CL_InferentialTheory, CR_InferentialTheory):
    # This function first randomly draws a target to argue against and then defend it with a randomly drawn move.
    # All sentences are equally likely to be defended by this function.
    target = random.sample(frame.L, 1)[0]
    return FirstMoveAgainst_RandomPremise(frame = frame, target = target, CL_InferentialTheory = CL_InferentialTheory,
                          CR_InferentialTheory = CR_InferentialTheory)



def InitialNextStage(last_stage, targetstage, pragsig, move):
    """
    Return next stage, which is equivalent to making a move, requiring specification of the current stage and what move
    is to be made. This is perhaps the most important function in this program.
    This function is not intended to be called manually. It requires objects of class Stage and objects of class MoveType
    as inputs, which makes it almost impossible to run manually. Instead, this function does the hardwork of making moves.
    Other functions intending to be called, requiring less demanding inputs, are defined using this function.

    Notice, since we build LastStage as an attribute of a stage. When we know what the last stage of a stage is, we
    actually have access to all previous stages. This feature is important for the operation of this function.

    This function requires inputs of what the last stage is, what the target stage is, what the pragmatic
    significance of the (move of the) next stage is, and what move is made.

    Parameters
    ----------
    last_stage : Stage
        An object of class Stage, namely the stage right before the one to be generated by this function.
    targetstage : Stage
        An object of class Stage, namely the stage targeted by the move being made.
    pragsig : str
        The pragmatic significance of the move being made.
    move : MoveType
        The move is being made.

    Returns
    -------
    Stage
        The next stage in which the move specified in the input is made.
    """
    if last_stage.Agent == 'CL' and move not in last_stage.CR_InferentialTheory.ForMove and move not in last_stage.CR_InferentialTheory.AgainstMove:
        print('Error: Attempted move is not in CL\'s Inferential Theory.')
    if last_stage.Agent == 'CR' and move not in last_stage.CL_InferentialTheory.ForMove and move not in last_stage.CL_InferentialTheory.AgainstMove:
        print('Error: Attempted move is not in CR\'s Inferential Theory.')

    frame = last_stage.MSF
    a = agentswitch(last_stage.Agent)
    if move.Val == 'reason against': # For the case where the valence of next move is reason-against.
        # To simplify the scoring process, I keep a list of controversial sentences.
        # This step updates the set of controversial claims.
        controv = frozenset.union(last_stage.ControSet, frozenset([move.Conc]))
        # The next four lines update the sufficient conditions for scoring.
        scon = list()
        for i in move.Prem:
            scon.append(('A', None, 'A', i))
        suffcon = last_stage.SuffCon + [('A', move.Prem, 'R', move.Conc)] + scon

    else:   # This is for the case where the valence of next move is reason-for.
        controv = frozenset.union(last_stage.ControSet, frozenset([move.Conc]))
        scon = list()
        for i in move.Prem:
            scon.append(('A', None, 'A', i))
        suffcon = last_stage.SuffCon + [('A', move.Prem, 'A', move.Conc)] + scon

    # The following block updates the commitments of CL and CR in different cases.
    # Updating commitments is a very simple process that has nothing to do with entitlements.
    if a == 'CL':
        if move.Val == 'reason against':
            cl_ac = frozenset.union(last_stage.FScoreSit.CL.AC, move.Prem)
            cl_rc = frozenset.union(last_stage.FScoreSit.CL.RC, frozenset([move.Conc]))
        else:
            cl_ac = frozenset.union(last_stage.FScoreSit.CL.AC, move.Prem, frozenset([move.Conc]))
            cl_rc = last_stage.FScoreSit.CL.RC
        cr_ac = last_stage.FScoreSit.CR.AC
        cr_rc = last_stage.FScoreSit.CR.RC
    else:
        if move.Val == 'reason against':
            cr_ac = frozenset.union(last_stage.FScoreSit.CR.AC, move.Prem)
            cr_rc = frozenset.union(last_stage.FScoreSit.CR.RC, frozenset([move.Conc]))
        else:
            cr_ac = frozenset.union(last_stage.FScoreSit.CR.AC, move.Prem, frozenset([move.Conc]))
            cr_rc = last_stage.FScoreSit.CR.RC
        cl_ac = last_stage.FScoreSit.CL.AC
        cl_rc = last_stage.FScoreSit.CL.RC

        #Now we are done with commitments, sufficient conditions and controversial statements. Time for entitlements!

# We first initiate lists of potential entitlements of CL and CR. E.g. p_cl_ae intended to be the set of sentences that
# the CL is potentially entitled to accept. It starts as the set of sentences CL is committed to accept.
    p_cl_ae = cl_ac
    p_cl_re = cl_rc
    p_cr_ae = cr_ac
    p_cr_re = cr_rc
    cl_ae = list()
    cl_re = list()
    cr_ae = list()
    cr_re = list()
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
    # sufficient condition to be actualized, i.e. for each suffcon, either its premises are not met, or its conclusion
    # has already been actualized.
    n = 0
    while n < len(suffcon):
        n = 0
        for i in reversed(suffcon):
            if i[2] == 'A':  # The case of A -> A condition
                if i[1] == None:  # The case of automatic satisfication
                    if i[3] in p_cl_ae and i[3] not in cl_ae:  # Case of CL
                        cl_ae.append(i[3])
                        p_cr_re = p_cr_re - frozenset([i[3]])
                        break
                    if i[3] in p_cr_ae and i[3] not in cr_ae:  # Case of CR
                        cr_ae.append(i[3])
                        p_cl_re = p_cl_re - frozenset([i[3]])
                        break
                elif i[1] != None:  # The case of conditional satisfication
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
    cl = Score('CL', AC = cl_ac, AE = cl_ae, RC = cl_rc, RE = cl_re)
    cr = Score('CR', AC = cr_ac, AE = cr_ae, RC = cr_rc, RE = cr_re)
    # Creating ScoreSit.
    finalscore = ScoreSit(CL_Score = cl, CR_Score = cr)
    return Stage(MSF = frame, TurnNum = last_stage.TurnNum + 1, Agent = a, CL_InferentialTheory = last_stage.CL_InferentialTheory,
                 CR_InferentialTheory = last_stage.CR_InferentialTheory, AScoreSit = last_stage.FScoreSit,
                 TargetMove = targetstage, PragSig = pragsig, PrimeMove = move, FScoreSit = finalscore,
                 LastStage=last_stage, ControSet = controv, SuffCon = suffcon)


def InitialNextStage_2(stage, prime):
    # This is the second part of InitialNextStage. Most parameters required by InitialNextStage can be inferred from the
    # move to be take. Thus this function does the inferring and reduces the number of parameters required by InitialNextStage.
    if prime.Val == 'reason for':
        for i in reversed(PrevStages(stage)+[stage]):
            if i.PragSig == 'proposal' and i.PrimeMove.Conc == prime.Conc and i.Agent != stage.Agent:
                targetstage = None
                pragsig = 'proposal'
                break
            elif i.PrimeMove.Val == 'reason against' and i.PrimeMove.Conc == prime.Conc and i.Agent == stage.Agent:
                targetstage = i
                pragsig = 'conclusion challenge'
                break
            else:
                targetstage = None
                pragsig = None
    elif prime.Val == 'reason against':
        for i in reversed(PrevStages(stage) + [stage]):
            if i.PragSig == 'proposal' and i.PrimeMove.Conc == prime.Conc and i.Agent != stage.Agent:
                targetstage = None
                pragsig = 'proposal'
                break
            elif i.PrimeMove.Val == 'reason against' and i.Agent == stage.Agent:
                if prime.Conc in i.PrimeMove.Prem:
                    targetstage = i
                    pragsig = 'premise challenge'
                    break
            elif i.PrimeMove.Val == 'reason for' and i.Agent == stage.Agent:
                if prime.Conc in i.PrimeMove.Prem:
                    targetstage = i
                    pragsig = 'premise challenge'
                    break
                elif prime.Conc == i.PrimeMove.Conc:
                    targetstage = i
                    pragsig = 'conclusion challenge'
                    break
            else:
                targetstage = None
                pragsig = None

    return InitialNextStage(last_stage = stage, targetstage = targetstage, pragsig = pragsig, move = prime)

def ManualNextStage(last_stage, targetstage, pragsig, proposal, val):
    '''
    Generate next stage with more friendly, albeit still not friendly enough, inputs. Instead of inputting an object of
    class MoveType, you only need to put in a proposal and its valence.

    Parameters
    ----------
    last_stage : Stage
        An object of class Stage, namely the stage right before the one to be generated by this function.
    targetstage : Stage
        An object of class Stage, namely the stage targeted by the move being made.
    pragsig : str
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
    agent = agentswitch(last_stage.Agent)
    prime = None
    if val == 'reason against':
        for m in last_stage.MSF.AgainstMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason against':
                prime = m
                break
    else:
        for m in last_stage.MSF.ForMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason for':
                prime = m
                break
    if prime == None:
        print('The proposed next move is not in the given MSF.')
    elif agent == 'CL' and prime not in last_stage.CL_InferentialTheory.ForMove and prime not in last_stage.CL_InferentialTheory.AgainstMove:
        print('The proposed next move is not in the InferentialTheory of CL, who is the next agent to make a move.')
    elif agent == 'CR' and prime not in last_stage.CR_InferentialTheory.ForMove and prime not in last_stage.CR_InferentialTheory.AgainstMove:
        print('The proposed next move is not in the InferentialTheory of CR, who is the next agent to make a move.')
    else:
        return InitialNextStage(last_stage, targetstage, pragsig, prime)

def ManualNextStage_2(last_stage, targetstage, pragsig, premise, val, conclusion):
    frame = last_stage.MSF
    proposal = (frozenset([frame.L.index(s) for s in premise]), frame.L.index(conclusion))
    return ManualNextStage(last_stage = last_stage, targetstage = targetstage, pragsig = pragsig, proposal = proposal,
                           val = val)

def ManualNextStageInfer(last_stage, proposal, val):
    agent = agentswitch(last_stage.Agent)
    prime = None
    if val == 'reason against':
        for m in last_stage.MSF.AgainstMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason against':
                prime = m
                break
    else:
        for m in last_stage.MSF.ForMove:
            if m.Prem == proposal[0] and m.Conc == proposal[1] and m.Val == 'reason for':
                prime = m
                break
    if prime == None:
        print('The proposed next move is not in the given MSF.')
    elif agent == 'CL' and prime not in last_stage.CL_InferentialTheory.ForMove and prime not in last_stage.CL_InferentialTheory.AgainstMove:
        print('The proposed next move is not in the InferentialTheory of CL, who is the next agent to make a move.')
    elif agent == 'CR' and prime not in last_stage.CR_InferentialTheory.ForMove and prime not in last_stage.CR_InferentialTheory.AgainstMove:
        print('The proposed next move is not in the InferentialTheory of CR, who is the next agent to make a move.')
    else:
        return InitialNextStage_2(last_stage, prime)

def RandomNextStage(stage):
    moves = frozenset.union(stage.AvailableMove['for'], stage.AvailableMove['against'])
    prime = random.sample(moves, 1)[0]
    return InitialNextStage_2(stage = stage, prime = prime)


def NewCommitment(move, laststage):
    #Computing what the move is grossly adding.
    if move.Val == 'reason for':
        gross_new_AC = frozenset.union(move.Prem, frozenset([move.Conc]))
        gross_new_RC = frozenset()
    if move.Val == 'reason against':
        gross_new_AC = move.Prem
        gross_new_RC = frozenset([move.Conc])

    #Computing what the move's net new commitments.
    if laststage.Agent == 'CL':
        newAC = gross_new_AC - laststage.FScoreSit.CR.AC
        newRC = gross_new_RC - laststage.FScoreSit.CR.RC

    if laststage.Agent == 'CR':
        newAC = gross_new_AC - laststage.FScoreSit.CL.AC
        newRC = gross_new_RC - laststage.FScoreSit.CL.RC

    return (newAC, newRC)



def Minimize_AC_NextStage(stage):
    moves = frozenset.union(stage.AvailableMove['for'], stage.AvailableMove['against'])
    lst_new_AC_length = set()
    pool = list()
    for i in moves:
        lst_new_AC_length.add(len(NewCommitment(i, stage)[0]))
    min_new_AC_length = min(lst_new_AC_length)
    for i in moves:
        if len(NewCommitment(i,stage)[0]) == min_new_AC_length:
            pool.append(i)

    prime = random.sample(frozenset(pool), 1)[0]

    return InitialNextStage_2(stage = stage, prime = prime)



def NextStage(laststage, CL_strategy, CR_strategy):
    if laststage.Agent == 'CL':
        if CR_strategy == 'random':
            return RandomNextStage(stage = laststage)
        elif CR_strategy == 'minimize AC':
            return Minimize_AC_NextStage(stage = laststage)
        elif CR_strategy == 'one step ahead':
            return OneStepAhead_NextStage(stage = laststage)
        else: print('Error: Currently, CL and CR have only three strategies: \'random\', \'minimize AC\' and \'one step ahead\'.')

    elif laststage.Agent == 'CR':
        if CL_strategy == 'random':
            return RandomNextStage(stage = laststage)
        elif CL_strategy == 'minimize AC':
            return Minimize_AC_NextStage(stage = laststage)
        elif CL_strategy == 'one step ahead':
            return OneStepAhead_NextStage(stage = laststage)
        else:
            print('Error: Currently, CL and CR have only three strategies: \'random\', \'minimize AC\' and \'one step ahead\'.')



def OneStepAhead_NextStage(stage):
    moves = frozenset.union(stage.AvailableMove['for'], stage.AvailableMove['against'])
    pool = list()

    for i in moves:
        #Case for CL
        if stage.Agent == 'CL':
            if Verdict(InitialNextStage_2(stage = stage, prime = i)) == 'fail':
                pool.append(i)
        #Case for CR
        else:
            if Verdict(InitialNextStage_2(stage = stage, prime = i)) == 'sustain':
                pool.append(i)

    if len(pool) != 0:
        prime = random.sample(frozenset(pool), 1)[0]
    else:
        prime = random.sample(frozenset(moves), 1)[0]

    return InitialNextStage_2(stage = stage, prime = prime)



def Verdict(stage):     # Notice this function takes a single stage as an argument. You can use it to check the Verdict
                        # at any given stage, if you want.
    proposal = PrevStages(stage)[0].PrimeMove
    if proposal.Val == 'reason against':
        if proposal.Conc in stage.FScoreSit.CL.RE:
            return 'sustain'
        else:
            return 'fail'
    elif proposal.Val == 'reason for':
        if proposal.Conc in stage.FScoreSit.CL.AE:
            return 'sustain'
        else:
            return 'fail'

