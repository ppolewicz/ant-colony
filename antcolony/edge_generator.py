import random
from edge import Edge

# NOTE: classes of this module use chain inheritance

class AbstractEdgeGenerator(object):
    def generate_all(self, points):
        for source_point in points:
            for target_point in points:
                if source_point == target_point:
                    continue
                yield Edge(source_point, target_point, self.get_edge_cost(source_point, target_point))

class SimpleEdgeGenerator(AbstractEdgeGenerator):
    def get_edge_cost(self, source_point, target_point):
        distance = source_point.get_distance_to(target_point)
        return distance

class RandomCoefficientEdgeGenerator(SimpleEdgeGenerator):
    def __init__(self, min_random_coefficient, max_random_coefficient):
        super(RandomCoefficientEdgeGenerator, self).__init__()
        self.min_random_coefficient = min_random_coefficient
        self.max_random_coefficient = max_random_coefficient
    def get_edge_cost(self, source_point, target_point):
        base = super(RandomCoefficientEdgeGenerator, self).get_edge_cost(source_point, target_point)
        random_coefficient = random.randint(self.min_random_coefficient, self.max_random_coefficient)
        return base + random_coefficient

class LimitedRandomCoefficientEdgeGenerator(RandomCoefficientEdgeGenerator):
    def generate_all(self, points):
        min_hint_edges_from_point = 2
        max_hint_edges_from_point = 4
        existing_edges = set()
        for source_point in points:
            temporary_edges = []
            for target_point in points:
                if source_point == target_point:
                    continue
                edge = Edge(source_point, target_point, self.get_edge_cost(source_point, target_point))
                if edge in existing_edges:
                    continue
                temporary_edges.append(edge)
            temporary_edges.sort(key=lambda edge: edge.cost)
            for edge in temporary_edges[:random.randint(min_hint_edges_from_point, max_hint_edges_from_point)]:
                existing_edges.add(edge)
                yield edge

