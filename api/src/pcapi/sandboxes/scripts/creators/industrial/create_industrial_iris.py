from pcapi.core.geography.api import import_iris_from_7z
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


IRIS_FILE_PATH = "./src/pcapi/sandboxes/binaries/iris_min.7z"


@log_func_duration
def create_iris() -> None:
    import_iris_from_7z(IRIS_FILE_PATH)
