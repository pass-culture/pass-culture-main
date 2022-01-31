from time import time
from typing import Optional

from pcapi.models import db


VENUE_IDS_WITH_DUPLICATES_SQL = """
-- Two rows with the same venueId and the same id given by the provider
-- (isbn in the query) are duplicates.
SELECT distinct("venueId")
FROM (

    -- find venue ids that have duplicated offers
    SELECT "venueId"
    FROM (

        -- extract isbn from idAtProviders in order to perform
        -- a group by
        SELECT "id", "venueId", split_part("idAtProviders", '@', 1) isbn
        FROM offer
        WHERE "idAtProviders" is not null

    ) offer
    GROUP BY "venueId", "isbn"
    HAVING count("isbn") > 1

) sub
"""

UPDATE_VENUE_DUPLICATES_SQL = """
UPDATE offer
SET
    "lastProviderId" = null,
    "idAtProviders" = null,
    "idAtProvider" = null
WHERE
    id in (
        -- Do not update the most recent row: it is the valid one.
        -- Since offer ids are integers, we can sort them and move the most
        -- recent out.
        --
        -- sort(ids, 'desc') -> sort items, descending order
        -- (...)[2:] -> slice list, remove first item (1-based indexing)
        -- unnest(...) -> for each item, build a new row
        --
        -- NOTE: sort() is provided by the intarray module, which must be
        -- activated
        SELECT unnest((sort(ids, 'desc'))[2:])
        FROM (

            -- search for the duplicates offers from a specific venue
            -- convert id to integer, because sort() does not handle big integers
            SELECT array_agg(id::integer) as ids
            FROM (

                -- extract isbn from idAtProviders in order to perform
                -- a group by
                SELECT "id", "venueId", split_part("idAtProviders", '@', 1) isbn
                FROM offer
                WHERE
                    "idAtProviders" is not null
                    AND "venueId" = :venue_id

            ) extract_isbn
            GROUP BY "isbn"
            HAVING count("isbn") > 1

        ) agg_venue_ids
    )
RETURNING id
"""

COUNT_DUPLICATES_SQL = """
SELECT count(*)
FROM (
    SELECT "venueId", "isbn"
    FROM (

        -- extract isbn from idAtProviders in order to perform
        -- a group by
        SELECT "id", "venueId", split_part("idAtProviders", '@', 1) isbn
        FROM offer
        WHERE "idAtProviders" is not null

    ) extract_isbn
    GROUP BY "venueId", "isbn"
    HAVING count("isbn") > 1
) main
"""


def get_venue_ids_with_duplicates() -> set[int]:
    res = db.session.execute(VENUE_IDS_WITH_DUPLICATES_SQL)
    return {row.venueId for row in res}


def count_duplicate_offers() -> int:
    return db.session.execute(COUNT_DUPLICATES_SQL).scalar()


def handle_venue_duplicates(venue_id: int) -> set[int]:
    res = db.session.execute(UPDATE_VENUE_DUPLICATES_SQL, {"venue_id": venue_id})
    return {row[0] for row in res}


def handle_offer_duplicates(path: Optional[str]) -> set[int]:
    """
    Update offer rows that are duplicates.

    Note that the duplicating computation occurs twice: first time inside
    get_venue_ids_with_duplicates to get the venues with duplicates, second
    one in handle_venue_duplicates (for a specific venue) that does the update.
    """
    # Needed by the UPDATE_VENUE_DUPLICATES_SQL query
    db.session.execute("CREATE EXTENSION if not exists intarray")

    updated_ids = set()
    for venue_id in get_venue_ids_with_duplicates():
        updated_ids |= handle_venue_duplicates(venue_id)

    if not path:
        path = f"duplicated_offer_ids_{int(time())}"

    with open(path, mode="w") as f:
        rows = "\n,".join([str(updated_id) for updated_id in updated_ids])
        f.write(rows)

    return updated_ids
