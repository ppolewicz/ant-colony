#!/usr/bin/python2.7
import os
from collections import defaultdict
from pprint import pprint
import json, csv
import itertools

from util import avg

DATA_PATH = 'results'
result_filename = 'results.json'
stats_filename = 'stats.csv'
queens_in_worlds = defaultdict(lambda: set())
di_world_qualification = defaultdict(lambda: set())

queens = set()
worlds = set()

data = defaultdict(
    lambda: defaultdict(
        lambda: defaultdict(
            lambda: {}
        )
    )
)

for root, subfolders, files in os.walk(DATA_PATH):
    if root==DATA_PATH:
        continue
    if result_filename not in files:
        continue
    dirname = os.path.split(root)[-1]
    world_name, queen_name, amount_of_ants, incarnation_number = dirname.split('_')
    if queen_name=="BasicQueen-HalfLengthPenaltyExponent":
        continue
    #worlds.add(world_name)
    #results = json.load(open(os.path.join(root, result_filename)))
    #queen_name = '_'.join([queen_name, amount_of_ants])
    #queens.add(queen_name)
    #di = data[world_name, queen_name][incarnation_number]
    #di['cost'] = results['cost'] * int(amount_of_ants)
    #di['best_cost'] = results['best_finding_cost']
    #di['total_real_time'] = results['total_real_time']
    stats_path = os.path.join(root, stats_filename)

    # load data
    stats_data = []
    for row in itertools.islice(csv.reader(open(stats_path, 'rb')), 1, None):
        #print row[0], row[3]
        stats_data.append(row[3])

    # precompute
    group_size = 500
    aggregates = []
    while stats_data:
        aggregates.append(
            avg(
                [float(stats_data.pop()) for i in xrange(group_size)]
            )
        )
    aggregates.reverse()

    if aggregates[3] / 2 < aggregates[-1]:
        continue
    print root
    pprint(aggregates)
    #break
    raw_input()

raise Exception()

columns = sorted(queens)
writer = csv.writer(open('matrix.csv', 'wb'))
writer.writerow(['world'] + columns)

for world in worlds:
    #print 'world', world
    row = [world]
    for queen in columns:
        #print 'queen', queen
        incarnations = data.get((world, queen), {})
        results = [incarnation['cost'] for incarnation in incarnations.values()]
        if results:
            cell = min(results)
        else:
            cell = ''
        row.append(cell)
        #print 'cell', cell
    writer.writerow(row)
    #print row


