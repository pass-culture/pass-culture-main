from flask import current_app as app

from scripts.algolia_indexing.indexing import _process_venue_provider


@app.manager.option('-p',
                    '--venue-provider-id',
                    help='Venue provider id to be processed')
@app.manager.option('-p',
                    '--provider-id',
                    help='Provider id to be processed')
@app.manager.option('-v',
                    '--venueId',
                    help='Venue id to be processed')
def process_venue_provider_offers_for_algolia(provider_id: str, venue_id: int, venue_provider_id: int):
    _process_venue_provider(client=app.redis_client,
                            provider_id=provider_id,
                            venue_id=venue_id,
                            venue_provider_id=venue_provider_id)
