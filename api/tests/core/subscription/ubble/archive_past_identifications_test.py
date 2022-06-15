import datetime
from unittest import mock

import pytest

from pcapi.core.fraud.factories import BeneficiaryFraudCheckFactory
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.subscription.ubble.archive_past_identification_pictures import UbbleIdentificationPicturesArchiveResult
from pcapi.core.subscription.ubble.archive_past_identification_pictures import archive_past_identification_pictures
from pcapi.core.subscription.ubble.archive_past_identification_pictures import get_fraud_check_to_archive


class ArchivePastIdentificationPicturesTest:
    def test_should_throw_if_start_date_is_after_end_date(self):
        # Given
        start_date = datetime.datetime(2022, 1, 1)
        end_date = datetime.datetime(2021, 1, 1)

        # When
        with pytest.raises(ValueError):
            archive_past_identification_pictures(start_date, end_date)

    @mock.patch("pcapi.core.subscription.ubble.api.archive_ubble_user_id_pictures")
    @mock.patch("pcapi.core.subscription.ubble.archive_past_identification_pictures.get_fraud_check_to_archive")
    def test_should_call_action_function(
        self, mocked_get_fraud_check_to_archive, mocked_archive_ubble_user_id_pictures
    ):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)
        limit = 2

        first_fraud_check = BeneficiaryFraudCheck(
            status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, dateCreated=datetime.datetime(2021, 12, 31)
        )
        second_fraud_check = BeneficiaryFraudCheck(
            status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, dateCreated=datetime.datetime(2021, 12, 31)
        )
        third_fraud_check = BeneficiaryFraudCheck(
            status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, dateCreated=datetime.datetime(2021, 12, 31)
        )

        mocked_get_fraud_check_to_archive.side_effect = [
            [first_fraud_check, second_fraud_check],
            [third_fraud_check],
            [],
        ]
        mocked_archive_ubble_user_id_pictures.side_effect = [True, False, True]
        expected_result = UbbleIdentificationPicturesArchiveResult(2, 1)
        expected_default_offset = 0
        expected_second_offset = 2
        expected_last_offset = 4

        # When
        actual = archive_past_identification_pictures(start_date, end_date, limit)

        # Then
        mocked_get_fraud_check_to_archive.assert_has_calls(
            [
                mock.call(start_date, end_date, None, limit, expected_default_offset),
                mock.call(start_date, end_date, None, limit, expected_second_offset),
                mock.call(start_date, end_date, None, limit, expected_last_offset),
            ]
        )
        assert mocked_get_fraud_check_to_archive.call_count == 3
        assert mocked_archive_ubble_user_id_pictures.call_count == 3
        assert actual == expected_result

    @mock.patch("pcapi.core.subscription.ubble.api.archive_ubble_user_id_pictures")
    @mock.patch("pcapi.core.subscription.ubble.archive_past_identification_pictures.get_fraud_check_to_archive")
    def test_action_function_throw(self, mocked_get_fraud_check_to_archive, mocked_archive_ubble_user_id_pictures):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)

        first_fraud_check = BeneficiaryFraudCheck(
            status=FraudCheckStatus.OK, type=FraudCheckType.UBBLE, dateCreated=datetime.datetime(2021, 12, 31)
        )

        mocked_get_fraud_check_to_archive.side_effect = [[first_fraud_check], []]
        mocked_archive_ubble_user_id_pictures.side_effect = BeneficiaryFraudCheckMissingException()

        # When
        actual = archive_past_identification_pictures(start_date, end_date)

        # Then
        assert actual.errors == 1


class GetFraudCheckToArchiveTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_give_total_of_records(self):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)

        fraud_status_ok = FraudCheckStatus.OK
        fraud_type_ubble = FraudCheckType.UBBLE
        date_between_start_and_end = datetime.datetime(2021, 12, 31)
        id_picture_store_status_none = None

        # fraud_check_to_archive
        BeneficiaryFraudCheckFactory(
            status=fraud_status_ok,
            type=fraud_type_ubble,
            dateCreated=date_between_start_and_end,
            idPicturesStored=id_picture_store_status_none,
        )
        # fraud_check_unwanted_status
        BeneficiaryFraudCheckFactory(
            status=FraudCheckStatus.KO,
            type=fraud_type_ubble,
            dateCreated=date_between_start_and_end,
            idPicturesStored=id_picture_store_status_none,
        )
        # fraud_check_unwanted_date_created
        BeneficiaryFraudCheckFactory(
            status=fraud_status_ok,
            type=fraud_type_ubble,
            dateCreated=datetime.datetime(2022, 3, 1),
            idPicturesStored=id_picture_store_status_none,
        )
        # fraud_check_picture_store_status_true
        BeneficiaryFraudCheckFactory(
            status=fraud_status_ok, type=fraud_type_ubble, dateCreated=date_between_start_and_end, idPicturesStored=True
        )
        # fraud_check_picture_store_status_false
        BeneficiaryFraudCheckFactory(
            status=fraud_status_ok,
            type=fraud_type_ubble,
            dateCreated=date_between_start_and_end,
            idPicturesStored=False,
        )

        expected = 1

        # When
        actual = get_fraud_check_to_archive(start_date, end_date, id_picture_store_status_none)

        # Then
        assert len(actual) == expected
        actual_fraud_check = actual[0]
        assert actual_fraud_check.idPicturesStored == id_picture_store_status_none
        assert start_date < actual_fraud_check.dateCreated < end_date
        assert actual_fraud_check.type == fraud_type_ubble

    @pytest.mark.usefixtures("db_session")
    def test_should_select_false_id_picture_stored(self):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)
        expected_id_picture_stored_false = False

        # fraud_check_to_archive
        BeneficiaryFraudCheckFactory(
            status=FraudCheckStatus.OK,
            type=FraudCheckType.UBBLE,
            dateCreated=datetime.datetime(2021, 12, 31),
            idPicturesStored=expected_id_picture_stored_false,
        )
        # fraud_check_picture_store_status_true
        BeneficiaryFraudCheckFactory(
            status=FraudCheckStatus.OK,
            type=FraudCheckType.UBBLE,
            dateCreated=datetime.datetime(2021, 12, 31),
            idPicturesStored=None,
        )

        expected = 1

        # When
        actual = get_fraud_check_to_archive(start_date, end_date, expected_id_picture_stored_false)

        # Then
        assert len(actual) == expected
        actual_fraud_check = actual[0]
        assert actual_fraud_check.idPicturesStored == expected_id_picture_stored_false

    @pytest.mark.usefixtures("db_session")
    def test_should_give_limit_result_size_with_offset(self):
        # Given
        start_date = datetime.datetime(2021, 1, 1)
        end_date = datetime.datetime(2022, 1, 1)
        limit = 1
        offset = 1

        first_fraud_check = BeneficiaryFraudCheckFactory(
            status=FraudCheckStatus.OK,
            type=FraudCheckType.UBBLE,
            dateCreated=datetime.datetime(2021, 12, 31),
            idPicturesStored=None,
        )
        second_fraud_check = BeneficiaryFraudCheckFactory(
            status=FraudCheckStatus.OK,
            type=FraudCheckType.UBBLE,
            dateCreated=datetime.datetime(2022, 1, 1),
            idPicturesStored=None,
        )

        expected_length = 1

        # When
        first_call_result = get_fraud_check_to_archive(start_date, end_date, None, limit)
        second_call_result = get_fraud_check_to_archive(start_date, end_date, None, limit, offset)

        # Then
        assert len(first_call_result) == expected_length
        first_call_fraud_check = first_call_result[0]
        assert first_call_fraud_check.dateCreated == datetime.datetime(2021, 12, 31)
        assert first_call_fraud_check.id == first_fraud_check.id
        assert len(second_call_result) == expected_length
        second_call_fraud_check = second_call_result[0]
        assert second_call_fraud_check.dateCreated == datetime.datetime(2022, 1, 1)
        assert second_call_fraud_check.id == second_fraud_check.id
