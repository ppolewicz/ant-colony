import random

class AbstractAnt(object):
    def __init__(self, world_parameters):
        self.world_parameters = world_parameters
        self.food = 0

    def tick(self, current_point):
        """
           returns the result of Ant's decision process.
           returns two element tuple
           first element is the target point
           second element is a number representing the amount of pheromone dropped on the way to the target
           the amount of pheromone has to be within the world's limits
        """
        raise NotImplementedError()

class PurelyRandomAnt(AbstractAnt):
    """ ant that selects edges randomly. Very inefficient (unless very lucky). """
    def tick(self, current_point):
        choices = current_point.get_edges()
        target = random.choice(choices)
        return target, self.world_parameters.max_pheromone_dropped_by_ant

class RandomAnt(PurelyRandomAnt):
    def tick(self, current_point):
        if self.food:
            anthill = current_point.get_anthill()
            if anthill is not None:
                return anthill, self.world_parameters.max_pheromone_dropped_by_ant

