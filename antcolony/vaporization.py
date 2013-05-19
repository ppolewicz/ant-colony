from simulation_event import AbstractSimulationEvent
import math

class AbstractPheromoneVaporization(AbstractSimulationEvent):
    PERIOD = 100
    def __init__(self, trigger_level, rate=None, end_time=PERIOD):
        self.end_time = end_time
        self.rate = rate
        self.trigger_level = trigger_level
    def set_rate(self, rate):
        self.rate = rate
    def reset(self):
        self.end_time = self.PERIOD
        self.rate = None
    def process_end(self, reality, stats):
        changed = []
        avg_pheromone = reality.world.get_average_pheromone_level()
        max_pheromone = reality.world.get_max_pheromone_level()
        if max_pheromone/(avg_pheromone or 1) >= self.trigger_level:
            for edge in reality.world.edges:
                for edge_end in (edge.a_end, edge.b_end):
                    new = self.compute_new_value(edge_end.pheromone_level)
                    if edge_end.pheromone_level!=new:
                        changed.append(edge_end.edge)
                        edge_end.pheromone_level = new
        return self.__class__(self.trigger_level, self.rate, self.end_time+self.PERIOD), frozenset(changed)
    def compute_new_value(self, pheromone_level):
        raise NotImplementedError()

class MultiplierPheromoneVaporization(AbstractPheromoneVaporization):
    MULTIPLIER = 0.8
    def compute_new_value(self, pheromone_level):
        return max(0.0, pheromone_level*self.MULTIPLIER)

class ExponentPheromoneVaporization(AbstractPheromoneVaporization):
    # suspect this works well for values greater than 1
    EXPONENT = 0.95
    def compute_new_value(self, pheromone_level):
        return max(0.0, pheromone_level**self.EXPONENT)

class LogarithmPheromoneVaporization(AbstractPheromoneVaporization):
    def compute_new_value(self, pheromone_level):
        return max(0.0, math.log(pheromone_level+1))

