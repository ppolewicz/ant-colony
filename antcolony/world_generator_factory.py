from point_generator import SimplePointGenerator, ChessboardPointGenerator, HexagonPointGenerator
from edge_generator import ChessboardEdgeGenerator, CrossedChessboardEdgeGenerator, LimitedQuantityEdgeGenerator, LimitedQuantityRandomCoefficientEdgeGenerator, LimitedRangeRandomCoefficientEdgeGenerator
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
        #edge_generator = SimpleEdgeGenerator()
        edge_generator = LimitedQuantityEdgeGenerator()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

class SlightlyRandomizedWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    """ generates worlds with edge costs only slightly different than the distance between the points """
    @classmethod
    def create_world_generator(cls, number_of_dimensions, number_of_points):
        point_generator = SimplePointGenerator(number_of_dimensions, 0, 100)
        edge_generator = LimitedQuantityRandomCoefficientEdgeGenerator(0.8, 1.2)
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

class CustomWidthWorldGeneratorFactory(AbstractWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = None
    POINT_GENERATOR_CLASS = None
    @classmethod
    def create_world_generator(cls, number_of_dimensions, width):
        number_of_points = width ** number_of_dimensions
        point_generator = cls.POINT_GENERATOR_CLASS(number_of_dimensions, 0, width)
        edge_generator = cls.EDGE_GENERATOR_CLASS()
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)

class ChessboardWorldGeneratorFactory(CustomWidthWorldGeneratorFactory):
    """ generates n-dimensional raster-shaped worlds with equal edge costs equal to the distance between the points, like this:
        *----*----*
        |    |    |
        |    |    |
        |    |    |
        |    |    |
        *----*----*
        |    |    |
        |    |    |
        |    |    |
        |    |    |
        *----*----*
        """
    EDGE_GENERATOR_CLASS = ChessboardEdgeGenerator
    POINT_GENERATOR_CLASS = ChessboardPointGenerator

class CrossedChessboardWorldGeneratorFactory(ChessboardWorldGeneratorFactory):
    """ generates 2-dimensional raster-shaped worlds with equal edge costs equal to the distance between the points, like this:
        *----*----*
        |\  /|\  /|
        | \/ | \/ |
        | /\ | /\ |
        |/  \|/  \|
        *----*----*
        |\  /|\  /|
        | \/ | \/ |
        | /\ | /\ |
        |/  \|/  \|
        *----*----*
        """
    EDGE_GENERATOR_CLASS = CrossedChessboardEdgeGenerator

class HexagonWorldGeneratorFactory(CustomWidthWorldGeneratorFactory):
    EDGE_GENERATOR_CLASS = LimitedRangeRandomCoefficientEdgeGenerator
    POINT_GENERATOR_CLASS = HexagonPointGenerator
    @classmethod
    def create_world_generator(cls, number_of_dimensions, width):
        number_of_points = width ** number_of_dimensions
        point_generator = cls.POINT_GENERATOR_CLASS(number_of_dimensions, 0, width)
        edge_generator = cls.EDGE_GENERATOR_CLASS(0.5, 2.0)
        return SimpleWorldGenerator(number_of_dimensions, point_generator, edge_generator, number_of_points)
