import sqlalchemy.sql.functions as sqla_func

from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Venue
from pcapi.models import db


# FIXME (amarinier 24/03/2022): to delete when PC-13938 is merged


def rename_bu_not_matching_venue_public_name():
    print("Renaming bu with invalid name...")
    invalid_bu = (
        BusinessUnit.query.join(Venue, BusinessUnit.siret == Venue.siret)
        .filter(BusinessUnit.siret.isnot(None))
        .filter(BusinessUnit.name != sqla_func.coalesce(Venue.publicName, Venue.name))
        .all()
    )
    for bu in invalid_bu:
        bu_venue = Venue.query.filter(Venue.siret == bu.siret).first()
        print(f"Updating Business unit {bu.id} with siret {bu.siret}")
        if bu_venue:
            bu.name = bu_venue.publicName or bu_venue.name
            db.session.add(bu)
    print("Done : all bu have been renamed")
    db.session.commit()
