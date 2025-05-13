import datetime
from decimal import Decimal
from unittest import mock

import pytest
from sqlalchemy import exc as sa_exc

from pcapi.core.bookings import exceptions as booking_exceptions
from pcapi.core.educational import exceptions
from pcapi.core.educational import factories
from pcapi.core.educational.models import ALLOWED_ACTIONS_BY_DISPLAYED_STATUS
from pcapi.core.educational.models import COLLECTIVE_OFFER_TEMPLATE_STATUSES
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveDmsApplication
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferAllowedAction
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import HasImageMixin
from pcapi.core.educational.models import TEMPLATE_ALLOWED_ACTIONS_BY_DISPLAYED_STATUS
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.models import db
from pcapi.models.offer_mixin import CollectiveOfferStatus
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import db as db_utils
from pcapi.utils.image_conversion import CropParams
from pcapi.utils.image_conversion import ImageRatio


pytestmark = pytest.mark.usefixtures("db_session")

ALL_DISPLAYED_STATUSES = set(CollectiveOfferDisplayedStatus)


class EducationalDepositTest:
    def test_should_raise_insufficient_fund(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=True)

        # Then
        with pytest.raises(exceptions.InsufficientFund):
            educational_deposit.check_has_enough_fund(Decimal(1100.00))

    def test_should_raise_insufficient_temporary_fund(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=False)

        # Then
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            educational_deposit.check_has_enough_fund(Decimal(900.00))


class CollectiveStockIsBookableTest:
    def test_not_bookable_if_booking_limit_datetime_has_passed(self) -> None:
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        collective_stock = factories.CollectiveStockFactory(bookingLimitDatetime=past)
        assert not collective_stock.isBookable

    def test_not_bookable_if_offerer_is_not_validated(self) -> None:
        collective_stock = factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer__validationStatus=ValidationStatus.NEW
        )
        assert not collective_stock.isBookable

    def test_not_bookable_if_offerer_is_not_active(self) -> None:
        collective_stock = factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer__isActive=False,
        )
        assert not collective_stock.isBookable

    def test_not_bookable_if_offer_is_not_active(self) -> None:
        collective_stock = factories.CollectiveStockFactory(collectiveOffer__isActive=False)
        assert not collective_stock.isBookable

    def test_not_bookable_if_offer_is_event_with_passed_start_datetime(self) -> None:
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        collective_stock = factories.CollectiveStockFactory(startDatetime=past)
        assert not collective_stock.isBookable

    def test_not_bookable_if_no_remaining_stock(self) -> None:
        collective_stock = factories.CollectiveStockFactory()
        factories.CollectiveBookingFactory(collectiveStock=collective_stock)
        assert not collective_stock.isBookable

    def test_bookable(self) -> None:
        collective_stock = factories.CollectiveStockFactory()
        assert collective_stock.isBookable

    def test_bookable_if_booking_is_cancelled(self) -> None:
        collective_stock = factories.CollectiveStockFactory()
        factories.CollectiveBookingFactory(collectiveStock=collective_stock, status=CollectiveBookingStatus.CANCELLED)

        assert not collective_stock.isBookable


