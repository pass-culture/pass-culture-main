from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.local_providers.local_provider import _save_same_thumb_from_thumb_count_to_index
from pcapi.model_creators.provider_creators import create_providable_info
from pcapi.models import ApiErrors
from pcapi.models import LocalProviderEvent
from pcapi.models import Product
from pcapi.models import ThingType
from pcapi.models.local_provider_event import LocalProviderEventType
from pcapi.repository import repository

from . import provider_test_utils


@pytest.mark.usefixtures("db_session")
class UpdateObjectsTest:
    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_iterator_is_called_until_exhausted(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[], [], []]

        # When
        local_provider.updateObjects()

        # Then
        assert next_function.call_count == 4

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_iterator_should_log_provider_event_from_start_to_stop(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[], []]

        # When
        local_provider.updateObjects()

        # Then
        provider_events = LocalProviderEvent.query.order_by(LocalProviderEvent.id.asc()).all()
        assert provider_events[0].type == LocalProviderEventType.SyncStart
        assert provider_events[1].type == LocalProviderEventType.SyncEnd

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_creates_new_object_when_no_object_in_database(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info()
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        new_product = Product.query.one()
        assert new_product.name == "New Product"
        assert new_product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert new_product.type == str(ThingType.LIVRE_EDITION)

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_updates_existing_object(self, next_function):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))
        product = offers_factories.ThingProductFactory(
            dateModifiedAtLastProvider=datetime(2000, 1, 1),
            lastProvider=provider,
            idAtProviders=providable_info.id_at_providers,
            name="Old product name",
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
        )
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        product = Product.query.one()
        assert product.name == "New Product"
        assert product.type == str(ThingType.LIVRE_EDITION)
        assert product.dateModifiedAtLastProvider == providable_info.date_modified_at_provider

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_existing_object_when_date_is_older_than_last_modified_date(self, next_function):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))
        product = offers_factories.ThingProductFactory(
            dateModifiedAtLastProvider=datetime(2020, 1, 1),
            lastProvider=provider,
            idAtProviders=providable_info.id_at_providers,
            name="Old product name",
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
        )
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        product = Product.query.one()
        assert product.name == "Old product name"
        assert product.type == str(ThingType.INSTRUMENT)
        assert product.dateModifiedAtLastProvider == datetime(2020, 1, 1)

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_objects_when_venue_provider_is_not_active(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))
        venue_provider = offerers_factories.VenueProviderFactory(isActive=False)
        local_provider = provider_test_utils.TestLocalProvider(venue_provider)
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert Product.query.count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_does_not_update_objects_when_provider_is_not_active(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider", isActive=False)
        providable_info = create_providable_info(date_modified=datetime(2018, 1, 1))
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert Product.query.count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProviderNoCreation.__next__")
    def test_does_not_create_new_object_when_can_create_is_false(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderNoCreation")
        providable_info = create_providable_info()
        local_provider = provider_test_utils.TestLocalProviderNoCreation()
        next_function.side_effect = [[providable_info]]

        # When
        local_provider.updateObjects()

        # Then
        assert Product.query.count() == 0

    @patch("tests.local_providers.provider_test_utils.TestLocalProvider.__next__")
    def test_creates_only_one_object_when_limit_is_one(self, next_function):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info1 = create_providable_info()
        providable_info2 = create_providable_info(id_at_providers="2")
        local_provider = provider_test_utils.TestLocalProvider()
        next_function.side_effect = [[providable_info1], [providable_info2]]

        # When
        local_provider.updateObjects(limit=1)

        # Then
        new_product = Product.query.one()
        assert new_product.name == "New Product"
        assert new_product.type == str(ThingType.LIVRE_EDITION)


@pytest.mark.usefixtures("db_session")
class CreateObjectTest:
    def test_returns_object_with_expected_attributes(self):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info()
        local_provider = provider_test_utils.TestLocalProvider()

        # When
        product = local_provider._create_object(providable_info)

        # Then
        assert isinstance(product, Product)
        assert product.name == "New Product"
        assert product.type == str(ThingType.LIVRE_EDITION)
        assert product.lastProviderId == provider.id

    def test_raises_api_errors_exception_when_errors_occur_on_model_and_log_error(self):
        # Given
        offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithApiErrors")
        providable_info = create_providable_info()
        local_provider = provider_test_utils.TestLocalProviderWithApiErrors()

        # When
        with pytest.raises(ApiErrors) as api_errors:
            local_provider._create_object(providable_info)

        # Then
        assert api_errors.value.errors["url"] == [
            "Une offre de type Vente et location d’instruments de musique ne peut pas être numérique"
        ]
        assert Product.query.count() == 0
        provider_event = LocalProviderEvent.query.one()
        assert provider_event.type == LocalProviderEventType.SyncError


@pytest.mark.usefixtures("db_session")
class HandleUpdateTest:
    def test_returns_object_with_expected_attributes(self):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProvider")
        providable_info = create_providable_info()
        product = offers_factories.ThingProductFactory(
            name="Old product name",
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProvider()

        # When
        local_provider._handle_update(product, providable_info)

        # Then
        product = Product.query.one()
        assert product.name == "New Product"
        assert product.type == str(ThingType.LIVRE_EDITION)

    def test_raises_api_errors_exception_when_errors_occur_on_model(self):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithApiErrors")
        providable_info = create_providable_info()
        product = offers_factories.ThingProductFactory(
            name="Old product name",
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProviderWithApiErrors()

        # When
        with pytest.raises(ApiErrors) as api_errors:
            local_provider._handle_update(product, providable_info)

        # Then
        assert api_errors.value.errors["url"] == [
            "Une offre de type Vente et location d’instruments de musique ne peut pas être numérique"
        ]
        provider_event = LocalProviderEvent.query.one()
        assert provider_event.type == LocalProviderEventType.SyncError


@pytest.mark.usefixtures("db_session")
class HandleThumbTest:
    def test_call_save_thumb_should_increase_thumbCount_by_1(self):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = create_providable_info()
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

    def test_create_several_thumbs_when_thumb_index_is_4_and_current_thumbCount_is_0(self):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumbIndexAt4")
        providable_info = create_providable_info()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumbIndexAt4()

        # When
        local_provider._handle_thumb(product)
        repository.save(product)

        # Then
        assert local_provider.checkedThumbs == 1
        assert local_provider.updatedThumbs == 0
        assert local_provider.createdThumbs == 4
        assert product.thumbCount == 4


@pytest.mark.usefixtures("db_session")
class SaveThumbFromThumbCountToIndexTest:
    def test_should_iterate_from_current_thumbCount_to_thumbIndex_when_thumbCount_is_0(self, app):
        # Given
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = create_providable_info()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
            thumbCount=0,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumb()
        thumb = local_provider.get_object_thumb()

        # When
        thumb_index = 4
        _save_same_thumb_from_thumb_count_to_index(product, thumb_index, thumb)
        repository.save(product)

        # Then
        assert product.thumbCount == 4

    def test_should_only_replace_image_at_specific_thumb_index_when_thumbCount_is_superior_to_thumbIndex(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="TestLocalProviderWithThumb")
        providable_info = create_providable_info()
        product = offers_factories.ThingProductFactory(
            idAtProviders=providable_info.id_at_providers,
            lastProvider=provider,
            thumbCount=4,
        )
        local_provider = provider_test_utils.TestLocalProviderWithThumb()
        thumb = local_provider.get_object_thumb()

        # When
        thumb_index = 1
        _save_same_thumb_from_thumb_count_to_index(product, thumb_index, thumb)
        repository.save(product)

        # Then
        assert product.thumbCount == 4
