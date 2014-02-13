from simulation_event import AbstractSimulationEvent

class AbstractPeriodicRealityProcessor(AbstractSimulationEvent):
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
        raise NotImplementedError()

class AbstractEdgeProcessor(AbstractPeriodicRealityProcessor):
    def process_end(self, reality, stats):
        changed_pheromone_edges = []
        avg_pheromone = reality.world.get_average_pheromone_level()
        max_pheromone = reality.world.get_max_pheromone_level()
        if max_pheromone/(avg_pheromone or 1) >= self.trigger_level:
            for edge in reality.world.edges:
                for edge_end in (edge.a_end, edge.b_end):
                    new = self.compute_new_pheromone(edge_end.pheromone_level)
                    if edge_end.pheromone_level!=new:
                        changed_pheromone_edges.append(edge_end.edge)
                        edge_end.pheromone_level = new
                edge.cost = self.compute_new_cost(edge.cost)
        return self.__class__(self.trigger_level, self.rate, self.end_time+self.PERIOD), frozenset(changed_pheromone_edges)
    def compute_new_cost(self, old_cost):
        raise NotImplementedError()
    def compute_new_pheromone(self, old_pheromone_level):
        raise NotImplementedError()

class AbstractPeriodicEdgeCostModifier(AbstractPeriodicRealityProcessor):
    def compute_new_pheromone(self, old_pheromone_level):
        return old_pheromone_level