class CollectiveOfferIsSoldOutTest:
    def test_is_sold_out_property_false(self) -> None:
        offer = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert not offer.isSoldOut

    def test_offer_property_is_not_sold_out_when_booking_is_cancelled(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert not offer.isSoldOut

    def test_offer_property_is_sold_out(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock)

        assert offer.isSoldOut

    def test_offer_property_is_sold_out_when_some_booking_are_cancelled(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)

        assert offer.isSoldOut

    def test_is_sold_out_query_false(self) -> None:
        offer = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer)

        soldout_offer = factories.CollectiveOfferFactory()
        soldout_stock = factories.CollectiveStockFactory(collectiveOffer=soldout_offer)
        factories.CollectiveBookingFactory(collectiveStock=soldout_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(False)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_not_sold_out_when_booking_is_cancelled(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        soldout_offer = factories.CollectiveOfferFactory()
        soldout_stock = factories.CollectiveStockFactory(collectiveOffer=soldout_offer)
        factories.CollectiveBookingFactory(collectiveStock=soldout_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(False)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock)

        undsold_offer = factories.CollectiveOfferFactory()
        undsold_stock = factories.CollectiveStockFactory(collectiveOffer=undsold_offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(True)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out_when_some_booking_are_cancelled(self) -> None:
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)

        undsold_offer = factories.CollectiveOfferFactory()
        undsold_stock = factories.CollectiveStockFactory(collectiveOffer=undsold_offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(True)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out_on_realistic_case(self) -> None:
        offer_1 = factories.CollectiveOfferFactory()
        stock_1 = factories.CollectiveStockFactory(collectiveOffer=offer_1)
        factories.CollectiveBookingFactory(collectiveStock=stock_1, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock_1)
        factories.CollectiveBookingFactory(collectiveStock=stock_1, status=CollectiveBookingStatus.CANCELLED)
        offer_2 = factories.CollectiveOfferFactory()
        stock_2 = factories.CollectiveStockFactory(collectiveOffer=offer_2)
        factories.CollectiveBookingFactory(collectiveStock=stock_2)

        offer_3 = factories.CollectiveOfferFactory()
        stock_3 = factories.CollectiveStockFactory(collectiveOffer=offer_3)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock_3)
        offer_4 = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer_4)

        results = (
            db.session.query(CollectiveOffer)
            .filter(CollectiveOffer.isSoldOut.is_(True))
            .order_by(CollectiveOffer.id)
            .all()
        )

        assert len(results) == 2
        assert results[0].id == offer_1.id
        assert results[1].id == offer_2.id

        results = (
            db.session.query(CollectiveOffer)
            .filter(CollectiveOffer.isSoldOut.is_(False))
            .order_by(CollectiveOffer.id)
            .all()
        )

        assert len(results) == 2
        assert results[0].id == offer_3.id
        assert results[1].id == offer_4.id


class CollectiveStockIsEditableTest:
    def test_booked_stock_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.APPROVED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.USED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert not stock.isEditable

    def test_unbooked_stock_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.APPROVED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert stock.isEditable

    def test_no_bookings_stock_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.APPROVED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)

        assert stock.isEditable

    def test_booked_stock_not_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.REJECTED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.USED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert not stock.isEditable

    def test_unbooked_stock_not_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.REJECTED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert not stock.isEditable

    def test_no_bookings_stock_not_editable_offer(self) -> None:
        offer = factories.CollectiveOfferFactory(validation=OfferValidationStatus.REJECTED)
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)

        assert not stock.isEditable


class CollectiveOfferIsEditableTest:
    @pytest.mark.parametrize(
        "state,expected", [("PENDING", False), ("REJECTED", False), ("APPROVED", True), ("DRAFT", True)]
    )
    def test_offer_for_status(self, state, expected) -> None:
        offer = factories.CollectiveOfferFactory(validation=state)
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert offer.isEditable == expected


class CollectiveOfferIsEditableByProTest:
    @pytest.mark.parametrize(
        "state,expected", [("PENDING", False), ("REJECTED", False), ("APPROVED", True), ("DRAFT", True)]
    )
    def test_offer_for_status(self, state, expected) -> None:
        offer = factories.CollectiveOfferFactory(validation=state)
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert offer.isEditableByPcPro == expected

    @pytest.mark.parametrize("state", OfferValidationStatus)
    def test_offer_from_public_api_for_status(self, state) -> None:
        provider = providers_factories.PublicApiProviderFactory()
        offer = factories.CollectiveOfferFactory(validation=state, providerId=provider.id)
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert offer.isEditableByPcPro == False


