import random
from simulation_event import AbstractSimulationEvent

class AbstractPeriodicRealityProcessor(AbstractSimulationEvent):
    PERIOD = 100
    def __init__(self, end_time=PERIOD):
        self.end_time = end_time
    def reset(self):
        self.end_time = self.PERIOD
    def set_ant_count(self, ant_count):
        self.ant_count = ant_count
    def process_end(self, reality, stats):
        raise NotImplementedError('%s did not implement a mandatory method' % (self.__class__.__name__,))

class AbstractPeriodicEdgeModifier(AbstractPeriodicRealityProcessor):
    PERIOD = 10000
    def __init__(self, cost_trigger_level, cost_trigger_level_addition, **kwargs):
        super(AbstractPeriodicEdgeModifier, self).__init__(**kwargs)
        self.cost_trigger_level = cost_trigger_level
        self.cost_trigger_level_addition = cost_trigger_level_addition
    def process_end(self, reality, stats):
        next_trigger_level = self.cost_trigger_level
        #print 'processing %s' % (self.__class__.__name__,), self.cost_trigger_level, reality.world.completion_level()
        if reality.world.completion_level() >= self.cost_trigger_level:
            print self.__class__.__name__, 'processing edges at', reality.world.completion_level()
            next_trigger_level += self.cost_trigger_level_addition
            for edge in reality.world.edges:
                edge.cost = self.compute_new_cost(edge.cost)
        return self.__class__(
                next_trigger_level,
                self.cost_trigger_level_addition,
                end_time=self.end_time+self.PERIOD), frozenset()
    def compute_new_cost(self, old_cost):
        raise NotImplementedError()

class EdgeMutator(AbstractPeriodicEdgeModifier):
    def compute_new_cost(self, old_cost):
        return old_cost * 2.0 / random.randint(1, 4)

class AbstractPeriodicEdgePheromoneModifier(AbstractPeriodicEdgeModifier):
    def __init__(self, trigger_level, **kwargs):
        super(AbstractPeriodicEdgeModifier, self).__init__(**kwargs)
        self.pheromone_trigger_level = trigger_level
    def process_end(self, reality, stats):
        changed_pheromone_edges = []
        avg_pheromone = reality.world.get_average_pheromone_level()
        max_pheromone = reality.world.get_max_pheromone_level()
        if max_pheromone/(avg_pheromone or 1) >= self.pheromone_trigger_level:
            for edge in reality.world.edges:
                for edge_end in (edge.a_end, edge.b_end):
                    new = self.compute_new_pheromone(edge_end.pheromone_level)
                    if edge_end.pheromone_level!=new:
                        changed_pheromone_edges.append(edge_end.edge)
                        edge_end.pheromone_level = new
        return self.__class__(self.pheromone_trigger_level, end_time=self.end_time+self.PERIOD), frozenset(changed_pheromone_edges)
    def compute_new_pheromone(self, old_pheromone_level):
        raise NotImplementedError()


