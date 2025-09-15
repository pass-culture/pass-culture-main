import logging
from unittest import mock

import pytest
from factory.faker import faker

import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_repository
import pcapi.core.reactions.factories as reactions_factories
from pcapi.core.categories import subcategories
from pcapi.core.chronicles import factories as chronicles_factories
from pcapi.core.offers import factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models
from pcapi.core.products import api as products_api
from pcapi.core.products import exceptions as products_exceptions
from pcapi.core.products import factories as products_factories
from pcapi.core.products import models as products_models
from pcapi.core.providers.allocine import get_allocine_products_provider
from pcapi.core.reactions import models as reactions_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType

from tests.connectors.titelive import fixtures


Fake = faker.Faker(locale="fr_FR")


@pytest.mark.usefixtures("db_session")
class UpsertMovieProductFromProviderTest:
    @classmethod
    def setup_class(cls):
        cls.allocine_provider = get_allocine_products_provider()
        cls.allocine_stocks_provider = providers_repository.get_provider_by_local_class("AllocineStocks")
        cls.boost_provider = providers_repository.get_provider_by_local_class("BoostStocks")

    def setup_method(self):
        db.session.query(products_models.Product).delete()

    def teardown_method(self):
        db.session.query(products_models.Product).delete()

    def _get_movie(self, allocine_id: str | None = None, visa: str | None = None):
        return products_models.Movie(
            title="Mon film",
            duration=90,
            description="description de Mon film",
            poster_url=None,
            allocine_id=allocine_id,
            visa=visa,
            extra_data={"allocineId": int(allocine_id) if allocine_id else None, "visa": visa},
        )

    def test_creates_allocine_product_without_visa_if_does_not_exist(self):
        movie = self._get_movie(allocine_id="12345")

        product = products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData.get("visa") is None

    def test_creates_allocine_product_even_if_the_title_is_too_long(self):
        movie = self._get_movie(allocine_id="12345")
        movie.title = "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de la cinquième division entre 1953 et 1956"

        product = products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert (
            product.name
            == "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de…"
        )

    def test_do_nothing_if_no_allocine_id_and_no_visa(self):
        movie = self._get_movie(allocine_id=None, visa=None)

        with assert_num_queries(0):
            product = products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product is None

    def test_does_not_create_product_if_exists(self):
        product = products_factories.ProductFactory(extraData={"allocineId": 12345})
        movie = self._get_movie(allocine_id="12345")

        new_product = products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert product.id == new_product.id

    def test_updates_product_if_exists(self):
        allocine_id = 12345
        visa = "67890"

        allocine_movie = products_factories.ProductFactory(extraData={"allocineId": allocine_id})
        random_movie_with_visa = products_factories.ProductFactory(extraData={"visa": visa})

        movie = self._get_movie(allocine_id=str(allocine_id), visa=visa)
        offer = offers_factories.OfferFactory(product=random_movie_with_visa)

        # When
        products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        # Then
        assert allocine_movie.lastProvider.id == self.allocine_provider.id

        db.session.refresh(offer)
        assert offer.productId == allocine_movie.id

    def test_updates_product_if_exists_and_title_is_too_ling(self):
        allocine_id = 12345
        visa = "67890"

        allocine_movie = products_factories.ProductFactory(extraData={"allocineId": allocine_id})
        random_movie_with_visa = products_factories.ProductFactory(extraData={"visa": visa})

        movie = self._get_movie(allocine_id=str(allocine_id), visa=visa)
        movie.title = "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de la cinquième division entre 1953 et 1956"
        offer = offers_factories.OfferFactory(product=random_movie_with_visa)

        product = products_api.upsert_movie_product_from_provider(movie, self.allocine_provider, "idAllocine")

        assert allocine_movie.lastProvider.id == self.allocine_provider.id

        db.session.refresh(offer)
        assert offer.productId == allocine_movie.id
        assert (
            product.name
            == "Chroniques fidèles survenues au siècle dernier à l’hôpital psychiatrique Blida-Joinville, au temps où le Docteur Frantz Fanon était chef de…"
        )

    def test_does_not_update_allocine_product_from_non_allocine_synchro(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        # When
        products_api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost")

        # Then
        assert product.lastProvider.id == self.allocine_provider.id

    def test_updates_allocine_product_from_allocine_stocks_synchro(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.allocine_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocineStocks")

        assert product.lastProvider.id == self.allocine_stocks_provider.id

    def test_updates_product_from_same_synchro(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id, extraData={"allocineId": 12345}
        )
        movie = self._get_movie(allocine_id="12345")

        products_api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoost2")

        assert product.lastProvider.id == self.boost_provider.id

    def test_updates_allocine_id_when_updates_product_by_visa(self):
        product = products_factories.ProductFactory(lastProviderId=self.boost_provider.id, extraData={"visa": "54321"})
        movie = self._get_movie(allocine_id="12345", visa="54321")

        products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345

    def test_updates_visa_when_updating_with_visa_provided(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa="54322")

        products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54322"

    def test_keep_visa_when_updating_with_no_visa_provided(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "visa": "54321"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)

        products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData["allocineId"] == 12345
        assert product.extraData["visa"] == "54321"

    def test_does_not_update_data_when_provided_data_is_none(self):
        product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            extraData={"allocineId": 12345, "title": "Mon vieux film"},
        )
        movie = self._get_movie(allocine_id="12345", visa=None)
        movie.extra_data = None

        products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocine")

        assert product.extraData == {"allocineId": 12345, "title": "Mon vieux film"}

    def test_handles_coexisting_incomplete_movies(self, caplog):
        boost_product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="MON VIEUX FILM D'EPOQUE",
            description="Vieux film des années 50",
            extraData={"visa": "54321", "title": "MON VIEUX FILM D'EPOQUE"},
        )
        boost_product_id = boost_product.id
        allocine_product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="Mon vieux film d'époque",
            description="Vieux film des années cinquante",
            extraData={"allocineId": 12345, "title": "Mon vieux film d'époque"},
        )
        offer = offers_factories.OfferFactory(product=boost_product)
        reaction = reactions_factories.ReactionFactory(product=boost_product)
        products_factories.ProductMediationFactory(product=boost_product)
        movie = self._get_movie(allocine_id="12345", visa="54321")

        with caplog.at_level(logging.INFO):
            products_api.upsert_movie_product_from_provider(movie, self.allocine_stocks_provider, "idAllocineProducts")

        assert caplog.records[0].extra == {
            "allocine_id": "12345",
            "visa": "54321",
            "provider_id": self.allocine_stocks_provider.id,
            "deleted": {
                "name": "MON VIEUX FILM D'EPOQUE",
                "description": "Vieux film des années 50",
            },
            "kept": {
                "name": "Mon vieux film d'époque",
                "description": "Vieux film des années cinquante",
            },
        }
        assert offer.product == allocine_product
        assert reaction.product == allocine_product
        assert (
            db.session.query(products_models.ProductMediation)
            .filter(products_models.ProductMediation.productId == boost_product_id)
            .count()
            == 0
        )
        assert (
            db.session.query(products_models.Product).filter(products_models.Product.id == boost_product_id).count()
            == 0
        )
        assert allocine_product.extraData == {"allocineId": 12345, "visa": "54321", "title": "Mon vieux film d'époque"}

    def test_should_not_merge_when_visa_and_allocineId_sent_by_provider_are_incoherent(self, caplog):
        movie = products_models.Movie(
            allocine_id="1000006691",  # allocine_id pointing to "L'Accident de piano"
            visa="164773",  # pointing to "F1 Film"
            title="F1 : LE FILM",
            description="Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            duration=None,
            poster_url=None,
            extra_data={},
        )

        f1_movie_product = products_factories.ProductFactory(
            lastProviderId=self.boost_provider.id,
            name="F1® LE FILM",
            description="Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            extraData={"visa": "164773", "title": "F1® LE FILM"},
        )
        accident_piano_movie_product = products_factories.ProductFactory(
            lastProviderId=self.allocine_provider.id,
            name="L'Accident de piano",
            description="Magalie est une star du web hors sol et sans morale qui gagne des fortunes en postant des contenus choc sur les réseaux. Après un accident grave survenu sur le tournage d'une de ses vidéos, Magalie s'isole à la montagne avec Patrick, son assistant personnel, pour faire un break. Une journaliste détenant une information sensible commence à lui faire du chantage… La vie de Magalie bascule.",
            extraData={"allocineId": 1000006691, "title": "L'Accident de piano"},
        )
        accident_piano_movie_product_id = accident_piano_movie_product.id

        with caplog.at_level(logging.WARNING):
            product = products_api.upsert_movie_product_from_provider(movie, self.boost_provider, "idBoostProducts")

        assert caplog.records[0].message == "Provider sent incoherent visa and allocineId"
        assert caplog.records[0].extra == {
            "movie": {
                "allocine_id": "1000006691",
                "visa": "164773",
                "title": "F1 : LE FILM",
                "description": "Sonny Hayes était le prodige de la F1 des années 90 jusqu’à son terrible accident. Trente ans plus tard, devenu un pilote indépendant, il est contacté par Ruben Cervantes, patron d’une écurie en faillite qui le convainc de revenir pour sauver l’équipe et prouver qu’il est toujours le meilleur. Aux côtés de Joshua Pearce, diamant brut prêt à devenir le numéro 1, Sonny réalise vite qu'en F1, son coéquipier est aussi son plus grand rival, que le danger est partout et qu'il risque de tout perdre.",
            },
            "provider_id": self.boost_provider.id,
            "product_id": f1_movie_product.id,
        }
        assert product == f1_movie_product
        assert db.session.query(products_models.Product).filter_by(id=accident_piano_movie_product_id).one_or_none()