class CollectiveOfferIsArchiveTest:
    @pytest.mark.parametrize("state", OfferValidationStatus)
    def test_date_archive_for_status(self, state) -> None:
        offer = factories.CollectiveOfferFactory.build(validation=state)

        assert offer.isArchived == False

        offer.isActive = False
        offer.dateArchived = datetime.datetime.utcnow()

        assert offer.isArchived == True
        assert offer.status == CollectiveOfferStatus.ARCHIVED.value

    def test_query_is_archived(self) -> None:
        offer_archived = factories.CollectiveOfferFactory(isActive=False, dateArchived=datetime.datetime.utcnow())
        offer_not_archived = factories.CollectiveOfferFactory(dateArchived=None)

        results = db.session.query(CollectiveOffer.id).filter(CollectiveOffer.isArchived).all()
        results_ids = {id for (id,) in results}

        assert len(results) == 1
        assert offer_archived.id in results_ids
        assert offer_not_archived.id not in results_ids

    def test_query_status_for_archived(self) -> None:
        offer_archived = factories.CollectiveOfferFactory(isActive=False, dateArchived=datetime.datetime.utcnow())
        offer_not_archived = factories.CollectiveOfferFactory(dateArchived=None)

        results = db.session.query(CollectiveOffer.id, CollectiveOffer.status).all()
        status_by_id = dict(results)

        assert status_by_id[offer_archived.id] == "ARCHIVED"
        assert status_by_id[offer_not_archived.id] == "ACTIVE"

        results_archived = db.session.query(CollectiveOffer.id).filter(CollectiveOffer.status == "ARCHIVED").all()
        results_archived_ids = {id for (id,) in results_archived}
        assert len(results_archived_ids) == 1
        assert offer_archived.id in results_archived_ids


class CollectiveOfferTemplateIsEditableTest:
    @pytest.mark.parametrize(
        "state,expected", [("PENDING", False), ("REJECTED", False), ("APPROVED", True), ("DRAFT", True)]
    )
    def test_offer_is_editable_by_pc_pro_for_status(self, state, expected) -> None:
        offer = factories.CollectiveOfferTemplateFactory(validation=state)

        assert offer.isEditableByPcPro == expected

    @pytest.mark.parametrize(
        "state,expected", [("PENDING", False), ("REJECTED", False), ("APPROVED", True), ("DRAFT", True)]
    )
    def test_offer_is_editable_for_status(self, state, expected) -> None:
        offer = factories.CollectiveOfferTemplateFactory(validation=state)

        assert offer.isEditable == expected


class CollectiveStockIsCancellableFromOfferer:
    def test_collective_stock_is_cancellable(self):
        stock: CollectiveStock = factories.CollectiveStockFactory.build()
        factories.CancelledCollectiveBookingFactory.build(collectiveStock=stock)
        factories.PendingCollectiveBookingFactory.build(collectiveStock=stock)
        assert stock.is_cancellable_from_offerer

    def test_collective_stock_has_used_collective_booking(self):
        stock: CollectiveStock = factories.CollectiveStockFactory.build()
        factories.UsedCollectiveBookingFactory.build(collectiveStock=stock)
        assert not stock.is_cancellable_from_offerer

    def test_collective_stock_has_reimbursed_collective_booking(self):
        stock: CollectiveStock = factories.CollectiveStockFactory.build()
        factories.ReimbursedCollectiveBookingFactory.build(collectiveStock=stock)
        assert not stock.is_cancellable_from_offerer


