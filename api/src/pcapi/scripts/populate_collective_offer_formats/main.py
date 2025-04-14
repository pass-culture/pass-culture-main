from pcapi.app import app
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


def populate() -> None:
    collective_offers = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.formats == None
    ).all()
    collective_offer_templates = educational_models.CollectiveOfferTemplate.query.filter(
        educational_models.CollectiveOfferTemplate.formats == None
    ).all()

    offerer_addresses = offerers_models.OffererAddress.query.filter(
        offerers_models.OffererAddress.offererId == None
    ).all()

    for offerer_address in offerer_addresses:
        venues = offerers_models.Venue.query.filter(offerers_models.Venue.offererAddressId == offerer_address.id).all()
        venue = venues[0]
        offerer_address.offererId = venue.managingOffererId
        db.session.add(offerer_address)

    for collective_offer in collective_offers:
        collective_offer.formats = [EacFormat.CONCERT]
        db.session.add(collective_offer)

    for collective_offer_template in collective_offer_templates:
        collective_offer_template.formats = [EacFormat.CONCERT]
        db.session.add(collective_offer_template)

    db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    populate()
