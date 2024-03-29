from importlib import import_module


# Taken from django.utils.module_loading
def import_string(dotted_path: str | None) -> type:
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    if not dotted_path:
        raise ImportError("Import path cannot be empty")
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError(f'"{dotted_path}" doesn\'t look like a module path') from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError(f'Module "{module_path}" does not define a "{class_name}" attribute/class') from err
