import os
import json

from reality_factory import RealityFactory

class Simulator(object):
    pass

class Simulation(object):
    pass


#reality = RealityFactory.create_reality(0, 1, 20, 2)
#edgelist = [(edge.a_end, edge.b_end, {'weight': edge.cost}) for edge in reality.world.edges]
#from vizualizer import Vizualizer
#Vizualizer.draw_edges(edgelist)

#pprint(reality.world.to_json())
world_dir = 'worlds'
for x in xrange(20):
    reality = RealityFactory.create_reality(min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1, number_of_points=20, number_of_dimensions=2)
    json.dump(reality.world.to_json(), open(os.path.join(world_dir, 'world-%s.json' % (x,)), 'w'))

for file_ in os.listdir(world_dir):
    file_ = os.path.join(world_dir, file_)
    assert os.path.isfile(file_), 'unidentified object in %s/: %s' % (world_dir, file_)
    json_world = json.load(open(file_, 'r'))
    reality = RealityFactory.from_json_world(json_world, min_pheromone_dropped_by_ant=0, max_pheromone_dropped_by_ant=1)


