""" defines functions to run environment episodes
"""

import random
from agents.agent import Agent
from agents.msf import MSF
from env.inquiry import Inquiry
from env.stage import next_stage
from env.transition_function import first_move_for_random_premise, first_move_against_random_premise,\
                                    manual_initial_move_for,manual_initial_move_against,\
                                    random_first_move_for, random_first_move_against

import pdb


def run_episode(frame: MSF, cl_agent: Agent, cr_agent: Agent, target :str = 'random', proposal: str = 'undeclared', episode_goal: str ="argue_for"):
    """runs a single dialogue between two agents

    Args:
        episode_goal (str, optional): Defines the moves made by agents in the dialogue. Defaults to 'argue_for'.

    Returns:
        _type_: _description_
    """

    valid_episode_goals = ["argue_for", "argue_against"]
    if episode_goal not in valid_episode_goals:
        raise ValueError(f"Error: Inquiry goal must be one of {valid_episode_goals}.")

    # take first action to set up the env
    # input conclusion as a string, e.g. 'a_2'
    if proposal != 'undeclared' and target != 'random':
        print('You can either specify proposal, of form ([1,2,3],4), or target, of form \'a_2\', but not both.')

    elif target != 'random':
        if episode_goal == "argue_for":
            c = first_move_for_random_premise(frame = frame, conclusion = target,
                                            cl_inferential_theory = cl_agent.inferential_theory,
                                            cr_inferential_theory = cr_agent.inferential_theory)
        elif episode_goal == "argue_against":
            c = first_move_against_random_premise(frame = frame, target = target,
                                                cl_inferential_theory = cl_agent.inferential_theory,
                                                cr_inferential_theory = cr_agent.inferential_theory)

    elif proposal != 'undeclared':
        (a,b) = proposal
        if episode_goal == "argue_for":
            c = manual_initial_move_for(frame = frame, proposal = (frozenset(a), b), cl_inferential_theory = cl_agent.inferential_theory,
                                        cr_inferential_theory = cr_agent.inferential_theory)
        elif episode_goal == "argue_against":
            c = manual_initial_move_against(frame = frame, proposal = (frozenset(a), b), cl_inferential_theory = cl_agent.inferential_theory,
                                        cr_inferential_theory = cr_agent.inferential_theory)

    else:
        if episode_goal == "argue_for":
            c = random_first_move_for(frame = frame, cl_inferential_theory = cl_agent.inferential_theory, cr_inferential_theory = cr_agent.inferential_theory)
        elif episode_goal == "argue_against":
            c = random_first_move_against(frame = frame, cl_inferential_theory = cl_agent.inferential_theory, cr_inferential_theory = cr_agent.inferential_theory)

        lst = [c]


    # take the rest of the actions
    while c.available_moves['for'] != frozenset() or c.available_moves['against'] != frozenset():
        c = next_stage(last_stage = c, cl_strategy = cl_agent.policy_name, cr_strategy = cr_agent.policy_name)
        lst.append(c)

    result = Inquiry(msf = c.msf, list_of_stages = lst, cl_inferential_theory = cl_agent.inferential_theory, cr_inferential_theory = cr_agent.inferential_theory, cl_strategy =
    cl_agent.policy_name, cr_strategy = cr_agent.policy_name)

    return result


def run_episode_from_stage(orig_inq, stage_num, next_stage_flag = None, cl_strategy = None, cr_strategy = None):
    if not cl_strategy:
        cl_strategy = orig_inq.cl_strategy
    if not cr_strategy:
        cr_strategy = orig_inq.cr_strategy

    stage_list = orig_inq.list_of_stages[:stage_num]

    if next_stage_flag:
        stage_list.append(next_stage_flag)

    stage = stage_list[-1]

    while stage.available_moves['for'] != frozenset() or stage.available_moves['against'] != frozenset():
        stage = next_stage_flag(last_stage=stage, cl_strategy=cl_strategy, cr_strategy=cr_strategy)
        stage_list.append(stage)

    return Inquiry(msf = stage.msf, list_of_stages = stage_list, cl_inferential_theory=orig_inq.cl_inferential_theory, cr_inferential_theory = orig_inq.cr_inferential_theory, cl_strategy = cl_strategy, cr_strategy = cr_strategy)
