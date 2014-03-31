from stats import QueenStats
from ant_move import AntStartMove
from edge import DummyEdgeEnd

class Simulator(object):
    def __init__(self, reality, simulation_class, reality_processors):
        self.reality = reality
        self.simulation_class = simulation_class
        self.reality_processors = reality_processors
    def simulate(self, queen, amount_of_ants, stats_saver):
        ant_classes = queen.spawn_ants(amount_of_ants)
        ants = [ant_class(self.reality.environment_parameters) for ant_class in ant_classes]
        anthills = self.reality.world.get_anthills()
        antmoves = list(self.get_start_antmoves(ants, anthills))
        for reality_processor in self.reality_processors:
            reality_processor.set_ant_count(len(ants))
        antmoves.extend(self.reality_processors)
        stats = QueenStats(self.reality, len(ants), stats_saver)
        simulation = self.simulation_class(self.reality, antmoves, stats)
        return simulation
    def get_results(self, simulation):
        ticks = simulation.ticks
        stats = simulation.stats
        elapsed_time = self.reality.world.elapsed_time
        return elapsed_time, ticks, stats
    def reset(self):
        self.reality.world.reset()
        for reality_processor in self.reality_processors:
            reality_processor.reset()
    def get_start_antmoves(self, ants, anthills):
        """ iterator """
        counter = 0
        number_of_anthills = len(anthills)
        anthills = list(anthills)
        for ant in ants:
            anthill = anthills[counter % number_of_anthills]
            yield AntStartMove(ant, DummyEdgeEnd(anthill))
            counter += 1

