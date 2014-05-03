#!/usr/bin/env python2.7
import json
import os
import time

import ant
import ant2
from periodic_processor import CostInvertingEdgeMutator, CostMultiplierEdgeMutator
from queen import BasicQueen
from reality_factory import JsonRealityDeserializer
from reality_factory import ChessboardRealityFactory, SlightlyRandomizedRealityFactory, SimpleRealityFactory
from reality_factory import CrossedChessboardRealityFactory, UpperLeftCornerThresholdDistanceCrossedChessboardRealityFactory, UpperLeftCornerTrueDistanceCrossedChessboardRealityFactory
from reality_factory import HexagonRealityFactory, UpperLeftCornerThresholdDistanceHexagonRealityFactory, UpperLeftCornerTrueDistanceHexagonRealityFactory
from simulation import LastSpawnStepSimulation, MultiSpawnStepSimulation, SpawnStepSimulation, TickStepSimulation
from simulator import Simulator
from simulation_director import AnimatingVisualizerSimulationDirector, BasicSimulationDirector, FileDrawingVisualizerSimulationDirector, FileRouteDrawingVisualizerSimulationDirector, ScreenRouteDrawingVisualizerSimulationDirector
from stats_saver import CSVStatsSaver, NullStatsSaver, TSVStatsSaver
from util import nice_json_dump
from vaporization import ExponentPheromoneVaporization, LogarithmPheromoneVaporization, MultiplierPheromoneVaporization
from vizualizer import draw_link_costs, draw_pheromone_levels

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
#options.world_type = 'CrossedChessboard'
#options.world_type = 'SlightlyRandomized'
#options.world_type = 'Simple'
#options.world_type = 'Hexagon'
options.world_type = 'UpperLeftCornerThresholdDistanceCrossedChessboard'
#options.world_type = 'UpperLeftCornerThresholdDistanceHexagon'
#options.world_type = 'UpperLeftCornerTrueDistanceCrossedChessboard'
#options.world_type = 'UpperLeftCornerTrueDistanceHexagon'

# number of dimensions
#options.number_of_dimensions = 1
options.number_of_dimensions = 2
#options.number_of_dimensions = 3

# initial food
#options.force_initial_food = 1500
#options.force_initial_food = 5000
#options.force_initial_food = 10
options.force_initial_food = 10000
#options.force_initial_food = None # World's default

# queen
options.queens = []
#options.queens += ['PurelyRandom']                # purely random ant (expect horrible performance)
#options.queens += ['Ant2.BasicAnt']               # Basic ant
#options.queens += ['Ant2.PathShorteningAnt']      # BasicAnt that eagerly eliminates cycles in it's return path
#options.queens += ['Ant2.ShortcutAnt']            # BasicAnt that tries to find a shortcut to anthill
options.queens += ['Ant2.AdvancedAnt']            # ant that eagerly eliminates cycles in it's return path and tries to find a shortcut to anthill
#options.queens += ['Ant2.AdvancedQuadraticAnt']   # AdvancedAnt which squares pheromone before using roulette
#options.queens += ['Ant2.AdvancedRootAnt']        # AdvancedAnt which square roots pheromone before using roulette
#options.queens += ['Ant2.AdvancedBadLuckAnt']     # AdvancedAnt which picks a random candidate edge instead of using roulette
#options.queens += ['Ant2.AdvancedIgnorantAnt']    # AdvancedAnt which doesn't ignore a point which was rejected previously
#options.queens += ['Ant2.LinearPenaltyAnt']       # AdvancedAnt which applies only proportional length coefficient pheromone drop (instead of exponent)
#options.queens += ['Ant2.HalfLengthPenaltyExponent']

# amounts of ants
options.amounts_of_ants = [1]
options.amounts_of_ants = [20]
#options.amounts_of_ants = [1, 8, 20]

# amount of tests performed on a (queen, world) pair
options.how_many_tests_per_queenworld = 2
options.how_many_tests_per_queenworld = 1

# director
options.director = 'Basic'
#options.director = 'AnimatingVisualizer'
options.director = 'ScreenRouteDrawingVisualizer'
options.director = 'FileRouteDrawingVisualizer' # doesn't show on screen, but saves png route screenshots
#options.director = 'FileDrawingVisualizer' # doesn't show on screen, but saves png world screenshots

# how often a frame should be drawn, if director is drawing
#options.simulation_granularity = 'Tick'
#options.simulation_granularity = 'Spawn'
options.simulation_granularity = 'MultiSpawn'
#options.simulation_granularity = 'LastSpawn'

# how many spawns between frames are drawn. This only makes sense when simulation_granularity == 'MultiSpawn'.
options.force_spawn_amount = None
options.force_spawn_amount = 250

# what should be the mode of pheromone vaporization
options.vaporizator_mode = 'Multiplier'
#options.vaporizator_mode = 'Exponent'
#options.vaporizator_mode = 'Logarithm' # vaporize edges with high pheromone concentration much faster than the ones with low concentration

# what format should the stats be saved in
options.statssaver_extension = 'csv'
#options.statssaver_extension = 'tsv'
#options.statssaver_extension = None # stats saving disabled

##########################################################################################################################################################


