class EnvironmentParameters(object):
    def __init__(self, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, anthill):
        self.min_pheromone_dropped_by_ant = min_pheromone_dropped_by_ant
        self.max_pheromone_dropped_by_ant = max_pheromone_dropped_by_ant
        self.anthill = anthill
    def __repr__(self):
        return """EnvironmentParameters:
    min_pheromone_dropped_by_ant: %s
    max_pheromone_dropped_by_ant: %s
                         anthill: %s""" % (self.min_pheromone_dropped_by_ant, self.max_pheromone_dropped_by_ant, self.anthill)
    @classmethod
    def from_world(cls, world, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant):
        return cls(min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, world.get_anthill())

