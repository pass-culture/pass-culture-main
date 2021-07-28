from collections import OrderedDict
from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offerers.factories import VirtualVenueTypeFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.offers.factories import VirtualVenueFactory
from pcapi.core.users.factories import ProFactory
from pcapi.core.users.models import Token
from pcapi.core.users.models import User
from pcapi.models import UserOfferer
from pcapi.routes.serialization.users import ProUserCreationBodyModel
from pcapi.scripts.offerer.import_offerer_from_csv import create_offerer_from_csv
from pcapi.scripts.offerer.import_offerer_from_csv import create_user_model_from_csv
from pcapi.scripts.offerer.import_offerer_from_csv import create_venue_from_csv
from pcapi.scripts.offerer.import_offerer_from_csv import import_new_offerer_from_csv


class CreateOffererFromCSVTest:
    def test_map_an_offerer_from_ordered_dict(self):
        # given
        csv_row = OrderedDict(
            [
                ("SIREN", "178281689"),
                ("City", "MALAKOFF"),
                ("nom_structure", "Ma structure"),
                ("adresse", "152 AV LAPIN, 92240"),
                ("Street Address", "152 AV LAPIN"),
                ("code_postal", "92240"),
            ]
        )

        # when
        offerer = create_offerer_from_csv(csv_row)

        # then
        assert isinstance(offerer, Offerer)
        assert offerer.siren == "178281689"
        assert offerer.city == "MALAKOFF"
        assert offerer.name == "Ma structure"
        assert offerer.postalCode == "92240"
        assert offerer.address == "152 AV LAPIN"

    def test_use_Postal_code_when_sirene_postal_code_is_not_set(self):
        # given
        csv_row = OrderedDict(
            [
                ("SIREN", "178281689"),
                ("City", "MALAKOFF"),
                ("nom_structure", "Ma structure"),
                ("adresse", "152 AV LAPIN, 92240"),
                ("Street Address", "152 AV LAPIN"),
                ("code_postal", ""),
                ("Postal Code", "92240"),
            ]
        )

        # when
        offerer = create_offerer_from_csv(csv_row)

        # then
        assert isinstance(offerer, Offerer)
        assert offerer.siren == "178281689"
        assert offerer.city == "MALAKOFF"
        assert offerer.name == "Ma structure"
        assert offerer.postalCode == "92240"
        assert offerer.address == "152 AV LAPIN"

    def test_use_Name_when_nom_structure_is_not_set(self):
        # given
        csv_row = OrderedDict(
            [
                ("SIREN", "178281689"),
                ("City", "MALAKOFF"),
                ("nom_structure", ""),
                ("Name", "Ma structure"),
                ("adresse", "152 AV LAPIN, 92240"),
                ("Street Address", "152 AV LAPIN"),
                ("code_postal", ""),
                ("Postal Code", "92240"),
            ]
        )

        # when
        offerer = create_offerer_from_csv(csv_row)

        # then
        assert isinstance(offerer, Offerer)
        assert offerer.siren == "178281689"
        assert offerer.city == "MALAKOFF"
        assert offerer.name == "Ma structure"
        assert offerer.postalCode == "92240"
        assert offerer.address == "152 AV LAPIN"


