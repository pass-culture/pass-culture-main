from collections import defaultdict

from pcapi.core.finance.models import BusinessUnit
from pcapi.repository import repository


def rename_invalid_business_unit():
    business_unit_list = BusinessUnit.query.filter(BusinessUnit.siret.is_(None)).all()
    business_units_by_offerer = defaultdict(lambda: [])
    for business_unit in business_unit_list:
        if len(business_unit.venues) > 0:
            offerer_id = business_unit.venues[0].managingOffererId
            business_units_by_offerer[offerer_id].append(business_unit)

    for offerer_id, offerer_business_unit_list in business_units_by_offerer.items():
        nb_business_unit = 0
        for business_unit in offerer_business_unit_list:
            nb_business_unit += 1
            business_unit.name = f"Point de remboursement #{nb_business_unit}"
            repository.save(business_unit)