@pytest.mark.usefixtures("db_session")
class WhitelistExistingProductTest:
    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_modify_product_if_existing_and_not_gcu_compatible(self, requests_mock, settings):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
        )

        product = products_factories.ProductFactory(
            name="test",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            extraData={
                "author": "author",
                "prix_livre": "66.6€",
                "collection": "collection",
                "comic_series": "comic_series",
                "date_parution": "date_parution",
                "distributeur": "distributeur",
                "editeur": "editeur",
                "num_in_collection": "test",
                "schoolbook": False,
                "csr_id": "csr_id",
                "gtl_id": "gtl_id",
                "code_clil": "code_clil",
                "rayon": "test",
            },
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        products_api.whitelist_product(ean)

        assert db.session.query(products_models.Product).one() == product
        assert product.isGcuCompatible
        oeuvre = fixtures.BOOK_BY_SINGLE_EAN_FIXTURE["oeuvre"]
        article = oeuvre["article"][0]
        assert product.name == oeuvre["titre"]
        assert product.description == article["resume"]
        assert product.extraData["author"] == oeuvre["auteurs"]
        assert product.extraData["prix_livre"] == article["prix"]
        assert product.extraData["collection"] == article["collection"]
        assert product.extraData["comic_series"] == article["serie"]
        assert product.extraData["date_parution"] == "2014-10-02 00:00:00"
        assert product.extraData["distributeur"] == article["distributeur"]
        assert product.extraData["editeur"] == article["editeur"]
        assert product.extraData["num_in_collection"] == article["collection_no"]
        assert product.extraData["schoolbook"] == (article["scolaire"] == "1")
        assert product.extraData["csr_id"] == "0105"
        assert product.extraData["gtl_id"] == "01050000"
        assert product.extraData["code_clil"] == "3665"

    @pytest.mark.settings(TITELIVE_EPAGINE_API_USERNAME="test@example.com", TITELIVE_EPAGINE_API_PASSWORD="qwerty123")
    def test_create_product_if_not_existing(self, requests_mock, settings):
        ean = "9782070455379"
        requests_mock.post(
            f"{settings.TITELIVE_EPAGINE_API_AUTH_URL}/login/test@example.com/token",
            json={"token": "XYZ"},
        )
        requests_mock.get(
            f"{settings.TITELIVE_EPAGINE_API_URL}/ean/{ean}",
            json=fixtures.BOOK_BY_SINGLE_EAN_FIXTURE,
        )
        assert not db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one_or_none()

        products_api.whitelist_product(ean)

        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product
        assert len(product.extraData["gtl_id"]) == 8


@pytest.mark.usefixtures("db_session")
class ProductCountsConsistencyTest:
    def test_chronicles_count(self) -> None:
        product_1 = products_factories.ProductFactory()
        product_2 = products_factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product_1, product_2])

        product_1.chroniclesCount = 0

        assert products_api.fetch_inconsistent_products() == {product_1.id}

    def test_headlines_count(self) -> None:
        product_1 = products_factories.ProductFactory()
        product_2 = products_factories.ProductFactory()
        offers_factories.HeadlineOfferFactory(offer__product=product_1)
        offers_factories.HeadlineOfferFactory(offer__product=product_2)

        product_1.headlinesCount = 0

        assert products_api.fetch_inconsistent_products() == {product_1.id}

    def test_likes_count(self) -> None:
        product = products_factories.ProductFactory()
        reactions_factories.ReactionFactory(product=product, reactionType=reactions_models.ReactionTypeEnum.LIKE)

        product.likesCount = 0

        assert products_api.fetch_inconsistent_products() == {product.id}

    def test_ids_are_unique(self) -> None:
        product = products_factories.ProductFactory()
        chronicles_factories.ChronicleFactory.create(products=[product])
        reactions_factories.ReactionFactory(product=product, reactionType=reactions_models.ReactionTypeEnum.LIKE)

        product.chroniclesCount = 0
        product.likesCount = 0

        assert products_api.fetch_inconsistent_products() == {product.id}


