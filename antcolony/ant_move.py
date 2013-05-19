from edge import DummyEdgeEnd
from simulation_event import AbstractSimulationEvent
from stats import TripStats

class AbstractAntMove(AbstractSimulationEvent):
    def __init__(self, ant, origin, destination, end_time, pheromone_to_drop, trip_stats):
        self.ant = ant
        self.origin = origin
        self.destination = destination
        if self.origin is not None and self.destination is not None:
            if self.origin.edge is not None and self.destination.edge is not None:
                #print 'origin', self.origin
                #print 'destination', self.destination
                assert self.origin.edge == self.destination.edge
        self.end_time = end_time
        self.pheromone_to_drop = pheromone_to_drop
        self.trip_stats = trip_stats
    def process_start(self):
        self.origin.drop_pheromone(self.pheromone_to_drop)
        return frozenset((self.origin.edge, self.origin.point))
    def process_end(self, reality, stats):
        changed = [self.destination.edge]
        self.trip_stats.edge_visited(self.destination.edge)
        self.destination.drop_pheromone(self.pheromone_to_drop)
        if not self.destination.point.is_anthill() and self.destination.point.food > 0 and not self.ant.food: # ant has found the food
            changed.append(self.destination.point)
            self.trip_stats.food_found()
            self.destination.point.food -= 1
            self.ant.food += 1
            stats.food_found(self.trip_stats)
            stats.present()
        elif self.destination.point.is_anthill(): # ant has returned to the anthill
            if self.ant.food: # with food
                changed.append(self.destination.point)
                self.destination.point.food += self.ant.food
                self.trip_stats.back_home()
                new_ant = self.ant.__class__(self.ant.world_parameters)
                return AntRestartMove(new_ant, anthill=DummyEdgeEnd(self.destination.point), end_time=reality.world.elapsed_time), frozenset(changed)
            else: # with no food
                self.trip_stats.reset_route()
        new_destination_edge, pheromone_to_drop = self.ant.tick(self.destination.point)
        assert new_destination_edge in (end.edge for end in self.destination.point.edge_ends), 'Illegal ant move'
        assert reality.environment_parameters.min_pheromone_dropped_by_ant <= pheromone_to_drop <= reality.environment_parameters.max_pheromone_dropped_by_ant, 'Illegal ant pheromone drop: %s' % (repr(pheromone_to_drop),)
        self.trip_stats.normal_move(new_destination_edge.cost)
        new_destination = new_destination_edge.get_other_end_by_point(self.destination.point)
        origin = new_destination_edge.get_other_end(new_destination)
        end_time = reality.world.elapsed_time + new_destination_edge.cost
        return AntMove(
            ant=self.ant,
            origin=origin,
            destination=new_destination,
            end_time=end_time,
            pheromone_to_drop=pheromone_to_drop,
            trip_stats=self.trip_stats,
        ), frozenset(changed)
    def __cmp__(self, other):
        return self.end_time - other.end_time
    def __repr__(self):
        return '%s@%s' % (self.__class__.__name__, self.end_time,)

class AntRestartMove(AbstractAntMove):
    def __init__(self, ant, anthill, end_time):
        super(AntRestartMove, self).__init__(ant, None, anthill, end_time=end_time, pheromone_to_drop=0, trip_stats=TripStats())
    def process_start(self):
        return frozenset()

class AntStartMove(AntRestartMove):
    def __init__(self, ant, anthill):
        super(AntStartMove, self).__init__(ant, anthill, end_time=0)

class AntMove(AbstractAntMove):
    pass

