import json

def avg(iterable):
    sum_ = 0
    element_count = 0
    for element in iterable:
        sum_ += element
        element_count += 1
    return sum_ / element_count

def get_average_coordinates(li_coordinates):
    """ Get coordinates of a point between two points. """
    assert len(li_coordinates) == 2 and len(li_coordinates[0]) == 2, 'This would probably work for any number of dimensions or coordinates, but was not tested'
    return [avg(i) for i in zip(*li_coordinates)]

def nice_json_dump(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

def corner_coordinates(iter_coordinates):
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for x, y in iter_coordinates:  # two dimensions support only
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
    left_lower_corner_coordinates  = [min_x, min_y]
    left_upper_corner_coordinates  = [min_x, max_y]
    right_lower_corner_coordinates = [max_x, min_y]
    right_upper_corner_coordinates = [max_x, max_y]
    return left_lower_corner_coordinates, left_upper_corner_coordinates, right_upper_corner_coordinates, right_lower_corner_coordinates

class Corner(object):
    LOWER_LEFT = 0
    UPPER_LEFT = 1
    UPPER_RIGHT = 2
    LOWER_RIGHT = 3