class HasImageMixinTest:
    def test_basic_methods(self):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageCrop = {}
        image.imageCredit = "toto"
        image.imageId = "123654789654"
        image.imageHasOriginal = True

        assert image.imageUrl == "http://localhost/storage/thumbs/image/123654789654.jpg"
        assert image.imageOriginalUrl == "http://localhost/storage/thumbs/image/123654789654_original.jpg"
        assert image._get_image_storage_id() == "image/123654789654.jpg"
        assert image._get_image_storage_id(original=True) == "image/123654789654_original.jpg"

    @mock.patch("pcapi.core.object_storage.store_public_object")
    @mock.patch("pcapi.core.object_storage.delete_public_object")
    @mock.patch(
        "pcapi.utils.image_conversion.process_original_image", return_value=b"processed original image contents"
    )
    @mock.patch("pcapi.utils.image_conversion.standardize_image", return_value=b"standardized image contents")
    def test_set_new_image(self, standardize_image, process_original_image, delete_public_object, store_public_object):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageHasOriginal = False
        image.imageCrop = None
        image.imageId = None
        image_data = b"unprocessed image"
        ratio = ImageRatio.PORTRAIT
        credit = "credit on image"
        crop_data = CropParams(
            x_crop_percent=0.5,
            y_crop_percent=0.10,
            height_crop_percent=0.60,
            width_crop_percent=0.33,
        )
        image.set_image(
            image=image_data,
            credit=credit,
            crop_params=crop_data,
            ratio=ratio,
            keep_original=False,
        )
        assert image.imageCrop is None
        assert image.imageId.startswith(str(image.id).zfill(10))
        assert image.imageCredit == credit
        assert image.imageHasOriginal is False
        standardize_image.assert_called_once_with(content=image_data, ratio=ratio, crop_params=crop_data)
        process_original_image.assert_not_called()
        store_public_object.assert_called_once_with(
            folder=image.FOLDER,
            object_id=image._get_image_storage_id(),
            blob=b"standardized image contents",
            content_type="image/jpeg",
        )
        delete_public_object.assert_not_called()

    @mock.patch("pcapi.core.object_storage.store_public_object")
    @mock.patch("pcapi.core.object_storage.delete_public_object")
    @mock.patch(
        "pcapi.utils.image_conversion.process_original_image", return_value=b"processed original image contents"
    )
    @mock.patch("pcapi.utils.image_conversion.standardize_image", return_value=b"standardized image contents")
    def test_set_replace_image(
        self, standardize_image, process_original_image, delete_public_object, store_public_object
    ):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageCrop = {
            "x_crop_percent": 0.1,
            "y_crop_percent": 0.5,
            "height_crop_percent": 0.12,
            "width_crop_percent": 0.97,
        }
        image.imageCredit = "toto"
        image.imageHasOriginal = True
        image.imageId = "123456"

        image_data = b"unprocessed image"
        ratio = ImageRatio.PORTRAIT
        credit = "credit on image"
        crop_data = CropParams(
            x_crop_percent=0.5,
            y_crop_percent=0.10,
            height_crop_percent=0.60,
            width_crop_percent=0.33,
        )
        image.set_image(
            image=image_data,
            credit=credit,
            crop_params=crop_data,
            ratio=ratio,
            keep_original=False,
        )
        assert image.imageCrop is None
        assert image.imageCredit == credit
        assert image.imageId != "123"
        assert image.imageId.startswith(str(image.id).zfill(10))
        assert image.imageHasOriginal is False
        standardize_image.assert_called_once_with(content=image_data, ratio=ratio, crop_params=crop_data)
        process_original_image.assert_not_called()
        store_public_object.assert_called_once_with(
            folder=image.FOLDER,
            object_id=image._get_image_storage_id(),
            blob=b"standardized image contents",
            content_type="image/jpeg",
        )
        assert delete_public_object.call_count == 2
        delete_public_object.assert_any_call(folder=image.FOLDER, object_id="image/123456.jpg")
        delete_public_object.assert_any_call(folder=image.FOLDER, object_id="image/123456_original.jpg")

    @mock.patch("pcapi.core.object_storage.store_public_object")
    @mock.patch("pcapi.core.object_storage.delete_public_object")
    @mock.patch(
        "pcapi.utils.image_conversion.process_original_image", return_value=b"processed original image contents"
    )
    @mock.patch("pcapi.utils.image_conversion.standardize_image", return_value=b"standardized image contents")
    def test_set_new_image_keep_original(
        self, standardize_image, process_original_image, delete_public_object, store_public_object
    ):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageCrop = None
        image_data = b"unprocessed image"
        image.imageId = None
        ratio = ImageRatio.PORTRAIT
        credit = "credit on image"
        crop_data = CropParams(
            x_crop_percent=0.5,
            y_crop_percent=0.10,
            height_crop_percent=0.60,
            width_crop_percent=0.33,
        )
        image.set_image(
            image=image_data,
            credit=credit,
            crop_params=crop_data,
            ratio=ratio,
            keep_original=True,
        )
        assert image.imageCrop == crop_data.__dict__
        assert image.imageCredit == credit
        assert image.imageId.startswith(str(image.id).zfill(10))
        assert image.imageHasOriginal is True
        standardize_image.assert_called_once_with(content=image_data, ratio=ratio, crop_params=crop_data)
        process_original_image.assert_called_once_with(content=image_data, resize=False)
        assert store_public_object.call_count == 2
        store_public_object.assert_any_call(
            folder=image.FOLDER,
            object_id=image._get_image_storage_id(original=True),
            blob=b"processed original image contents",
            content_type="image/jpeg",
        )
        store_public_object.assert_any_call(
            folder=image.FOLDER,
            object_id=image._get_image_storage_id(),
            blob=b"standardized image contents",
            content_type="image/jpeg",
        )

        delete_public_object.assert_not_called()

    @mock.patch("pcapi.core.object_storage.delete_public_object")
    def test_delete_image(self, delete_public_object):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageId = "456789"
        image.imageCredit = "toto"
        image.imageHasOriginal = False
        image.delete_image()
        assert image.imageCrop is None
        assert image.imageCredit is None
        assert image.imageHasOriginal is None
        assert image.imageId is None
        delete_public_object.assert_called_once_with(folder=image.FOLDER, object_id="image/456789.jpg")

    @mock.patch("pcapi.core.object_storage.delete_public_object")
    def test_delete_image_with_original(self, delete_public_object):
        class Image(HasImageMixin):
            pass

        image = Image()
        image.id = 1
        image.imageId = "123456"
        image.imageCrop = {
            "x_crop_percent": 0.1,
            "y_crop_percent": 0.5,
            "height_crop_percent": 0.12,
            "width_crop_percent": 0.97,
        }
        image.imageCredit = "toto"
        image.imageHasOriginal = True
        image.delete_image()
        assert image.imageCrop is None
        assert image.imageCredit is None
        assert image.imageHasOriginal is None
        assert image.imageId is None
        assert delete_public_object.call_count == 2
        delete_public_object.assert_any_call(folder=image.FOLDER, object_id="image/123456.jpg")
        delete_public_object.assert_any_call(folder=image.FOLDER, object_id="image/123456_original.jpg")


