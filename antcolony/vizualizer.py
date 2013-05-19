import os.path
import itertools
from sys import float_info
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation
from edge import Edge
from point import AbstractPoint

#import random

#print plt.cm._cmapnames; exit()

class ScreenPresentingDirectorMixin(object):
    def direct(self):
        self._prepare_world()
        redraw = RedrawHints()
        stop_condition = StopCondition()
        my_animate = lambda frame_number: self.animate(frame_number, stop_condition, redraw)
        anim = animation.FuncAnimation(self.fig, my_animate, frames=1500, init_func=self.init, interval=20, blit=False)
        plt.show()
        anim # documentation and examples say that this has to be like that. Suspect some garbage collector issues.

class FileSavingDirectorMixin(object):
    def __init__(self, simulation, artifact_directory=None, *args, **kwargs):
        self.artifact_directory = artifact_directory
        super(FileSavingDirectorMixin, self).__init__(simulation, artifact_directory, *args, **kwargs)
    def direct(self):
        self._prepare_world()
        redraw = RedrawHints()
        stop_condition = StopCondition()

        for frame_number in itertools.count():
            self.animate(frame_number, stop_condition, redraw)
            plt.savefig(os.path.join(self.artifact_directory, "%s.png" % frame_number))
            if self.simulation.reality.world.is_resolved():
                break

class AbstractVisualizer(object):
    #EDGE_CMAP = plt.cm.jet
    EDGE_CMAP = plt.cm.winter_r
    NODE_SIZE = 100 # default was 600
    def __init__(self, simulation, *args, **kwargs):
        self.simulation = simulation
        self.fig = None
    def direct(self):
        raise NotImplementedError('You should use one of the director mixins')
    def render_reality(self, reality, filename=None):
        return self.render_world(reality.world, filename)
    def _prepare_world(self):
        world = self.simulation.reality.world
        self.g = nx.Graph()
        g = self.g
        g.add_nodes_from(world.points)

        edgelist = [
            (edge.a_end.point, edge.b_end.point, min(edge.pheromone_level(), 1))
            for edge in world.edges
        ]
        g.add_weighted_edges_from(edgelist)

        if self.fig is not None:
            self.fig.clear()
        else:
            self.fig = plt.figure(figsize=(14, 10), dpi=72) #, dpi=80 # figsize is in inches

        normal_points = {point: point.coordinates for point in world.points if not point.is_anthill() and not point.has_food()}
        nx.draw_networkx_nodes(g, pos=normal_points, nodelist=normal_points.keys(), node_color='w', node_size=self.NODE_SIZE)

        food_points = {point: point.coordinates for point in world.get_food_points()}
        nx.draw_networkx_nodes(g, pos=food_points, nodelist=food_points.keys(), node_color='g', node_size=self.NODE_SIZE, label='food')

        anthills = {point: point.coordinates for point in world.get_anthills()}
        nx.draw_networkx_nodes(g, pos=anthills, nodelist=anthills.keys(), node_color='b', node_size=self.NODE_SIZE, label='anthill')

        self.all_points = {point: point.coordinates for point in world.points}

    def render_world(self, world, filename=None):
        self._prepare_world()
        self._draw_edges_pheromone(world.edges)
        #plt.sci(nodes)
        plt.colorbar()
        #,width=2,edge_cmap=plt.cm.Jet,with_labels=True
        #nx.draw(g)
        if filename:
            plt.savefig(os.path.join(self.artifact_directory, "%s.png" % (filename,)))
        else:
            plt.show()

    def init(self):
        return []

    def pre_animate(self):
        pass

    def animate(self, frame_number, stop_condition, redraw_hints):
        #if stop_condition():
        #    print 'simulation should end!'
        #    return []
        changed_entities, end, edges_to_mark = self.simulation.advance()
        g = self.g
        all_points = self.all_points
        if end:
            stop_condition.stop()
            print 'simulation should end!'
            return []
        self.pre_animate()

        changed_edge_objects = self.get_changed_edge_objects(changed_entities, redraw_hints)

        changed_point_objects = [point for point in changed_entities if isinstance(point, AbstractPoint)]

        changed_points = changed_point_objects
        nx.draw_networkx_nodes(g, pos=all_points, nodelist=redraw_hints.points, node_color='w', node_size=self.NODE_SIZE)
        nx.draw_networkx_nodes(g, pos=all_points, nodelist=changed_points, node_color='r', node_size=self.NODE_SIZE)
        redraw_hints.points = changed_points

        self._draw_edges_pheromone(changed_edge_objects)
        self.process_visited_edges(redraw_hints, edges_to_mark)
        #plt.colorbar()
        return []

    def _draw_edges_pheromone(self, edge_objects):
        vmin = 0
        edge_tuples = [(edge.a_end.point, edge.b_end.point) for edge in edge_objects]
        edges_pheromone = [edge.pheromone_level() for edge in edge_objects]
        vmax = max(edges_pheromone + [float_info.min])
        nx.draw_networkx_edges(self.g, edgelist=edge_tuples, pos=self.all_points, edge_color=edges_pheromone, width=4, edge_cmap=self.EDGE_CMAP, edge_vmin=vmin, edge_vmax=vmax)

    def process_visited_edges(self, redraw_hints, edges_to_mark):
        redraw_hints.edges = set(edges_to_mark)

class RedrawHints(object):
    def __init__(self):
        self.points = set()
        self.edges = set()

class StopCondition(object):
    def __init__(self):
        self.keep_going = 1
    def stop(self):
        self.keep_going = 0
    def __call__(self, *args):
        return self.keep_going <= 0

class ResettingVisualizer(AbstractVisualizer):
    def pre_animate(self):
        self.fig.clear()
        self._prepare_world()
    def get_changed_edge_objects(self, changed_entities, redraw_hints):
        return self.simulation.reality.world.edges

class StateVisualizer(AbstractVisualizer):
    def get_changed_edge_objects(self, changed_entities, redraw_hints):
        return list(
            set(
                [edge for edge in changed_entities if isinstance(edge, Edge)]
            ) & redraw_hints.edges
        )

#class AnimatingVisualizer(StateVisualizer, ScreenPresentingDirectorMixin): # this makes sense when We render each tick, but performance improvement is questionable

class FileDrawingVisualizer(FileSavingDirectorMixin, ResettingVisualizer):
    pass

class AnimatingVisualizer(ScreenPresentingDirectorMixin, ResettingVisualizer):
    pass

class RouteDrawingVisualizer(ResettingVisualizer):
    def process_visited_edges(self, redraw_hints, edges_to_mark, *args, **kwargs):
        super(RouteDrawingVisualizer, self).process_visited_edges(redraw_hints, edges_to_mark, *args, **kwargs)
        marked_edges = [(edge.a_end.point, edge.b_end.point) for edge in edges_to_mark]
        nx.draw_networkx_edges(self.g, edgelist=marked_edges, pos=self.all_points, edge_color='r', width=1)

class ScreenRouteDrawingVisualizer(ScreenPresentingDirectorMixin, RouteDrawingVisualizer):
    pass

class FileRouteDrawingVisualizer(FileSavingDirectorMixin, RouteDrawingVisualizer):
    pass


if __name__=='__main__':
    edgelist = [
        (0, 1, 1),
        (1, 2, 2),
        (2, 3, 3),
        (3, 4, 4),
        (4, 0, 5),
    ]

    g = nx.Graph()
    g.add_weighted_edges_from(edgelist)
    nx.draw(g)
    plt.show()

