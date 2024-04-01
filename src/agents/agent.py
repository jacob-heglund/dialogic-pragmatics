from agents.inferential_theory import InferentialTheory, random_inferential_theory_generator


class Agent():
    def __init__(self, msf, policy_name="random", inferential_theory_name="default") -> None:
        self.msf = msf
        self.valid_policy_names = ["random", "minimize_ac", "one_step_ahead"]
        if policy_name in self.valid_policy_names:
            self.policy_name = policy_name
        else:
            raise ValueError(f"Error: Agent policy must be one of {self.valid_policy_names}.")


        self.valid_inferential_theory_names = ["default", "random"]
        self.inferential_theory_name = inferential_theory_name

        self.inferential_theory = None
        self._build_inferential_theory()


    def _build_inferential_theory(self):

        if self.inferential_theory_name == "default":
            self.inferential_theory = InferentialTheory(self.msf.for_move, self.msf.against_move)

        elif self.inferential_theory_name == "random":
            self.inferential_theory = random_inferential_theory_generator(msf=self.msf, for_move_size="random", against_move_size="random", for_move_chance=0.5, against_move_chance=0.5)

        else:
            raise ValueError(f"Error: Inferential theory must be one of {self.valid_inferential_theory_names}.")

