import simplejson as json

from pcapi.sandboxes.scripts import getters


def get_testcafe_helper(module_name, getter_name):  # type: ignore [no-untyped-def]
    module = getattr(getters, module_name)
    getter = getattr(module, getter_name)
    return getter()


def get_testcafe_helpers(module_name):  # type: ignore [no-untyped-def]
    module = getattr(getters, module_name)
    items = [
        (key.split("get_")[1].upper(), getattr(module, key)()) for key in dir(module) if key.startswith("get_existing")
    ]
    return dict(items)


def print_dumped_object(obj):  # type: ignore [no-untyped-def]
    print(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True))


def get_all_getters():  # type: ignore [no-untyped-def]
    module_names = [m for m in dir(getters) if type(getattr(getters, m)).__name__ == "module"]
    helpers = {}
    for module_name in module_names:
        if module_name == "sandboxes":
            continue
        helpers.update(get_testcafe_helpers(module_name))
    return helpers


def print_testcafe_helper(module_name, getter_name):  # type: ignore [no-untyped-def]
    helper = get_testcafe_helper(module_name, getter_name)
    print_dumped_object(helper)


def print_testcafe_helpers(module_name):  # type: ignore [no-untyped-def]
    helpers_by_name = get_testcafe_helpers(module_name)
    print("\n{} :".format(module_name))
    print_dumped_object(helpers_by_name)


def print_all_testcafe_helpers():  # type: ignore [no-untyped-def]
    module_names = [
        module_name
        for module_name in dir(getters)
        if type(getattr(getters, module_name)).__name__ == "module" and module_name != "sandboxes"
    ]
    for module_name in module_names:
        print_testcafe_helpers(module_name)
