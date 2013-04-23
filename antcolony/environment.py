class EnvironmentParameters(object):
    def __init__(self, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant, anthill, num_points, num_edges):
        self.min_pheromone_dropped_by_ant = min_pheromone_dropped_by_ant
        self.max_pheromone_dropped_by_ant = max_pheromone_dropped_by_ant
        self.anthill = anthill
        self.num_points = num_points
        self.num_edges = num_edges
    def __repr__(self):
        return """EnvironmentParameters:
    min_pheromone_dropped_by_ant: %s
    max_pheromone_dropped_by_ant: %s
                         anthill: %s
                      num_points: %s
                       num_edges: %s""" % (self.min_pheromone_dropped_by_ant, self.max_pheromone_dropped_by_ant, self.anthill, self.num_points, self.num_edges)
    @classmethod
    def from_world(cls, world, min_pheromone_dropped_by_ant, max_pheromone_dropped_by_ant):
        return cls(
            min_pheromone_dropped_by_ant,
            max_pheromone_dropped_by_ant,
            world.get_anthill(),
            len(world.points),
            len(world.edges)
        )

