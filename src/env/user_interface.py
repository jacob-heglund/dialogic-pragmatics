"""defines user interface
"""
import ast

from env.episode_runners import run_episode, run_episode_from_stage
from env.stage import manual_next_stage_infer


class EmptyClass(object):
    pass


class UserInterface():
    def __init__(self, lang, interactive=False) -> None:
        """
        defines user interface for DP1

        goal (str): Defines the moves made by agents in the dialogue. Defaults to 'argue_for'.
        """

        # TODO these should be turned into a config file / args
        self.args = EmptyClass()
        self.args.lang = lang

        # agent setup
        # cl agent
        self.args.cl_policy_name = "one_step_ahead"
        self.args.cl_inferential_theory_name = "random"

        # cr agent
        self.args.cr_policy_name = "minimize_ac"
        self.args.cr_inferential_theory_name = "random"

        # env setup
        self.args.target = "random"
        self.args.proposal = "undeclared"
        self.args.goal = "argue_for"


        if interactive == False:
            self.run_env()

        else:
            print('Welcome to the Dialogic Pragmatics Inquiry Interface!')
            print()
            run_type = input("Use default parameters? (y/n): ").strip().lower()
            if run_type == "n":
                self.run_env_manual()
            else:
                self.run_env_interactive()

    def run_env(self) -> None:
        # define a single msf shared by both agents

        # in standard RL we would write "for n in range(n_episodes)", but we're just 1 episode runs for now
        env = run_episode(self.args)

        print()
        env.show()
        print()

    def run_env_interactive(self) -> None:
        # define a single msf shared by both agents
        #TODO this should probably get pushed into episode_runners or the env itself
        msf = random_msf(language = self.lang)
        cl_agent = Agent(msf, policy_name="one_step_ahead", inferential_theory_name="default")
        cr_agent = Agent(msf, policy_name="minimize_ac", inferential_theory_name="default")

        # in standard RL we would write "for t in n_episodes here", but we're just doing a 1 episode version for now
        ep = run_episode(target='random', proposal='undeclared')

        print()
        ep.show()
        print()

        while True:
            if input('Walk through inquiry stage by stage? (y/n): ').strip().lower() != 'n':
                take_input = True
                i = 0
                while i < len(ep.stage_list):
                    print()
                    print('Stage', i, ':')
                    print()
                    ep.view_stage(stage_idx=i)

                    if i+1 == len(ep.stage_list):
                        print()
                        print('End of inquiry.')

                    if take_input:
                        print()
                        command = input('next (enter) / all / break / #: ').strip().lower()
                        if command == 'all' or command == 'a':
                            take_input = False
                        elif command == 'break' or command == 'b':
                            break
                        elif command.isnumeric():
                            i = int(command)
                            continue

                    i = i+1
                print()

            rerun = input('Rerun inquiry from a certain stage? (y/n/#): ').strip().lower()

            if rerun != 'y' and not rerun.isnumeric():
                break
            if rerun.isnumeric():
                stage_num = int(rerun)
            else:
                stage_num = int(input('Please enter the stage number you want to rerun from (i.e., the earliest stage that you would like to be different): '))

            agent = ep.stage_list[stage_num].agent

            manual_next = input('Would you like to specify a next move for ' + agent + '? (y/n): ')

            if manual_next == 'y':

                next_move = input('Please specify a next move for ' + agent + ', of form {1, 2, 3}⊨4 or {5, 6}#0 : ')

                if '⊨' not in next_move and '#' not in next_move:
                    next_stage = None
                    print('No valid move entered. ' + agent + ' will select its own next move.')
                    print()
                else:
                    if '⊨' in next_move:
                        (prem_string, conc_string) = next_move.strip(" ',").split("⊨")
                        val = 'reason for'
                    else:
                        (prem_string, conc_string) = next_move.strip(" ',").split("#")
                        val = 'reason against'

                    proposal = (frozenset(ast.literal_eval(prem_string)), int(conc_string))

                    prev_stage = ep.stage_list[stage_num-1]

                    next_stage = manual_next_stage_infer(prev_stage, proposal, val)

                    #target_num = int(input('Please enter the stage number that this move targets (e.g., the stage whose proposal it challenges) : '))
                    #target_stage = ep.stage_list[target_num]

                    #prag_sig = input("Please enter the pragmatic significance of this move. Options are 'premise challenge' or 'conclusion challenge': ").strip().lower()

                    #next_stage = manual_next_stage(prev_stage, target_stage, prag_sig, proposal, val)
            else:
                next_stage = None

            ep = run_episode_from_stage(ep, stage_num, next_stage)
            print()
            ep.show_full_table()
            print()

        if input('Export inferential theories? (y/n): ').strip().lower() == 'y':
            cl_filename = input("Enter filename for CL's inferential theory: ").strip()
            cr_filename = input("Enter filename for CR's inferential theory: ").strip()
            cl_agent.inferential_theory.export(filename=cl_filename)
            cr_agent.inferential_theory.export(filename=cr_filename)



