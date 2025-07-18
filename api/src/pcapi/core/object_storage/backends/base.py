class FileNotFound(Exception):
    pass


class BaseBackend:
    def __init__(
        self,
        project_id: str | None = None,
        bucket_name: str = "",
    ) -> None:
        pass

    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        raise NotImplementedError()

    def get_public_object(self, folder: str, object_id: str) -> bytes:
        raise NotImplementedError()

    def delete_public_object(self, folder: str, object_id: str) -> None:
        raise NotImplementedError()

    def delete_public_object_recursively(self, storage_path: str) -> None:
        raise NotImplementedError()

    def list_files(self, folder: str, *, max_results: int = 1000) -> list[str]:
        raise NotImplementedError()
