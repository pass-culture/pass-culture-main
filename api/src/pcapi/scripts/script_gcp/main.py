"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=bsr-script-gcp-files-size \
  -f NAMESPACE=script_gcp \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.object_storage.backends.gcp import GCPBackend


logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10_000_000


def main(bucket_name: str) -> None:
    backend = GCPBackend(bucket_name=bucket_name)
    storage_client = backend.get_gcp_storage_client()
    blobs = storage_client.list_blobs(bucket_name, prefix="thumbs/collectiveoffer")

    result = 0
    for blob in blobs:
        if blob.size > MAX_FILE_SIZE:
            result += 1
            logger.info("Fichier : %s, Taille : %d", blob.name, blob.size)

    logger.info("Total des fichiers : %d", result)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket-name", type=str, help="bucket name", required=True)
    args = parser.parse_args()

    main(bucket_name=args.bucket_name)
