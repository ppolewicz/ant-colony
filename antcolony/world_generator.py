from world import World

class SimpleWorldGenerator(object):
    def __init__(self, number_of_points, number_of_dimensions, point_generator, edge_generator):
        self.number_of_points = number_of_points
        self.number_of_dimensions = number_of_dimensions
        self.point_generator = point_generator
        self.edge_generator = edge_generator
    def generate(self):
        points = set(self.point_generator.generate_all(self.number_of_points))
        edges = set(self.edge_generator.generate_all(points))
        return World(points, edges)

