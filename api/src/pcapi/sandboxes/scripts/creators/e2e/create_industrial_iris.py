from pcapi.core.geography.api import import_iris_from_7z


IRIS_FILE_PATH = "./src/pcapi/sandboxes/binaries/iris_min.7z"


def create_iris() -> None:
    import_iris_from_7z(IRIS_FILE_PATH)
