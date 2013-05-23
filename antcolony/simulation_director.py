from vizualizer import AnimatingVisualizer
from vizualizer import FileDrawingVisualizer
from vizualizer import FileRouteDrawingVisualizer
from vizualizer import ScreenRouteDrawingVisualizer

class AbstractSimulationDirector(object):
    def direct(self, simulation, artifact_directory):
        raise NotImplementedError()

class BasicSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation, artifact_directory):
        while 1:
            changed, is_resolved, edges_to_mark = simulation.advance()
            if is_resolved:
                break

class FileDrawingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation, artifact_directory):
        FileDrawingVisualizer(simulation, artifact_directory).direct()

class ScreenRouteDrawingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation, artifact_directory):
        ScreenRouteDrawingVisualizer(simulation).direct()

class FileRouteDrawingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation, artifact_directory):
        FileRouteDrawingVisualizer(simulation, artifact_directory).direct()

class AnimatingVisualizerSimulationDirector(AbstractSimulationDirector):
    def direct(self, simulation, artifact_directory):
        AnimatingVisualizer(simulation).direct()

