from domain.offerer.offerer import Offerer
from models import Offerer as OffererSQLEntity

def to_domain(offerer_sql_entity: OffererSQLEntity) -> Offerer:
    return Offerer(siren=offerer_sql_entity.siren)
