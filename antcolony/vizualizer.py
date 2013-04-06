import networkx as nx
import matplotlib.pyplot as plt

class Vizualizer(object):
    @classmethod
    def draw_edges(cls, edgelist):
        g = nx.Graph(edgelist)
        nx.draw(g)
        plt.show()

