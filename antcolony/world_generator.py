from world import World

class AbstractWorldGenerator(object):
    def generate(self):
        raise NotImplementedError()

class SimpleWorldGenerator(AbstractWorldGenerator):
    """ Very agnostic world generator """
    def __init__(self, number_of_dimensions, point_generator, edge_generator, edge_cost_generator, *args, **kwargs):
        self.number_of_dimensions = number_of_dimensions
        self.point_generator = point_generator
        self.edge_generator = edge_generator
        self.edge_cost_generator = edge_cost_generator
        self.args = args
        self.kwargs = kwargs
    def generate(self):
        points = set(self.point_generator.generate_all(*self.args, **self.kwargs))
        edges = set(self.edge_generator.generate_and_register(points, self.edge_cost_generator, *self.args, **self.kwargs))
        return World(points, edges)