class CreateVenueFromCSVTest:
    @pytest.mark.usefixtures("db_session")
    def test_map_a_venue_from_ordered_dict(self, app):
        # given
        offerer = OffererFactory(siren="828768000")
        VenueTypeFactory(label="Librairie")
        csv_row = OrderedDict(
            [
                ("Street Address", "46 AV DE LA ROUE"),
                ("adresse", "46 AV DE LA ROUE, 92240"),
                ("code_postal", "92240"),
                ("commune", "MALAKOFF"),
                ("Département", "92"),
                ("SIRET", "82876800012119"),
                ("nom_lieu", "Not_found"),
                ("geoloc", "[45.847218, 12.360398]"),
                ("Catégorie", "Librairie"),
                ("Email", "librairie.fictive@example.com"),
            ]
        )

        # when
        venue = create_venue_from_csv(csv_row, offerer)

        # then
        assert isinstance(venue, Venue)
        assert venue.address == "46 AV DE LA ROUE"
        assert venue.postalCode == "92240"
        assert venue.city == "MALAKOFF"
        assert venue.departementCode == "92"
        assert venue.siret == "82876800012119"
        assert venue.name == "Not_found"
        assert venue.publicName == "Not_found"
        assert venue.latitude == 45.847218
        assert venue.longitude == 12.360398
        assert venue.bookingEmail == "librairie.fictive@example.com"

    @pytest.mark.usefixtures("db_session")
    def test_use_Postal_code_when_no_SIRENE_code_postal(self, app):
        # given
        offerer = OffererFactory(siren="828768000")
        VenueTypeFactory(label="Librairie")
        csv_row = OrderedDict(
            [
                ("Street Address", "46 AV DE LA ROUE"),
                ("adresse", "46 AV DE LA ROUE, 92240"),
                ("code_postal", ""),
                ("Postal Code", "92240"),
                ("commune", "MALAKOFF"),
                ("Département", "92"),
                ("SIRET", "82876800012119"),
                ("nom_lieu", "Not_found"),
                ("geoloc", "[45.847218, 12.360398]"),
                ("Catégorie", "Librairie"),
                ("Email", "librairie.fictive@example.com"),
            ]
        )

        # when
        venue = create_venue_from_csv(csv_row, offerer)

        # then
        assert isinstance(venue, Venue)
        assert venue.postalCode == "92240"

    @pytest.mark.usefixtures("db_session")
    def test_should_have_a_venue_type(self, app):
        # given
        offerer = OffererFactory(siren="828768000")
        VenueTypeFactory(label="Librairie")
        csv_row = OrderedDict(
            [
                ("Street Address", "46 AV DE LA ROUE"),
                ("Email", "librairie.fictive@example.com"),
                ("adresse", "46 AV DE LA ROUE, 92240"),
                ("code_postal", "92240"),
                ("commune", "MALAKOFF"),
                ("Département", "92"),
                ("nom_lieu", ""),
                ("SIRET", "76800828012119.0"),
                ("geoloc", "[45.847218, 12.360398]"),
                ("Catégorie", "Librairie"),
                ("nom_structure", "Ma structure"),
            ]
        )

        # when
        venue = create_venue_from_csv(csv_row, offerer)

        # then
        assert venue.venueType is not None
        assert venue.venueType.label == "Librairie"

    @pytest.mark.usefixtures("db_session")
    def test_create_venue_name_when_information_missing(self, app):
        # given
        offerer = OffererFactory(siren="828768000")
        VenueTypeFactory(label="Librairie")
        VenueFactory()
        csv_row = OrderedDict(
            [
                ("Street Address", "46 AV DE LA ROUE"),
                ("Email", "librairie.fictive@example.com"),
                ("adresse", "46 AV DE LA ROUE, 92240"),
                ("code_postal", "92240"),
                ("commune", "MALAKOFF"),
                ("Département", "92"),
                ("nom_lieu", ""),
                ("SIRET", "76800828012119.0"),
                ("geoloc", "[45.847218, 12.360398]"),
                ("Catégorie", "Librairie"),
                ("nom_structure", "Ma structure"),
            ]
        )

        # when
        venue = create_venue_from_csv(csv_row, offerer)

        # then
        assert venue.name == "Lieu 1 - Ma structure"

    @pytest.mark.usefixtures("db_session")
    def test_when_geolocation_is_missing(self, app):
        # given
        offerer = OffererFactory(siren="828768000")
        VenueTypeFactory(label="Librairie")
        VenueFactory()
        csv_row = OrderedDict(
            [
                ("Street Address", "46 AV DE LA ROUE"),
                ("Email", "librairie.fictive@example.com"),
                ("adresse", "46 AV DE LA ROUE, 92240"),
                ("code_postal", "92240"),
                ("commune", "MALAKOFF"),
                ("Département", "92"),
                ("nom_lieu", ""),
                ("SIRET", "76800828012119.0"),
                ("geoloc", ""),
                ("Catégorie", "Librairie"),
                ("nom_structure", "Ma structure"),
            ]
        )

        # when
        venue = create_venue_from_csv(csv_row, offerer)

        # then
        assert venue.latitude is None
        assert venue.longitude is None


class CreateProUserFromCSVTest:
    def test_map_a_creation_model_from_csv(self):
        # Given
        csv_row = OrderedDict(
            [
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("code_postal", "44016"),
                ("City", "NANTES CEDEX 1"),
            ]
        )

        # When
        pro_model = create_user_model_from_csv(csv_row)

        # Then
        assert isinstance(pro_model, ProUserCreationBodyModel)
        assert pro_model.email == "librairie.fictive@example.com"
        assert pro_model.first_name == "Anthony"
        assert pro_model.last_name == "Champion"
        assert pro_model.public_name == "Anthony Champion"
        assert pro_model.phone_number == "0102345678"
        assert pro_model.postal_code == "44016"
        assert pro_model.city == "NANTES CEDEX 1"

    def test_fill_missing_phone_with_fake_number(self):
        # Given
        csv_row = OrderedDict(
            [
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", ""),
                ("Postal Code", "44016.0"),
                ("code_postal", "44016"),
                ("City", "NANTES CEDEX 1"),
            ]
        )

        # When
        pro_model = create_user_model_from_csv(csv_row)

        # Then
        assert isinstance(pro_model, ProUserCreationBodyModel)
        assert pro_model.phone_number == "0000000000"

    def test_use_Postal_code_when_sirene_postal_code_is_not_set(self):
        # Given
        csv_row = OrderedDict(
            [
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("code_postal", ""),
                ("Postal Code", "44016"),
                ("City", "NANTES CEDEX 1"),
            ]
        )

        # When
        pro_model = create_user_model_from_csv(csv_row)

        # Then
        assert pro_model.postal_code == "44016"


