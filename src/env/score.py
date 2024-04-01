"""defines scoring
"""

class Score:
    def __init__(self, subject, ac, rc, ae, re):
        self.subject = subject
        self.ac = ac    # accept committed
        self.rc = rc    # reject committed
        self.ae = ae    # accept entitled
        self.re = re    # reject entitled


class ScoreSit:
    def __init__(self, cl_score, cr_score):
        self.cl = cl_score
        self.cr = cr_score
        self.common_ground = frozenset.intersection(self.cl.ac, self.cr.ac)
