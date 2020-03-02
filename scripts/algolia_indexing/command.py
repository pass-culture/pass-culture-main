from flask import current_app as app

from scripts.algolia_indexing.indexing import _process_venue_provider


@app.manager.option('-p',
                    '--venue-provider-id',
                    help='Venue provider to retrieve')
@app.manager.option('-p',
                    '--provider-id',
                    help='Provider to retrieve')
@app.manager.option('-v',
                    '--venueId',
                    help='Venue to retrieve')
def process_venue_provider_offers_for_algolia(provider_id: str, venue_id: int, venue_provider_id: int):
    _process_venue_provider(client=app.redis_client,
                            provider_id=provider_id,
                            venue_id=venue_id,
                            venue_provider_id=venue_provider_id)
