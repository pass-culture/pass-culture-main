import enum
from datetime import date
from datetime import datetime
from datetime import timedelta

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

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
    offerer: sa_orm.Mapped[offerers_models.Offerer] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    venueId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="SET NULL"), nullable=True)
    venue: sa_orm.Mapped[offerers_models.Venue] = sa_orm.relationship("Venue", foreign_keys=[venueId])

    __table_args__ = (
        sa.Index(
            "ix_special_event_trgm_unaccent_title",
            sa.func.immutable_unaccent(title),
            postgresql_using="gin",
        ),
    )

    @property
    def endImportDate(self) -> date:
        # TODO (rpaoloni 16/05/2025): replace with a column in db (should be done in pc-36166)
        return self.eventDate + timedelta(days=7)

    @property
    def isFinished(self) -> bool:
        return self.endImportDate < date.today()


class SpecialEventQuestion(PcObject, Base, Model):
    __tablename__ = "special_event_question"
    eventId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event.id"), index=True, nullable=False)
    event: sa_orm.Mapped[SpecialEvent] = sa_orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], backref=sa_orm.backref("questions")
    )
    externalId: str = sa.Column(sa.Text(), index=True, unique=True, nullable=False)
    title: str = sa.Column(sa.Text(), nullable=False)


class SpecialEventResponseStatus(enum.StrEnum):
    PRESELECTED = "PRESELECTED"
    BACKUP = "BACKUP"
    VALIDATED = "VALIDATED"
    WITHDRAWN = "WITHDRAWN"
    WAITING = "WAITING"
    NEW = "NEW"
    REJECTED = "REJECTED"


class SpecialEventResponse(PcObject, Base, Model):
    """
    User response to a special event, linked with his/her answers.
    Email should be the same as the one stored in user table, but is stored here in case of "no match".
    Phone number is not mandatory for underage beneficiaries, so they have to provide one here to be called if their
    application is selected.
    """

    __tablename__ = "special_event_response"
    eventId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event.id"), nullable=False)
    event: sa_orm.Mapped[SpecialEvent] = sa_orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], backref=sa_orm.backref("responses")
    )
    externalId: str = sa.Column(sa.Text(), index=True, unique=True, nullable=False)
    dateSubmitted: datetime = sa.Column(sa.DateTime, nullable=False)
    phoneNumber: str | None = sa.Column(sa.Text(), nullable=True)
    email: str | None = sa.Column(sa.Text(), nullable=True)
    status: SpecialEventResponseStatus = sa.Column(
        MagicEnum(SpecialEventResponseStatus), nullable=False, default=SpecialEventResponseStatus.NEW
    )
    userId: int | None = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)
    user: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship(
        "User", foreign_keys=[userId], backref=sa_orm.backref("specialEventResponses")
    )

    __table_args__ = (sa.Index("ix_special_event_response_eventid_status", eventId, status),)


class SpecialEventAnswer(PcObject, Base, Model):
    """
    Answer to every single question when applying for a special event.
    """

    __tablename__ = "special_event_answer"
    responseId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event_response.id"), index=True, nullable=False)
    response: sa_orm.Mapped[SpecialEventResponse] = sa_orm.relationship(
        "SpecialEventResponse", foreign_keys=[responseId], backref=sa_orm.backref("answers")
    )
    questionId: int = sa.Column(sa.BigInteger, sa.ForeignKey("special_event_question.id"), index=True, nullable=False)
    text: str = sa.Column(sa.Text(), nullable=False)
