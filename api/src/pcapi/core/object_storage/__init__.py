from pcapi import settings
from pcapi.utils.module_loading import import_string


OVH = "OVH"
GCP = "GCP"
GCP_ALTERNATE = "GCP_ALTERNATE"
LOCAL_FILE_STORAGE = "local"
BACKENDS_MAPPING = {
    OVH: "pcapi.core.object_storage.backends.ovh.OVHBackend",
    GCP: "pcapi.core.object_storage.backends.gcp.GCPBackend",
    GCP_ALTERNATE: "pcapi.core.object_storage.backends.gcp.GCPAlternateBackend",
    LOCAL_FILE_STORAGE: "pcapi.core.object_storage.backends.local.LocalBackend",
}


def _check_backends_module_paths() -> None:
    """When the app starts, this checks if the module paths are correct"""
    for path in BACKENDS_MAPPING.values():
        import_string(path)


_check_backends_module_paths()


def _check_backend_setting() -> None:
    """When the app starts, this checks if the env variable is correct"""
    if settings.OBJECT_STORAGE_PROVIDER:
        providers = settings.OBJECT_STORAGE_PROVIDER.split(",")
        if any(provider not in BACKENDS_MAPPING for provider in providers):
            available_backends = ", ".join(str(var) for var in BACKENDS_MAPPING)
            raise RuntimeError(
                "Unknown storage provider(%s). Accepted values are: %s" % (providers, available_backends)
            )


_check_backend_setting()


def _get_backends() -> set:
    backends_set = set()
    if settings.OBJECT_STORAGE_PROVIDER:
        _providers = settings.OBJECT_STORAGE_PROVIDER.split(",")
        for p in _providers:
            backends_set.add(BACKENDS_MAPPING[p])
    elif settings.IS_RUNNING_TESTS or settings.IS_DEV:
        backends_set.add(BACKENDS_MAPPING["local"])
    else:
        backends_set.add(BACKENDS_MAPPING["OVH"])
    return backends_set


def store_public_object(folder: str, object_id: str, blob: bytes, content_type: str) -> None:
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        backend().store_public_object(folder, object_id, blob, content_type)


def delete_public_object(folder: str, object_id: str) -> None:
    for backend_path in _get_backends():
        backend = import_string(backend_path)
        backend().delete_public_object(folder, object_id)
