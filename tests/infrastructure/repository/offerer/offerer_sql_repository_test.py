from pcapi.infrastructure.repository.offerer import offerer_domain_converter
from pcapi.infrastructure.repository.offerer.offerer_sql_repository import OffererSQLRepository
from pcapi.repository import repository
import pytest
from pcapi.model_creators.generic_creators import create_offerer

class OffererSQLRepositoryTest:
    def setup_method(self):
        self.offerer_sql_repository = OffererSQLRepository()

    @pytest.mark.usefixtures("db_session")
    def test_returns_an_offerer_when_offerer_with_siren_is_found(self, app):
        # given
        siren = "123456789"
        offerer = create_offerer(siren=siren)
        repository.save(offerer)

        expected_offerer = offerer_domain_converter.to_domain(offerer)

        # when
        offerer = self.offerer_sql_repository.find_by_siren(siren)

        # then
        assert offerer.siren == expected_offerer.siren
        assert offerer.id == expected_offerer.id

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_an_offerer_when_no_offerer_was_found(self, app):
        # given
        siren = "123456789"
        offerer = create_offerer(siren=siren)
        repository.save(offerer)

        expected_offerer = offerer_domain_converter.to_domain(offerer)

        # when
        offerer = self.offerer_sql_repository.find_by_siren(siren="987654321")

        # then
        assert offerer is None
