from sandboxes.scripts.creators.grid.create_grid_events import *
from sandboxes.scripts.creators.grid.create_grid_event_occurrences import *
from sandboxes.scripts.creators.grid.create_grid_event_offers import *
from sandboxes.scripts.creators.grid.create_grid_event_stocks import *
from sandboxes.scripts.creators.grid.create_grid_mediations import *
from sandboxes.scripts.creators.grid.create_grid_thing_offers import *
from sandboxes.scripts.creators.grid.create_grid_thing_stocks import *
from sandboxes.scripts.creators.grid.create_grid_things import *
from sandboxes.scripts.creators.grid.create_grid_offerers import *
from sandboxes.scripts.creators.grid.create_grid_venues import *

def save_grid_sandbox():
    grid_offerers_by_name = create_grid_offerers()

    grid_venues_by_name = create_grid_venues(grid_offerers_by_name)

    grid_events_by_name = create_grid_events()

    grid_things_by_name = create_grid_things()

    grid_event_offers_by_name = create_grid_event_offers(
        grid_events_by_name,
        grid_venues_by_name
    )

    grid_thing_offers_by_name = create_grid_event_offers(
        grid_things_by_name,
        grid_venues_by_name
    )

    grid_offers_by_name = dict(
        grid_event_offers_by_name,
        **grid_thing_offers_by_name
    )

    grid_event_occurrences_by_name = create_grid_event_occurrences(grid_event_offers_by_name)

    create_grid_event_stocks(grid_event_offers_by_name)

    create_grid_thing_stocks(grid_thing_offers_by_name)

    create_grid_mediations(grid_offers_by_name)
