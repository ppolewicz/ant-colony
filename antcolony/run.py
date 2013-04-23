#!/usr/bin/python2.7
import os
import json

import ant
import ant2
from queen import BasicQueen
from reality_factory import JsonRealityDeserializer
from reality_factory import ChessboardRealityFactory, CrossedChessboardRealityFactory, SlightlyRandomizedRealityFactory, SimpleRealityFactory
from simulator import Simulation, avg

assert __name__ == '__main__', 'this module should not be included, but invoked'

def prepare_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            if os.path.isfile(file_path) and file_path.startswith('world-') and file_path.endswith('.json'):
                os.unlink(file_path)

class DummyClass(object):
    pass


options = DummyClass()
options.world_dir = 'worlds'

##########################################################################################################################################################

options.generate_worlds = 1    # world generator enabled: create 1 world
#options.generate_worlds = 20  # world generator enabled: create 20 worlds
#options.generate_worlds = 0   # world generator disabled

# generated world type
#options.world_type = 'Chessboard'
options.world_type = 'CrossedChessboard'
#options.world_type = 'SlightlyRandomized'
#options.world_type = 'Simple'

# number of dimensions
#options.number_of_dimensions = 1
options.number_of_dimensions = 2
#options.number_of_dimensions = 3

# amount of ants
options.amount_of_ants = 1
#options.amount_of_ants = 20

# amount of tests performed on a (queen, world) pair
options.how_many_tests_per_queenworld = 1

##########################################################################################################################################################


if options.generate_worlds>0:
    prepare_directory(options.world_dir)
    for x in xrange(options.generate_worlds):
        if options.world_type=='Chessboard':
            reality = ChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=10)
        elif options.world_type=='CrossedChessboard':
            reality = CrossedChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=10)
        elif options.world_type=='Simple':
            reality = SimpleRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=30)
        elif options.world_type=='SlightlyRandomized':
            reality = SlightlyRandomizedRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=30)
        else:
            raise Exception('Bad world type configuration')
        json.dump(reality.world.to_json(), open(os.path.join(options.world_dir, 'world-%s.json' % (x,)), 'w'))

for file_ in sorted(os.listdir(options.world_dir)):
    file_ = os.path.join(options.world_dir, file_)
    assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (options.world_dir, file_)
    json_world = json.load(open(file_, 'r'))
    reality = JsonRealityDeserializer.from_json_world(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, json_world=json_world)

    if options.queen == 'PurelyRandom':
        queen = BasicQueen(ant.PurelyRandomAnt)
    elif options.queen == 'Ant2':
        queen = BasicQueen(ant2.BasicAnt)
    else:
        raise Exception('Bad queen configuration')

    s = Simulation(reality)

    edgelist = [(edge.a_end.point, edge.b_end.point, {'weight': edge.cost}) for edge in reality.world.edges]
    from vizualizer import Vizualizer
    Vizualizer.draw_edges(edgelist)
    exit(1)

    for options.amount_of_ants in [1]:
        results = [s.run(queen, options.amount_of_ants, reality) for i in xrange(options.how_many_tests_per_queenworld)]
        elapsed = avg([elapsed for (elapsed, ticks) in results]) / options.amount_of_ants
        ticks = avg([ticks for (elapsed, ticks) in results])
        print 'world: %s, queen: %s, ants: %s, avg.decisions: %s, avg.time/ant: %s' % (file_, options.queen, options.amount_of_ants, ticks, elapsed)


