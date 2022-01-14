class BaseBackend:
    def store_public_object(self, folder: str, object_id: str, blob: bytes, content_type: str) -> None:
        raise NotImplementedError()

    def delete_public_object(self, folder: str, object_id: str) -> None:
        raise NotImplementedError()
