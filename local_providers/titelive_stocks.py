from datetime import datetime
from typing import Union, List, Optional

import requests
from sqlalchemy import Sequence

from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import Offer, VenueProvider
from models.db import db, Model
from models.stock import Stock
from repository import thing_queries, local_provider_event_queries, venue_queries

PRICE_DIVIDER_TO_EURO = 100
URL_TITELIVE_WEBSERVICE_STOCKS = "https://stock.epagine.fr/stocks/"
NB_DATA_LIMIT_PER_REQUEST = 5000


def make_url(last_seen_isbn, last_date_checked, venue_siret):
    if last_seen_isbn:
        return 'https://stock.epagine.fr/stocks/%s?after=%s&modifiedSince=%s' \
               % (venue_siret, last_seen_isbn, last_date_checked)
    else:
        return 'https://stock.epagine.fr/stocks/%s?modifiedSince=%s' \
               % (venue_siret, last_date_checked)


def get_data(last_seen_isbn, last_date_checked, venue_siret):
    page_url = make_url(last_seen_isbn, last_date_checked, venue_siret)
    req_result = requests.get(page_url)
    return req_result.json()


class TiteLiveStocks(LocalProvider):
    help = ""
    identifier_description = "Code Titelive de la librairie"
    identifier_regexp = "^\d+$"
    name = "TiteLive Stocks (Epagine / Place des libraires.com)"
    object_type = Stock
    can_create = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider, **options)
        self.venueId = self.venue_provider.venueId
        existing_venue = venue_queries.find_by_id(self.venueId)
        assert existing_venue is not None
        self.venue_siret = existing_venue.siret
        self.venue_booking_email = existing_venue.bookingEmail

        latest_local_provider_event = local_provider_event_queries.find_latest_sync_start_event(self.provider)
        if latest_local_provider_event is None:
            self.last_ws_requests = datetime.utcfromtimestamp(0).timestamp() * 1000
        else:
            self.last_ws_requests = latest_local_provider_event.date.timestamp() * 1000
        self.last_seen_isbn = ''
        self.index = -1
        self.more_pages = True
        self.data = None
        self.product = None
        self.offer_id = None

    def __next__(self) -> Optional[List[ProvidableInfo]]:
        self.index = self.index + 1

        if self.data is None \
                or len(self.data['stocks']) <= self.index:

            if not self.more_pages:
                raise StopIteration

            self.index = 0

            self.data = get_data(self.last_seen_isbn,
                                 self.last_ws_requests,
                                 self.venue_provider.venueIdAtOfferProvider)

            if 'status' in self.data \
                    and self.data['status'] == 404:
                raise StopIteration

            if len(self.data['stocks']) < NB_DATA_LIMIT_PER_REQUEST:
                self.more_pages = False

        self.titelive_stock = self.data['stocks'][self.index]
        self.last_seen_isbn = str(self.titelive_stock['ref'])

        with db.session.no_autoflush:
            self.product = thing_queries.find_thing_product_by_isbn_only_for_type_book(self.titelive_stock['ref'])

        if self.product is None:
            return None

        providable_info_stock = self.create_providable_info(Stock)
        providable_info_offer = self.create_providable_info(Offer)

        return [providable_info_offer, providable_info_stock]

    def fill_object_attributes(self, stock_or_offer: Union[Stock, Offer]):
        assert stock_or_offer.idAtProviders == "%s@%s" % (self.titelive_stock['ref'], self.venue_siret)
        if isinstance(stock_or_offer, Stock):
            self.update_stock(stock_or_offer, self.titelive_stock)
        elif isinstance(stock_or_offer, Offer):
            self.update_offer(stock_or_offer, self.titelive_stock)

    def update_stock(self, stock: Stock, stock_information: dict):
        stock.price = int(stock_information['price']) / PRICE_DIVIDER_TO_EURO
        stock.available = int(stock_information['available'])
        stock.bookingLimitDatetime = None
        stock.offerId = self.offer_id

    def update_offer(self, offer: Offer, stock_information: dict):
        offer.name = self.product.name
        offer.description = self.product.description
        offer.type = self.product.type
        offer.extraData = self.product.extraData
        offer.bookingEmail = self.venue_booking_email
        offer.venueId = self.venueId
        offer.productId = self.product.id

        if offer.id is None:
            next_id = self.get_next_offer_id_from_sequence()
            offer.id = next_id

        self.offer_id = offer.id

        if int(stock_information['available']) == 0:
            offer.isActive = False

    def get_next_offer_id_from_sequence(self):
        sequence = Sequence('offer_id_seq')
        return db.session.execute(sequence)

    def create_providable_info(self, model_object: Model) -> ProvidableInfo:
        providable_info = ProvidableInfo()
        providable_info.type = model_object
        providable_info.id_at_providers = "%s@%s" % (self.titelive_stock['ref'], self.venue_siret)
        providable_info.date_modified_at_provider = datetime.utcnow()
        return providable_info
