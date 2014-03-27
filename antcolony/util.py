import json

def avg(iterable):
    sum_ = 0
    element_count = 0
    for element in iterable:
        sum_ += element
        element_count += 1
    return sum_ / element_count

def nice_json_dump(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

