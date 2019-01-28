import json

from sandboxes.scripts.utils import getters

def print_testcafe_helpers():
    items = [
        (key.split('get_')[1].upper(), getattr(getters, key)())
        for key in dir(getters)
        if key.startswith('get_')
    ]
    print(json.dumps(dict(items), indent=2))