class CollectiveOfferTemplateIsEligibleForSearchTest:
    def test_is_eligible_for_search(self):
        searchable_offer = factories.CollectiveOfferTemplateFactory()
        virtual_venue = offerers_factories.VirtualVenueFactory()
        unsearchable_offer = factories.CollectiveOfferTemplateFactory(venue=virtual_venue)
        assert searchable_offer.is_eligible_for_search
        assert not unsearchable_offer.is_eligible_for_search

    @pytest.mark.parametrize(
        "validation_status,is_eligible_for_search",
        [
            (ValidationStatus.NEW, False),
            (ValidationStatus.PENDING, False),
            (ValidationStatus.VALIDATED, True),
            (ValidationStatus.REJECTED, False),
            (ValidationStatus.CLOSED, False),
        ],
    )
    def test_offerer_validation_status(self, validation_status, is_eligible_for_search):
        collective_offer_template = factories.CollectiveOfferTemplateFactory(
            isActive=True, venue__managingOfferer__validationStatus=validation_status
        )
        assert collective_offer_template.is_eligible_for_search is is_eligible_for_search


class EducationalInstitutionProgramTest:
    def test_unique_program_for_an_educational_institution(self):
        program1 = factories.EducationalInstitutionProgramFactory()
        program2 = factories.EducationalInstitutionProgramFactory()
        institution = factories.EducationalInstitutionFactory()
        factories.EducationalInstitutionProgramAssociationFactory(institution=institution, program=program1)

        with pytest.raises(sa_exc.IntegrityError):
            factories.EducationalInstitutionProgramAssociationFactory(institution=institution, program=program2)
            db.session.commit()

    def test_programs_at_date_for_an_educational_institution(self):
        program1 = factories.EducationalInstitutionProgramFactory()

        institution = factories.EducationalInstitutionFactory()

        past = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution, program=program1, timespan=db_utils.make_timerange(past, None)
        )

        assert institution.programs_at_date(datetime.datetime.utcnow()) == [program1]

        before_meg_start = datetime.datetime(2020, 1, 1)
        assert institution.programs_at_date(before_meg_start) == []

    def test_programs_at_date_for_an_educational_institution_leaving_program(self):
        program = factories.EducationalInstitutionProgramFactory()

        institution = factories.EducationalInstitutionFactory()

        today = datetime.datetime.utcnow()
        past = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        futur_date = today + datetime.timedelta(days=365)
        factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution, program=program, timespan=(db_utils.make_timerange(start=past, end=futur_date))
        )

        assert institution.programs_at_date(today) == [program]

        very_futur_date = today + datetime.timedelta(days=365 * 2)
        assert institution.programs_at_date(very_futur_date) == []


