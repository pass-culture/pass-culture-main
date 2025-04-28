from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.local_providers.local_provider import _upload_thumb
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from . import provider_test_utils


@pytest.mark.usefixtures("db_session")
class UpdateObjectsTest:
    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_iterator_is_called_until_exhausted(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[], [], []]

        # When
        local_provider.updateObjects()

        # Then
        assert next_function.call_count == 4

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_iterator_should_log_provider_event_from_start_to_stop(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[], []]

        # When
        local_provider.updateObjects()

        # Then
        provider_events = (
            db.session.query(providers_models.LocalProviderEvent)
            .order_by(providers_models.LocalProviderEvent.id.asc())
            .all()
        )
        assert provider_events[0].type == providers_models.LocalProviderEventType.SyncStart
        assert provider_events[1].type == providers_models.LocalProviderEventType.SyncEnd

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_creates_new_object_when_no_object_in_database(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo()
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        new_product = db.session.query(offers_models.Product).one()
        assert new_product.name == "New Product"
        assert new_product.subcategoryId == subcategories.LIVRE_PAPIER.id

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_updates_existing_object(self, next_function):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo(date_modified_at_provider=datetime(2018, 1, 1))
        product = offers_factories.ThingProductFactory(
            dateModifiedAtLastProvider=datetime(2000, 1, 1),
            lastProvider=provider,
            idAtProviders=providable_info.id_at_providers,
            name="Old product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.name == "New Product"
        assert product.dateModifiedAtLastProvider == providable_info.date_modified_at_provider

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_existing_object_when_date_is_older_than_last_modified_date(self, next_function):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo(date_modified_at_provider=datetime(2018, 1, 1))
        product = offers_factories.ThingProductFactory(
            dateModifiedAtLastProvider=datetime(2020, 1, 1),
            lastProvider=provider,
            idAtProviders=providable_info.id_at_providers,
            name="Old product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.name == "Old product name"
        assert product.dateModifiedAtLastProvider == datetime(2020, 1, 1)

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_objects_when_venue_provider_is_not_active(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo(date_modified_at_provider=datetime(2018, 1, 1))
        venue_provider = providers_factories.VenueProviderFactory(isActive=False)
        local_provider = provider_test_utils.TestLocalProvider(venue_provider)
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_objects_when_provider_is_not_active(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider", isActive=False)
        providable_info = ProvidableInfo(date_modified_at_provider=datetime(2018, 1, 1))
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProviderNoCreation.__next__")
    def test_does_not_create_new_object_when_can_create_is_false(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProviderNoCreation")
        providable_info = ProvidableInfo()
        local_provider = provider_test_utils.TestLocalProviderNoCreation()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert db.session.query(offers_models.Product).count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_creates_only_one_object_when_limit_is_one(self, next_function):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info1 = ProvidableInfo()
        providable_info2 = ProvidableInfo(id_at_providers="2")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info1], [providable_info2]]

        # When
        local_provider.updateObjects(limit=1)

        # Then
        new_product = db.session.query(offers_models.Product).one()
        assert new_product.name == "New Product"
        assert new_product.subcategoryId == subcategories.LIVRE_PAPIER.id


@pytest.mark.usefixtures("db_session")
class CreateObjectTest:
    def test_returns_object_with_expected_attributes(self):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo()
        local_provider = provider_test_utils.TestLocalProvider()

        # When
        product = local_provider._create_object(providable_info)

        # Then
        assert isinstance(product, offers_models.Product)
        assert product.name == "New Product"
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.lastProviderId == provider.id

    def test_raises_api_errors_exception_when_errors_occur_on_model_and_log_error(self):
        # Given
        providers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithApiErrors")
        providable_info = ProvidableInfo(type=offers_models.Offer)
        venue_provider = providers_factories.VenueProviderFactory()
        local_provider = provider_test_utils.TestLocalProviderWithApiErrors(venue_provider)

        # When
        with pytest.raises(ApiErrors) as api_errors:
            local_provider._create_object(providable_info)

        # Then
        assert api_errors.value.errors["url"] == [
            "Une offre de sous-catégorie Achat instrument ne peut pas être numérique"
        ]
        assert db.session.query(offers_models.Product).count() == 0
        provider_event = db.session.query(providers_models.LocalProviderEvent).one()
        assert provider_event.type == providers_models.LocalProviderEventType.SyncError


@pytest.mark.usefixtures("db_session")
class HandleUpdateTest:
    def test_returns_object_with_expected_attributes(self):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = ProvidableInfo()
        product = offers_factories.ThingProductFactory(
            name="Old product name",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProvider()

        # When
        local_provider._handle_update(product, providable_info)

        # Then
        product = db.session.query(offers_models.Product).one()
        assert product.name == "New Product"
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id

    def test_raises_api_errors_exception_when_errors_occur_on_model(self):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithApiErrors")
        providable_info = ProvidableInfo()
        product = offers_factories.ThingOfferFactory(
            name="Old product name",
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            idAtProvider=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProviderWithApiErrors()

        # When
        with pytest.raises(ApiErrors) as api_errors:
            local_provider._handle_update(product, providable_info)

        # Then
        assert api_errors.value.errors["url"] == [
            "Une offre de sous-catégorie Achat instrument ne peut pas être numérique"
        ]
        provider_event = db.session.query(providers_models.LocalProviderEvent).one()
        assert provider_event.type == providers_models.LocalProviderEventType.SyncError


@pytest.mark.usefixtures("db_session")
class HandleThumbTest:
    def test_handle_thumb_increments_thumbCount(self):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = ProvidableInfo()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumb()

        # When
        local_provider._handle_thumb(product)
        repository.save(product)

        # Then
        assert local_provider.checkedThumbs == 1
        assert local_provider.updatedThumbs == 0
        assert local_provider.createdThumbs == 1
        assert product.thumbCount == 1


@pytest.mark.usefixtures("db_session")
class UploadThumbTest:
    def test_first_thumb(self, app):
        # Given
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = ProvidableInfo()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
            thumbCount=0,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumb()
        thumb = local_provider.get_object_thumb()

        # When
        _upload_thumb(product, thumb)
        repository.save(product)

        # Then
        assert product.thumbCount == 1
        assert product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(product.id)}"

    @patch("pcapi.core.object_storage.store_public_object")
    def test_fifth_thumb(self, mock_store_public_object):
        provider = providers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = ProvidableInfo()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
            thumbCount=4,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumb()
        thumb = local_provider.get_object_thumb()

        # When
        _upload_thumb(product, thumb)
        repository.save(product)

        # Then
        assert product.thumbCount == 5
        assert product.thumbUrl == f"http://localhost/storage/thumbs/products/{humanize(product.id)}_4"
        mock_store_public_object.assert_called_once()
        assert mock_store_public_object.call_args.kwargs["folder"] == "thumbs"
        assert mock_store_public_object.call_args.kwargs["object_id"] == f"products/{humanize(product.id)}_4"
        assert mock_store_public_object.call_args.kwargs["content_type"] == "image/jpeg"
