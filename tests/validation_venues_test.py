import pytest

from models import ApiErrors
from validation.venues import validate_coordinates, check_get_venues_params



@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_latitude_is_not_a_decimal():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates('48°4565', None)

    # then
    assert e.value.errors['latitude'] == ['Format incorrect']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_longitude_is_not_a_decimal():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, '48°4565')

    # then
    assert e.value.errors['longitude'] == ['Format incorrect']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_for_both_latitude_and_longitude():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates('53°4565', '48°4565')

    # then
    assert e.value.errors['latitude'] == ['Format incorrect']
    assert e.value.errors['longitude'] == ['Format incorrect']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_latitude_is_greater_than_90():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(92.543, None)

    # then
    assert e.value.errors['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_latitude_is_lower_than_minus_90():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(-92.543, None)

    # then
    assert e.value.errors['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_longitude_is_greater_than_180():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, 182.66464)

    # then
    assert e.value.errors['longitude'] == ['La longitude doit être comprise entre -180.0 et +180.0']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_longitude_is_lower_than_minus_180():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(None, -182.66464)

    # then
    assert e.value.errors['longitude'] == ['La longitude doit être comprise entre -180.0 et +180.0']


@pytest.mark.standalone
def test_validate_coordinates_raises_an_api_errors_if_both_latitude_and_longitude_are_out_of_bounds():
    # when
    with pytest.raises(ApiErrors) as e:
        validate_coordinates(93.46, -182.66464)

    # then
    assert e.value.errors['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
    assert e.value.errors['longitude'] == ['La longitude doit être comprise entre -180.0 et +180.0']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_date(app):
    # given
    not_valid_date = {}
    not_valid_date['from_date'] = '12/52-0001'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_date)

    # then
    assert errors.value.errors['date_format'] == ['to_date ou from_date doit être de type aaaa-mm-jj']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_dpt_list(app):
    # given
    not_valid_dpt_list = {}
    not_valid_dpt_list['dpt'] = ['93', '17', 'Paris']

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_dpt_list)

    # then
    assert errors.value.errors['dpt'] == ['dpt doit être de type xx ou xxx (2 ou 3 chiffres), ou 2A, ou 2B)']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_zip_codes_list(app):
    # given
    not_valid_zip_codes_list = {}
    not_valid_zip_codes_list['zip_codes'] = ['69000', '13020', '78sang40RpZ']

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_zip_codes_list)

    # then
    assert errors.value.errors['zip_codes'] == \
        ['zip_codes de type xxxxx (5 chiffres, ex: 78140 ou 2a000)']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_has_validated_offerer_input(app):
    # given
    not_valid_has_validated_offerer_input = {}
    not_valid_has_validated_offerer_input['has_validated_offerer'] = 'oui'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_has_validated_offerer_input)

    # then
    assert errors.value.errors['has_validated_offerer'] == ['has_validated_offerer accepte YES ou NO']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_has_siret_input(app):
    # given
    not_valid_has_siret_input = {}
    not_valid_has_siret_input['has_siret'] = "peut-être"
    
    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_has_siret_input)

    # then
    assert errors.value.errors['has_siret'] == ['has_siret_input accepte YES ou NO']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_venue_type_input(app):
    # given
    not_valid_venue_type_input = {}
    not_valid_venue_type_input['venue_type'] = "De type moderne"

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_venue_type_input)

    # then
    assert errors.value.errors['venue_type'] == ['venue_type_input accepte NOT_VIRTUAL ou VIRTUAL']

@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_has_offer_input(app):
    # given
    not_valid_has_offer_input = {}
    not_valid_has_offer_input['has_offer'] = 'plein'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_has_offer_input)

    # then
    assert errors.value.errors['has_offer'] == ['has_offer_input accepte ALL ou VALID ou WITHOUT ou EXPIRED']

@pytest.mark.standalone
def test_check_get_venues_params_does_not_raise_api_error_if_good_param(app):
    params = {}
    params['dpt'] = ['32', '35', '36']
    params['has_validated_offerer'] = 'YES'
    params['zip_codes'] = ['32000', '35000', '36000']
    params['from_date'] = '2018-05-30'
    params['to_date'] = '2018-12-31'
    params['has_siret'] = 'YES'
    params['venue_type'] = 'VIRTUAL'
    params['has_offer'] = 'VALID'
    
    # when
    try:
        check_get_venues_params(params)
    
    except ApiErrors:
        # Then
        assert True
