#!/usr/bin/python2.7
import os
import json

import ant
import ant2
from queen import BasicQueen
from reality_factory import JsonRealityDeserializer
from reality_factory import ChessboardRealityFactory, CrossedChessboardRealityFactory, SlightlyRandomizedRealityFactory, SimpleRealityFactory
from simulation import LastSpawnStepSimulation, MultiSpawnStepSimulation, SpawnStepSimulation, TickStepSimulation
from simulator import Simulator
from simulation_director import AnimatingVisualizerSimulationDirector, BasicSimulationDirector, FileDrawingVisualizerSimulationDirector, FileRouteDrawingVisualizerSimulationDirector, ScreenRouteDrawingVisualizerSimulationDirector
from util import avg, nice_json_dump
from vaporization import ExponentPheromoneVaporization, LogarithmPheromoneVaporization, MultiplierPheromoneVaporization
from vizualizer import FileCostDrawingVisualizer, FileDrawingVisualizer

assert __name__ == '__main__', 'this module should not be included, but invoked'

def prepare_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            if os.path.isfile(file_path) and not file_path.startswith('.py'):
                os.unlink(file_path)

class Options(object):
    EXCLUDED_FROM_JSON = set(['EXCLUDED', 'to_json'])
    def to_json(self):
        return {k: v for k, v in self.__dict__ if k not in self.EXCLUDED_FROM_JSON}

class BadConfigurationException(Exception):
    pass


options = Options()
options.world_dir = 'worlds'
options.root_artifact_directory = 'results'

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

# amounts of ants
options.amounts_of_ants = [1]
#options.amounts_of_ants = [1, 20, 100]

# amount of tests performed on a (queen, world) pair
options.how_many_tests_per_queenworld = 3

# director
#options.director = 'Basic'
#options.director = 'AnimatingVisualizer'
options.director = 'ScreenRouteDrawingVisualizer'
#options.director = 'FileRouteDrawingVisualizer' # doesn't show on screen, but saves png route screenshots
#options.director = 'FileDrawingVisualizer' # doesn't show on screen, but saves png world screenshots

# how often a frame should be drawn, if director drawing anything
#options.simulation_granularity = 'Tick'
#options.simulation_granularity = 'Spawn'
options.simulation_granularity = 'MultiSpawn'
#options.simulation_granularity = 'LastSpawn'

# what should be the mode of pheromone vaporization
#options.vaporizator_mode = 'Multiplier' # fair
#options.vaporizator_mode = 'Exponent' # probably broken
options.vaporizator_mode = 'Logarithm' # vaporize edges with high pheromone concentration faster than the ones withg low concentration

##########################################################################################################################################################


if options.generate_worlds>0:
    prepare_directory(options.world_dir)
    for i in xrange(options.generate_worlds):
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
        filepath = os.path.join(options.world_dir, '%sWorld-%s.json' % (options.world_type, i,))
        nice_json_dump(reality.world.to_json(), filepath)

if options.simulation_granularity=='Tick':
    simulation_class = TickStepSimulation
elif options.simulation_granularity=='Spawn':
    simulation_class = SpawnStepSimulation
elif options.simulation_granularity=='MultiSpawn':
    simulation_class = MultiSpawnStepSimulation
elif options.simulation_granularity=='LastSpawn':
    simulation_class = LastSpawnStepSimulation
else:
    raise BadConfigurationException('Bad simulation granularity configuration')

if options.vaporizator_mode=='Exponent':
    vaporizator_class = ExponentPheromoneVaporization
elif options.vaporizator_mode=='Logarithm':
    vaporizator_class = LogarithmPheromoneVaporization
elif options.vaporizator_mode=='Multiplier':
    vaporizator_class = MultiplierPheromoneVaporization
else:
    raise BadConfigurationException('Bad vaporizator mode configuration')
vaporizator = vaporizator_class(trigger_level=50)

if options.director == 'Basic':
    director = BasicSimulationDirector()
elif options.director == 'AnimatingVisualizer':
    director = AnimatingVisualizerSimulationDirector()
elif options.director == 'ScreenRouteDrawingVisualizer':
    director = ScreenRouteDrawingVisualizerSimulationDirector()
elif options.director == 'FileRouteDrawingVisualizer':
    director = FileRouteDrawingVisualizerSimulationDirector()
elif options.director == 'FileDrawingVisualizer':
    director = FileDrawingVisualizerSimulationDirector()
else:
    raise BadConfigurationException('Bad simulation granularity configuration')

force_initial_food = options.force_initial_food

for file_ in sorted(os.listdir(options.world_dir)):
    file_ = os.path.join(options.world_dir, file_)
    assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (options.world_dir, file_)
    with open(file_, 'r') as f:
        json_world = json.load(f)
    reality = JsonRealityDeserializer.from_json_world(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, json_world=json_world)
    world_name = os.path.splitext(os.path.basename(file_))[0]
    if force_initial_food:
        reality.world.reset(force_initial_food)

    if options.queen == 'PurelyRandom':
        queen = BasicQueen(ant.PurelyRandomAnt)
    elif options.queen == 'Ant2':
        queen = BasicQueen(ant2.BasicAnt)
    else:
        raise BadConfigurationException('Bad queen configuration')

    for run_id in xrange(options.how_many_tests_per_queenworld):
        for amount_of_ants in options.amounts_of_ants:
            artifact_directory = os.path.join(
                options.root_artifact_directory,
                '%(world_name)s_%(queen_name)s_%(amount_of_ants)s_%(run_id)s' % {
                    'world_name': world_name,
                    'queen_name': queen.get_name(),
                    'amount_of_ants': amount_of_ants,
                    'run_id': run_id,
                },
            )
            #assert not os.path.exists(artifact_directory), 'result directory would be overwritten: %s' % (artifact_directory,)
            prepare_directory(artifact_directory)
            simulator = Simulator(reality, simulation_class, vaporizator)
            simulation = simulator.simulate(queen, amount_of_ants)
            FileCostDrawingVisualizer(simulation, artifact_directory).render_reality(reality, 'link_costs')
            director.direct(simulation, artifact_directory)
            result = simulator.get_results(simulation)

            # this used to agregate data from several runs
            results = [result]
            elapsed = avg([elapsed for (elapsed, ticks) in results])
            elapsed_balanced = elapsed / amount_of_ants
            ticks = avg([ticks for (elapsed, ticks) in results])

            data = {
                'world': world_name,
                'world_filepath': file_,
                'queen': queen.get_name(),
                'ants': amount_of_ants,
                'ticks': ticks,
                'cost': elapsed,
                'cost_balanced': elapsed_balanced,
                'total_food': reality.world.get_total_food(),
            }
            nice_json_dump(reality.world.to_json(), os.path.join(artifact_directory, os.path.basename(file_)))
            FileDrawingVisualizer(simulation, artifact_directory).render_reality(reality, 'end')
            nice_json_dump(data, os.path.join(artifact_directory, 'results.json'))
            print 'world: %s, queen: %s, ants: %s, avg.decisions: %s, avg.time/ant: %s' % (file_, queen.get_name(), amount_of_ants, ticks, elapsed_balanced)
            simulator.reset()


