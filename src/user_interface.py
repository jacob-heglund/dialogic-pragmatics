"""defines user interface
"""
import ast

from msf import random_msf
from inferential_theory import random_inferential_theory_generator
from inquiry import inquiry_for, inquiry_from_stage
from stage import manual_next_stage_infer


class UserInterface():
    def __init__(self, lang) -> None:
        self.lang = lang

    def run(self) -> None:
        """
        defines user interface for DP1
        """
        print('Welcome to the Dialogic Pragmatics Inquiry Interface!')
        print()

        msf = random_msf(language = self.lang)

        if input("Use default parameters? (y/n): ").strip().lower() == 'n':
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

            print("The following agent strategies are available: 'random', 'minimize ac', and 'one step ahead'.")

            while True:
                cl_strat = input('Please enter a strategy for CL: ').strip()
                if cl_strat == 'random' or cl_strat == 'minimize ac' or cl_strat == 'one step ahead':
                    break
                else:
                    print('Invalid input!')
                    print("The following agent strategies are available: 'random', 'minimize ac', and 'one step ahead'.")

            while True:
                cr_strat = input('Please enter a strategy for CR: ').strip()
                if cr_strat == 'random' or cr_strat == 'minimize ac' or cr_strat == 'one step ahead':
                    break
                else:
                    print('Invalid input!')
                    print("The following agent strategies are available: 'random', 'minimize ac', and 'one step ahead'.")

            inq = inquiry_for(frame=msf, target=target, proposal=proposal, cl_strategy=cl_strat, cr_strategy=cr_strat, cl_inferential_theory=cl_inferential_theory, cr_inferential_theory=cr_inferential_theory)
        else: # use default params
            cl_inferential_theory = random_inferential_theory_generator(msf=msf, for_move_size='random', against_move_size='random', for_move_chance=1 / 2, against_move_chance=1 / 2)
            cr_inferential_theory = random_inferential_theory_generator(msf=msf, for_move_size='random', against_move_size='random', for_move_chance=1 / 2, against_move_chance=1 / 2)
            inq = inquiry_for(frame=msf, target='random', proposal='undeclared', cl_strategy='one step ahead', cr_strategy='minimize ac', cl_inferential_theory=cl_inferential_theory, cr_inferential_theory=cr_inferential_theory)

        print()
        inq.show()
        print()

        while True:
            if input('Walk through inquiry stage by stage? (y/n): ').strip().lower() != 'n':
                take_input = True
                i = 0
                while i < len(inq.list_of_stages):
                    print()
                    print('Stage', i, ':')
                    print()
                    inq.viewstage(stage=i)

                    if i+1 == len(inq.list_of_stages):
                        print()
                        print('End of inquiry.')

                    if take_input:
                        print()
                        command = input('next (reTURN) / all / break / #: ').strip().lower()
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

            agent = inq.list_of_stages[stage_num].agent

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

                    last_stage = inq.list_of_stages[stage_num-1]

                    next_stage = manual_next_stage_infer(last_stage, proposal, val)

                    #target_num = int(input('Please enter the stage number that this move targets (e.g., the stage whose proposal it challenges) : '))
                    #target_stage = inq.list_of_stages[target_num]

                    #prag_sig = input("Please enter the pragmatic significance of this move. Options are 'premise challenge' or 'conclusion challenge': ").strip().lower()

                    #next_stage = manual_next_stage(last_stage, target_stage, prag_sig, proposal, val)
            else:
                next_stage = None

            inq = inquiry_from_stage(inq, stage_num, next_stage)
            print()
            inq.show_full_table()
            print()

        if input('Export inferential theories? (y/n): ').strip().lower() == 'y':
            cl_filename = input("Enter filename for CL's inferential theory: ").strip()
            cr_filename = input("Enter filename for CR's inferential theory: ").strip()
            cl_inferential_theory.export(filename=cl_filename)
            cr_inferential_theory.export(filename=cr_filename)
