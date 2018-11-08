""" sandbox webapp """
from sandboxes.scripts.creators import create_grid_event_occurrences, \
                                       create_grid_events, \
                                       create_grid_event_offers, \
                                       create_grid_things, \
                                       create_grid_thing_offers, \
                                       create_grid_offerers, \
                                       create_grid_venues, \
                                       create_scratch_bookings, \
                                       create_scratch_deposits, \
                                       create_scratch_events, \
                                       create_scratch_event_occurrences, \
                                       create_scratch_mediations, \
                                       create_scratch_event_offers, \
                                       create_scratch_offerers, \
                                       create_scratch_recommendations, \
                                       create_scratch_stocks, \
                                       create_scratch_things, \
                                       create_scratch_thing_offers, \
                                       create_scratch_user_offerers, \
                                       create_scratch_users, \
                                       create_scratch_venues

def save_sandbox():
    grid_offerers_by_name = create_grid_offerers()
    scratch_offerers_by_name = create_scratch_offerers()
    scratch_users_by_name = create_scratch_users()
    create_scratch_user_offerers(scratch_users_by_name, scratch_offerers_by_name)
    grid_venues_by_name = create_grid_venues(grid_offerers_by_name)
    scratch_events_by_name = create_scratch_events()
    grid_events_by_name = create_grid_events()
    scratch_things_by_name = create_scratch_things()
    grid_things_by_name = create_grid_things()
    scratch_event_offers_by_name = create_scratch_event_offers()
    grid_event_offers_by_name = create_grid_event_offers(grid_events_by_name, grid_venues_by_name)
    grid_thing_offers_by_name = create_grid_event_offers(grid_things_by_name, grid_venues_by_name)
    scratch_thing_offers_by_name = create_scratch_thing_offers()
