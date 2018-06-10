""" provider """
from os import path
from pathlib import Path
import subprocess
from flask import current_app as app

from utils.human_ids import dehumanize
from utils.rest import update


def create_venue_provider(venue, venue_provider_dict):
    from_dict = {
        "isActive": True,
        "providerId": venue_provider_dict['providerId']
    }

    provider = app.model.Provider\
                        .query\
                        .filter_by(
                            id=dehumanize(venue_provider_dict['providerId'])
                        ).first_or_404()
    if provider.localClass == 'OpenAgendaEvents':
        from_dict['venueIdAtOfferProvider'] = venue_provider_dict['identifier']
    else:
        from_dict['venueIdAtOfferProvider'] = venue_provider_dict['venueIdAtOfferProvider']

    new_vp = app.model.VenueProvider(from_dict=from_dict)
    new_vp.venue = venue
    app.model.PcObject.check_and_save(new_vp)
    
    subprocess.Popen([
        'pc',
        'update_providables',
        '-p',
        new_vp.provider.name,
        '-v',
        str(new_vp.venueId)
    ], cwd=Path(path.dirname(path.realpath(__file__))) / '..')

def edit_venue_provider(venue, venue_provider_dict):
    vp = app.model.VenueProvider.query.filter_by(
            venueId=venue.id,
            providerId=dehumanize(venue_provider_dict['providerId'])
        ).first_or_404()
    update(vp, venue_provider_dict, **{ "skipped_keys": ['providers']})
    app.model.PcObject.check_and_save(vp)
    return vp
