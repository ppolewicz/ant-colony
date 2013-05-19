class AbstractEdgeEnd(object):
    def drop_pheromone(self, amount):
        raise NotImplementedError()

class EdgeEnd(AbstractEdgeEnd):
    def __init__(self, edge, point):
        self.edge = edge
        self.point = point
        self.reset()
    def drop_pheromone(self, amount):
        self.pheromone_level += amount
    def reset(self):
        self.pheromone_level = 0.0
    def __repr__(self):
        return 'EdgeEnd of %s, point: %s, pheromone: %s' % (self.edge, self.point, self.pheromone_level)

class DummyEdgeEnd(AbstractEdgeEnd):
    def __init__(self, point):
        self.point = point
        self.edge = None
    def drop_pheromone(self, amount):
        pass

class Edge(object):
    JSON_KEY_ENDPOINTS = 'endpoints'
    JSON_KEY_COST = 'cost'
    JSON_KEY_PHEROMONE = 'pheromone'
    def __init__(self, point_A, point_B, cost):
        a_point, b_point = sorted([point_A, point_B])
        assert a_point!=b_point, a_point
        self.a_end = EdgeEnd(self, a_point)
        self.b_end = EdgeEnd(self, b_point)
        self.cost = cost
    def __eq__(self, other):
        if self.a_end.point!=other.a_end.point:
            return False
        return self.b_end.point==other.b_end.point
    def __hash__(self):
        return hash((self.a_end.point, self.b_end.point))
    def __repr__(self):
        return 'Edge{%s <[%s]--[%s]> %s (%s)}' % (self.a_end.point, self.a_end.pheromone_level, self.b_end.pheromone_level, self.b_end.point, self.cost)
    def get_other_end(self, end):
        if end.point==self.a_end.point:
            return self.b_end
        elif end.point==self.b_end.point:
            return self.a_end
        else:
            assert False, 'This is an end of some other edge'
    def get_other_end_by_point(self, point):
        if point==self.a_end.point:
            return self.b_end
        elif point==self.b_end.point:
            return self.a_end
        else:
            assert False, "This edge's neither point is the one that was supplied"
    def pheromone_sum(self):
        return self.a_end.pheromone_level + self.b_end.pheromone_level
    def pheromone_level(self):
        return self.pheromone_sum() / 2
    def register_with_points(self):
        for end in self.a_end, self.b_end:
            end.point.add_edge_end(end)
    def reset(self):
        for end in self.a_end, self.b_end:
            end.reset()
    def to_json(self):
        return {
            self.JSON_KEY_ENDPOINTS: (
                self.a_end.point.coordinates,
                self.b_end.point.coordinates,
            ),
            self.JSON_KEY_COST: self.cost,
            self.JSON_KEY_PHEROMONE: self.pheromone_level(),
        }
    @classmethod
    def from_json(cls, json_edge, point_index):
        cost = json_edge[cls.JSON_KEY_COST]
        point_A, point_B = [point_index[tuple(coordinate)] for coordinate in json_edge[cls.JSON_KEY_ENDPOINTS]]
        obj = cls(point_A, point_B, cost)
        obj.a_end.pheromone_level = obj.b_end.pheromone_level = json_edge[cls.JSON_KEY_PHEROMONE]
        return obj

if __name__=='__main__':
    from pprint import pprint
    pprint(
        set(
            [
                Edge((1,), (2,), 5),
                Edge((1,), (2,), 5),
                Edge((1,), (2,), 6),
            ]
        )
    )