@pytest.mark.usefixtures("db_session")
class ApproveProductAndRejectedOffersTest:
    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_no_approve_product_and_offers_with_unknown_product(self, mocked_async_index_offer_ids):
        # Given
        ean = "ean-de-test"

        # When
        with pytest.raises(products_exceptions.ProductNotFound):
            products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_no_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        # When
        products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product.isGcuCompatible

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_on_approved_offers(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(product=product)
        factories.OfferFactory(product=product)

        # When
        products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.APPROVED).count()
            == 2
        )

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_rejected_offer_for_gcu_inappropriate(
        self, mocked_async_index_offer_ids
    ):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        offert_to_approve = factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )
        factories.OfferFactory(product=product, lastValidationType=OfferValidationType.MANUAL)

        # When
        products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.APPROVED).count()
            == 2
        )
        assert (
            db.session.query(models.Offer)
            .filter(
                models.Offer.id == offert_to_approve.id, models.Offer.lastValidationType == OfferValidationType.AUTO
            )
            .count()
            == 1
        )

        mocked_async_index_offer_ids.assert_called()
        assert set(mocked_async_index_offer_ids.call_args[0][0]) == set([offert_to_approve.id])

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_manually_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.MANUAL
        )

        # When
        products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.REJECTED).count()
            == 1
        )
        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_should_approve_product_and_offers_with_one_offer_auto_rejected(self, mocked_async_index_offer_ids):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product, validation=OfferValidationStatus.REJECTED, lastValidationType=OfferValidationType.AUTO
        )

        # When
        products_api.approves_provider_product_and_rejected_offers(ean)

        # Then
        product = db.session.query(products_models.Product).filter(products_models.Product.ean == ean).one()
        assert product.isGcuCompatible

        assert (
            db.session.query(models.Offer).filter(models.Offer.validation == OfferValidationStatus.REJECTED).count()
            == 1
        )
        mocked_async_index_offer_ids.assert_not_called()

    def test_should_approve_product_and_offers_with_update_exception(self):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        ean = Fake.ean13()
        product = products_factories.ThingProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            ean=ean,
            lastProvider=provider,
            gcuCompatibilityType=products_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE,
        )

        factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        # When
        with pytest.raises(products_exceptions.NotUpdateProductOrOffers):
            with mock.patch("pcapi.models.db.session.commit", side_effect=Exception):
                products_api.approves_provider_product_and_rejected_offers(ean)
