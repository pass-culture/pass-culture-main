from importlib.util import module_from_spec
from importlib.util import spec_from_file_location


def get_imported_module(file_name, folder_path="/tmp/uploads/", module_name=None):
    if module_name is None:
        module_name = file_name.replace(".py", "")
    imported_spec = spec_from_file_location(module_name, "{}/{}".format(folder_path, file_name))
    imported_module = module_from_spec(imported_spec)
    imported_spec.loader.exec_module(imported_module)
    return imported_module
