"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=clean_outdated_algolia_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import json
import logging
import io
import itertools
import os
import pathlib
import time
import typing
import zipfile

import requests

from pcapi import settings
from pcapi.core.search import get_base_query_for_offer_indexation
from pcapi.core.search import unindex_offer_ids
from pcapi.core.offers import models as offers_models
from pcapi.core.search.backends.algolia import AlgoliaBackend
from pcapi.models import db


logger = logging.getLogger(__name__)
OUTPUT_DIRECTORY = os.environ.get("OUTPUT_DIRECTORY", ".")


def get_offer_ids_non_eligible_for_search(offer_ids: list[str]) -> list[str]:
    offer_ids_set = set(offer_ids)
    # Filter only offers with numeric ids from algolia (we are supposed to unindex offer with "humanized" ids anyway)
    non_numeric_offer_ids = {e for e in offer_ids_set if not e.isnumeric()}
    offers = (
        get_base_query_for_offer_indexation()
        .filter(offers_models.Offer.id.in_(offer_ids_set - non_numeric_offer_ids))
        .all()
    )
    offers_non_eligible_for_search = []
    for offer in offers:
        if not offer.is_eligible_for_search:
            offers_non_eligible_for_search.append(str(offer.id))
    not_found_offer_ids = offer_ids_set - {str(offer.id) for offer in offers}
    offers_non_eligible_for_search += list(not_found_offer_ids)
    if offers_non_eligible_for_search:
        logger.info("Found %d offer non eligible for search", len(offers_non_eligible_for_search))
    return offers_non_eligible_for_search


def fetch_offer_ids_from_algolia(offer_ids_output_file: pathlib.Path) -> None:
    url = f"https://{settings.ALGOLIA_APPLICATION_ID}-dsn.algolia.net/1/indexes/{settings.ALGOLIA_OFFERS_INDEX_NAME}/browse"
    headers = {
        "X-Algolia-Application-Id": settings.ALGOLIA_APPLICATION_ID,
        "X-Algolia-API-Key": settings.ALGOLIA_API_KEY,
        "Content-Type": "application/json",
    }
    batch_size = 10000

    payload = {
        "query": "",
        "attributesToRetrieve": ["objectID"],
        "hitsPerPage": batch_size,
    }

    cursor = None
    count = 0

    logger.info("Exporting offer ids to %s", offer_ids_output_file)
    while True:
        if cursor:
            payload = {"cursor": cursor}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()

        hits = data.get("hits", [])
        ids = [hit["objectID"] for hit in hits]
        with open(offer_ids_output_file, "a+") as f:
            f.write("\n".join(ids))
        count += len(ids)
        logger.info("Exported %d offer ids", count)

        cursor = data.get("cursor")
        if not cursor:
            break


def compress_imported_offer_ids(uncompressed_file: pathlib.Path) -> pathlib.Path:
    compressed_file = pathlib.Path(f"{uncompressed_file}.zip")
    logger.info("Compressing output file %s into %s", uncompressed_file, compressed_file)
    with zipfile.ZipFile(
        compressed_file,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zfile:
        zfile.write(uncompressed_file, arcname=uncompressed_file.name)
    logger.info("Compression done, deleting source file %s", uncompressed_file)
    # Delete big text file
    uncompressed_file.unlink()
    return compressed_file


def read_offer_ids_from_compressed_file(
    compressed_offer_ids_file: pathlib.Path, filename: str, chunk_size: int
) -> typing.Iterator:
    with zipfile.ZipFile(compressed_offer_ids_file, "r") as zf:
        with zf.open(filename, "r") as f:
            text_file = io.TextIOWrapper(f)
            for chunk in itertools.batched(text_file, chunk_size):
                yield [e.strip() for e in chunk]


def write_non_eligible_offer_ids(output_file: pathlib.Path, offer_ids: list[str]) -> None:
    with open(output_file, "a+") as f:
        f.write("\n".join(offer_ids))


def step_1() -> None:
    # 1st run: export all offer ids from algolia into a compressed file in the bucket
    offer_ids_output_file = pathlib.Path(OUTPUT_DIRECTORY) / "offer_ids.txt"
    logger.info("Step 1: extracting all of offer ids from algolia into file %s", offer_ids_output_file)
    fetch_offer_ids_from_algolia(offer_ids_output_file)
    compressed_offer_ids_file = compress_imported_offer_ids(offer_ids_output_file)
    logger.info("Offer ids completely extracted, output file: %s", compressed_offer_ids_file)


def step_2() -> None:
    # 2nd run: open compressed offer ids file from bucket and create a new offer ids file consisting only of those
    # non eligible for search
    # __file__ = "src"
    namespace_dir = pathlib.Path(__file__).resolve().parent
    compressed_offer_ids_file = namespace_dir / "offer_ids.txt.zip"
    offer_ids_non_eligible_for_search_output_file = (
        pathlib.Path(OUTPUT_DIRECTORY) / "offer_ids_non_eligible_for_search.txt"
    )
    logger.info("Exporting non eligible offer ids to %s", offer_ids_non_eligible_for_search_output_file.name)
    chunk_size = 100
    count = 0
    for i, chunk in enumerate(
        read_offer_ids_from_compressed_file(compressed_offer_ids_file, "offer_ids.txt", chunk_size), 1
    ):
        logger.info("Checking offers chunk #%d", i)
        now = time.perf_counter()
        non_eligible_offer_ids = get_offer_ids_non_eligible_for_search(chunk)
        if non_eligible_offer_ids:
            write_non_eligible_offer_ids(offer_ids_non_eligible_for_search_output_file, non_eligible_offer_ids)
        count += len(chunk)
        logger.info("Checked %s offers. Chunk processing time: %.2f seconds", count, (time.perf_counter() - now))
    compressed_non_eligible_offer_ids_file = compress_imported_offer_ids(offer_ids_non_eligible_for_search_output_file)
    logger.info(
        "Offer ids non eligible for search completely extracted into file %s", compressed_non_eligible_offer_ids_file
    )


def offer_id_is_valid(offer_id: str) -> bool:
    return bool(offer_id) and len(offer_id) < 10 and offer_id.isnumeric()


def step_3() -> None:
    # 3rd run: fetch the ids of offers non eligible for search from previously exported file and delete them from algolia
    # __file__ = "src"
    algolia_backend = AlgoliaBackend()
    namespace_dir = pathlib.Path(__file__).resolve().parent
    compressed_non_eligible_offer_ids_file = namespace_dir / "offer_ids_non_eligible_for_search.txt.zip"
    chunk_size = 1000
    max_offer_id = 438203723
    for i, chunk in enumerate(
        read_offer_ids_from_compressed_file(
            compressed_non_eligible_offer_ids_file, "offer_ids_non_eligible_for_search.txt", chunk_size
        ),
        1,
    ):
        valid_offer_ids = [e for e in chunk if offer_id_is_valid(e)]
        invalid_offer_ids = [e for e in chunk if not offer_id_is_valid(e)]
        if valid_offer_ids:
            logger.info("Unindexing offers chunk #%d (chunk size = %d)", i, len(valid_offer_ids))
            unindex_offer_ids(valid_offer_ids)
        if invalid_offer_ids and settings.ALGOLIA_OFFERS_INDEX_NAME is not None:
            logger.info("Unindexing offers chunk #%d with non numeric id (chunk size = %d)", i, len(invalid_offer_ids))
            algolia_backend.delete_objects(settings.ALGOLIA_OFFERS_INDEX_NAME, invalid_offer_ids)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()
    step_3()
