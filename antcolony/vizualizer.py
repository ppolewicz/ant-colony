import os.path
import itertools
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
    def direct(self):
        base_file_path = 'render' # TODO
        self._prepare_world()
        redraw = RedrawHints()
        stop_condition = StopCondition()

        for frame_number in itertools.count():
            self.animate(frame_number, stop_condition, redraw)
            plt.savefig(os.path.join(base_file_path, "%s.png" % frame_number))
            if self.simulation.reality.world.is_resolved():
                break

class AbstractVisualizer(object):
    #EDGE_CMAP = plt.cm.jet
    EDGE_CMAP = plt.cm.winter_r
    def __init__(self, simulation, *args, **kwargs):
        self.simulation = simulation
        self.fig = None
        #super(xxxVisualizer, self).__init__(*args, **kwargs)
    def direct(self):
        raise NotImplementedError('You should use one of the director mixins')
    @classmethod
    def render_reality(cls, reality):
        return cls.render_world(reality.world)
    def _prepare_world(self):
        world = self.simulation.reality.world
        self.g = nx.Graph()
        g = self.g
        g.add_nodes_from(world.points)

        edgelist = [
            (edge.a_end.point, edge.b_end.point, min(edge.pheromone_sum()/2, 1))
            for edge in world.edges
        ]
        g.add_weighted_edges_from(edgelist)

        if self.fig is not None:
            self.fig.clear()
        else:
            self.fig = plt.figure()

        normal_points = {point: point.coordinates for point in world.points if not point.is_anthill() and not point.has_food()}
        nx.draw_networkx_nodes(g, pos=normal_points, nodelist=normal_points.keys(), node_color='w')

        food_points = {point: point.coordinates for point in world.get_food_points()}
        nx.draw_networkx_nodes(g, pos=food_points, nodelist=food_points.keys(), node_color='g', label='food')

        anthills = {point: point.coordinates for point in world.get_anthills()}
        nx.draw_networkx_nodes(g, pos=anthills, nodelist=anthills.keys(), node_color='b', label='anthill')

        self.all_points = {point: point.coordinates for point in world.points}

    def render_world(self, world):
        nx.draw_networkx_edges(self.g, pos=self.all_points, edge_color=[c for a,b,c in self.edgelist], width=4, edge_cmap=self.EDGE_CMAP, edge_vmin=0, edge_vmax=15)
        #plt.sci(nodes)
        plt.colorbar()
        #,width=2,edge_cmap=plt.cm.Jet,with_labels=True
        #nx.draw(g)
        plt.show()

    def init(self):
        return []

    def pre_animate(self):
        pass

    def animate(self, frame_number, stop_condition, redraw_hints):
        self.pre_animate()
        g = self.g
        all_points = self.all_points
        changed_entities, end, edges_to_mark = self.simulation.advance()
        if end:
            stop_condition.stop()
            print 'simulation should end!'
            return []

        changed_edge_objects = self.get_changed_edge_objects(changed_entities, redraw_hints)
        changed_edges = [(edge.a_end.point, edge.b_end.point) for edge in changed_edge_objects]

        changed_point_objects = [point for point in changed_entities if isinstance(point, AbstractPoint)]

        changed_points = changed_point_objects
        nx.draw_networkx_nodes(g, pos=all_points, nodelist=redraw_hints.points, node_color='w')
        nx.draw_networkx_nodes(g, pos=all_points, nodelist=changed_points, node_color='r')
        redraw_hints.points = changed_points

        vmin = 0
        vmax = 1
        #vmax = max([edge.pheromone_sum()/2 for edge in changed_edge_objects] + [1])
        nx.draw_networkx_edges(g, edgelist=changed_edges, pos=all_points, edge_color=[edge.pheromone_sum()/2 for edge in changed_edge_objects], width=4, edge_cmap=self.EDGE_CMAP, edge_vmin=vmin, edge_vmax=vmax)
        self.process_visited_edges(redraw_hints, edges_to_mark)
        #plt.colorbar()
        return []

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
        return self.keep_going

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

