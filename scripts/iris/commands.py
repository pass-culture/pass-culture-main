from flask import current_app as app

from domain.iris import MAXIMUM_DISTANCE_IN_METERS
from scripts.iris.link_iris_to_venues import link_irises_to_existing_physical_venues


@app.manager.option('-sr',
                    '--search-radius',
                    help='Maximum retrival distance for venue',
                    type=int)
def link_iris_to_venues(search_radius: int = MAXIMUM_DISTANCE_IN_METERS):
    with app.app_context():
        link_irises_to_existing_physical_venues(search_radius)
