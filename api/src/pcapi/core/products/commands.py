import datetime
import logging
import textwrap

import click
import sqlalchemy.exc as sa_exc

import pcapi.core.fraud.models as fraud_models
import pcapi.core.offers.api as offers_api
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
import pcapi.utils.cron as cron_decorators
from pcapi.connectors.big_query.queries.product import BigQueryProductModel
from pcapi.connectors.big_query.queries.product import ProductsToSyncQuery
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories.subcategories import LIVRE_PAPIER
from pcapi.core.providers import constants
from pcapi.core.providers.models import LocalProviderEventType
from pcapi.core.providers.titelive_api import TiteliveDatabaseNotInitializedException
from pcapi.core.providers.titelive_api import activate_newly_eligible_product_and_offers
from pcapi.core.providers.titelive_book_search import get_book_format
from pcapi.core.providers.titelive_book_search import get_gtl_id
from pcapi.core.providers.titelive_book_search import get_ineligibility_reasons
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.utils.blueprint import Blueprint
from pcapi.utils.repository import transaction


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


class BigQueryProductSync:
    titelive_base = TiteliveBase.BOOK

    def __init__(self) -> None:
        self.product_whitelist_eans = {ean for (ean,) in db.session.query(fraud_models.ProductWhitelist.ean).all()}
        logger.info("Loaded %d EANs from the whitelist.", len(self.product_whitelist_eans))

    def get_last_sync_date(self, provider: providers_models.Provider) -> datetime.date:
        last_sync_event = (
            db.session.query(providers_models.LocalProviderEvent)
            .filter(
                providers_models.LocalProviderEvent.provider == provider,
                providers_models.LocalProviderEvent.type == LocalProviderEventType.SyncEnd,
                providers_models.LocalProviderEvent.payload == self.titelive_base.value,
            )
            .order_by(providers_models.LocalProviderEvent.id.desc())
            .first()
        )
        if last_sync_event is None or not last_sync_event.payload:
            raise TiteliveDatabaseNotInitializedException()
        return last_sync_event.date.date()

    def log_sync_status(
        self, provider: providers_models.Provider, event_type: LocalProviderEventType, message: str | None = None
    ) -> providers_models.LocalProviderEvent:
        message = f"{self.titelive_base.value} : {message}" if message else self.titelive_base.value
        return providers_models.LocalProviderEvent(
            date=datetime.datetime.utcnow(),
            payload=message,
            provider=provider,
            type=event_type,
        )

    def run_synchronization(self, from_date: datetime.date, to_date: datetime.date) -> None:
        logger.info("Starting product synchronization from %s to %s.", from_date.isoformat(), to_date.isoformat())

        total_products_upserted = 0
        ineligible_eans = []

        products_iterator = ProductsToSyncQuery(from_date=from_date, to_date=to_date).execute()
        for bq_product in products_iterator:
            reasons = get_ineligibility_reasons(bq_product, bq_product.titre)

            if reasons:
                if bq_product.gencod in self.product_whitelist_eans:
                    logger.info(
                        "Skipping ineligibility for EAN %s (reasons: %s): product is whitelisted.",
                        bq_product.gencod,
                        reasons,
                    )
                else:
                    ineligible_eans.append(bq_product.gencod)
                    logger.info("Rejecting product EAN %s for reason(s): %s.", bq_product.gencod, reasons)
                    continue

            product = self.create_or_update(bq_product)
            try:
                with transaction():
                    db.session.add(product)
                total_products_upserted += 1
            except sa_exc.IntegrityError as exc:
                logger.error("Failed to upsert product with EAN %s: %s", product.ean, exc)

        if ineligible_eans:
            offers_api.reject_inappropriate_products(ineligible_eans, author=None)

        logger.info("Synchronization complete. Summary:")
        logger.info("  > %d products upserted.", total_products_upserted)
        logger.info("  > %d products rejected.", len(ineligible_eans))
        logger.info("  > %d products processed in total.", total_products_upserted + len(ineligible_eans))

    def synchronize_products(self, from_date: datetime.date | None, to_date: datetime.date | None) -> None:
        provider = providers_repository.get_provider_by_name(providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME)

        if from_date is None:
            try:
                from_date = self.get_last_sync_date(provider) - datetime.timedelta(days=1)
            except TiteliveDatabaseNotInitializedException:
                logger.warning("No last synchronization date found. Use the --from-date option for the initial run.")
                return

        if to_date is None:
            to_date = datetime.date.today() - datetime.timedelta(days=1)

        if from_date >= to_date:
            logger.warning("Start date %s is after end date %s. Aborting synchronization.", from_date, to_date)
            return

        try:
            with transaction():
                start_sync_event = self.log_sync_status(provider, LocalProviderEventType.SyncStart)
                db.session.add(start_sync_event)

            self.run_synchronization(from_date, to_date)

            with transaction():
                stop_sync_event = self.log_sync_status(provider, LocalProviderEventType.SyncEnd)
                db.session.add(stop_sync_event)

        except Exception as e:
            with transaction():
                sync_error_event = self.log_sync_status(
                    provider, LocalProviderEventType.SyncError, e.__class__.__name__
                )
                db.session.add(sync_error_event)
            raise

    def create_or_update(self, bq_product: BigQueryProductModel) -> offers_models.Product:
        product = db.session.query(offers_models.Product).filter_by(ean=bq_product.gencod).one_or_none()

        is_update = product is not None
        if not is_update:
            product = offers_models.Product(ean=bq_product.gencod)

        product.name = textwrap.shorten(
            bq_product.titre, width=constants.TITELIVE_PRODUCT_NAME_MAX_LENGTH, placeholder="…"
        )
        product.description = bq_product.resume
        product.lastProvider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        product.subcategoryId = LIVRE_PAPIER.id

        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(self._build_product_extra_data(bq_product))

        if is_update:
            activate_newly_eligible_product_and_offers(product)

        return product

    def _build_product_extra_data(self, bq_product: BigQueryProductModel) -> offers_models.OfferExtraData:
        gtl_id = get_gtl_id(bq_product)

        return offers_models.OfferExtraData(
            author=", ".join(bq_product.auteurs_multi) if bq_product.auteurs_multi else None,
            bookFormat=get_book_format(bq_product.codesupport),
            date_parution=str(bq_product.dateparution) if bq_product.dateparution else None,
            editeur=bq_product.editeur,
            gtl_id=gtl_id,
            langueiso=bq_product.langueiso,
            prix_livre=bq_product.prix,
        )


@blueprint.cli.command("synchronize_titelive_book_products_from_bigquery")
@click.option(
    "--from-date",
    help="Synchronise les produits modifiés depuis cette date (YYYY-MM-DD HH:MM:SS)",
    type=click.DateTime(),
    default=None,
)
@click.option(
    "--to-date",
    help="Synchronise les produits modifiés jusqu'à cette date (YYYY-MM-DD HH:MM:SS)",
    type=click.DateTime(),
    default=None,
)
@cron_decorators.log_cron_with_transaction
@cron_decorators.cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE_PRODUCTS_FROM_BIGQUERY_TABLES)
def synchronize_products_from_bigquery(
    from_date: datetime.datetime | None = None, to_date: datetime.datetime | None = None
) -> None:
    BigQueryProductSync().synchronize_products(
        from_date.date() if from_date else None, to_date.date() if to_date else None
    )