class CreateAnEntireOffererFromCSVRowTest:
    @freeze_time("2021-05-04 00:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_created_pro_is_activated_with_90_days_reset_password(self, app):
        # Given
        VirtualVenueTypeFactory()
        VenueTypeFactory(label="Librairie")
        offerer = OffererFactory(siren="636710003")
        VenueFactory(managingOfferer=offerer)
        VirtualVenueFactory(managingOfferer=offerer)
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", "63671000326012"),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        user = User.query.first()
        token = Token.query.first()
        assert not user.validationToken
        assert user.resetPasswordToken is None
        assert token.user == user
        assert token.expirationDate == datetime(2021, 8, 2)

    @pytest.mark.usefixtures("db_session")
    def test_when_is_a_new_offerer(self, app):
        # Given
        VenueTypeFactory(label="Librairie")
        VirtualVenueTypeFactory()
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", "63671000326012"),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert User.query.count() == 1
        assert Offerer.query.count() == 1
        assert UserOfferer.query.count() == 1
        assert Venue.query.count() == 2

    @pytest.mark.usefixtures("db_session")
    def test_when_is_already_existing_offerer(self, app):
        # Given
        VirtualVenueTypeFactory()
        VenueTypeFactory(label="Librairie")
        offerer = OffererFactory(siren="636710003")
        VenueFactory(managingOfferer=offerer)
        VirtualVenueFactory(managingOfferer=offerer)
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", "63671000326012"),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert Offerer.query.count() == 1
        assert Venue.query.count() == 3

    @pytest.mark.usefixtures("db_session")
    def test_when_no_siret_for_venue_creation(self, app):
        # Given
        VirtualVenueTypeFactory()
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", ""),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert User.query.count() == 1
        assert Offerer.query.count() == 1
        assert UserOfferer.query.count() == 1
        assert Venue.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_when_user_already_exists(self, app):
        # Given
        VirtualVenueTypeFactory()
        ProFactory(email="librairie.fictive@example.com")
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", ""),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert User.query.count() == 1
        assert Offerer.query.count() == 1
        assert UserOfferer.query.count() == 1
        assert Venue.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_ignore_when_user_has_no_postal(self, app):
        # Given
        VirtualVenueTypeFactory()
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", ""),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", "63671000326012.0"),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", ""),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert User.query.count() == 0
        assert Offerer.query.count() == 0
        assert UserOfferer.query.count() == 0
        assert Venue.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_when_siret_wrong(self, app):
        # Given
        VenueTypeFactory(label="Librairie")
        VirtualVenueTypeFactory()
        ProFactory(email="librairie.fictive@example.com")
        csv_row = OrderedDict(
            [
                ("", "104"),
                ("Company ID", "1099515212"),
                ("Email", "librairie.fictive@example.com"),
                ("First Name", "Anthony"),
                ("Last Name", "Champion"),
                ("Phone", "01 02 34 56 78"),
                ("Postal Code", "44016.0"),
                ("City", "NANTES CEDEX 1"),
                ("SIRET", "1"),
                ("SIREN", "636710003"),
                ("Département", "44"),
                ("Name", "Fictive"),
                ("Catégorie", "Librairie"),
                ("Street Address", "45 RUE DU JOYEUX LURON"),
                ("nom_structure", "SARL"),
                ("adresse", "45 RUE DU JOYEUX LURON, 44000"),
                ("code_postal", "44000"),
                ("commune", "NANTES"),
                ("geoloc", "[44.455621, -2.546101]"),
                ("nom_lieu", "Ma librairie"),
                ("siege_social", "45 RUE DU JOYEUX LURON, 44000"),
                ("lieu_deja_inscrit", "0"),
                ("structure_deja_inscrite", "0"),
            ]
        )

        # When
        import_new_offerer_from_csv(csv_row)

        # Then
        assert User.query.count() == 1
        assert Offerer.query.count() == 1
        assert UserOfferer.query.count() == 1
        assert Venue.query.count() == 1
