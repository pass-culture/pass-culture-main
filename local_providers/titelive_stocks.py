from datetime import datetime
from typing import Union, List

from sqlalchemy import Sequence

from domain.titelive import get_stocks_information
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import Offer, VenueProvider
from models.db import db
from models.stock import Stock
from repository import product_queries

PRICE_DIVIDER_TO_EURO = 100


class TiteLiveStocks(LocalProvider):
    name = "TiteLive Stocks (Epagine / Place des libraires.com)"
    can_create = True

    def __init__(self, venue_provider: VenueProvider, **options):
        super().__init__(venue_provider, **options)
        self.venue = self.venue_provider.venue

        self.last_seen_isbn = ''
        self.data = iter([])
        self.product = None
        self.offer_id = None

    def __next__(self) -> List[ProvidableInfo]:
        try:
            self.titelive_stock = next(self.data)
        except StopIteration:
            self.data = get_stocks_information(self.venue_provider.venueIdAtOfferProvider,
                                               self.last_seen_isbn)
            self.titelive_stock = next(self.data)

        self.last_seen_isbn = str(self.titelive_stock['ref'])
        self.product = product_queries.find_thing_product_by_isbn_only_for_type_book(self.titelive_stock['ref'])

        if not self.product:
            return []

        providable_info_stock = self.create_providable_info(Stock, f"{self.titelive_stock['ref']}@{self.venue.siret}",
                                                            datetime.utcnow())
        providable_info_offer = self.create_providable_info(Offer, f"{self.titelive_stock['ref']}@{self.venue.siret}",
                                                            datetime.utcnow())
        return [providable_info_offer, providable_info_stock]

    def fill_object_attributes(self, stock_or_offer: Union[Stock, Offer]):
        if isinstance(stock_or_offer, Stock):
            self.fill_stock_attributes(stock_or_offer, self.titelive_stock)
        elif isinstance(stock_or_offer, Offer):
            self.fill_offer_attributes(stock_or_offer, self.titelive_stock)

    def fill_stock_attributes(self, stock: Stock, stock_information: dict):
        stock.price = int(stock_information['price']) / PRICE_DIVIDER_TO_EURO
        stock.available = int(stock_information['available'])
        stock.bookingLimitDatetime = None
        stock.offerId = self.offer_id

    def fill_offer_attributes(self, offer: Offer, stock_information: dict):
        offer.name = self.product.name
        offer.description = self.product.description
        offer.type = self.product.type
        offer.extraData = self.product.extraData
        offer.bookingEmail = self.venue.bookingEmail
        offer.venueId = self.venue.id
        offer.productId = self.product.id

        is_new_offer_to_create = not offer.id
        if is_new_offer_to_create:
            next_id = self.get_next_offer_id_from_sequence()
            offer.id = next_id

        self.offer_id = offer.id

        offer_has_available_stock = int(stock_information['available']) > 0
        offer.isActive = offer_has_available_stock

    def get_next_offer_id_from_sequence(self):
        sequence = Sequence('offer_id_seq')
        return db.session.execute(sequence)
