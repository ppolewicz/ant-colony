from vizualizer import Vizualizer

class AbstractSimulationDirector(object):
    def direct(self, simulation):
        pass

class BasicSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        while 1:
            changed, is_resolved = simulation.advance()
            if is_resolved:
                break

class VizualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        Vizualizer.direct(simulation)

