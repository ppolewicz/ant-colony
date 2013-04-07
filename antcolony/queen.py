class Queen(object):
    pass

class QueenInWorldPerformance(object):
    def __init__(self, queen, world):
        self.queen = queen
        self.world = world

class QueenCombinedPerformance(object):
    pass

class QueenEvaluator(object):
    pass

class BasicQueen(object):
    def __init__(self, ant_class):
        self.ant_class = ant_class
    def spawn_ants(self, amount_of_ants):
        return [self.ant_class] * amount_of_ants

