from pcapi.core.offerers.models import Offerer as OffererSQLEntity
from pcapi.domain.offerer.offerer import Offerer


def to_domain(offerer_sql_entity: OffererSQLEntity) -> Offerer:
    return Offerer(id=offerer_sql_entity.id, siren=offerer_sql_entity.siren)