if options.generate_worlds>0:
    prepare_directory(options.world_dir)
    for i in xrange(options.generate_worlds):
        chessboard_size = 20
        number_of_points = 10
        hexagon_board_size = 30
        if options.world_type=='Chessboard':
            reality = ChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='CrossedChessboard':
            reality = CrossedChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='UpperLeftCornerThresholdDistanceCrossedChessboard':
            reality = UpperLeftCornerThresholdDistanceCrossedChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='UpperLeftCornerTrueDistanceCrossedChessboard':
            reality = UpperLeftCornerTrueDistanceCrossedChessboardRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=chessboard_size)
        elif options.world_type=='Hexagon':
            reality = HexagonRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=hexagon_board_size)
        elif options.world_type=='UpperLeftCornerTrueDistanceHexagon':
            reality = UpperLeftCornerTrueDistanceHexagonRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=hexagon_board_size)
        elif options.world_type=='UpperLeftCornerThresholdDistanceHexagon':
            reality = UpperLeftCornerThresholdDistanceHexagonRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, width=hexagon_board_size)
        elif options.world_type=='Simple':
            reality = SimpleRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=number_of_points)
        elif options.world_type=='SlightlyRandomized':
            reality = SlightlyRandomizedRealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_dimensions=options.number_of_dimensions, number_of_points=number_of_points)
        else:
            raise BadConfigurationException('Bad world type configuration')
        filepath = os.path.join(options.world_dir, '%sWorld-%s.json' % (options.world_type, i,))
        nice_json_dump(reality.world.to_json(), filepath)

if options.simulation_granularity=='MultiSpawn':
    simulation_class = MultiSpawnStepSimulation
    force_spawn_amount = options.force_spawn_amount
elif options.force_spawn_amount is not None:
    raise BadConfigurationException('force_spawn_amount is only supported for MultiSpawn simulation granularity')
elif options.simulation_granularity=='Tick':
    simulation_class = TickStepSimulation
elif options.simulation_granularity=='Spawn':
    simulation_class = SpawnStepSimulation
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
vaporizator = vaporizator_class(trigger_level=5)

edge_mutations_count = 1 # TODO
if 0: # TODO
    edge_mutator_class = CostMultiplierEdgeMutator
else:
    edge_mutator_class = CostInvertingEdgeMutator

p = 1/float(edge_mutations_count+1)
edge_mutator = edge_mutator_class(p, p)

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

if options.statssaver_extension == 'csv':
    statssaver_class = CSVStatsSaver
elif options.statssaver_extension == 'tsv':
    statssaver_class = TSVStatsSaver
elif options.statssaver_extension is None:
    statssaver_class = NullStatsSaver
else:
    raise BadConfigurationException('Bad statssaver extension configuration')

force_initial_food = options.force_initial_food
for queen_name in options.queens:
    for file_ in sorted(os.listdir(options.world_dir)):
        file_ = os.path.join(options.world_dir, file_)
        assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (options.world_dir, file_)
        with open(file_, 'r') as f:
            json_world = json.load(f)
        reality = JsonRealityDeserializer.from_json_world(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, json_world=json_world)
        world_name = os.path.splitext(os.path.basename(file_))[0]
        if force_initial_food:
            reality.world.reset(force_initial_food)

        if queen_name == 'PurelyRandom':
            queen = BasicQueen(ant.PurelyRandomAnt)
        elif queen_name.startswith('Ant2.'):
            antclass = ant2.__dict__[queen_name[5:]]
            queen = BasicQueen(antclass)
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

                if os.path.exists(artifact_directory):
                    continue

                #import pycallgraph
                #pycallgraph.start_trace()

                prepare_directory(artifact_directory)
                simulator = Simulator(reality, simulation_class, [vaporizator, edge_mutator])
                stats_saver = statssaver_class(artifact_directory)
                simulation = simulator.simulate(queen, amount_of_ants, stats_saver)
                if simulation_class == MultiSpawnStepSimulation and options.force_spawn_amount:
                    simulation.spawn_amount = force_spawn_amount
                draw_link_costs(simulation, artifact_directory, reality)

                start_time = time.time()
                director.direct(simulation, artifact_directory)
                total_real_time = time.time() - start_time
                elapsed, ticks, queenstats = simulator.get_results(simulation)

                # this used to agregate data from several runs
                elapsed_balanced = elapsed / amount_of_ants

                data = {
                    'world': world_name,
                    'world_filepath': file_,
                    'queen': queen.get_name(),
                    'ants': amount_of_ants,
                    'ticks': ticks,
                    'cost': elapsed,
                    'cost_balanced': elapsed_balanced,
                    'total_food': reality.world.get_total_food(),
                    'best_finding_cost': queenstats.best_finding_cost,
                    'moves_leading_to_food_being_found': queenstats.moves_leading_to_food_being_found,
                    'total_real_time': total_real_time,
                }
                nice_json_dump(reality.world.to_json(), os.path.join(artifact_directory, os.path.basename(file_)))
                draw_pheromone_levels(simulation, artifact_directory, reality, force_name='end')
                draw_link_costs(simulation, artifact_directory, reality, force_name='end')
                nice_json_dump(data, os.path.join(artifact_directory, 'results.json'))
                print 'world: %s, queen: %s, ants: %s, avg.decisions: %s, avg.time/ant: %s' % (file_, queen.get_name(), amount_of_ants, ticks, elapsed_balanced)
                simulator.reset()
                #pycallgraph.make_dot_graph('profile.png')
                #exit()


