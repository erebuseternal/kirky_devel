class Issue(Exception):
    def __init__(self, problem):
        self.problem = problem

    def __str__(self):
        return 'ERROR: the problem was: %s' % self.problem