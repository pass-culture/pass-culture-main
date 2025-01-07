from datetime import date
from datetime import datetime
import enum

import sqlalchemy as sa

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


class SpecialEvent(PcObject, Base, Model):
    __tablename__ = "special_event"
    dateCreated: datetime = sa.Column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )
    externalId: str = sa.Column(sa.Text(), index=True, unique=True, nullable=False)
    title: str = sa.Column(sa.Text(), nullable=False)
    eventDate: date = sa.Column(sa.Date, index=True, nullable=False, server_default=sa.func.now())
    offererId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="SET NULL"), nullable=True)
    offerer: offerers_models.Offerer = sa.orm.relationship("Offerer", foreign_keys=[offererId])
    venueId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="SET NULL"), nullable=True)
    venue: offerers_models.Offerer = sa.orm.relationship("Venue", foreign_keys=[venueId])

    __table_args__ = (
        sa.Index(
            "ix_special_event_trgm_unaccent_title",
            sa.func.immutable_unaccent(title),
            postgresql_using="gin",
        ),
    )


class SpecialEventQuestion(PcObject, Base, Model):
    __tablename__ = "special_event_question"
    eventId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event.id"), index=True, nullable=False)
    event: SpecialEvent = sa.orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], backref=sa.orm.backref("questions")
    )
    externalId: str = sa.Column(sa.Text(), index=True, unique=True, nullable=False)
    title: str = sa.Column(sa.Text(), nullable=False)


class SpecialEventResponseStatus(enum.Enum):
    NEW = "NEW"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    PRESELECTED = "PRESELECTED"


class SpecialEventResponse(PcObject, Base, Model):
    """
    User response to a special event, linked with his/her answers.
    Email should be the same as the one stored in user table, but is stored here in case of "no match".
    Phone number is not mandatory for underage beneficiaries, so they have to provide one here to be called if their
    application is selected.
    """

    __tablename__ = "special_event_response"
    eventId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event.id"), index=True, nullable=False)
    event: SpecialEvent = sa.orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], backref=sa.orm.backref("responses")
    )
    externalId: str = sa.Column(sa.Text(), index=True, unique=True, nullable=False)
    dateSubmitted: datetime = sa.Column(sa.DateTime, nullable=False)
    phoneNumber: str | None = sa.Column(sa.Text(), nullable=True)
    email: str | None = sa.Column(sa.Text(), nullable=True)
    status: SpecialEventResponseStatus = sa.Column(
        MagicEnum(SpecialEventResponseStatus), nullable=False, default=SpecialEventResponseStatus.NEW
    )
    userId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)
    user: users_models.User = sa.orm.relationship(
        "User", foreign_keys=[userId], backref=sa.orm.backref("specialEventResponses")
    )


class SpecialEventAnswer(PcObject, Base, Model):
    """
    Answer to every single question when applying for a special event.
    """

    __tablename__ = "special_event_answer"
    responseId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event_response.id"), index=True, nullable=False)
    response: SpecialEventResponse = sa.orm.relationship(
        "SpecialEventResponse", foreign_keys=[responseId], backref=sa.orm.backref("answers")
    )
    questionId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event_question.id"), index=True, nullable=False)
    text: str = sa.Column(sa.Text(), nullable=False)
