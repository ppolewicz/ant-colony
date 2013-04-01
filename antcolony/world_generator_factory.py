from point_generator import SimplePointGenerator
from edge_generator import SimpleEdgeGenerator, LimitedRandomCoefficientEdgeGenerator
from world_generator import SimpleWorldGenerator

class SimpleWorldGeneratorFactory(object):
    """ generates worlds with edge costs equal to distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_points, number_of_dimensions):
        point_generator = SimplePointGenerator(number_of_dimensions, 0, 20)
        edge_generator = SimpleEdgeGenerator()
        return SimpleWorldGenerator(number_of_points, number_of_dimensions, point_generator, edge_generator)

class SlightlyRandomizedWorldGeneratorFactory(object):
    """ generates worlds with edge costs only slightly different than the distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_points, number_of_dimensions):
        point_generator = SimplePointGenerator(number_of_dimensions, 0, 20)
        edge_generator = LimitedRandomCoefficientEdgeGenerator(0, 2)
        return SimpleWorldGenerator(number_of_points, number_of_dimensions, point_generator, edge_generator)

