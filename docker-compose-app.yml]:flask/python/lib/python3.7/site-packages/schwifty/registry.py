import json
from pkg_resources import resource_filename


_registry = {}


def has(name):
    return name in _registry


def get(name):
    if not has(name):
        with open(resource_filename(__name__, name + '-registry.json'), 'r') as fp:
            save(name, json.load(fp))
    return _registry[name]


def save(name, data):
    _registry[name] = data


def build_index(base_name, index_name, key, **predicate):
    def make_key(entry):
        return tuple(entry[k] for k in key) if isinstance(key, tuple) else entry[key]

    def match(entry):
        return all(entry[key] == value for key, value in predicate.items())

    base = get(base_name)
    save(index_name, dict((make_key(entry), entry) for entry in base if match(entry)))


def manipulate(name, func):
    registry = get(name)
    if isinstance(registry, dict):
        for key, value in registry.items():
            registry[key] = func(key, value)
    elif isinstance(registry, list):
        registry = [func(item) for item in registry]
    save(name, registry)
