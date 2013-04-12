from point_generator import SimplePointGenerator, ChessboardPointGenerator
from edge_generator import SimpleEdgeGenerator, LimitedRandomCoefficientEdgeGenerator, ChessboardEdgeGenerator
from world_generator import SimpleWorldGenerator

class AbstractWorldGeneratorFactory(object):
    """ generates N-dimensional worlds """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, *args, **kwargs):
        raise NotImplementedError()

class SimpleWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    """ generates worlds with edge costs equal to distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, number_of_points):
        point_generator = SimplePointGenerator(number_of_dimensions, 0, 100)
        edge_generator = SimpleEdgeGenerator()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

class SlightlyRandomizedWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    """ generates worlds with edge costs only slightly different than the distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, number_of_points):
        point_generator = SimplePointGenerator(number_of_dimensions, 0, 100)
        edge_generator = LimitedRandomCoefficientEdgeGenerator(0, 20)
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

class ChessboardWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    """ generates N-dimensional raster-shaped worlds with equal edge costs equal to the distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, width):
        number_of_points = width ** number_of_dimensions
        point_generator = ChessboardPointGenerator(number_of_dimensions, 0, width)
        edge_generator = ChessboardEdgeGenerator()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