"""
    This is definitely broken after all the changes I made
    def run_env_manual(self) -> None:
        msf = random_msf(language = self.lang)

        cl_for_size_or_chance = abs(float(input("Enter an integer to specify the number of reasons-for for CL, or a decimal between 0 and 1 to specify a chance: ")))
        if 0 < cl_for_size_or_chance < 1:
            cl_for_size = 'random'
            cl_for_chance = cl_for_size_or_chance
        else:
            cl_for_size = int(cl_for_size_or_chance)
            cl_for_chance = -1  # this value won't matter since size overrides chance

        cl_agn_size_or_chance = abs(float(input("Enter an integer to specify the number of reasons-against for CL, or a decimal between 0 and 1 to specify a chance: ")))
        if 0 < cl_agn_size_or_chance < 1:
            cl_agn_size = 'random'
            cl_agn_chance = cl_agn_size_or_chance
        else:
            cl_agn_size = int(cl_agn_size_or_chance)
            cl_agn_chance = -1  # this value won't matter since size overrides chance

        cr_for_size_or_chance = abs(float(input("Enter an integer to specify the number of reasons-for for CR, or a decimal between 0 and 1 to specify a chance: ")))
        if 0 < cr_for_size_or_chance < 1:
            cr_for_size = 'random'
            cr_for_chance = cr_for_size_or_chance
        else:
            cr_for_size = int(cr_for_size_or_chance)
            cr_for_chance = -1  # this value won't matter since size overrides chance

        cr_agn_size_or_chance = abs(float(input("Enter an integer to specify the number of reasons-against for CR, or a decimal between 0 and 1 to specify a chance: ")))
        if 0 < cr_agn_size_or_chance < 1:
            cr_agn_size = 'random'
            cr_agn_chance = cr_agn_size_or_chance
        else:
            cr_agn_size = int(cr_agn_size_or_chance)
            cr_agn_chance = -1  # this value won't matter since size overrides chance

        cl_inferential_theory = random_inferential_theory_generator(msf=msf, for_move_size=cl_for_size, against_move_size=cl_agn_size, for_move_chance=cl_for_chance, against_move_chance=cl_agn_chance)
        cr_inferential_theory = random_inferential_theory_generator(msf=msf, for_move_size=cr_for_size, against_move_size=cr_agn_size, for_move_chance=cr_for_chance, against_move_chance=cr_agn_chance)

        print("CL's inferential theory:")
        print()
        cl_inferential_theory.show()
        print()
        print("CR's inferential theory:")
        print()
        cr_inferential_theory.show()
        print()

        while True:
            target_or_proposal = input("Please specify an initial proposal (of form {1, 2, 3}⊨4) or a target (of form a_2), or enter 'random' for a random initial proposal: ").strip().lower()

            if target_or_proposal == 'random':
                target = 'random'
                proposal = 'undeclared'
                break
            elif target_or_proposal.startswith('a'):
                target = target_or_proposal
                proposal = 'undeclared' # this value won't matter since we are specifying target
                break
            elif target_or_proposal.strip(" ',").startswith('{'):
                (prem_string, conc_string) = target_or_proposal.strip(" ',").split("⊨")
                proposal = (ast.literal_eval(prem_string), int(conc_string))
                target = 'random' # this value won't matter since we are specifying proposal
                break
            else:
                print('Invalid input!')

        print("The following agent strategies are available: 'random', 'minimize_ac', and 'one_step_ahead'.")

        while True:
            cl_strat = input('Please enter a strategy for CL: ').strip()
            if cl_strat == 'random' or cl_strat == 'minimize_ac' or cl_strat == 'one_step_ahead':
                break
            else:
                print('Invalid input!')
                print("The following agent strategies are available: 'random', 'minimize_ac', and 'one_step_ahead'.")

        while True:
            cr_strat = input('Please enter a strategy for CR: ').strip()
            if cr_strat == 'random' or cr_strat == 'minimize_ac' or cr_strat == 'one_step_ahead':
                break
            else:
                print('Invalid input!')
                print("The following agent strategies are available: 'random', 'minimize_ac', and 'one_step_ahead'.")

        ep = run_episode(frame=msf, target=target, proposal=proposal, cl_strategy=cl_strat, cr_strategy=cr_strat, cl_inferential_theory=cl_inferential_theory, cr_inferential_theory=cr_inferential_theory)

"""