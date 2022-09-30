import argparse
import datetime
import math
import sys
import time
import traceback
import typing

import requests

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.models.feature import FeatureToggle


MAX_RETRIES = 3
CHUNK_SIZE = 20
DELAY = 0.3
RETRY_DELAY = 3


class ZSIStats:
    server_errors: int = 0
    offerer_more_than_one: int = 0
    offerer_not_found: int = 0
    offerer_found: int = 0
    venue_more_than_one: int = 0
    venue_not_found: int = 0
    venue_found: int = 0
    problematic_offerer_ids: list[int] = []
    problematic_venue_ids: list[int] = []
    created_offerer_ids: list[int] = []
    created_venue_ids: list[int] = []
    updated_offerer_ids: list[int] = []
    updated_venue_ids: list[int] = []


def print_ts(*print_args: typing.Any) -> None:
    print(f"[{datetime.datetime.utcnow().isoformat()}]", *print_args)


def _handle_venue(
    venue: offerers_models.Venue,
    parent_organization_id: int | None,
    session: requests.Session,
    dry: bool,
    stats: ZSIStats,
) -> None:
    from pcapi.core.users.external import zendesk_sell

    if venue.isVirtual or not venue.isPermanent:
        return

    time.sleep(DELAY)

    try:
        zendesk_venue_data = zendesk_sell.get_venue_by_id(venue, session=session)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        stats.venue_more_than_one += 1
        stats.problematic_venue_ids.append(venue.id)
        print_ts(f"    {venue} has multiple results:")
        for item in e.items:
            print_ts(
                f'        ==> sell id: {item["id"]}, '
                f'venue_id: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value]}, '
                f'siret: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIRET.value]}'
            )
    except zendesk_sell.ContactNotFoundError:
        stats.venue_not_found += 1
        if not dry:
            if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                time.sleep(DELAY)
                zendesk_venue_data = zendesk_sell.zendesk_create_venue(venue, parent_organization_id, session=session)
                stats.created_venue_ids.append(zendesk_venue_data["id"])
                print_ts(f"    {venue} created")
            else:
                stats.created_venue_ids.append(venue.id)
                print_ts(f"    {venue} not found in Zendesk Sell")
        else:
            stats.created_venue_ids.append(venue.id)
            print_ts(f"    {venue} created")
    else:
        stats.venue_found += 1
        if not dry:
            zendesk_venue_id = zendesk_venue_data["id"]
            time.sleep(DELAY)
            zendesk_sell.zendesk_update_venue(zendesk_venue_id, venue, parent_organization_id, session=session)
            stats.updated_venue_ids.append(zendesk_venue_id)
        else:
            stats.updated_venue_ids.append(venue.id)
        print_ts(f"    {venue} updated")


def _handle_offerer(offerer: offerers_models.Offerer, session: requests.Session, dry: bool, stats: ZSIStats) -> None:
    from pcapi.core.users.external import zendesk_sell

    if zendesk_sell.is_offerer_only_virtual(offerer):
        return

    parent_organization_id: int | None = zendesk_sell.SEARCH_PARENT

    time.sleep(DELAY)

    try:
        zendesk_offerer_data = zendesk_sell.get_offerer_by_id(offerer, session=session)
    except zendesk_sell.ContactFoundMoreThanOneError as e:
        stats.offerer_more_than_one += 1
        stats.problematic_offerer_ids.append(offerer.id)
        print_ts(f"{offerer} has multiple results:")
        for item in e.items:
            print_ts(
                f'    ==> sell id: {item["id"]}, '
                f'offerer_id: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value]}, '
                f'siren: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value]}'
            )
    except zendesk_sell.ContactNotFoundError:
        stats.offerer_not_found += 1
        if not dry:
            if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                time.sleep(DELAY)
                zendesk_offerer_data = zendesk_sell.zendesk_create_offerer(offerer, session=session)
                print_ts(f"{offerer} created")
                stats.created_offerer_ids.append(zendesk_offerer_data["id"])
                parent_organization_id = zendesk_offerer_data["id"]
            else:
                stats.created_offerer_ids.append(offerer.id)
                print_ts(f"{offerer} not found in Zendesk Sell")
                parent_organization_id = None  # Do not search again when updating venue
        else:
            stats.created_offerer_ids.append(offerer.id)
            print_ts(f"{offerer} created")
    else:
        stats.offerer_found += 1
        if not dry:
            offerer_zendesk_id = zendesk_offerer_data["id"]
            time.sleep(DELAY)
            zendesk_sell.zendesk_update_offerer(offerer_zendesk_id, offerer, session=session)
            print_ts(f"{offerer} updated")
            stats.updated_offerer_ids.append(offerer_zendesk_id)
            parent_organization_id = offerer_zendesk_id
        else:
            stats.updated_offerer_ids.append(offerer.id)
            print_ts(f"{offerer} updated")

    for venue in offerer.managedVenues:
        _handle_venue(venue, parent_organization_id, session, dry, stats)


