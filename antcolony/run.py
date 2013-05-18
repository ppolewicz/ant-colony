#!/usr/bin/python2.7
import os
import json

import ant
import ant2
from queen import BasicQueen
from reality_factory import JsonRealityDeserializer
from reality_factory import ChessboardRealityFactory, CrossedChessboardRealityFactory, SlightlyRandomizedRealityFactory, SimpleRealityFactory
from simulator import Simulator, MultiSpawnStepSimulation, SpawnStepSimulation, TickStepSimulation
from simulation_director import BasicSimulationDirector, AnimatingVisualizerSimulationDirector, FileRouteDrawingVisualizerSimulationDirector, ScreenRouteDrawingVisualizerSimulationDirector
from util import avg
from vaporization import ExponentPheromoneVaporization, MultiplierPheromoneVaporization

assert __name__ == '__main__', 'this module should not be included, but invoked'

def prepare_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            if os.path.isfile(file_path) and not file_path.startswith('.py'):
                os.unlink(file_path)

class DummyClass(object):
    pass

class BadConfigurationException(Exception):
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

# initial food
options.force_initial_food = 1500
#options.force_initial_food = 10000
#options.force_initial_food = None # World's default

# queen
#options.queen = 'PurelyRandom'
options.queen = 'Ant2'

# amount of ants
options.amount_of_ants = 1
#options.amount_of_ants = 20

# amount of tests performed on a (queen, world) pair
options.how_many_tests_per_queenworld = 1

# director
#options.director = 'Basic'
#options.director = 'AnimatingVisualizer'
options.director = 'ScreenRouteDrawingVisualizer'
#options.director = 'FileRouteDrawingVisualizer' # doesn't show on screen, but saves png screenshots

# how often a frame should be drawn, if director drawing anything
#options.simulation_granularity = 'Tick'
#options.simulation_granularity = 'Spawn'
options.simulation_granularity = 'MultiSpawn'

# what should be the mode of pheromone vaporization
#options.vaporizator_mode = 'Multiplier' # fair
options.vaporizator_mode = 'Exponent' # vaporize edges with high pheromone concentration faster

##########################################################################################################################################################


if options.generate_worlds>0:
    prepare_directory(options.world_dir)
    for x in xrange(options.generate_worlds):
        chessboard_size = 20
        number_of_points = 10
        if options.world_type=='Chessboard':
            reality = ChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='CrossedChessboard':
            reality = CrossedChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='Simple':
            reality = SimpleRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=number_of_points)
        elif options.world_type=='SlightlyRandomized':
            reality = SlightlyRandomizedRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=number_of_points)
        else:
            raise BadConfigurationException('Bad world type configuration')
        json.dump(reality.world.to_json(), open(os.path.join(options.world_dir, 'world-%s.json' % (x,)), 'w'))

if options.simulation_granularity=='Tick':
    simulation_class = TickStepSimulation
elif options.simulation_granularity=='Spawn':
    simulation_class = SpawnStepSimulation
elif options.simulation_granularity=='MultiSpawn':
    simulation_class = MultiSpawnStepSimulation
else:
    raise BadConfigurationException('Bad simulation granularity configuration')

if options.vaporizator_mode=='Multiplier':
    vaporizator_class = MultiplierPheromoneVaporization
elif options.vaporizator_mode=='Exponent':
    vaporizator_class = ExponentPheromoneVaporization
else:
    raise BadConfigurationException('Bad vaporizator mode configuration')

if options.director == 'Basic':
    director = BasicSimulationDirector()
elif options.director == 'AnimatingVisualizer':
    director = AnimatingVisualizerSimulationDirector()
elif options.director == 'ScreenRouteDrawingVisualizer':
    director = ScreenRouteDrawingVisualizerSimulationDirector()
elif options.director == 'FileRouteDrawingVisualizer':
    prepare_directory('render')
    director = FileRouteDrawingVisualizerSimulationDirector()
else:
    raise BadConfigurationException('Bad simulation granularity configuration')

force_initial_food = options.force_initial_food

for file_ in sorted(os.listdir(options.world_dir)):
    file_ = os.path.join(options.world_dir, file_)
    assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (options.world_dir, file_)
    json_world = json.load(open(file_, 'r'))
    reality = JsonRealityDeserializer.from_json_world(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, json_world=json_world)
    if force_initial_food:
        reality.world.reset(force_initial_food)

    if options.queen == 'PurelyRandom':
        queen = BasicQueen(ant.PurelyRandomAnt)
    elif options.queen == 'Ant2':
        queen = BasicQueen(ant2.BasicAnt)
    else:
        raise BadConfigurationException('Bad queen configuration')

    for options.amount_of_ants in [1]:

        simulator = Simulator(reality, simulation_class, vaporizator_class)
        simulation = simulator.simulate(queen, options.amount_of_ants)
        #Visualizer.render_reality(reality)
        director.direct(simulation)
        #simulator.run_simulation(simulation)
        result = simulator.get_results(simulation)
        print 'result', repr(result)
        #exit(1)

        #results = [simulator.run(queen, options.amount_of_ants, reality) for i in xrange(options.how_many_tests_per_queenworld)]
        results = [result]
        elapsed = avg([elapsed for (elapsed, ticks) in results]) / options.amount_of_ants
        ticks = avg([ticks for (elapsed, ticks) in results])
        print 'world: %s, queen: %s, ants: %s, avg.decisions: %s, avg.time/ant: %s' % (file_, options.queen, options.amount_of_ants, ticks, elapsed)


