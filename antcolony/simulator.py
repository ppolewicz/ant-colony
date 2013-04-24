import heapq

from edge import DummyEdgeEnd

def avg(iterable):
    return sum(iterable) / len(iterable)

class AbstractSimulationEvent(object):
    def process_start(self):
        return tuple()
    def process_end(self, world, stats):
        return tuple()

class PheromoneVaporization(AbstractSimulationEvent):
    #AMOUNT = 1 # per ant
    AMOUNT = 0 # per ant XXX
    PERIOD = 200
    def __init__(self, end_time, ant_count):
        self.end_time = end_time
        self.ant_count = ant_count
    def process_end(self, world, stats):
        changed = []
        for edge in world.edges:
            for edge_end in (edge.a_end, edge.b_end):
                new = max(0, edge_end.pheromone_level - (self.AMOUNT*self.ant_count))
                if edge_end.pheromone_level!=new:
                    edge_end.pheromone_level = new
                    changed.append(edge_end.edge)
        return PheromoneVaporization(self.end_time+self.PERIOD, self.ant_count), tuple(changed)

class AbstractAntMove(AbstractSimulationEvent):
    def __init__(self, ant, origin, destination, end_time, pheromone_to_drop, trip_stats):
        self.ant = ant
        self.origin = origin
        self.destination = destination
        self.end_time = end_time
        self.pheromone_to_drop = pheromone_to_drop
        self.trip_stats = trip_stats
    def process_start(self):
        self.origin.drop_pheromone(self.pheromone_to_drop)
        #return (self.origin.edge,)
        return (self.origin.edge, self.origin.point)
    def process_end(self, world, stats):
        changed = [self.destination.edge]
        self.destination.drop_pheromone(self.pheromone_to_drop)
        if not self.destination.point.is_anthill() and self.destination.point.food > 0 and not self.ant.food:
            changed.append(self.destination.point)
            self.trip_stats.food_found()
            self.destination.point.food -= 1
            self.ant.food += 1
            stats.food_found(self.trip_stats)
            stats.present()
        elif self.destination.point.is_anthill() and self.ant.food:
            changed.append(self.destination.point)
            self.destination.point.food += self.ant.food
            self.trip_stats.back_home()
            new_ant = self.ant.__class__(self.ant.world_parameters)
            return AntRestartMove(new_ant, anthill=DummyEdgeEnd(self.destination.point), end_time=world.elapsed_time), tuple(changed)
        new_destination_edge, pheromone_to_drop = self.ant.tick(self.destination.point)
        self.trip_stats.normal_move(new_destination_edge.cost)
        new_destination = new_destination_edge.get_other_end(self.destination)
        end_time = world.elapsed_time + new_destination_edge.cost
        return AntMove(
            ant=self.ant,
            origin=self.destination,
            destination=new_destination,
            end_time=end_time,
            pheromone_to_drop=pheromone_to_drop,
            trip_stats=self.trip_stats,
        ), tuple(changed)
    def __cmp__(self, other):
        return self.end_time - other.end_time
    def __repr__(self):
        return '%s@%s' % (self.__class__.__name__, self.end_time,)

class AntRestartMove(AbstractAntMove):
    def __init__(self, ant, anthill, end_time):
        super(AntRestartMove, self).__init__(ant, None, anthill, end_time=end_time, pheromone_to_drop=0, trip_stats=TripStats())
    def process_start(self):
        return tuple()

class AntStartMove(AntRestartMove):
    def __init__(self, ant, anthill):
        super(AntStartMove, self).__init__(ant, anthill, end_time=0)

class AntMove(AbstractAntMove):
    pass

class TripStats(object):
    def __init__(self):
        self.food_found_after = 0, 0
        self.total_cost = 0
        self.total_moves = 0
    def food_found(self):
        self.food_found_after = self.total_moves, self.total_cost
    def normal_move(self, cost):
        self.total_moves += 1
        self.total_cost += cost
    def back_home(self):
        #print 'moves: %s, cost: %s, to find: %s' % (self.total_moves, self.total_cost, self.food_found_after)
        pass

class QueenStats(object):
    def __init__(self, reality, number_of_ants):
        self.reality = reality
        self.food_discovered = 0
        self.moves_leading_to_food_being_found = 0
        self.number_of_ants = number_of_ants
        self.best_finding_cost = 999999999
    def food_found(self, trip_stats):
        self.food_discovered += 1
        self.moves_leading_to_food_being_found += trip_stats.food_found_after[0]
        self.best_finding_cost = min(self.best_finding_cost, trip_stats.food_found_after[1])
    def present(self):
        avg_cost = (self.reality.world.elapsed_time*self.number_of_ants)/self.food_discovered
        avg_moves = self.moves_leading_to_food_being_found/self.food_discovered
        avg_pheromone = avg([edge.a_end.pheromone_level + edge.b_end.pheromone_level for edge in self.reality.world.edges]) / 2
        print 'food found: %d, best: %.3f, avg. pheromone: %.3f, avg. moves to find: %d, avg. cost to find: %.3f, time: %d' % (self.food_discovered, self.best_finding_cost, avg_pheromone, avg_moves, avg_cost, self.reality.world.elapsed_time)

class Simulation(object):
    def __init__(self, reality, antmoves, stats):
        self.reality = reality
        self.antmoves = antmoves
        heapq.heapify(antmoves)
        self.stats = stats
        self.ticks = 0
    def advance(self):
        print 'ticks', self.ticks
        if self.reality.is_resolved():
            return [], True
        return self.tick(), False
    def tick(self):
        ant_move = heapq.heappop(self.antmoves)
        self.reality.world.elapsed_time = ant_move.end_time # simulation is now at the point of ant_move.ant arriving at ant_move.destination
        #print 'processing ant_move', ant_move.end_time
        #print '[%f] %s is moving to %s, %s' % (self.reality.world.elapsed_time, ant_move.ant, ant_move.destination.point, ant_move.ant.food)
        #print sum([food_point.food for food_point in self.reality.world.get_food_points()])
        new_antmove, changed_items_end = ant_move.process_end(self.reality.world, self.stats)
        assert not self.reality.world.elapsed_time > ant_move.end_time
        changed_items_start = new_antmove.process_start()
        assert changed_items_start is not None, new_antmove
        heapq.heappush(self.antmoves, new_antmove)
        self.ticks += 1
        return changed_items_start + changed_items_end

class Simulator(object):
    def __init__(self, reality):
        self.reality = reality
    def simulate(self, queen, amount_of_ants, reality):
        ant_classes = queen.spawn_ants(amount_of_ants)
        ants = [ant_class(self.reality.environment_parameters) for ant_class in ant_classes]
        anthills = reality.world.get_anthills()
        antmoves = list(self.get_start_antmoves(ants, anthills))
        antmoves.append(PheromoneVaporization(PheromoneVaporization.PERIOD, len(ants)))
        stats = QueenStats(reality, len(ants))
        return Simulation(reality, antmoves, stats)
    def get_results(self, simulation):
        ticks = simulation.ticks
        elapsed_time = self.reality.world.elapsed_time
        self.reality.world.reset()
        return elapsed_time, ticks
    @classmethod
    def run_simulation(cls, simulation):
        while not simulation.advance():
            pass
    def get_start_antmoves(self, ants, anthills):
        """ iterator """
        counter = 0
        number_of_anthills = len(anthills)
        anthills = list(anthills)
        for ant in ants:
            anthill = anthills[counter % number_of_anthills]
            yield AntStartMove(ant, DummyEdgeEnd(anthill))
            counter += 1

