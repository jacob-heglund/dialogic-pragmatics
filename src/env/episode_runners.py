""" defines functions to run environment episodes
"""

from env.env import Environment
import pdb


def run_episode(args: object):
    """runs a single dialogue between agents

    Args:
        args: object class that contains the env setup args as attributes

    Returns:
        _type_: _description_
    """

    env = Environment(args.lang, args.target, args.proposal, args.goal, args.cl_inferential_theory_name, args.cr_inferential_theory_name, args.cl_policy_name, args.cr_policy_name)

    # run the episode
    done = False
    curr_stage = None

    while not done:
        curr_agent = env.get_curr_agent(curr_stage)
        action = curr_agent.get_action(curr_stage)
        next_stage, done = env.step(action)

        # update for next loop
        curr_stage = next_stage

    return env


def run_episode_from_stage(orig_inq, stage_num, next_stage_flag = None, cl_strategy = None, cr_strategy = None):
    if not cl_strategy:
        cl_strategy = orig_inq.cl_strategy
    if not cr_strategy:
        cr_strategy = orig_inq.cr_strategy

    stage_list = orig_inq.stage_list[:stage_num]

    if next_stage_flag:
        stage_list.append(next_stage_flag)

    stage = stage_list[-1]

    while stage.available_moves['for'] != frozenset() or stage.available_moves['against'] != frozenset():
        stage = next_stage_flag(prev_stage=stage, cl_strategy=cl_strategy, cr_strategy=cr_strategy)
        stage_list.append(stage)

    return Environment(msf = stage.msf, stage_list = stage_list, cl_inferential_theory=orig_inq.cl_inferential_theory, cr_inferential_theory = orig_inq.cr_inferential_theory, cl_strategy = cl_strategy, cr_strategy = cr_strategy)
