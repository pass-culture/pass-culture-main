import csv

from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.models import VenueType
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


def update_venue_type(file_path: str):  # type: ignore [no-untyped-def]
    updated_venue_count = 0
    venues_to_update = _read_venue_type_from_file(file_path)
    venue_ids_in_error = []

    for venue_to_update in venues_to_update:
        venue_id = int(venue_to_update[0])
        venue = Venue.query.filter_by(id=venue_id).one_or_none()
        if venue:
            venue_type_label = venue_to_update[1]
            venue_type = VenueType.query.filter_by(label=venue_type_label).one_or_none()
            if venue_type:
                venue.venueTypeId = venue_type.id
                try:
                    repository.save(venue)
                    updated_venue_count += 1
                except ApiErrors:
                    venue_ids_in_error.append(venue_id)
            else:
                print(f"venue type id not found for label : {venue_type_label} and venueId : {venue_id}")
        else:
            print(f"venue not found for id : {venue_id}")
    if venue_ids_in_error:
        print(f"Venues in error : {str(venue_ids_in_error)[1:-1]}")
    print(f"{updated_venue_count} venues have been updated")


def _read_venue_type_from_file(file_path: str) -> list[tuple]:
    with open(file_path, mode="r", newline="\n", encoding="utf-8") as file:
        data = [tuple(line) for line in csv.reader(file, delimiter=";")]
        return data
