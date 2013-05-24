#!/usr/bin/python2.7
import os
from collections import defaultdict
from pprint import pprint
import json

DATA_PATH = 'results'
result_filename = 'results.json'
queens_in_worlds = defaultdict(lambda: set())
di_world_qualification = defaultdict(lambda: set())

data = []

for root, subfolders, files in os.walk(DATA_PATH):
    if root==DATA_PATH:
        continue
    if result_filename not in files:
        continue
    dirname = os.path.split(root)[-1]
    world_name, queen_name, amount_of_ants, incarnation_number = dirname.split('_')
    queens_in_worlds[world_name].add(queen_name)
    di_world_qualification[queen_name].add(world_name)
    results = json.load(open(os.path.join(root, result_filename)))
    data.append([results['total_real_time'], dirname])


#pprint({k: v for k, v in queens_in_worlds.iteritems()})

#class AllResults(object):
#    pass

#pprint({k: v for k, v in di_world_qualification.iteritems()})

for di in (di_world_qualification, queens_in_worlds):
    for k in sorted(di, reverse=True):
        v = di[k]
        #print '%s: %s' % (k, len(v))
        print '%s: %s' % (k, v)
    print '-'*50

