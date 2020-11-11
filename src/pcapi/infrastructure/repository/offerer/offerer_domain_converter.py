from pcapi.domain.offerer.offerer import Offerer
from pcapi.models import Offerer as OffererSQLEntity


def to_domain(offerer_sql_entity: OffererSQLEntity) -> Offerer:
    return Offerer(id=offerer_sql_entity.id, siren=offerer_sql_entity.siren)
