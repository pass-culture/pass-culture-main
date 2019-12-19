from decimal import Decimal

from models import PcObject
from models.db import db
from scripts.update_venue_with_sirene_data import update_venue_with_sirene_data
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue


class UpdateVenueWithSireneDataTest:
    @clean_database
    def test_update_venue_with_sirene_data_changes_given_venue_information(self, app):
        # Given
        sirene_data = {
            "etablissement": {
                "id": 1,
                "siren": "123456789",
                "siret": "12345678900001",
                "l1_normalisee": 'Nouveau nom',
                "l4_normalisee": '1 rue Nouvelle Adresse',
                "l1_declaree": 'Pas le bon nouveau nom',
                "code_postal": "29001",
                "libelle_commune": "Nouvelleville",
                "longitude": "-4.48",
                "latitude": "48.39",
            }
        }
        offerer = create_offerer("123456789")
        venue = create_venue(
            offerer,
            siret='12345678900002',
            address='1 rue Vieille Adresse',
            name='Vieux nom',
            city='Vieilleville',
            latitude='48.863',
            longitude='2.36',
            postal_code='75001')
        PcObject.save(venue)

        # When
        update_venue_with_sirene_data(sirene_data, '12345678900002')

        # Then
        db.session.refresh(venue)
        assert venue.siret == "12345678900001"
        assert venue.address == '1 rue Nouvelle Adresse'
        assert venue.name == 'Nouveau nom'
        assert venue.city == "Nouvelleville"
        assert venue.latitude == Decimal('48.39')
        assert venue.longitude == Decimal('-4.48')
        assert venue.postalCode == "29001"

    @clean_database
    def test_update_offerer_with_sirene_data_keeps_old_information_when_not_given_by_api(self, app):
        # Given
        sirene_data = {
            "etablissement": {
                "id": 1,
                "siren": "123456789",
                "siret": "12345678900001",
                "l1_normalisee": 'Nouveau nom',
                "l4_normalisee": '1 rue Nouvelle Adresse',
                "l1_declaree": 'Pas le bon nouveau nom',
                "code_postal": "29001",
                "longitude": "-4.48",
                "latitude": "48.39",
            }
        }
        offerer = create_offerer("123456789")
        venue = create_venue(
            offerer,
            siret='12345678900002',
            address='1 rue Vieille Adresse',
            name='Vieux nom',
            city='Vieilleville',
            latitude='48.863',
            longitude='2.36',
            postal_code='75001')
        PcObject.save(venue)

        # When
        update_venue_with_sirene_data(sirene_data, old_siret='12345678900002')

        # Then
        db.session.refresh(venue)
        assert venue.siret == "12345678900001"
        assert venue.address == '1 rue Nouvelle Adresse'
        assert venue.name == 'Nouveau nom'
        assert venue.city == "Vieilleville"
        assert venue.latitude == Decimal('48.39')
        assert venue.longitude == Decimal('-4.48')
        assert venue.postalCode == "29001"
