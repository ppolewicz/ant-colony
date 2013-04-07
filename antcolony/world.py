from point import AnthillPoint, FoodPoint, Point
from edge import Edge

class World(object):
    JSON_KEY_EDGES = 'edges'
    JSON_KEY_POINTS = 'points'

    JSON_KEY_ANTHILL_POINTS = 'anthills'
    JSON_KEY_FOOD_POINTS = 'food'
    JSON_KEY_ORDINARY_POINTS = 'ordinary'
    def __init__(self, points, edges):
        self.points = points
        self.edges = edges
        self.elapsed_time = 0.0
    def is_resolved(self):
        return not self.get_food_points()
    def get_anthills(self):
        return [point for point in self.points if point.is_anthill()]
    def get_anthill(self):
        anthills = self.get_anthills()
        assert len(anthills)==1, 'multiple anthills are not fully supported'
        return anthills[0]
    def get_food_points(self):
        return [point for point in self.points if not point.is_anthill() and point.food > 0]
    def get_ordinary_points(self):
        return [point for point in self.points if not point.is_anthill() and not point.food > 0]
    def __repr__(self):
        return 'World (%f):\n    ' % self.elapsed_time + '\n    '.join(map(str, self.edges))
    def to_json(self):
        points = {}
        points[self.JSON_KEY_ANTHILL_POINTS] = [anthill.to_json() for anthill in self.get_anthills()]
        points[self.JSON_KEY_FOOD_POINTS] = [foodpoint.to_json() for foodpoint in self.get_food_points()]
        points[self.JSON_KEY_ORDINARY_POINTS] = [point.to_json() for point in self.get_ordinary_points()]

        output = {}
        output[self.JSON_KEY_POINTS] = points
        output[self.JSON_KEY_EDGES] = [edge.to_json() for edge in self.edges]
        return output
    @classmethod
    def from_json(cls, json_world):
        point_index = {}
        points = set()
        json_points = json_world[cls.JSON_KEY_POINTS]
        for point_type_key, point_class in [
            (cls.JSON_KEY_FOOD_POINTS, FoodPoint),
            (cls.JSON_KEY_ANTHILL_POINTS, AnthillPoint),
            (cls.JSON_KEY_ORDINARY_POINTS, Point),
            ]:
            for json_point in json_points[point_type_key]:
                p = point_class.from_json(json_point)
                point_index[p.coordinates] = p
                points.add(p)
        edges = set()
        for json_edge in json_world[cls.JSON_KEY_EDGES]:
            e = Edge.from_json(json_edge, point_index)
            e.register_with_points()
            edges.add(e)
        return cls(points, edges)

