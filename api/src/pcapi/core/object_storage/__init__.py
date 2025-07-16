from pcapi import settings
from pcapi.core.object_storage.backends.base import BaseBackend
from pcapi.core.object_storage.backends.gcp import GCPAlternateBackend
from pcapi.core.object_storage.backends.gcp import GCPBackend
from pcapi.core.object_storage.backends.local import LocalBackend
from pcapi.utils.module_loading import import_string


GCP = "GCP"
GCP_ALTERNATE = "GCP_ALTERNATE"
LOCAL_FILE_STORAGE = "local"
BACKENDS_MAPPING = {GCP: GCPBackend, GCP_ALTERNATE: GCPAlternateBackend, LOCAL_FILE_STORAGE: LocalBackend}


def check_backend_setting() -> None:
    """When the app starts, check that the env variable is correct."""
    providers = (settings.OBJECT_STORAGE_PROVIDER or "").split(",")
    providers = [p.strip() for p in providers]
    if not providers:
        raise RuntimeError("The OBJECT_STORAGE_PROVIDER env var must be defined")

    for provider in providers:
        if provider not in BACKENDS_MAPPING:
            available_backends = ", ".join(str(short_name) for short_name in BACKENDS_MAPPING)
            raise RuntimeError(f'Unknown storage provider ("{providers}"). Accepted values are: {available_backends}')


check_backend_setting()


def _get_backends(bucket: str, project_id: str | None) -> set[BaseBackend]:
    providers = (settings.OBJECT_STORAGE_PROVIDER or "").split(",")
    providers = [p.strip() for p in providers]
    if not providers:
        raise RuntimeError("The OBJECT_STORAGE_PROVIDER env var must be defined")

    backends: set[BaseBackend] = set()
    for provider in providers:
        ObjectStorageBackend = BACKENDS_MAPPING[provider]
        backends.add(ObjectStorageBackend(project_id, bucket))

    return backends


def store_public_object(
    folder: str, object_id: str, blob: bytes, content_type: str, *, bucket: str = "", project_id: str | None = None
) -> None:
    for backend in _get_backends(bucket, project_id):
        backend.store_public_object(folder, object_id, blob, content_type)


def get_public_object(folder: str, object_id: str, *, bucket: str = "", project_id: str | None = None) -> list[bytes]:
    files = []
    for backend in _get_backends(bucket, project_id):
        files.append(backend.get_public_object(folder, object_id))
    return files


def delete_public_object(folder: str, object_id: str, *, bucket: str = "", project_id: str | None = None) -> None:
    for backend in _get_backends(bucket, project_id):
        backend.delete_public_object(folder, object_id)


def delete_public_object_recursively(storage_path: str, bucket: str = "", project_id: str | None = None) -> None:
    for backend in _get_backends(bucket, project_id):
        backend.delete_public_object_recursively(storage_path)


def list_files(folder: str, *, bucket: str = "", max_results: int = 1000, project_id: str | None = None) -> list[str]:
    files = []
    for backend in _get_backends(bucket, project_id):
        files.extend(backend.list_files(folder, max_results=max_results))
    return files
