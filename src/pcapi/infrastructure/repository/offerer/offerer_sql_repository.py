from pcapi.core.offerers.models import Offerer as OffererSQLEntity
from pcapi.domain.offerer.offerer import Offerer
from pcapi.domain.offerer.offerer_repository import OffererRepository
from pcapi.infrastructure.repository.offerer import offerer_domain_converter


class OffererSQLRepository(OffererRepository):
    def find_by_siren(self, siren: str) -> Offerer:
        offerer_sql_entity = OffererSQLEntity.query.filter_by(siren=siren).first()
        if not offerer_sql_entity:
            return None
        return offerer_domain_converter.to_domain(offerer_sql_entity)
