import pytest

from models import PcObject
from models.db import db
from scripts.update_offerer_with_sirene_data import parse_sirene_data, update_offerer_with_sirene_data
from tests.conftest import clean_database
from tests.test_utils import create_offerer


@pytest.mark.standalone
def test_parse_sirene_data_returns_dictionary_with_model_keys():
    # given
    sirene_data = {
        "siege_social": {
            "l1_normalisee": 'Nom',
            "l4_normalisee": '1 rue Test',
            "libelle_commune": 'Testville',
            "latitude": '48.853',
            "longitude": '2.35',
            "code_postal": '75000',
            "siren": '123456789'
        }
    }

    # when
    parsed_data = parse_sirene_data(sirene_data)

    # then
    assert parsed_data == {
        "name": 'Nom',
        "address": '1 rue Test',
        "city": 'Testville',
        "latitude": '48.853',
        "longitude": '2.35',
        "postalCode": '75000',
        "siren": "123456789"
    }


@pytest.mark.standalone
def test_parse_sirene_data_returns_dictionary_with_model_keys_even_with_missing_information():
    # given
    sirene_data = {
        "siege_social": {
            "l1_normalisee": 'Nom',
            "libelle_commune": 'Testville',
            "latitude": '48.853',
            "longitude": '2.35',
            "code_postal": '75000',
            "siren": '123456789'
        }
    }

    # when
    parsed_data = parse_sirene_data(sirene_data)

    # then
    assert parsed_data == {
        "name": 'Nom',
        "city": 'Testville',
        "latitude": '48.853',
        "longitude": '2.35',
        "postalCode": '75000',
        "siren": "123456789"
    }


@pytest.mark.standalone
@clean_database
def test_update_offerer_with_sirene_data_changes_given_offerer_information(app):
    # Given
    sirene_data = {
        "siege_social": {
            "l1_normalisee": 'Nom',
            "l4_normalisee": '1 rue Test',
            "libelle_commune": 'Testville',
            "latitude": '48.853',
            "longitude": '2.35',
            "code_postal": '75000',
            "siren": '123456789'
        }
    }
    offerer = create_offerer(
        siren='123456789',
        address='1 rue Vieille Adresse',
        name='Vieux nom',
        city='Vieilleville',
        latitude='48.863',
        longitude='2.36',
        postal_code='75001')
    PcObject.check_and_save(offerer)

    # When
    update_offerer_with_sirene_data(sirene_data)

    # Then
    db.session.refresh(offerer)
    assert offerer.siren == '123456789'
    assert offerer.address == '1 rue Test'
    assert offerer.name == 'Nom'
    assert offerer.city == 'Testville'
    assert offerer.latitude == '48.853'
    assert offerer.longitude == '2.35'
    assert offerer.postalCode == '75000'


@pytest.mark.standalone
@clean_database
def test_update_offerer_with_sirene_data_keeps_old_information_when_not_given_by_api(app):
    # Given
    sirene_data = {
        "siege_social": {
            "l4_normalisee": '1 rue Test',
            "libelle_commune": 'Testville',
            "latitude": '48.853',
            "longitude": '2.35',
            "code_postal": '75000',
            "siren": '123456789'
        }
    }
    offerer = create_offerer(
        siren='123456789',
        address='1 rue Vieille Adresse',
        name='Vieux nom',
        city='Vieilleville',
        latitude='48.863',
        longitude='2.36',
        postal_code='75001')
    PcObject.check_and_save(offerer)

    # When
    update_offerer_with_sirene_data(sirene_data)

    # Then
    db.session.refresh(offerer)
    assert offerer.siren == '123456789'
    assert offerer.address == '1 rue Test'
    assert offerer.name == 'Vieux nom'
    assert offerer.city == 'Testville'
    assert offerer.latitude == '48.853'
    assert offerer.longitude == '2.35'
    assert offerer.postalCode == '75000'
