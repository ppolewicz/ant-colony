import os
import json
import heapq

import ant
from queen import BasicQueen
from reality_factory import RealityFactory
from edge import DummyEdgeEnd

class AbstractAntMove(object):
    def __init__(self, ant, origin, destination, end_time, pheromone_to_drop):
        self.ant = ant
        self.origin = origin
        self.destination = destination
        self.end_time = end_time
        self.pheromone_to_drop = pheromone_to_drop
    def process_start(self):
        self.origin.drop_pheromone(self.pheromone_to_drop)
    def process_end(self, world):
        self.destination.drop_pheromone(self.pheromone_to_drop)
        new_destination_edge, pheromone_to_drop = self.ant.tick(self.destination.point)
        if not self.destination.point.is_anthill() and self.destination.point.food > 0 and not self.ant.food:
            self.destination.point.food -= 1
            self.ant.food += 1
        elif self.destination.point.is_anthill() and self.ant.food:
            self.destination.point.food += self.ant.food
            new_ant = self.ant.__class__(self.ant.world_parameters)
            return AntRestartMove(new_ant, anthill=DummyEdgeEnd(self.destination.point), end_time=world.elapsed_time)
        new_destination = new_destination_edge.get_other_end(self.destination)
        end_time = world.elapsed_time + new_destination_edge.cost
        return AntMove(ant=self.ant, origin=self.destination, destination=new_destination, end_time=end_time, pheromone_to_drop=pheromone_to_drop)
    def __cmp__(self, other):
        return self.end_time - other.end_time
    def __repr__(self):
        return '%s@%s' % (self.__class__.__name__, self.end_time,)

class AntRestartMove(AbstractAntMove):
    def __init__(self, ant, anthill, end_time):
        super(AntRestartMove, self).__init__(ant, None, anthill, end_time=end_time, pheromone_to_drop=0)
    def process_start(self):
        pass

class AntStartMove(AntRestartMove):
    def __init__(self, ant, anthill):
        super(AntStartMove, self).__init__(ant, anthill, end_time=0)

class AntMove(AbstractAntMove):
    pass

class Simulation(object):
    def __init__(self, reality):
        self.reality = reality
    def run(self, queen, amount_of_ants):
        ant_classes = queen.spawn_ants(amount_of_ants)
        ants = [ant_class(self.reality.environment_parameters) for ant_class in ant_classes]
        anthills = reality.world.get_anthills()
        antmoves = list(self.get_start_antmoves(ants, anthills))
        heapq.heapify(antmoves)
        ticks = 0
        while not self.reality.is_resolved():
            antmoves = self.tick(antmoves)
            ticks += 1
        elapsed_time = self.reality.world.elapsed_time
        self.reality.world.reset()
        return elapsed_time, ticks
    def get_start_antmoves(self, ants, anthills):
        """ iterator """
        counter = 0
        number_of_anthills = len(anthills)
        anthills = list(anthills)
        for ant in ants:
            anthill = anthills[counter % number_of_anthills]
            yield AntStartMove(ant, DummyEdgeEnd(anthill))
            counter += 1
    def tick(self, antmoves):
        ant_move = heapq.heappop(antmoves)
        self.reality.world.elapsed_time = ant_move.end_time # simulation is now at the point of ant_move.ant arriving at ant_move.destination
        #print 'processing ant_move', ant_move.end_time
        #print '[%f] %s is moving to %s, %s' % (self.reality.world.elapsed_time, ant_move.ant, ant_move.destination.point, ant_move.ant.food)
        #print sum([food_point.food for food_point in self.reality.world.get_food_points()])
        new_antmove = ant_move.process_end(self.reality.world)
        assert not self.reality.world.elapsed_time > ant_move.end_time
        new_antmove.process_start()
        heapq.heappush(antmoves, new_antmove)
        return antmoves


#reality = RealityFactory.create_reality(0, 1, 20, 2)
#edgelist = [(edge.a_end, edge.b_end, {'weight': edge.cost}) for edge in reality.world.edges]
#from vizualizer import Vizualizer
#Vizualizer.draw_edges(edgelist)

#pprint(reality.world.to_json())

world_dir = 'worlds'
#for x in xrange(20):
#    reality = RealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_points=30, number_of_dimensions=2)
#    json.dump(reality.world.to_json(), open(os.path.join(world_dir, 'world-%s.json' % (x,)), 'w'))

#import sys
#sys.exit(0)
def avg(iterable):
    return sum(iterable) / len(iterable)

for file_ in sorted(os.listdir(world_dir)):
#for file_ in ['world-12.json']:
#for file_ in ['world-11.json']:
    file_ = os.path.join(world_dir, file_)
    assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (world_dir, file_)
    json_world = json.load(open(file_, 'r'))
    reality = RealityFactory.from_json_world(json_world, min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1)

    queen = BasicQueen(ant.PurelyRandomAnt)
    amount_of_ants = 20
    #amount_of_ants = 1
    s = Simulation(reality)

    #edgelist = [(edge.a_end.point, edge.b_end.point, {'weight': edge.cost}) for edge in reality.world.edges]
    #from vizualizer import Vizualizer
    #Vizualizer.draw_edges(edgelist)

    #print file_, s.run(queen, amount_of_ants)
    for amount_of_ants in [1, 20, 400]:
        results = [s.run(queen, amount_of_ants) for i in xrange(100)]
        elapsed = avg([elapsed for (elapsed, ticks) in results])
        ticks = avg([ticks for (elapsed, ticks) in results])
        print file_, amount_of_ants, elapsed, ticks


