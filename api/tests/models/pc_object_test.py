from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

import pytest
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID

from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_stock
from pcapi.models import Offer
from pcapi.models.api_errors import DateTimeCastError
from pcapi.models.api_errors import DecimalCastError
from pcapi.models.api_errors import UuidCastError
from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject
from pcapi.routes.serialization import serialize
from pcapi.utils.human_ids import NonDehumanizableId
from pcapi.utils.human_ids import dehumanize


class TimeInterval(PcObject, Model):
    start = Column(DateTime)
    end = Column(DateTime)


class TestPcObject(PcObject, Model):
    date_attribute = Column(DateTime, nullable=True)
    entityId = Column(BigInteger, nullable=True)
    float_attribute = Column(Float, nullable=True)
    integer_attribute = Column(Integer, nullable=True)
    uuid_attribute = Column(UUID(as_uuid=True), nullable=True)
    uuidId = Column(UUID(as_uuid=True), nullable=True)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()


def test_equality():
    assert Offer(id=1) == Offer(id=1)
    assert Offer(id=1) != Offer(id=2)
    assert Offer(id=1) != User(id=1)
    assert Offer(id=1) != 1


class SerializeTest:
    def test_on_datetime_list_returns_string_with_date_in_ISO_8601_list(self):
        # Given
        offer = Offer()
        offer.subcategoryId = "LIVRE_PAPIER"
        offer.stocks = [create_stock(beginning_datetime=now, offer=offer)]

        # When
        serialized_list = serialize(offer.dateRange)

        # Then
        for dt in serialized_list:  # pylint: disable=not-an-iterable
            self._assert_is_in_ISO_8601_format(dt)

    def test_on_enum_returns_dict_with_enum_value(self):
        # Given
        class EnumTest(Enum):
            TEST = {"toto": "tata", "is_toto": False, "toto_list": ["toto", "tata"]}

        enum = EnumTest.TEST

        # When
        serialized_enum = serialize(enum)

        # Then
        assert serialized_enum == {"toto": "tata", "is_toto": False, "toto_list": ["toto", "tata"]}

    def _assert_is_in_ISO_8601_format(self, date_text):
        try:
            format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
            datetime.strptime(date_text, format_string)
        except TypeError:
            assert False, "La date doit être un str"
        except ValueError:
            assert False, "La date doit être au format ISO 8601 %Y-%m-%dT%H:%M:%S.%fZ"


class PopulateFromDictTest:
    def test_user_string_fields_are_stripped_of_whitespace(self):
        # Given
        user_data = {
            "email": "   test@example.com",
            "firstName": "John   ",
            "lastName": None,
            "postalCode": "   93100   ",
            "publicName": "",
        }

        # When
        user = User(from_dict=user_data)

        # Then
        assert user.email == "test@example.com"
        assert user.firstName == "John"
        assert user.lastName == None
        assert user.postalCode == "93100"
        assert user.publicName == ""

    def test_on_pc_object_for_sql_integer_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"integer_attribute": "yolo"}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_pc_object.populate_from_dict(data)

        # Then
        assert errors.value.errors["integer_attribute"] == ["Invalid value for integer_attribute (integer): 'yolo'"]

    def test_on_pc_object_for_sql_integer_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"integer_attribute": "12.9"}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.integer_attribute == Decimal("12.9")

    def test_on_pc_object_for_sql_float_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"float_attribute": "12.9"}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.float_attribute == Decimal("12.9")

    def test_on_pc_object_for_sql_integer_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"integer_attribute": 12}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.integer_attribute == 12

    def test_on_pc_object_for_sql_float_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"float_attribute": 12.9}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.float_attribute == 12.9

    def test_on_pc_object_for_valid_sql_uuid_value(self):
        # Given
        test_pc_object = TestPcObject()
        uuid_attribute = str(uuid.uuid4())
        data = {"uuid_attribute": uuid_attribute}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.uuid_attribute == uuid_attribute

    def test_on_pc_object_for_valid_sql_uuid_value_with_key_finishing_by_Id(self):
        # Given
        test_pc_object = TestPcObject()
        uuid_id = str(uuid.uuid4())
        data = {"uuidId": uuid_id}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.uuidId == uuid_id

    def test_on_pc_object_for_valid_sql_humanize_id_value_with_key_finishing_by_Id(self):
        # Given
        test_pc_object = TestPcObject()
        humanized_entity_id = "AE"
        data = {"entityId": humanized_entity_id}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.entityId == dehumanize(humanized_entity_id)

    def test_on_pc_object_for_sql_float_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"float_attribute": "yolo"}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_pc_object.populate_from_dict(data)

        # Then
        assert errors.value.errors["float_attribute"] == ["Invalid value for float_attribute (float): 'yolo'"]

    def test_on_pc_object_for_sql_datetime_value_in_wrong_format_returns_400_and_affected_key_in_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"date_attribute": {"date_attribute": None}}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            test_pc_object.populate_from_dict(data)

        # Then
        assert errors.value.errors["date_attribute"] == [
            "Invalid value for date_attribute (datetime): {'date_attribute': None}"
        ]

    def test_deserializes_datetimes(self):
        # Given
        raw_data = {"start": "2018-03-03T15:25:35.123Z", "end": "2018-04-04T20:10:30.456Z"}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)

    def test_deserializes_datetimes_without_milliseconds(self):
        # Given
        raw_data = {"start": "2018-03-03T15:25:35", "end": "2018-04-04T20:10:30"}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_deserializes_datetimes_without_milliseconds_with_trailing_z(self):
        # Given
        raw_data = {"start": "2018-03-03T15:25:35Z", "end": "2018-04-04T20:10:30Z"}

        # When
        time_interval.populate_from_dict(raw_data)

        # Then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_raises_type_error_if_raw_date_is_invalid(self):
        # Given
        raw_data = {"start": "2018-03-03T15:25:35.123Z", "end": "abcdef"}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            time_interval.populate_from_dict(raw_data)

        # Then
        assert errors.value.errors["end"] == ["Invalid value for end (datetime): 'abcdef'"]

    def test_raises_type_error_if_raw_uuid_is_invalid(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"uuidId": "foo"}

        # When
        with pytest.raises(UuidCastError) as errors:
            test_pc_object.populate_from_dict(data)

        # Then
        assert errors.value.errors["uuidId"] == ["Invalid value for uuidId (uuid): 'foo'"]

    def test_raises_type_error_if_raw_humanized_id_is_invalid(self):
        # Given
        test_pc_object = TestPcObject()
        data = {"entityId": "12R-..2foo"}

        # When
        with pytest.raises(NonDehumanizableId):
            test_pc_object.populate_from_dict(data)
