"""defines scoring
"""

class Score:
    def __init__(self, Subject, AC, RC, AE, RE):
        self.Subject = Subject
        self.AC = AC    #accept committed
        self.RC = RC    #reject committed
        self.AE = AE    #accept entitled
        self.RE = RE    #reject entitled


class ScoreSit:
    def __init__(self, CL_Score, CR_Score):
        self.CL = CL_Score
        self.CR = CR_Score
        self.CommonGround = frozenset.intersection(self.CL.AC, self.CR.AC)



