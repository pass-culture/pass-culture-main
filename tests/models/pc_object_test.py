from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import Column, DateTime, Integer, Float

from models import PcObject, Offer, User
from models import ThingType
from models.api_errors import DecimalCastError, DateTimeCastError
from models.db import Model
from models.pc_object import serialize
from tests.test_utils import create_stock


class TimeInterval(PcObject, Model):
    start = Column(DateTime)
    end = Column(DateTime)


class TestPcObject(PcObject, Model):
    integer_attribute = Column(Integer, nullable=True)
    float_attribute = Column(Float, nullable=True)
    date_attribute = Column(DateTime, nullable=True)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()


@pytest.mark.standalone
class SerializeTest:
    def test_on_datetime_list_returns_string_with_date_in_ISO_8601_list(self):
        # Given
        offer = Offer()
        offer.stocks = [
            create_stock(offer=offer,
                         beginning_datetime=now,
                         end_datetime=now + timedelta(hours=3))
        ]

        # When
        serialized_list = serialize(offer.dateRange)

        # Then
        for datetime in serialized_list:
            self._assert_is_in_ISO_8601_format(datetime)

    def test_on_enum_returns_dict_with_enum_value(self):
        # Given
        enum = ThingType.JEUX

        # When
        serialized_enum = serialize(enum)

        # Then
        assert serialized_enum == {
            'conditionalFields': [],
            'proLabel': 'Jeux (support physique)',
            'appLabel': 'Support physique',
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': 'Jouer',
            'description': 'Résoudre l’énigme d’un jeu de piste dans votre ville ? '
                           'Jouer en ligne entre amis ? '
                           'Découvrir cet univers étrange avec une manette ?'
        }

    def _assert_is_in_ISO_8601_format(self, date_text):
        try:
            format_string = '%Y-%m-%dT%H:%M:%S.%fZ'
            datetime.strptime(date_text, format_string)
        except TypeError:
            assert False, 'La date doit être un str'
        except ValueError:
            assert False, 'La date doit être au format ISO 8601 %Y-%m-%dT%H:%M:%S.%fZ'


@pytest.mark.standalone
class PopulateFromDictTest:
    def test_user_string_fields_are_stripped_of_whitespace(self):
        # given
        user_data = {
            'email': '   test@example.com',
            'firstName': 'John   ',
            'lastName': None,
            'postalCode': '   93100   ',
            'publicName': ''
        }

        # when
        user = User(from_dict=user_data)

        # then
        assert user.email == 'test@example.com'
        assert user.firstName == 'John'
        assert user.lastName == None
        assert user.postalCode == '93100'
        assert user.publicName == ''

    def test_on_pc_object_for_sql_integer_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'integer_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_pc_object.populate_from_dict(data)
        assert errors.value.errors['integer_attribute'] == ["Invalid value for integer_attribute (integer): 'yolo'"]

    def test_on_pc_object_for_sql_integer_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'integer_attribute': '12.9'}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.integer_attribute == Decimal('12.9')

    def test_on_pc_object_for_sql_float_value_with_str_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'float_attribute': '12.9'}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.float_attribute == Decimal('12.9')

    def test_on_pc_object_for_sql_integer_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'integer_attribute': 12.9}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.integer_attribute == 12.9

    def test_on_pc_object_for_sql_float_value_with_12dot9_sets_attribute_to_12dot9(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'float_attribute': 12.9}

        # When
        test_pc_object.populate_from_dict(data)

        # Then
        assert test_pc_object.float_attribute == 12.9

    def test_on_pc_object_for_sql_float_value_with_string_raises_decimal_cast_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'float_attribute': 'yolo'}

        # When
        with pytest.raises(DecimalCastError) as errors:
            test_pc_object.populate_from_dict(data)
        assert errors.value.errors['float_attribute'] == ["Invalid value for float_attribute (float): 'yolo'"]

    def test_on_pc_object_for_sql_datetime_value_in_wrong_format_returns_400_and_affected_key_in_error(self):
        # Given
        test_pc_object = TestPcObject()
        data = {'date_attribute': {'date_attribute': None}}

        # When
        with pytest.raises(DateTimeCastError) as errors:
            test_pc_object.populate_from_dict(data)

        # Then
        assert errors.value.errors['date_attribute'] == [
            "Invalid value for date_attribute (datetime): {'date_attribute': None}"]

    def test_deserializes_datetimes(self):
        # given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': '2018-04-04T20:10:30.456Z'}

        # when
        time_interval.populate_from_dict(raw_data)

        # then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35, 123000)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30, 456000)

    def test_deserializes_datetimes_without_milliseconds(self):
        # given
        raw_data = {'start': '2018-03-03T15:25:35', 'end': '2018-04-04T20:10:30'}

        # when
        time_interval.populate_from_dict(raw_data)

        # then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_deserializes_datetimes_without_milliseconds_with_trailing_z(self):
        # given
        raw_data = {'start': '2018-03-03T15:25:35Z', 'end': '2018-04-04T20:10:30Z'}

        # when
        time_interval.populate_from_dict(raw_data)

        # then
        assert time_interval.start == datetime(2018, 3, 3, 15, 25, 35)
        assert time_interval.end == datetime(2018, 4, 4, 20, 10, 30)

    def test_raises_type_error_if_raw_date_is_invalid(self):
        # given
        raw_data = {'start': '2018-03-03T15:25:35.123Z', 'end': 'abcdef'}

        # when
        with pytest.raises(DateTimeCastError) as errors:
            time_interval.populate_from_dict(raw_data)

        # then
        assert errors.value.errors['end'] == ["Invalid value for end (datetime): 'abcdef'"]