class CollectiveOfferDisplayedStatusTest:
    @pytest.mark.parametrize(
        "status",
        ALL_DISPLAYED_STATUSES - {CollectiveOfferDisplayedStatus.CANCELLED},
    )
    def test_get_offer_displayed_status(self, status):
        offer = factories.create_collective_offer_by_status(status)

        assert offer.displayedStatus == status

    def test_get_offer_displayed_status_cancelled(self):
        offer = factories.CancelledWithoutBookingCollectiveOfferFactory()
        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.CANCELLED

    def test_get_offer_displayed_status_cancelled_with_booking(self):
        offer = factories.CancelledWithBookingCollectiveOfferFactory()
        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.CANCELLED

    def test_get_displayed_status_for_expired_offer_due_to_booking_date_passed(self):
        offer = factories.ExpiredWithBookingCollectiveOfferFactory()

        stock = offer.collectiveStock

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.EXPIRED

        futur = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        stock.bookingLimitDatetime = futur

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.PREBOOKED

    def test_get_displayed_status_for_offer_when_in_between_startDatetime_endDatetime(self):
        offer = factories.CollectiveOfferFactory()
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        futur = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        stock = factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=yesterday, endDatetime=futur, bookingLimitDatetime=futur
        )
        _booking = factories.UsedCollectiveBookingFactory(collectiveStock=stock)

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED

    def test_get_displayed_status_for_offer_with_cancelled_booking(self):
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)

        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=yesterday, endDatetime=yesterday)
        factories.CancelledCollectiveBookingFactory(
            collectiveStock=stock, dateCreated=yesterday - datetime.timedelta(days=3)
        )
        factories.ReimbursedCollectiveBookingFactory(collectiveStock=stock, dateCreated=datetime.datetime.utcnow())

        assert offer.lastBookingStatus == CollectiveBookingStatus.REIMBURSED
        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.REIMBURSED


class CollectiveOfferTemplateDisplayedStatusTest:
    @pytest.mark.parametrize("status", COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_get_offer_displayed_status(self, status):
        offer = factories.create_collective_offer_template_by_status(status)
        assert offer.displayedStatus == status

    def test_get_displayed_status_for_inactive_offer_with_end_date_passed(self):
        offer = factories.CollectiveOfferTemplateFactory(
            validation=OfferValidationStatus.APPROVED,
            isActive=False,
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=4),
                end=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            ),
        )
        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED

        offer.dateRange = None
        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.HIDDEN


