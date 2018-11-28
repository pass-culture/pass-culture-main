import pytest

from models import ApiErrors
from validation.exports import check_get_venues_params


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_date(app):
    # given
    not_valid_date = {}
    not_valid_date['from_date'] = '12/52-0001'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_date)

    # then
    assert errors.value.errors['date_format'] == ['to_date and from_date are of type yyyy-mm-dd']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_dpt_list(app):
    # given
    not_valid_dpt_list = {}
    not_valid_dpt_list['dpt'] = ['93', '17', 'Paris']

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_dpt_list)

    # then
    assert errors.value.errors['dpt'] == ['dpt is of type xx or xxx (2 or 3 digits), or 2A, or 2B']


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
        ['zip_codes is of type xxxxx (5 digits, ex: 78140 ou 2a000)']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_has_validated_offerer_param(app):
    # given
    not_valid_has_validated_offerer_param = {}
    not_valid_has_validated_offerer_param['has_validated_offerer'] = 'oui'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_has_validated_offerer_param)

    # then
    assert errors.value.errors['has_validated_offerer'] == ['has_validated_offerer is a boolean, it accepts True or False']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_has_siret_param(app):
    # given
    not_valid_has_siret_param = {}
    not_valid_has_siret_param['has_siret'] = "peut-être"
    
    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_has_siret_param)

    # then
    assert errors.value.errors['has_siret'] == ['has_siret is a boolean, it accepts True or False']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_is_virtual_param(app):
    # given
    not_valid_is_virtual_param = {}
    not_valid_is_virtual_param['is_virtual'] = "De type moderne"

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_is_virtual_param)

    # then
    assert errors.value.errors['is_virtual'] == ['is_virtual is a boolean, it accepts True or False']


@pytest.mark.standalone
def test_check_get_venues_params_raises_api_error_if_not_valid_is_validated_param(app):
    # given
    not_valid_is_validated_param = {}
    not_valid_is_validated_param['is_validated'] = 'plein'

    # when
    with pytest.raises(ApiErrors) as errors:
        check_get_venues_params(not_valid_is_validated_param)

    # then
    assert errors.value.errors['is_validated'] == ['is_validated is a boolean, it accepts True or False']


# @pytest.mark.standalone
# def test_check_if_bool_dont_raises_error_with_true(app):
#     # given
#     trueBool = True

#     # when
#      # pytest.raises(ApiErrors) as errors:
#     try:
#         _check_if_bool(trueBool)
#     except ApiErrors:
#     # then
#         assert True


# @pytest.mark.standalone
# def test_check_if_bool_dont_raises_error_with_false(app):
#     # given
#     trueBool = False

#     # when
#     try:
#         _check_if_bool(trueBool)
#     except ApiErrors:

#     # then
#         assert True


@pytest.mark.standalone
def test_check_get_venues_params_does_not_raise_api_error_if_good_param(app):
    params = {}
    params['dpt'] = ['32', '35', '36']
    params['has_validated_offerer'] = True
    params['zip_codes'] = ['32000', '35000', '36000']
    params['from_date'] = '2018-05-30'
    params['to_date'] = '2018-12-1'
    params['has_siret'] = False
    params['is_virtual'] = True
    params['has_offer'] = 'VALID'
    
    # when
    try:
        check_get_venues_params(params)
    
    except ApiErrors:
        # Then
        assert True
