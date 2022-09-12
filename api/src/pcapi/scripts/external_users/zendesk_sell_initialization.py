import argparse
import gc
import time

import requests


##
# The DRY option is in order to test the script before making irreversible action to the CRM
# #
def run_initialization(dry: bool = True) -> None:  # By default it's just printing and logging
    from pcapi.core.offerers import models as offerers_models
    from pcapi.core.users.external import zendesk_sell
    from pcapi.models.feature import FeatureToggle

    session = zendesk_sell.configure_session()

    CHUNK_SIZE = 50

    server_errors = 0
    offerer_more_than_one = 0
    offerer_not_found = 0
    offerer_found = 0
    venue_more_than_one = 0
    venue_not_found = 0
    venue_found = 0
    problematic_offerer_ids = []
    problematic_venue_ids = []
    created_offerer_ids = []
    created_venue_ids = []
    updated_offerer_ids = []
    updated_venue_ids = []

    offerers = offerers_models.Offerer.query.all()

    for index_offerer, offerer in enumerate(offerers):
        if index_offerer % CHUNK_SIZE == 0:
            collected = gc.collect()
            print(f" => Offerers collected {collected}")
        parent_organization_id = zendesk_sell.SEARCH_PARENT
        if zendesk_sell.is_offerer_only_virtual(offerer):
            continue
        try:
            zendesk_offerer_data = zendesk_sell.get_offerer_by_id(offerer, session=session)
            time.sleep(0.1)
        except zendesk_sell.ContactFoundMoreThanOneError as e:
            offerer_more_than_one += 1
            problematic_offerer_ids.append(offerer.id)
            for item in e.items:
                print(
                    f'    ==> sell id: {item["id"]}, '
                    f'offerer_id: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_OFFERER_ID.value]}, '
                    f'siren: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIREN.value]}'
                )
        except zendesk_sell.ContactNotFoundError:
            offerer_not_found += 1
            if not dry:
                if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                    try:
                        zendesk_offerer_data = zendesk_sell.zendesk_create_offerer(offerer, session=session)
                        time.sleep(0.1)
                    except requests.exceptions.HTTPError as http_error:
                        print("--Server Error creating Offerer--", str(http_error), str(http_error.response))
                        server_errors += 1

                    else:
                        parent_organization_id = zendesk_offerer_data["id"]
                        created_offerer_ids.append(parent_organization_id)
            else:
                created_offerer_ids.append(offerer.id)
                print(f"{offerer} created")

        except requests.exceptions.HTTPError as http_error:
            print("--Server Error searching Offerer--", str(http_error), str(http_error.response))
            server_errors += 1
        else:
            offerer_found += 1
            if not dry:
                offerer_zendesk_id = zendesk_offerer_data["id"]
                try:
                    zendesk_offerer_data = zendesk_sell.zendesk_update_offerer(
                        offerer_zendesk_id, offerer, session=session
                    )
                    time.sleep(0.1)
                except requests.exceptions.HTTPError as http_error:
                    print("--Server Error updating Offerer--", str(http_error), str(http_error.response))
                    server_errors += 1
                else:
                    print(f"{offerer} updated")
                    parent_organization_id = offerer_zendesk_id
                    updated_offerer_ids.append(parent_organization_id)
            else:
                updated_offerer_ids.append(offerer.id)
                print(f"{offerer} updated")

        for venue in offerer.managedVenues:
            print(f"    {venue}")
            if venue.isVirtual or not venue.isPermanent:
                continue
            try:
                zendesk_venue_data = zendesk_sell.get_venue_by_id(venue, session=session)
                time.sleep(0.1)
            except zendesk_sell.ContactFoundMoreThanOneError as e:
                venue_more_than_one += 1
                problematic_venue_ids.append(venue.id)
                for item in e.items:
                    print(
                        f'        ==> sell id: {item["id"]}, '
                        f'venue_id: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.PRODUCT_VENUE_ID.value]}, '
                        f'siret: {item["custom_fields"][zendesk_sell.ZendeskCustomFieldsShort.SIRET.value]}'
                    )
            except zendesk_sell.ContactNotFoundError:
                venue_not_found += 1
                if not dry:
                    if FeatureToggle.ENABLE_ZENDESK_SELL_CREATION.is_active():
                        try:
                            zendesk_venue_data = zendesk_sell.zendesk_create_venue(
                                venue, parent_organization_id, session=session
                            )
                            time.sleep(0.1)
                        except requests.exceptions.HTTPError as http_error:
                            print("--Server Error creating Venue--", str(http_error), str(http_error.response))
                            server_errors += 1
                        else:
                            created_venue_ids.append(zendesk_venue_data["id"])
                else:
                    created_venue_ids.append(venue.id)
                    print(f"    {venue} created")

            except requests.exceptions.HTTPError as http_error:
                print("--Server Error searching Venue--", str(http_error), str(http_error.response))
                server_errors += 1
            else:
                venue_found += 1
                if not dry:
                    zendesk_venue_id = zendesk_venue_data["id"]
                    try:
                        zendesk_venue_data = zendesk_sell.zendesk_update_venue(
                            zendesk_venue_id, venue, parent_organization_id, session=session
                        )
                        time.sleep(0.1)
                    except requests.exceptions.HTTPError as http_error:
                        print("--Server Error updating Venue--", str(http_error), str(http_error.response))
                        server_errors += 1
                    else:
                        updated_venue_ids.append(zendesk_venue_id)
                        print(f"    {venue} updated")
                else:
                    updated_venue_ids.append(venue.id)
                    print(f"    {venue} updated")

    print("==========")
    print(f"Venues found : {venue_found}")
    print(f"Venues not found (to create) : {venue_not_found}")
    print(f"Venues more than one result : {venue_more_than_one}")
    print(f"Offerers found : {offerer_found}")
    print(f"Offerers not found (to create) : {offerer_not_found}")
    print(f"Offerers more than one result : {offerer_more_than_one}")
    print(f"problematic offerers: {problematic_offerer_ids}")
    print(f"problematic venues: {problematic_venue_ids}")

    if not dry:
        print(f"Created offerers: {created_offerer_ids}")
        print(f"Created venues: {created_venue_ids}")
        print(f"Updated offerers: {updated_venue_ids}")
        print(f"Updated venues: {updated_offerer_ids}")
    else:
        print(f"Potentially created offerers: {created_offerer_ids}")
        print(f"Potentially created venues: {created_venue_ids}")
        print(f"Potentially updated offerers: {updated_venue_ids}")
        print(f"Potentially updated venues: {updated_offerer_ids}")

    print("==========")


if __name__ == "__main__":
    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Determine if the script should run in dry run or not""")
    parser.add_argument(
        "--no-dry-run", "-n", help="deactivate the dry run mode", dest="dry_run", action="store_false", default=True
    )
    args = parser.parse_args()
    with app.app_context():
        run_initialization(args.dry_run)
