import datetime
import decimal
import enum
import logging
import typing

import PIL

import pcapi.core.finance.api as finance_api
from pcapi.connectors.ems import EMSScheduleConnector
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.providers import exceptions
from pcapi.core.providers import models
from pcapi.core.providers.clients import cinema_client
from pcapi.core.search import models as search_models
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


class ShowFeatures(enum.StrEnum):
    VF = "VF"
    VO = "VO"
    THREE_D = "3D"
    ICE = "ICE"


class ShowStockData(typing.TypedDict):
    stock_uuid: str
    show_datetime: datetime.datetime
    remaining_quantity: int | None
    features: list
    price: decimal.Decimal
    price_label: str


class LoadableMovie(typing.TypedDict):
    movie_uuid: str
    movie_data: offers_models.Movie
    stocks_data: list[ShowStockData]


class ETLProcessException(Exception):
    pass


class ETLStopProcessException(ETLProcessException):
    pass


class CinemaETLProcessTemplate[APIClient: cinema_client.CinemaAPIClient | EMSScheduleConnector, ExtractResult]:
    """
    Extract Transform Load process to import movies & shows for cinema integrations.

    Each inheriting class must implement the following methods that are integration specific :
        - `_extract` : call cinema API (-> `ExtractResult`)
        - `_transform` : format API response into a generic list easily loadable in DB (`ExtractResult` -> `list[LoadableMovie]`)
        - `_extract_result_to_log_dict` : format API response into a loggable `dict` (`ExtractResult` -> `dict`)

    Common methods are :
       - `execute` : (main method) execute the entire Extract Transform Load process
       - `_load` : create or update `Product`, `Offer` & `Stock` based on received `list[LoadableMovie]`
       - `_post_load_product_poster_update` : fetch movie product poster when relevant
    """

    def __init__(self, venue_provider: models.VenueProvider, api_client: APIClient):
        self.venue_provider = venue_provider
        self.api_client = api_client

    def execute(self) -> None:
        """
        Check provider & venue_provider are active, then execute the etl process (extract, transform, load).
        Once the `Product`, `Offer` & `Stock` are loaded, this method enqueues indexation jobs for upserted offers.

        :raise: `InactiveProvider`, `InactiveVenueProvider`
        """
        # Check provider and venue_provider are active
        if not self.venue_provider.provider.isActive:
            self._log(logging.WARNING, "Init - Provider inactive")
            raise exceptions.InactiveProvider()
        if not self.venue_provider.isActive:
            self._log(logging.WARNING, "Init - VenueProvider inactive")
            raise exceptions.InactiveVenueProvider()

        self._log(logging.INFO, "Starting ETL process")

        # Step 1 : Extract (API calls)
        try:
            result = self._extract()
        except ETLStopProcessException as exc:
            self._log(logging.WARNING, "Step 1 - Stop", {"reason": str(exc)})
            return
        except Exception as exc:
            self._log(logging.WARNING, "Step 1 - Extract failed", {"exc": exc.__class__.__name__, "msg": str(exc)})
            raise

        self._log(logging.DEBUG, "Step 1 - Extract done", self._extract_result_to_log_dict(result))

        # Step 2 : Transform
        loadable_movies = self._transform(result)

        self._log(logging.DEBUG, " Step 2 - Transform done", loadable_movies)

        # Step 3 : Load
        try:
            offers_ids, products_with_poster = self._load(loadable_movies)
        except Exception as exc:
            self._log(logging.WARNING, "Step 3 - Load failed", {"exc": exc.__class__.__name__, "msg": str(exc)})
            raise

        self._log(logging.DEBUG, " Step 3 - Load done", loadable_movies)

        # Step 4 : Post Load actions
        search.async_index_offer_ids(
            offers_ids,
            reason=search_models.IndexationReason.STOCK_UPDATE,
            log_extra={
                "source": "provider_api",
                "venue_id": self.venue_provider.venueId,
                "provider_id": self.venue_provider.providerId,
            },
        )
        self._post_load_product_poster_update(products_with_poster)
        self._post_load_provider_specific_hook(extract_result=result)

        self._log(logging.INFO, "ETL process ended successfully")

    def _extract(self) -> ExtractResult:
        """Step 1: Fetch data from provider API (to be implemented in inheriting class)"""
        raise NotImplementedError()

    def _extract_result_to_log_dict(self, extract_result: ExtractResult) -> dict:
        """Helper method to easily log result from extract step (to be implemented in inheriting class)"""
        raise NotImplementedError()

    def _transform(self, extract_result: ExtractResult) -> list[LoadableMovie]:
        """
        Step 2: Transform data (to be implemented in inheriting class)

        Make data easily loadable by :
            - grouping shows by movie
            - formatting shows and movie information
        """
        raise NotImplementedError()

    def _load(self, loadable_movies: list[LoadableMovie]) -> tuple[set[int], list[tuple[offers_models.Product, str]]]:
        """
        Step 3: Load data into DB

        :return: the set of offer_ids to be reindexed on algolia, a list of product with their
                 poster url for post load treatment.
        """
        products_with_poster: list[tuple[offers_models.Product, str]] = []
        offers_ids = set()
        price_category_labels_by_label = {
            price_category_label.label: price_category_label
            for price_category_label in self.venue_provider.venue.priceCategoriesLabel
        }

        for loadable_movie in loadable_movies:
            with atomic():
                offer, product_with_poster = self._load_movie_and_stocks(loadable_movie, price_category_labels_by_label)

            offers_ids.add(offer.id)
            if product_with_poster:
                products_with_poster.append(product_with_poster)

        return offers_ids, products_with_poster

    def _load_movie_and_stocks(
        self,
        loadable_movie: LoadableMovie,
        price_category_labels_by_label: dict[str, offers_models.PriceCategoryLabel],
    ) -> tuple[offers_models.Offer, tuple[offers_models.Product, str] | None]:
        """
        This method does 3 things :
            1. Upsert movie product
            2. Upsert offer
            3. Upsert offer stocks (creating missing price categories if necessary)
        """
        # Product - Create Or Update
        product = offers_api.upsert_movie_product_from_provider(
            loadable_movie["movie_data"],
            self.venue_provider.provider,
        )

        # Offer - Create Or Update
        offer = offers_repository.get_offer_by_venue_and_movie_uuid(
            venue_id=self.venue_provider.venueId,
            movie_uuid=loadable_movie["movie_uuid"],
        )

        if not offer:  # create offer
            offer = offers_models.Offer()
            offer.idAtProvider = loadable_movie["movie_uuid"]
            offer.venueId = self.venue_provider.venueId
            offer.isDuo = self.venue_provider.isDuoOffers or False
            db.session.add(offer)

            self._log(
                logging.DEBUG,
                "Step 3 - New offer to be created",
                {
                    "id_at_provider": loadable_movie["movie_uuid"],
                    "name": loadable_movie["movie_data"].title,
                },
            )

        # fill generic information
        offer.offererAddress = self.venue_provider.venue.offererAddress
        offer.bookingEmail = self.venue_provider.venue.bookingEmail
        offer.withdrawalDetails = self.venue_provider.venue.withdrawalDetails
        offer.subcategoryId = subcategories.SEANCE_CINE.id
        offer.publicationDatetime = offer.publicationDatetime or get_naive_utc_now()
        offer.dateModifiedAtLastProvider = get_naive_utc_now()

        # fill product information
        offer.product = product
        if product:
            offer.name = product.name
            offer._description = None
            offer._durationMinutes = None
            offer._extraData = {}
        else:
            movie_data = loadable_movie["movie_data"]
            offer.name = movie_data.title
            offer.durationMinutes = movie_data.duration
            offer.description = movie_data.description
        db.session.flush()

        # Stock - Create Or Update
        price_categories_by_label_price = {}

        for price_category in offer.priceCategories:
            # we must use `float` on price_category.price for label_price_key
            # because providers send us price with a one digit precision
            # whereas we store price with a two digit precision
            label_price_key = f"{price_category.label}-{float(price_category.price)}"
            price_categories_by_label_price[label_price_key] = price_category

        for stock_data in loadable_movie["stocks_data"]:
            stock = offers_repository.get_stock_by_movie_stock_uuid(stock_data["stock_uuid"])

            # `stock.beginningDatetime` has changed
            if stock and stock.beginningDatetime != stock_data["show_datetime"]:
                stock.beginningDatetime = stock_data["show_datetime"]
                stock.bookingLimitDatetime = stock_data["show_datetime"]
                finance_api.update_finance_event_pricing_date(stock)

            if not stock:  # create stock
                stock = offers_models.Stock()
                stock.dnBookedQuantity = 0  # initialize value
                stock.idAtProviders = stock_data["stock_uuid"]
                db.session.add(stock)

                self._log(
                    logging.DEBUG,
                    "Step 3 - New stock to be created",
                    {
                        "id_at_provider": stock_data["stock_uuid"],
                        "beginningDatetime": stock_data["show_datetime"],
                    },
                )

            stock.offer = offer
            stock.beginningDatetime = stock_data["show_datetime"]
            stock.bookingLimitDatetime = stock_data["show_datetime"]
            if stock_data["remaining_quantity"] is None:
                stock.quantity = None
            else:
                stock.quantity = stock_data["remaining_quantity"] + stock.dnBookedQuantity
            stock.features = stock_data["features"]
            stock.price = stock_data["price"]
            stock.dateModifiedAtLastProvider = get_naive_utc_now()

            label_price_key = f"{stock_data['price_label']}-{stock_data['price']}"

            if label_price_key not in price_categories_by_label_price:  # create missing price category
                if stock_data["price_label"] not in price_category_labels_by_label:
                    # create missing price category label
                    price_category_label = offers_models.PriceCategoryLabel(
                        venue=self.venue_provider.venue,
                        label=stock_data["price_label"],
                    )
                    db.session.add(price_category_label)
                    price_category_labels_by_label[stock_data["price_label"]] = price_category_label

                price_category = offers_models.PriceCategory(
                    priceCategoryLabel=price_category_labels_by_label[stock_data["price_label"]],
                    price=stock_data["price"],
                    offer=offer,
                )
                db.session.add(price_category)
                price_categories_by_label_price[label_price_key] = price_category

            stock.priceCategory = price_categories_by_label_price[label_price_key]

        db.session.flush()

        if product and loadable_movie["movie_data"].poster_url:
            return offer, (product, loadable_movie["movie_data"].poster_url)

        return offer, None

    def _post_load_product_poster_update(self, product_with_poster: list[tuple[offers_models.Product, str]]) -> None:
        """
        For each product, if the product does not already have an image, this function fetches the movie poster
        on given `poster_url` and creates a `ProductMediation` of type poster.
        """
        for product, poster_url in product_with_poster:
            if product.productMediations:
                continue  # we don't update movie poster for now

            image = self.api_client.get_movie_poster(poster_url)

            if image:
                try:
                    with atomic():
                        offers_api.create_movie_poster(product, self.venue_provider.provider, image)

                    self._log(
                        logging.DEBUG,
                        "Post load - New movie poster created",
                        {"poster_url": poster_url, "product_id": product.id},
                    )
                except (offers_exceptions.ImageValidationError, PIL.UnidentifiedImageError) as e:
                    self._log(logging.WARNING, "Post load - Failed to create movie poster", {"reason": str(e)})

    def _log(self, level: int, message: str, data: dict | list | None = None) -> None:
        """
        Prefix log message with class name & enrich extra dict with `venue_provider` information

        :level: level defined in logging package, either `logging.INFO`, `logging.WARNING` or `logging.DEBUG`
        :data: dict to be added in extra dict under the "data" key
        """
        log_message = "[%s] %s" % (self.__class__.__name__, message)
        extra: dict = {
            "venue_id": self.venue_provider.venueId,
            "provider_id": self.venue_provider.providerId,
            "venue_provider_id": self.venue_provider.id,
            "venue_id_at_offer_provider": self.venue_provider.venueIdAtOfferProvider,
        }
        if data:
            extra["data"] = data

        if level == logging.WARNING:
            logger.warning(log_message, extra=extra)
        elif level == logging.DEBUG:
            logger.debug(log_message, extra=extra)
        elif level == logging.INFO:
            logger.info(log_message, extra=extra)

    def _post_load_provider_specific_hook(self, extract_result: ExtractResult) -> None:
        """
        Method called at the end of the execute method.
        Each implementation can add custom logic here.
        """
        return
