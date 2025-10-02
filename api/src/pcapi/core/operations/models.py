import enum
from datetime import date
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils.db import MagicEnum


class SpecialEvent(PcObject, Model):
    __tablename__ = "special_event"
    dateCreated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=datetime.utcnow, server_default=sa.func.now()
    )
    externalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), index=True, unique=True, nullable=False)
    title: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)
    endImportDate: sa_orm.Mapped[date] = sa_orm.mapped_column(sa.Date, index=True, nullable=False)
    eventDate: sa_orm.Mapped[date] = sa_orm.mapped_column(
        sa.Date, index=True, nullable=False, server_default=sa.func.now()
    )
    offererId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offerer.id", ondelete="SET NULL"), nullable=True
    )
    offerer: sa_orm.Mapped[offerers_models.Offerer | None] = sa_orm.relationship("Offerer", foreign_keys=[offererId])
    venueId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="SET NULL"), nullable=True
    )
    venue: sa_orm.Mapped[offerers_models.Venue | None] = sa_orm.relationship("Venue", foreign_keys=[venueId])
    questions: sa_orm.Mapped[list["SpecialEventQuestion"]] = sa_orm.relationship(
        "SpecialEventQuestion", foreign_keys="SpecialEventQuestion.eventId", back_populates="event"
    )

    @property
    def isFinished(self) -> bool:
        return self.endImportDate < date.today()


class SpecialEventQuestion(PcObject, Model):
    __tablename__ = "special_event_question"
    eventId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("special_event.id"), index=True, nullable=False
    )
    event: sa_orm.Mapped[SpecialEvent] = sa_orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], back_populates="questions"
    )
    externalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), index=True, unique=True, nullable=False)
    title: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)


class SpecialEventResponseStatus(enum.StrEnum):
    PRESELECTED = "PRESELECTED"
    BACKUP = "BACKUP"
    VALIDATED = "VALIDATED"
    WITHDRAWN = "WITHDRAWN"
    WAITING = "WAITING"
    NEW = "NEW"
    REJECTED = "REJECTED"


class SpecialEventResponse(PcObject, Model):
    """
    User response to a special event, linked with his/her answers.
    Email should be the same as the one stored in user table, but is stored here in case of "no match".
    Phone number is not mandatory for underage beneficiaries, so they have to provide one here to be called if their
    application is selected.
    """

    __tablename__ = "special_event_response"
    eventId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("special_event.id"), nullable=False)
    event: sa_orm.Mapped[SpecialEvent] = sa_orm.relationship(
        "SpecialEvent", foreign_keys=[eventId], backref=sa_orm.backref("responses")
    )
    externalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), index=True, unique=True, nullable=False)
    dateSubmitted: sa_orm.Mapped[datetime] = sa_orm.mapped_column(sa.DateTime, nullable=False)
    phoneNumber: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    email: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    status: sa_orm.Mapped[SpecialEventResponseStatus] = sa_orm.mapped_column(
        MagicEnum(SpecialEventResponseStatus), nullable=False, default=SpecialEventResponseStatus.NEW
    )
    userId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True
    )
    user: sa_orm.Mapped[users_models.User | None] = sa_orm.relationship(
        "User", foreign_keys=[userId], backref=sa_orm.backref("specialEventResponses")
    )

    __table_args__ = (sa.Index("ix_special_event_response_eventid_status", eventId, status),)


class SpecialEventAnswer(PcObject, Model):
    """
    Answer to every single question when applying for a special event.
    """

    __tablename__ = "special_event_answer"
    responseId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("special_event_response.id"), index=True, nullable=False
    )
    response: sa_orm.Mapped[SpecialEventResponse] = sa_orm.relationship(
        "SpecialEventResponse", foreign_keys=[responseId], backref=sa_orm.backref("answers")
    )
    questionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("special_event_question.id"), index=True, nullable=False
    )
    text: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text(), nullable=False)

    __table_args__ = (
        sa.Index(
            "ix_special_event_answer_trgm_unaccent_text",
            sa.func.immutable_unaccent("text"),
            postgresql_using="gin",
            postgresql_ops={
                "description": "gin_trgm_ops",
            },
        ),
    )
