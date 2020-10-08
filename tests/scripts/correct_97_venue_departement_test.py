from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.scripts.correct_venue_departement import correct_venue_departement
import pytest
from pcapi.model_creators.generic_creators import create_venue, create_offerer


class CorrectVenueDepartementTest:
    @pytest.mark.usefixtures("db_session")
    def test_changes_departement_code_to_973_when_postal_code_97300(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='97300')
        repository.save(venue)
        db.engine.execute(f'''UPDATE venue SET "departementCode"='97' WHERE id={venue.id}''')
        db.session.refresh(venue)

        # When
        correct_venue_departement()

        # Then
        assert venue.departementCode == '973'

    @pytest.mark.usefixtures("db_session")
    def test_changes_departement_code_to_974_when_postal_code_97400(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='97400')
        repository.save(venue)
        db.engine.execute(f'''UPDATE venue SET "departementCode"='97' WHERE id={venue.id}''')
        db.session.refresh(venue)

        # When
        correct_venue_departement()

        # Then
        assert venue.departementCode == '974'

    @pytest.mark.usefixtures("db_session")
    def test_changes_departement_code_to_04_when_postal_code_04000(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='04000')
        repository.save(venue)
        db.engine.execute(f'''UPDATE venue SET "departementCode"='4' WHERE id={venue.id}''')
        db.session.refresh(venue)

        # When
        correct_venue_departement()

        # Then
        assert venue.departementCode == '04'

    @pytest.mark.usefixtures("db_session")
    def test_keeps_departement_code_when_well_set(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='06000')
        repository.save(venue)
        db.engine.execute(f'''UPDATE venue SET "departementCode"='06' WHERE id={venue.id}''')
        db.session.refresh(venue)

        # When
        correct_venue_departement()

        # Then
        assert venue.departementCode == '06'

    @pytest.mark.usefixtures("db_session")
    def test_does_nothing_if_is_virtual_venue(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code=None, departement_code=None, is_virtual=True, address=None, city=None, siret=None)
        repository.save(venue)

        # When
        correct_venue_departement()

        # Then
        assert venue.departementCode is None
