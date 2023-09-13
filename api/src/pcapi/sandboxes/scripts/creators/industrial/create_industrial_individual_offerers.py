import datetime
import logging

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


def create_industrial_individual_offerers() -> None:
    logger.info("create_industrial_individual_offerers")

    ae_tag = offerers_models.OffererTag.query.filter_by(name="auto-entrepreneur").one()

    # offerer with tag but subscription row not yet created
    offerer = offerers_factories.NotValidatedOffererFactory(name="JOE DALTON", tags=[ae_tag])
    offerers_factories.VenueFactory(name="JOE DALTON", managingOfferer=offerer)
    offerers_factories.UserOffererFactory(
        offerer=offerer, user__firstName="Joe", user__lastName="Dalton", user__email="joe.dalton@example.com"
    )

    # individual offerer with email sent, no collective
    offerer = offerers_factories.NotValidatedOffererFactory(
        name="JACK DALTON",
        tags=[ae_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    offerers_factories.VenueFactory(name="JACK DALTON", managingOfferer=offerer)
    offerers_factories.UserOffererFactory(
        offerer=offerer, user__firstName="Jack", user__lastName="Dalton", user__email="jack.dalton@example.com"
    )
    offerers_factories.IndividualOffererSubscription(offerer=offerer)

    # individual offerer with Adage application submitted
    offerer = offerers_factories.NotValidatedOffererFactory(
        name="WILLIAM DALTON",
        tags=[ae_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    venue = offerers_factories.VenueFactory(name="WILLIAM DALTON", managingOfferer=offerer)
    offerers_factories.UserOffererFactory(
        offerer=offerer, user__firstName="William", user__lastName="Dalton", user__email="william.dalton@example.com"
    )
    offerers_factories.IndividualOffererSubscription(
        offerer=offerer, targetsCollectiveOffers=True, targetsIndividualOffers=True
    )
    educational_factories.CollectiveDmsApplicationFactory(venue=venue, state="en_instruction")

    # individual offerer with Adage application accepted and everything received
    offerer = offerers_factories.NotValidatedOffererFactory(
        name="AVERELL DALTON",
        tags=[ae_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    venue = offerers_factories.VenueFactory(name="AVERELL DALTON", managingOfferer=offerer)
    offerers_factories.UserOffererFactory(
        offerer=offerer, user__firstName="Averell", user__lastName="Dalton", user__email="averell.dalton@example.com"
    )
    offerers_factories.IndividualOffererSubscription(
        offerer=offerer,
        targetsCollectiveOffers=True,
        targetsIndividualOffers=False,
        isCriminalRecordReceived=True,
        dateCriminalRecordReceived=datetime.date.today() - datetime.timedelta(days=1),
        isCertificateReceived=True,
        certificateDetails="Diplôme de l'école Rantanplan",
        isExperienceReceived=True,
        has5yrExperience=True,
    )
    educational_factories.CollectiveDmsApplicationFactory(venue=venue, state="accepte")

    logger.info("created industrial individual offerers")
