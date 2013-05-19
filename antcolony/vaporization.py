from simulation_event import AbstractSimulationEvent

class AbstractPheromoneVaporization(AbstractSimulationEvent):
    PERIOD = 100
    TRIGGER_LEVEL = 50
    def __init__(self, ant_count, end_time=PERIOD):
        self.end_time = end_time
        self.ant_count = ant_count
    def process_end(self, reality, stats):
        changed = []
        avg_pheromone = reality.world.get_average_pheromone_level()
        max_pheromone = reality.world.get_max_pheromone_level()
        if max_pheromone/(avg_pheromone or 1) >= self.TRIGGER_LEVEL:
            for edge in reality.world.edges:
                for edge_end in (edge.a_end, edge.b_end):
                    new = self.compute_new_value(edge_end.pheromone_level)
                    if edge_end.pheromone_level!=new:
                        changed.append(edge_end.edge)
                        edge_end.pheromone_level = new
        return self.__class__(self.ant_count, self.end_time+self.PERIOD), frozenset(changed)
    def compute_new_value(self, pheromone_level):
        raise NotImplementedError()

class MultiplierPheromoneVaporization(AbstractPheromoneVaporization):
    MULTIPLIER = 0.8
    def compute_new_value(self, pheromone_level):
        return max(0.0, pheromone_level*self.MULTIPLIER)

class ExponentPheromoneVaporization(AbstractPheromoneVaporization):
    EXPONENT = 0.95
    def compute_new_value(self, pheromone_level):
        return max(0.0, pheromone_level**self.EXPONENT)

