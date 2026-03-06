"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=reindex_offer_bad_activities \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import itertools
import logging
import time

from algoliasearch.search_client import SearchClient
from algoliasearch.search_client import SearchIndex

from pcapi import settings
from pcapi.app import app
from pcapi.core.offerers.models import Activity
from pcapi.core.search import reindex_offer_ids


logger = logging.getLogger(__name__)


def fetch_object_ids_by_facet_pattern(index: SearchIndex, facet_name: str, value: str) -> list[int]:
    search_parameters = {
        "facetFilters": f'["{facet_name}:{value}"]',
        "attributesToRetrieve": ["objectID"],
        "hitsPerPage": 1000,
    }
    object_ids = []
    page = 0

    try:
        while True:
            search_parameters["page"] = page
            results = index.search("", search_parameters)
            object_ids.extend(hit["objectID"] for hit in results.get("hits", []))
            if page >= results.get("nbPages", 0) - 1:
                break

            page += 1

        return object_ids
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return []


def reindex_offer_invalid_activities(reindex: bool) -> None:
    client = SearchClient.create(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY)
    index = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)

    # Algolia cannot return more than 1,000 items (even with pagination)
    # And for some activities, there are more than 1k invalid offers
    # So we need to do it multiple times, until there is no more result.
    activities_remaining = {str(activity): 1 for activity in Activity}
    while any(activities_remaining.values()):
        for activity, remaining in activities_remaining.items():
            if not remaining:
                continue

            offer_ids = fetch_object_ids_by_facet_pattern(index, "venue.activity", activity)
            activities_remaining[activity] = len(offer_ids)

            if not offer_ids:
                logger.info(f"No more offers with invalid activity {activity}")
                continue

            logger.info(f"Activities remaining: {activities_remaining}")

            if reindex:
                logger.info(f"Reindexing {len(offer_ids)} offers for activity {activity}")
                for batch in itertools.batched(offer_ids, 1000):
                    reindex_offer_ids(batch)
            else:
                logger.info(f"Would reindex {len(offer_ids)} offers for activity {activity}")

        if not reindex:
            break

        # Let Algolia asynchronously index offers before re-fetching
        time.sleep(60)


if __name__ == "__main__":
    app.app_context().push()
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reindex", action="store_true")
    args = parser.parse_args()

    reindex_offer_invalid_activities(args.reindex)
