import json

def avg(iterable):
    return sum(iterable) / len(iterable)

def nice_json_dump(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

