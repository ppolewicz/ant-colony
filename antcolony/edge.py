class AbstractEdgeEnd(object):
    def drop_pheromone(self, amount):
        raise NotImplementedError()

class EdgeEnd(AbstractEdgeEnd):
    def __init__(self, edge, point, pheromone_level):
        self.edge = edge
        self.point = point
        self.pheromone_level = pheromone_level
    def drop_pheromone(self, amount):
        self.pheromone_level += amount
    def __repr__(self):
        return ''

class DummyEdgeEnd(AbstractEdgeEnd):
    def __init__(self, point):
        self.point = point
    def drop_pheromone(self, amount):
        pass

class Edge(object):
    JSON_KEY_ENDPOINTS = 'endpoints'
    JSON_KEY_COST = 'cost'
    def __init__(self, point_A, point_B, cost):
        a_point, b_point = sorted([point_A, point_B])
        assert a_point!=b_point
        self.a_end = EdgeEnd(self, a_point, 0)
        self.b_end = EdgeEnd(self, b_point, 0)
        self.cost = cost
    def __eq__(self, other):
        if self.a_end.point!=other.a_end.point:
            return False
        return self.b_end.point==other.b_end.point
    def __hash__(self):
        return hash((self.a_end.point, self.b_end.point))
    #def __repr__(self):
    #    return 'Edge{%s <[%s]--[%s]> %s (%s)}' % (self.a_end.point, self.a_end.pheromone_level, self.b_end.pheromone_level, self.b_end.point, self.cost)
    def get_other_end(self, end):
        if end.point==self.a_end.point:
            return self.b_end
        else:
            return self.a_end
    def register_with_points(self):
        for end in self.a_end, self.b_end:
            end.point.add_edge_end(end)
    def to_json(self):
        return {
            self.JSON_KEY_ENDPOINTS: (
                self.a_end.point.coordinates,
                self.b_end.point.coordinates,
            ),
            self.JSON_KEY_COST: self.cost,
        }
    @classmethod
    def from_json(cls, json_edge, point_index):
        cost = json_edge[cls.JSON_KEY_COST]
        point_A, point_B = [point_index[tuple(coordinate)] for coordinate in json_edge[cls.JSON_KEY_ENDPOINTS]]
        return cls(point_A, point_B, cost)

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

