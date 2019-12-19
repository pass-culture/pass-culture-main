from models import PcObject
from models.db import db
from scripts.update_offerer_with_sirene_data import update_offerer_with_sirene_data
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer


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
        postal_code='75001')
    PcObject.save(offerer)

    # When
    update_offerer_with_sirene_data(sirene_data)

    # Then
    db.session.refresh(offerer)
    assert offerer.siren == '123456789'
    assert offerer.address == '1 rue Test'
    assert offerer.name == 'Nom'
    assert offerer.city == 'Testville'
    assert offerer.postalCode == '75000'


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
        postal_code='75001')
    PcObject.save(offerer)

    # When
    update_offerer_with_sirene_data(sirene_data)

    # Then
    db.session.refresh(offerer)
    assert offerer.siren == '123456789'
    assert offerer.address == '1 rue Test'
    assert offerer.name == 'Vieux nom'
    assert offerer.city == 'Testville'
    assert offerer.postalCode == '75000'