##
# The DRY option is in order to test the script before making irreversible action to the CRM
# By default, dry run mode is enabled so the function only prints information to the console
def run_initialization(dry: bool = True, min_offerer_id: int = 0) -> None:
    from pcapi.core.users.external import zendesk_sell

    session = zendesk_sell.configure_session()

    total_offerer_rows = (
        db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id >= min_offerer_id).count()
    )
    max_chunks = math.ceil(total_offerer_rows / CHUNK_SIZE)

    print_ts(f"Total offerer rows: {total_offerer_rows}")
    print_ts(f"Total chunks: {max_chunks}")

    stats = ZSIStats()

    for chunk in range(max_chunks):
        print_ts(f"Chunk {chunk} ({chunk+1}/{max_chunks})")
        offerers = (
            offerers_models.Offerer.query.filter(offerers_models.Offerer.id >= min_offerer_id)
            .order_by(offerers_models.Offerer.id.asc())
            .offset(chunk * CHUNK_SIZE)
            .limit(CHUNK_SIZE)
            .all()
        )
        for offerer in offerers:
            retries = MAX_RETRIES
            while retries > 0:
                try:
                    _handle_offerer(offerer, session, dry, stats)
                    break
                except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as error:
                    print_ts("--Server Error --", str(error), str(error.response))
                    is_http_error = isinstance(error, requests.exceptions.HTTPError)
                    if not is_http_error or error.response.status_code == 500:
                        # Disconnected or Internal server error on Zendesk sell looks random, retry
                        time.sleep(RETRY_DELAY)
                        print_ts("Retrying...")
                        retries -= 1
                    else:
                        retries = 0

            if retries == 0:
                stats.server_errors += 1
                print_ts("-- Permanent Server Error --")

        print_ts("Expunging...")
        db.session.expunge_all()

    print("==========")
    print(f"Venues found : {stats.venue_found}")
    print(f"Venues not found (to create) : {stats.venue_not_found}")
    print(f"Venues more than one result : {stats.venue_more_than_one}")
    print(f"Offerers found : {stats.offerer_found}")
    print(f"Offerers not found (to create) : {stats.offerer_not_found}")
    print(f"Offerers more than one result : {stats.offerer_more_than_one}")
    print(f"problematic offerers: {stats.problematic_offerer_ids}")
    print(f"problematic venues: {stats.problematic_venue_ids}")

    prefix = "Potentially " if dry else ""
    print(f"{prefix}Created offerers: {stats.created_offerer_ids}")
    print(f"{prefix}Created venues: {stats.created_venue_ids}")
    print(f"{prefix}Updated offerers: {stats.updated_venue_ids}")
    print(f"{prefix}Updated venues: {stats.updated_offerer_ids}")

    print("==========")


if __name__ == "__main__":
    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Sync Zendesk Sell with PC production database""")
    parser.add_argument(
        "--no-dry-run", "-n", help="deactivate the dry run mode", dest="dry_run", action="store_false", default=True
    )
    parser.add_argument("--min-id", type=int, default=0, help="minimum offerer id (helps to resume or debug)")
    args = parser.parse_args()

    with app.app_context():
        try:
            run_initialization(dry=args.dry_run, min_offerer_id=args.min_id)
        except KeyboardInterrupt:
            print_ts("*** Interrupted from console ***")
            traceback.print_exc(file=sys.stdout)
