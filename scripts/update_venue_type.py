import csv
from typing import List

from repository import repository
from models import VenueSQLEntity, VenueType


def update_venue_type(file_path: str):
    updated_venue_count = 0
    venues_to_update = _read_venue_type_from_file(file_path)

    for venue_to_update in venues_to_update:
        venue_id = int(venue_to_update[0])
        venue = VenueSQLEntity.query.filter_by(id=venue_id).first()
        if venue:
            venue_type_label = venue_to_update[1]
            venue_type = VenueType.query.filter_by(
                label=venue_type_label).first()
            if venue_type:
                venue.venueTypeId = venue_type.id
                repository.save(venue)
                updated_venue_count += 1
            else:
                print(
                    f'venue type id not found for label : {venue_type_label}')
        else:
            print(f'venue not found for id : {venue_id}')
    print(f'{updated_venue_count} venues have been updated')


def _read_venue_type_from_file(file_path: str) -> List[tuple]:
    with open(file_path, mode='r', newline='\n') as file:
        data = [tuple(line) for line in csv.reader(file)]
        return data
