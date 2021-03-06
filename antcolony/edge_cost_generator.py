from math import hypot, sqrt
from point import distance_between_points
import random

from util import corner_coordinates, get_average_coordinates

class AbstractEdgeCostGenerator(object):
    def __init__(self, exponent=1):
        self.exponent = exponent
    def register_points(self, points):
        pass
    def get_edge_cost(self, source_point, target_point):
        raise NotImplementedError('%s failed to overload get_edge_cost' % (self.__class__.__name__,))

class DistanceEdgeCostGenerator(AbstractEdgeCostGenerator):
    def get_edge_cost(self, *args, **kwargs):
        return distance_between_points(*args, **kwargs) ** self.exponent

class RandomCoefficientEdgeCostGenerator(DistanceEdgeCostGenerator):
    def __init__(self, min_random_coefficient, max_random_coefficient):
        super(RandomCoefficientEdgeCostGenerator, self).__init__()
        self.min_random_coefficient = min_random_coefficient
        self.max_random_coefficient = max_random_coefficient
    def get_edge_cost(self, source_point, target_point):
        base = super(RandomCoefficientEdgeCostGenerator, self).get_edge_cost(source_point, target_point)
        random_coefficient = random.uniform(self.min_random_coefficient, self.max_random_coefficient)
        result = base * random_coefficient
        assert result >= 0, 'Negative edge cost! base: %s, random_coefficient: %s' % (base, random_coefficient)
        return result

class AbstractDistanceFromPointsEdgeCostGenerator(AbstractEdgeCostGenerator):
    def __init__(self, *args, **kwargs):
        self.reference_points = None
        super(AbstractDistanceFromPointsEdgeCostGenerator, self).__init__(*args, **kwargs)
    def get_edge_cost(self, source_point, target_point):
        t_x, t_y = get_average_coordinates([source_point.coordinates, target_point.coordinates])
        dist = 0
        for reference_point in self.reference_points:  # subclass was supposed to set this in register_points()
            r_x, r_y = reference_point
            dist += hypot(r_x - t_x, r_y - t_y) #** self.exponent
        dist = dist ** self.exponent
        dist += 1
        assert dist >= 0, 'Negative edge cost!'
        return dist

class TrueDistanceFromCornersEdgeCostGenerator(AbstractDistanceFromPointsEdgeCostGenerator):
    def __init__(self, corners, *args, **kwargs):
        self.corners = corners
        super(TrueDistanceFromCornersEdgeCostGenerator, self).__init__(*args, **kwargs)
    def register_points(self, points):
        point_coordinates = [point.coordinates for point in points]
        cc = corner_coordinates(point_coordinates)
        self.reference_points = [cc[id_] for id_ in self.corners]
        #self.reference_points = [cc[id_] for id_ in self.corners] + [[15, 15]]
        #self.reference_points = [(6, 21)]
        #self.reference_points = cc[0:3]
        #self.reference_points = [(10, -10)]
        return super(TrueDistanceFromCornersEdgeCostGenerator, self).register_points(points)

class AbstractPairOfCornersOrientedEdgeCostGenerator(AbstractEdgeCostGenerator):
    PENALTY_MULTIPLIER = 5
    def __init__(self, point_type_pairs, *args, **kwargs):
        self.point_type_pairs = point_type_pairs  # ex. upper left, lower right
        self.point_pairs = []
        super(AbstractPairOfCornersOrientedEdgeCostGenerator, self).__init__(*args, **kwargs)
    def register_points(self, points):
        point_coordinates = [point.coordinates for point in points]
        cc = corner_coordinates(point_coordinates)
        self.point_pairs = [[cc[id_a], cc[id_b]] for id_a, id_b in self.point_type_pairs]
        return super(AbstractPairOfCornersOrientedEdgeCostGenerator, self).register_points(points)
    def get_edge_cost(self, source_point, target_point):
        assert len(source_point.coordinates) == 2, "sorry, %s only supports two dimensions" % (self.__class__.__name__,)
        t_coords = get_average_coordinates([source_point.coordinates, target_point.coordinates])
        #for ((good_x, good_y), (bad_x, bad_y)) in self.point_pairs:
            #if t_x >= ((good_x+bad_x)/2) and t_y >= ((good_y+bad_y)/2):
        multiplier = self._is_point_in_penalty_zone(t_coords) and self.PENALTY_MULTIPLIER or 1
        dist = distance_between_points(source_point, target_point) * multiplier
        assert dist >= 0, 'Negative edge cost!'
        return dist

class ThresholdDistanceFromCornerEdgeCostGenerator(AbstractPairOfCornersOrientedEdgeCostGenerator):
    THRESHOLD = 0.8
    def _is_point_in_penalty_zone(self, t_coords):
        for good_coords, bad_coords in self.point_pairs:
            for coord_id, t_coord in enumerate(t_coords):
                good_coord = good_coords[coord_id]
                bad_coord = bad_coords[coord_id]
                coord_span = abs(good_coord-bad_coord)
                min_coord = min(good_coord, bad_coord)
                if good_coord > bad_coord:
                    threshold = 1 - self.THRESHOLD
                    if t_coord < ((coord_span * threshold) + min_coord):
                        return False  # if coordinate is out of penalty zone in *any* dimension, it is out of the penalty zone
                elif good_coord < bad_coord:
                    threshold = self.THRESHOLD
                    if t_coord > ((coord_span * threshold) + min_coord):
                        return False  # if coordinate is out of penalty zone in *any* dimension, it is out of the penalty zone
                else:
                    assert good_coord != bad_coord, "this isn't really a dimension"
        return True

def distance(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def is_between(a, c, b, epsilon=0):
    return abs(distance(a, c) + distance(c, b) - distance(a, b)) <= epsilon

class SlantedBlockadeEdgeCostGenerator(AbstractPairOfCornersOrientedEdgeCostGenerator):
    THRESHOLD = 0.05
    def register_points(self, points):
        r = super(SlantedBlockadeEdgeCostGenerator, self).register_points(points)
        for i, point_pair in enumerate(self.point_pairs):
            self.point_pairs[i][1] = get_average_coordinates(point_pair)
        return r  # ?
    def _is_point_in_penalty_zone(self, t_coords):
        for good_coords, bad_coords in self.point_pairs:
            if is_between(good_coords, bad_coords, t_coords, 0.0001):
                return True
        return False
    def get_edge_cost(self, source_point, target_point):
        assert len(source_point.coordinates) == 2, "sorry, %s only supports two dimensions" % (self.__class__.__name__,)
        multiplier = (
            self._is_point_in_penalty_zone(
                source_point.coordinates
            )
            or
            self._is_point_in_penalty_zone(
                target_point.coordinates
            )
        ) and self.PENALTY_MULTIPLIER or 1
        dist = distance_between_points(source_point, target_point) * multiplier
        assert dist >= 0, 'Negative edge cost!'
        return dist
