import logging

from pcapi.core.object_storage import GCPBackend


logger = logging.getLogger(__name__)


def copy_file_between_storage_backends(
    source_storage: GCPBackend,
    destination_storage: GCPBackend,
    source_folder: str,
    destination_folder: str,
    file_id: str,
) -> str | None:
    """
    Copies a file from a source storage to a destination storage.

    Args:
        source_storage: The source storage instance (must support object_exists and copy_object_to).
        destination_storage: The destination storage instance (must support object_exists).
        source_folder: The folder path within the source bucket.
            Ex: "artist/images"
        destination_folder: The folder path within the destination bucket.
            Ex: "thumbs/artist"
        file_id: The identifier of the file to copy.
            Ex: "b8f0e42a-7d91-4e20-9182-1a3b4c5d6e7f" (mediation_uuid)

    Returns:
        str | None: The file_id if the file is present in the destination (either pre-existing or successfully copied),
        or None if the file could not be found or copied.
    """
    if not file_id:
        return None

    try:
        if destination_storage.object_exists(destination_folder, file_id):
            return file_id

        if not source_storage.object_exists(source_folder, file_id):
            logger.warning(
                "File not found in source storage. Cannot copy.",
                extra={
                    "file_id": file_id,
                    "source_bucket": source_storage.bucket_name,
                    "source_folder": source_folder,
                },
            )
            return None

        logger.info(
            "Copying file between storage buckets...",
            extra={
                "file_id": file_id,
                "from_bucket": source_storage.bucket_name,
                "to_bucket": destination_storage.bucket_name,
            },
        )
        source_storage.copy_object_to(
            source_folder=source_folder,
            source_object_id=file_id,
            destination_backend=destination_storage,
            destination_folder=destination_folder,
            destination_object_id=file_id,
        )
        return file_id
    except Exception as err:
        logger.error(
            "Failed to copy file between storage buckets.",
            extra={
                "file_id": file_id,
                "from_bucket": source_storage.bucket_name,
                "to_bucket": destination_storage.bucket_name,
                "error": err,
            },
        )
        return None
