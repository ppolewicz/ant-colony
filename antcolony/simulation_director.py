from vizualizer import AnimatingVisualizer
from vizualizer import ScreenRouteDrawingVisualizer
from vizualizer import FileRouteDrawingVisualizer

class AbstractSimulationDirector(object):
    def direct(self, simulation):
        raise NotImplementedError()

class BasicSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        while 1:
            changed, is_resolved, edges_to_mark = simulation.advance()
            if is_resolved:
                break

class ScreenRouteDrawingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        ScreenRouteDrawingVisualizer(simulation).direct()

class FileRouteDrawingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        FileRouteDrawingVisualizer(simulation).direct()

class AnimatingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation):
        AnimatingVisualizer(simulation).direct()

