from flask import current_app as app

from models.provider import Provider
from utils.attr_dict import AttrDict

app.local_providers = AttrDict()
import local_providers.openagenda_events
#import local_providers.openagenda_offers  FOR DEMO PURPOSES ONLY
import local_providers.spreadsheet_offers
import local_providers.spreadsheet_exp_offers
import local_providers.spreadsheet_exp_thing_offers
import local_providers.spreadsheet_exp_venues
import local_providers.titelive_offers
import local_providers.titelive_venues
import local_providers.titelive_books
import local_providers.titelive_book_descriptions
import local_providers.titelive_book_thumbs

for name in app.local_providers.keys():
    provider = app.local_providers[name]
    db_provider = Provider.getByClassName(name)

    if not db_provider:
        p = Provider()
        p.name = provider.name
        p.localClass = name
        p.isActive = False
        app.db.session.add(p)
        app.db.session.commit()