class CollectiveOfferAllowedActionsTest:
    @pytest.mark.parametrize("status", ALL_DISPLAYED_STATUSES - {CollectiveOfferDisplayedStatus.ENDED})
    def test_get_offer_allowed_actions(self, status):
        offer = factories.create_collective_offer_by_status(status)
        assert offer.allowedActions == list(ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[status])

    def test_get_ended_offer_allowed_actions(self):
        offer = factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActions == [
            CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
            CollectiveOfferAllowedAction.CAN_DUPLICATE,
            CollectiveOfferAllowedAction.CAN_CANCEL,
        ]

    def test_get_ended_offer_two_days_past_allowed_actions(self):
        offer = factories.EndedCollectiveOfferFactory()

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActions == [
            CollectiveOfferAllowedAction.CAN_DUPLICATE,
        ]

    @pytest.mark.parametrize("status", ALL_DISPLAYED_STATUSES - {CollectiveOfferDisplayedStatus.ENDED})
    def test_get_offer_allowed_actions_public_api(self, status):
        offer = factories.create_collective_offer_by_status(status, provider=providers_factories.ProviderFactory())

        assert set(offer.allowedActions) == set(ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[status]) - {
            CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
            CollectiveOfferAllowedAction.CAN_EDIT_DATES,
            CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
            CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        }

    def test_get_offer_ended_allowed_actions_public_api(self):
        offer = factories.EndedCollectiveOfferFactory(
            booking_is_confirmed=True, provider=providers_factories.ProviderFactory()
        )

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActions == [
            CollectiveOfferAllowedAction.CAN_DUPLICATE,
            CollectiveOfferAllowedAction.CAN_CANCEL,
        ]

    def test_get_offer_ended_two_days_past_allowed_actions_public_api(self):
        offer = factories.EndedCollectiveOfferFactory(provider=providers_factories.ProviderFactory())

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActions == [CollectiveOfferAllowedAction.CAN_DUPLICATE]

    def test_get_offer_allowed_actions_for_cancelled_with_booking(self):
        offer = factories.CancelledWithBookingCollectiveOfferFactory()
        assert offer.allowedActions == list(
            ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[CollectiveOfferDisplayedStatus.CANCELLED]
        )

    def test_get_offer_allowed_actions_for_cancelled_without_booking(self):
        offer = factories.CancelledWithoutBookingCollectiveOfferFactory()
        assert offer.allowedActions == list(
            ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[CollectiveOfferDisplayedStatus.CANCELLED]
        )

    def test_get_offer_allowed_actions_for_cancelled_due_to_expiration(self):
        offer = factories.CancelledDueToExpirationCollectiveOfferFactory()
        assert offer.allowedActions == list(
            ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[CollectiveOfferDisplayedStatus.CANCELLED]
        )

    def test_is_two_days_past_end(self):
        offer = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert offer.collectiveStock.endDatetime > datetime.datetime.utcnow()
        assert not offer.is_two_days_past_end()

        offer.collectiveStock.endDatetime = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        assert offer.is_two_days_past_end()

    @pytest.mark.parametrize("status", COLLECTIVE_OFFER_TEMPLATE_STATUSES)
    def test_get_offer_template_allowed_actions(self, status):
        offer = factories.create_collective_offer_template_by_status(status)
        assert offer.allowedActions == list(TEMPLATE_ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[status])

    @pytest.mark.parametrize("status", ALL_DISPLAYED_STATUSES - {CollectiveOfferDisplayedStatus.ENDED})
    def test_get_offer_allowed_actions_for_public_api(self, status):
        offer = factories.create_collective_offer_by_status(status, provider=providers_factories.ProviderFactory())

        assert offer.allowedActionsForPublicApi == list(ALLOWED_ACTIONS_BY_DISPLAYED_STATUS[status])

    @pytest.mark.parametrize("status", ALL_DISPLAYED_STATUSES)
    def test_get_offer_allowed_actions_for_public_api_pc_pro_offer(self, status):
        offer = factories.create_collective_offer_by_status(status)

        assert offer.allowedActionsForPublicApi == []

    def test_get_ended_offer_allowed_actions_for_public_api(self):
        offer = factories.EndedCollectiveOfferFactory(
            booking_is_confirmed=True, provider=providers_factories.ProviderFactory()
        )

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActionsForPublicApi == [
            CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
            CollectiveOfferAllowedAction.CAN_DUPLICATE,
            CollectiveOfferAllowedAction.CAN_CANCEL,
        ]

    def test_get_ended_offer_two_days_past_allowed_actions_for_public_api(self):
        offer = factories.EndedCollectiveOfferFactory(provider=providers_factories.ProviderFactory())

        assert offer.displayedStatus == CollectiveOfferDisplayedStatus.ENDED
        assert offer.allowedActionsForPublicApi == [
            CollectiveOfferAllowedAction.CAN_DUPLICATE,
        ]


