import datetime
import logging

from pcapi.core.educational import factories as educational_factories
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


def create_industrial_individual_offerers() -> None:
    logger.info("create_industrial_individual_offerers")

    ae_tag = db.session.query(offerers_models.OffererTag).filter_by(name="auto-entrepreneur").one()
    adage_tag = db.session.query(offerers_models.OffererTag).filter_by(name="adage").one()

    instructor = users_factories.AdminFactory.create(firstName="Instructeur", lastName="d'Autoentrepreneur")
    other_instructor = users_factories.AdminFactory.create(firstName="Instructeur", lastName="Bis")

    # offerer with tag but subscription row not yet created
    offerer = offerers_factories.NotValidatedOffererFactory.create(name="JOE AUTOENTREPRENEUR", tags=[ae_tag])
    venue = offerers_factories.VenueFactory.create(name="JOE AUTOENTREPRENEUR", managingOfferer=offerer)
    offerers_factories.UserOffererFactory.create(
        offerer=offerer,
        user__firstName="Joe",
        user__lastName="Autoentrepreneur",
        user__email="joe.autoentrepreneur@example.com",
    )
    offerers_factories.VenueRegistrationFactory.create(venue=venue, webPresence="https://www.example.com/ae/joe")

    # individual offerer with email sent, no collective
    offerer = offerers_factories.NotValidatedOffererFactory.create(
        name="JACK AUTOENTREPRENEUR",
        tags=[ae_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    history_factories.ActionHistoryFactory.create(
        actionType=history_models.ActionType.OFFERER_PENDING,
        authorUser=instructor,
        offerer=offerer,
        comment="Première action",
    )
    venue = offerers_factories.VenueFactory.create(name="JACK AUTOENTREPRENEUR", managingOfferer=offerer)
    offerers_factories.UserOffererFactory.create(
        offerer=offerer,
        user__firstName="Jack",
        user__lastName="Autoentrepreneur",
        user__email="jack.autoentrepreneur@example.com",
    )
    offerers_factories.IndividualOffererSubscriptionFactory.create(offerer=offerer)
    offerers_factories.VenueRegistrationFactory.create(venue=venue, webPresence="https://www.example.com/ae/jack")

    # individual offerer with Adage application submitted
    offerer = offerers_factories.NotValidatedOffererFactory.create(
        name="WILLIAM AUTOENTREPRENEUR",
        tags=[ae_tag, adage_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    history_factories.ActionHistoryFactory.create(
        actionType=history_models.ActionType.OFFERER_PENDING,
        authorUser=instructor,
        offerer=offerer,
        comment="Première action",
    )
    venue = offerers_factories.VenueFactory.create(name="WILLIAM AUTOENTREPRENEUR", managingOfferer=offerer)
    offerers_factories.UserOffererFactory.create(
        offerer=offerer,
        user__firstName="William",
        user__lastName="Autoentrepreneur",
        user__email="william.autoentrepreneur@example.com",
    )
    offerers_factories.IndividualOffererSubscriptionFactory.create(offerer=offerer, isCriminalRecordReceived=True)
    offerers_factories.VenueRegistrationFactory.create(venue=venue, webPresence="https://www.example.com/ae/william")
    educational_factories.CollectiveDmsApplicationFactory.create(venue=venue, state="en_instruction")

    # individual offerer with Adage application accepted and everything received
    offerer = offerers_factories.NotValidatedOffererFactory.create(
        name="AVERELL AUTOENTREPRENEUR",
        tags=[ae_tag, adage_tag],
        validationStatus=ValidationStatus.PENDING,
    )
    history_factories.ActionHistoryFactory.create(
        actionType=history_models.ActionType.OFFERER_PENDING, authorUser=instructor, offerer=offerer
    )
    history_factories.ActionHistoryFactory.create(
        actionType=history_models.ActionType.OFFERER_PENDING,
        authorUser=other_instructor,
        offerer=offerer,
        comment="Seconde action",
    )
    venue = offerers_factories.VenueFactory.create(name="AVERELL AUTOENTREPRENEUR", managingOfferer=offerer)
    offerers_factories.UserOffererFactory.create(
        offerer=offerer,
        user__firstName="Averell",
        user__lastName="Autoentrepreneur",
        user__email="averell.autoentrepreneur@example.com",
    )
    offerers_factories.IndividualOffererSubscriptionFactory.create(
        offerer=offerer,
        isCriminalRecordReceived=True,
        dateCriminalRecordReceived=datetime.date.today() - datetime.timedelta(days=1),
        isCertificateReceived=True,
        certificateDetails="Diplôme de l'école Rantanplan",
        isExperienceReceived=True,
        has5yrExperience=True,
    )
    educational_factories.CollectiveDmsApplicationFactory.create(venue=venue, state="accepte")

    logger.info("created industrial individual offerers")
