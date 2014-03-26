import math
from periodic_processor import AbstractPeriodicEdgePheromoneModifier

class AbstractPheromoneVaporization(AbstractPeriodicEdgePheromoneModifier):
    pass

class MultiplierPheromoneVaporization(AbstractPheromoneVaporization):
    MULTIPLIER = 0.8
    def compute_new_pheromone(self, old_pheromone_level):
        return max(0.0, old_pheromone_level*self.MULTIPLIER)

class ExponentPheromoneVaporization(AbstractPheromoneVaporization):
    # suspect this works well for values greater than 1
    EXPONENT = 0.95
    def compute_new_pheromone(self, old_pheromone_level):
        return max(0.0, old_pheromone_level**self.EXPONENT)

class LogarithmPheromoneVaporization(AbstractPheromoneVaporization):
    def compute_new_pheromone(self, old_pheromone_level):
        return max(0.0, math.log(old_pheromone_level+1))

