"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=unindex_offers_from_closed_offerers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import itertools
import logging

import sqlalchemy as sa
from algoliasearch.search_client import SearchClient
from algoliasearch.search_client import SearchIndex

from pcapi import settings
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.search import reindex_offer_ids
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


def get_venue_ids_from_closed_offerers() -> list[str]:
    query = sa.select(Venue.id).join(Offerer).where(Offerer.validationStatus == ValidationStatus.CLOSED)
    return db.session.scalars(query)


def fetch_object_ids_by_facet_pattern(index: SearchIndex, facet_name: str, value: str) -> list[int]:
    search_parameters = {
        "facetFilters": [f"{facet_name}:{value}"],
        "attributesToRetrieve": ["objectID"],
        "hitsPerPage": 1000,
    }
    object_ids = []
    page = 0

    try:
        while True:
            search_parameters["page"] = page
            results = index.search("", search_parameters)
            hits = results.get("hits", [])
            object_ids.extend(int(hit["objectID"]) for hit in hits)

            if page >= results.get("nbPages", 0) - 1 or not hits:
                break
            page += 1

        return object_ids
    except Exception as e:
        logger.error(f"An error occurred while fetching from Algolia: {e}")
        return []


def reindex_offers_by_venue(reindex: bool) -> None:
    client = SearchClient.create(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY)
    index = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)

    venue_ids = get_venue_ids_from_closed_offerers()

    if not venue_ids:
        logger.info("No venues found to process.")
        return

    logger.info(f"Found {len(venue_ids)} venues to check for reindexing.")

    for venue_id in venue_ids:
        # Algolia limits results to 1000 per search.
        # If a venue has >1000 offers, we process the first 1000 and
        # the loop will need to be re-run.
        has_offers_indexed = True
        while has_offers_indexed:
            offer_ids = fetch_object_ids_by_facet_pattern(index, "venue.id", venue_id)

            if not offer_ids:
                logger.debug(f"No offers found for venue {venue_id}")
                has_offers_indexed = False
                continue

            if reindex:
                logger.info(f"Reindexing {len(offer_ids)} offers for venue {venue_id}")
                for batch in itertools.batched(offer_ids, 1000):
                    reindex_offer_ids(batch)
            else:
                logger.info(f"[DRY RUN] Would reindex {len(offer_ids)} offers for venue {venue_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reindex", action="store_true")
    args = parser.parse_args()

    reindex_offers_by_venue(args.reindex)