class CollectiveOfferTemplateHasEndDatePassedTest:
    def test_has_end_date_passed(self):
        offer_without_range = factories.CollectiveOfferTemplateFactory(dateRange=None)
        assert offer_without_range.dateRange is None
        assert not offer_without_range.hasEndDatePassed

        offer_with_range = factories.CollectiveOfferTemplateFactory()
        assert offer_with_range.dateRange is not None
        assert not offer_with_range.hasEndDatePassed

        now = datetime.datetime.utcnow()
        date_range = db_utils.make_timerange(
            start=now - datetime.timedelta(days=3),
            end=now - datetime.timedelta(days=1),
        )
        offer_passed = factories.CollectiveOfferTemplateFactory(dateRange=date_range)
        assert offer_passed.dateRange is not None
        assert offer_passed.hasEndDatePassed

        passed_offer = (
            db.session.query(CollectiveOfferTemplate).filter(CollectiveOfferTemplate.hasEndDatePassed.is_(True)).one()
        )
        assert passed_offer.id == offer_passed.id

        not_passed_offers = (
            db.session.query(CollectiveOfferTemplate).filter(CollectiveOfferTemplate.hasEndDatePassed.is_(False)).all()
        )
        assert len(not_passed_offers) == 2
        assert {o.id for o in not_passed_offers} == {offer_without_range.id, offer_with_range.id}


class CollectiveBookingTest:
    @pytest.mark.parametrize("status", set(CollectiveBookingStatus) - {CollectiveBookingStatus.CANCELLED})
    def test_uncancel_booking_raise(self, status):
        booking = factories.create_collective_booking_by_status(status)
        with pytest.raises(booking_exceptions.BookingIsNotCancelledCannotBeUncancelled):
            booking.uncancel_booking()

    def test_uncancel_booking_to_confirmed(self):
        booking = factories.CancelledCollectiveBookingFactory()
        booking.uncancel_booking()

        assert booking.cancellationDate is None
        assert booking.cancellationReason is None
        assert booking.cancellationUserId is None

        assert booking.status == CollectiveBookingStatus.CONFIRMED
        assert booking.dateUsed is None

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

    def test_uncancel_booking_to_used(self):
        booking = factories.CancelledCollectiveBookingFactory(
            collectiveStock__startDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=4),
            collectiveStock__endDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=3),
        )
        booking.uncancel_booking()

        assert booking.cancellationDate is None
        assert booking.cancellationReason is None
        assert booking.cancellationUserId is None

        assert booking.status == CollectiveBookingStatus.USED
        assert booking.dateUsed is not None

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

    def test_uncancel_booking_to_pending(self):
        booking = factories.CancelledCollectiveBookingFactory(confirmationDate=None)
        booking.uncancel_booking()

        assert booking.cancellationDate is None
        assert booking.cancellationReason is None
        assert booking.cancellationUserId is None

        assert booking.status == CollectiveBookingStatus.PENDING
        assert booking.dateUsed is None

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown


class CollectiveDmsApplicationTest:
    def test_siren(self):
        application = factories.CollectiveDmsApplicationFactory(venue__siret="12345678200010")
        assert application.siren == "123456782"

    def test_siren_sql_expression(self):
        application_1 = factories.CollectiveDmsApplicationFactory(venue__siret="12345678200010")
        application_2 = factories.CollectiveDmsApplicationFactory(venue__siret="12345678200028")
        factories.CollectiveDmsApplicationFactory(venue__siret="12345679000013")

        filtered = (
            db.session.query(CollectiveDmsApplication).filter(CollectiveDmsApplication.siren == "123456782").all()
        )
        assert set(filtered) == {application_1, application_2}
