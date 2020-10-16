import csv
from typing import List

from pcapi.repository import repository
from pcapi.models import VenueSQLEntity, ApiErrors
from pcapi.utils.logger import logger

def update_venue_creation_date(file_path: str):
    updated_venue_count = 0
    venues_to_update = _read_venue_creation_date_from_file(file_path)
    venue_ids_in_error = []

    for venue_to_update in venues_to_update:
        venue_id = int(venue_to_update[0])
        venue = VenueSQLEntity.query.filter_by(id=venue_id).first()
        venue.dateCreated = venue_to_update[1]
        try:
            repository.save(venue)
            updated_venue_count += 1
        except ApiErrors:
            venue_ids_in_error.append(venue_id)
    if venue_ids_in_error:
        logger.info(f'Venues in error : {str(venue_ids_in_error)[1:-1]}')
    logger.info(f'{updated_venue_count} venues have been updated')


def _read_venue_creation_date_from_file(file_path: str) -> List[tuple]:
    with open(file_path, mode='r', newline='\n') as file:
        data = [tuple(line) for line in csv.reader(file, delimiter=',')]
        return data
