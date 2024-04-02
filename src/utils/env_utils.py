"""basic environment utilities
"""
def switch_agents(x):
    """ This flips the agents: sending 'CL' to 'CR' and 'CR' to 'CL' """
    if x == 'CL':
        agent_name = 'CR'
    else:
        agent_name = 'CL'

    return agent_name

def get_prev_stages(stage):
    # This gives the list of all previous stages, given a stage, in increasing order of turn_idx, i.e. the initial stage
    # has index 0, and so on.
    prev_stages = []
    s = stage
    while s.prev_stage is not None:
        prev_stages.append(s.prev_stage)
        s = s.prev_stage
    prev_stages.reverse()
    return prev_stages


def get_verdict(stage):
    # Notice this function takes a single stage as an argument. You can use it to check the verdict
    # at any given stage, if you want.
    proposal = get_prev_stages(stage)[0].prime_move
    if proposal.val == 'reason against':
        if proposal.conc in stage.f_score_sit.cl.re:
            val = 'sustain'
        else:
            val = 'fail'
    elif proposal.val == 'reason for':
        if proposal.conc in stage.f_score_sit.cl.ae:
            val = 'sustain'
        else:
            val = 'fail'

    return val

