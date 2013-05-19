import random
from edge import Edge

# NOTE: classes of this module use chain inheritance

class AbstractEdgeGenerator(object):
    def generate_and_register(self, points, *args, **kwargs):
        edges = self._generate_all(points, *args, **kwargs)
        for edge in edges:
            edge.register_with_points()
            yield edge
    def _get_edge_cost(self, source_point, target_point):
        raise NotImplementedError()
    def _generate_all(self, points, *args, **kwargs):
        for source_point in points:
            for target_point in points:
                if source_point == target_point:
                    continue
                yield Edge(source_point, target_point, self._get_edge_cost(source_point, target_point))

class SimpleEdgeGenerator(AbstractEdgeGenerator):
    def _get_edge_cost(self, source_point, target_point):
        distance = source_point.get_distance_to(target_point)
        return distance

class RandomCoefficientEdgeGenerator(SimpleEdgeGenerator):
    def __init__(self, min_random_coefficient, max_random_coefficient):
        super(RandomCoefficientEdgeGenerator, self).__init__()
        self.min_random_coefficient = min_random_coefficient
        self.max_random_coefficient = max_random_coefficient
    def _get_edge_cost(self, source_point, target_point):
        base = super(RandomCoefficientEdgeGenerator, self)._get_edge_cost(source_point, target_point)
        random_coefficient = random.randint(self.min_random_coefficient, self.max_random_coefficient)
        result = base + random_coefficient
        assert result >= 0, 'Negative edge cost! base: %s, random_coefficient: %s' % (base, random_coefficient)
        return result

class LimitMixin(object):
    def _generate_all(self, points, *args, **kwargs):
        min_hint_edges_from_point = 1
        max_hint_edges_from_point = 2
        existing_edges = set()
        for source_point in points:
            temporary_edges = []
            for target_point in points:
                if source_point == target_point:
                    continue
                edge = Edge(source_point, target_point, self._get_edge_cost(source_point, target_point))
                if edge in existing_edges:
                    continue
                temporary_edges.append(edge)
            temporary_edges.sort(key=lambda edge: edge.cost)
            for edge in temporary_edges[:random.randint(min_hint_edges_from_point, max_hint_edges_from_point)]:
                existing_edges.add(edge)
                yield edge

class LimitedRandomCoefficientEdgeGenerator(LimitMixin, RandomCoefficientEdgeGenerator):
    pass

class LimitedEdgeGenerator(LimitMixin, SimpleEdgeGenerator):
    pass

class ChessboardEdgeGenerator(SimpleEdgeGenerator):
    def _get_candidates(self, source_coordinates):
        for axis_number in xrange(len(source_coordinates)):
            yield tuple(source_coordinates[:axis_number] + (source_coordinates[axis_number]+1,) + source_coordinates[axis_number+1:])
    def _generate_all(self, points, *args, **kwargs):
        point_index = {point.coordinates: point for point in points}
        for source_coordinates, source_point in point_index.iteritems():
            for candidate_coordinates in self._get_candidates(source_coordinates):
                target_point = point_index.get(candidate_coordinates, None)
                if target_point is not None:
                    yield Edge(source_point, target_point, self._get_edge_cost(source_point, target_point))

class CrossedChessboardEdgeGenerator(ChessboardEdgeGenerator):
    def _get_candidates(self, source_coordinates):
        assert len(source_coordinates) == 2, 'some edges would be missing'
        for i in super(CrossedChessboardEdgeGenerator, self)._get_candidates(source_coordinates):
            yield i
        #yield tuple([coordinate +1 for coordinate in source_coordinates]) # longest edge in this dimension
        yield tuple((source_coordinates[0]+1, source_coordinates[1]+1))
        yield tuple((source_coordinates[0]+1, source_coordinates[1]-1))

        # if someone would like to make it work for more dimensions, here are some clues:
        #import numpy
        #a = numpy.matrix([[1, 2], [3, 4]])
        #b = numpy.matrix([[2, 2], [2, 2]])
        #a+b
        #matrix([[3, 4], [5, 6]])
        #a.tolist()
        #itertools.product


if __name__=='__main__':
    from point import Point
    from pprint import pprint
    def make_points(li_coords):
        return [Point(coords) for coords in li_coords]
    coords_2d = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]
    coords_3d = [
        (0, 0, 0),
        (0, 0, 1),
        (0, 1, 0),
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 1, 1),
    ]
    points_2d = make_points(coords_2d)
    #points_3d = make_points(coords_3d)
    generator = ChessboardEdgeGenerator()
    generator = CrossedChessboardEdgeGenerator()
    points = points_2d
    pprint(
        list(
            generator._generate_all(points)
        )
    )

