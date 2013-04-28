import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import animation
from edge import Edge
from point import AbstractPoint

#import random
#print plt.cm._cmapnames; exit()

class Vizualizer(object):
    @classmethod
    def render_reality(cls, reality):
        return cls.render_world(reality.world)
    @classmethod
    def _prepare_world(cls, world):
        g = nx.Graph()
        g.add_nodes_from(world.points)

        edgelist = [
            #(edge.a_end.point, edge.b_end.point, edge.cost+random.randint(1, 10))
            #(edge.a_end.point, edge.b_end.point, {'weight': edge.cost*10})
            (edge.a_end.point, edge.b_end.point, min(edge.pheromone_sum()/2, 1))
            for edge in world.edges
        ]
        g.add_weighted_edges_from(edgelist)

        fig = plt.figure()

        normal_points = {point: point.coordinates for point in world.points if not point.is_anthill() and not point.has_food()}
        nx.draw_networkx_nodes(g, pos=normal_points, nodelist=normal_points.keys(), node_color='w')

        food_points = {point: point.coordinates for point in world.get_food_points()}
        nx.draw_networkx_nodes(g, pos=food_points, nodelist=food_points.keys(), node_color='g', label='food')

        anthills = {point: point.coordinates for point in world.get_anthills()}
        nx.draw_networkx_nodes(g, pos=anthills, nodelist=anthills.keys(), node_color='b', label='anthill')

        all_points = {point: point.coordinates for point in world.points}
        return g, all_points, edgelist, fig

    @classmethod
    def render_world(cls, world):
        g, all_points, edgelist, fig = cls._prepare_world(world)
        #edge_cmap = plt.cm.jet
        edge_cmap = plt.cm.winter_r
        nx.draw_networkx_edges(g, pos=all_points, edge_color=[c for a,b,c in edgelist], width=4, edge_cmap=edge_cmap, edge_vmin=0, edge_vmax=15)
        #plt.sci(nodes)
        plt.colorbar()
        #,width=2,edge_cmap=plt.cm.Jet,with_labels=Tru
        #nx.draw(g)
        plt.show()
    @classmethod
    def direct(cls, simulation):
        g, all_points, edgelist, fig = cls._prepare_world(simulation.reality.world)
        #edge_cmap = plt.cm.jet
        edge_cmap = plt.cm.winter_r
        class Redraw(object):
            pass
        redraw = Redraw()
        redraw.points = []
        def animate(simulation, frame_number, stop_condition, redraw):
            changed_entities, end = simulation.advance()
            #print 'changed_entities', changed_entities
            if end:
                stop_condition.stop()
                print 'simulation should end!'
                return []
            changed_edge_objects = [edge for edge in changed_entities if isinstance(edge, Edge)]
            #print 'changed_edge_objects', changed_edge_objects, changed_entities
            changed_edges = [(edge.a_end.point, edge.b_end.point) for edge in changed_edge_objects]

            changed_point_objects = [point for point in changed_entities if isinstance(point, AbstractPoint)]
            #print 'changed_point_objects', changed_point_objects

            #changed_points = [point.coordinates for point in changed_point_objects]
            changed_points = changed_point_objects
            nx.draw_networkx_nodes(g, pos=all_points, nodelist=redraw.points, node_color='w')
            nx.draw_networkx_nodes(g, pos=all_points, nodelist=changed_points, node_color='r')
            redraw.points = changed_points

            #nx.draw_networkx_edges(g, pos=all_points, edge_color=[random.randint(1, 10) for a,b,c in edgelist], width=4, edge_cmap=edge_cmap, edge_vmin=0, edge_vmax=15)
            vmin = 0
            #vmax = 2500
            vmax = 1
            #vmax = max(max([edge.pheromone_sum()/2 for edge in changed_edge_objects]), 1)
            #print 'vmax', vmax
            #print 'edge weight', [edge.pheromone_sum()/2 for edge in changed_edge_objects]
            nx.draw_networkx_edges(g, edgelist=changed_edges, pos=all_points, edge_color=[edge.pheromone_sum()/2 for edge in changed_edge_objects], width=4, edge_cmap=edge_cmap, edge_vmin=vmin, edge_vmax=vmax)
            #plt.colorbar()
            return []
        #def init():
        #    print 'init'
        #, init_func=init
        #anim = animation.ArtistAnimation(fig, animate('1'))
        class StopCondition(object):
            def __init__(self):
                self.keep_going = 1
            def stop(self):
                self.keep_going = 0
            def __call__(self, *args):
                return self.keep_going
        stop_condition = StopCondition()
        my_animate = lambda frame_number: animate(simulation, frame_number, stop_condition, redraw)
        ###import itertools
        ###frame_limiter = itertools.takewhile(stop_condition, itertools.count())
        ##frame_limiter = stop_condition
        ##, frames=frame_limiter
        #init = lambda: cls.render_reality(simulation.reality)
        def init():
            #edge_cmap = plt.cm.winter_r
            #nx.draw_networkx_edges(g, pos=all_points, edge_color=[15 for a,b,c in edgelist], width=4, edge_cmap=edge_cmap, edge_vmin=0, edge_vmax=15)
            return []

        #anim = animation.FuncAnimation(fig, my_animate, init_func=init, interval=20, blit=True)
        anim = animation.FuncAnimation(fig, my_animate, frames=100, init_func=init, interval=20, blit=False)
        plt.show()
        anim # XXX

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

