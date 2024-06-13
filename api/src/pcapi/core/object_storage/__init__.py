from pcapi import settings
from pcapi.utils.module_loading import import_string


GCP = "GCP"
GCP_ALTERNATE = "GCP_ALTERNATE"
LOCAL_FILE_STORAGE = "local"
BACKENDS_MAPPING = {
    GCP: "pcapi.core.object_storage.backends.gcp.GCPBackend",
    GCP_ALTERNATE: "pcapi.core.object_storage.backends.gcp.GCPAlternateBackend",
    LOCAL_FILE_STORAGE: "pcapi.core.object_storage.backends.local.LocalBackend",
}


class FileNotFound(Exception):
    pass


def _check_backends_module_paths() -> None:
    """When the app starts, this checks if the module paths are correct"""
    for path in BACKENDS_MAPPING.values():
        import_string(path)


_check_backends_module_paths()


def _get_backends() -> set:
    providers = (settings.OBJECT_STORAGE_PROVIDER or "").split(",")
    providers = [p.strip() for p in providers]
    if not providers:
        raise RuntimeError("The OBJECT_STORAGE_PROVIDER env var must be defined")
    return {BACKENDS_MAPPING[p] for p in providers}


def _check_backend_setting() -> None:
    """When the app starts, check that the env variable is correct."""
    try:
        _get_backends()
    except KeyError as exc:
        value = exc.args[0]
        available_backends = ", ".join(str(short_name) for short_name in BACKENDS_MAPPING)
        raise RuntimeError(f'Unknown storage provider ("{value}"). Accepted values are: {available_backends}')


_check_backend_setting()


def store_public_object(folder: str, object_id: str, blob: bytes, content_type: str, *, bucket: str = "") -> None:
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        backend(bucket_name=bucket).store_public_object(folder, object_id, blob, content_type)


def get_public_object(folder: str, object_id: str, *, bucket: str = "") -> list[bytes]:
    files = []
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        files.append(backend(bucket_name=bucket).get_public_object(folder, object_id))
    return files


def delete_public_object(folder: str, object_id: str, *, bucket: str = "") -> None:
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        backend(bucket_name=bucket).delete_public_object(folder, object_id)


def list_files(folder: str, *, bucket: str = "", max_results: int = 1000) -> list[str]:
    files = []
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        files.extend(backend(bucket_name=bucket).list_files(folder, max_results=max_results))
    return files
