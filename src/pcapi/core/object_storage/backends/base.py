class BaseBackend:
    def store_public_object(
        self, bucket: str, object_id: str, blob: bytes, content_type: str, symlink_path=None
    ) -> None:
        raise NotImplementedError()

    def delete_public_object(self, bucket: str, object_id: str) -> None:
        raise NotImplementedError()
