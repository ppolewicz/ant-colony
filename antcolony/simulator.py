from stats import QueenStats
from ant_move import AntStartMove
from edge import DummyEdgeEnd

class Simulator(object):
    def __init__(self, reality, simulation_class, vaporizator_class):
        self.reality = reality
        self.simulation_class = simulation_class
        self.vaporizator_class = vaporizator_class
    def simulate(self, queen, amount_of_ants, artifact_directory=None):
        ant_classes = queen.spawn_ants(amount_of_ants)
        ants = [ant_class(self.reality.environment_parameters) for ant_class in ant_classes]
        anthills = self.reality.world.get_anthills()
        antmoves = list(self.get_start_antmoves(ants, anthills))
        antmoves.append(self.vaporizator_class(ant_count=len(ants)))
        stats = QueenStats(self.reality, len(ants))
        return self.simulation_class(self.reality, antmoves, stats, artifact_directory)
    def get_results(self, simulation):
        ticks = simulation.ticks
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

