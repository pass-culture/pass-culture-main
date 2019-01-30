import simplejson as json

from sandboxes.scripts import getters

def get_testcafe_helpers(module_name):
    module = getattr(getters, module_name)
    items = [
        (key.split('get_')[1].upper(), getattr(module, key)())
        for key in dir(module)
        if key.startswith('get_existing')
    ]
    return dict(items)

def get_all_testcafe_helpers():
    module_names = [
        m for m in dir(getters)
        if type(getattr(getters, m)).__name__ == 'module'
    ]
    helpers = {}
    for module_name in module_names:
        if module_name == 'sandboxes':
            continue
        helpers.update(get_testcafe_helpers(module_name))
    return helpers

def print_testcafe_helpers(module_name):
    print('\n{} :'.format(module_name))
    print(json.dumps(get_testcafe_helpers(module_name), indent=2, sort_keys=True))

def print_all_testcafe_helpers():
    module_names = [
        m for m in dir(getters)
        if type(getattr(getters, m)).__name__ == 'module' \
        and module_name != 'sandboxes'
    ]
    for module_name in module_names:
        print_testcafe_helpers(module_name)
