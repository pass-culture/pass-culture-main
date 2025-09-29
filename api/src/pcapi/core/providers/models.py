import datetime
import decimal
import enum
import typing
from dataclasses import dataclass

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql as sa_sql

import pcapi.core.providers.constants as provider_constants
from pcapi.core.offerers.models import Venue
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    import pcapi.core.offerers.models as offerers_models
    from pcapi.core.educational.models import CollectiveOffer


class Provider(PcObject, Model, DeactivableMixin):
    __tablename__ = "provider"
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(90), index=True, nullable=False)

    localClass: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(60), nullable=True, unique=True)

    # bool meant for hiding custom provider (for instance, FNAC provider) in the pro Interface (if set to False)
    enabledForPro: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa_sql.expression.false()
    )

    enableParallelSynchronization: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa_sql.expression.false()
    )

    logoUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    bookingExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    cancelExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    notificationExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.VARCHAR(length=255), nullable=True)
    hmacKey: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    pricesInCents: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa_sql.expression.false()
    )

    collectiveOffers: sa_orm.Mapped[list["CollectiveOffer"]] = sa_orm.relationship(
        "CollectiveOffer", back_populates="provider"
    )

    offererProvider: sa_orm.Mapped["offerers_models.OffererProvider"] = sa_orm.relationship(
        "OffererProvider", back_populates="provider", uselist=False
    )
    venueProviders: sa_orm.Mapped[list["VenueProvider"]] = sa_orm.relationship(
        "VenueProvider", back_populates="provider", uselist=True
    )
    cinemaProviderPivots: sa_orm.Mapped[list["CinemaProviderPivot"]] = sa_orm.relationship(
        "CinemaProviderPivot", back_populates="provider", uselist=True
    )

    # presence of this field signifies the provider implements pass Culture's individual offers API
    apiKeys: sa_orm.Mapped[list["offerers_models.ApiKey"]] = sa_orm.relationship("ApiKey", back_populates="provider")

    @property
    def isAllocine(self) -> bool:
        from pcapi import local_providers  # avoid import loop

        return self.localClass == local_providers.AllocineStocks.__name__

    @property
    def isCinemaProvider(self) -> bool:
        return self.localClass in provider_constants.CINEMA_PROVIDER_NAMES

    @property
    def hasTicketingService(self) -> bool:
        return bool(self.bookingExternalUrl and self.cancelExternalUrl)

    @property
    def hasOffererProvider(self) -> bool:
        return bool(self.offererProvider)


class VenueProviderExternalUrls(PcObject, Model, DeactivableMixin):
    """
    Stores external Urls specific for a Venue. It will be set by providers via API.
    """

    __tablename__ = "venue_provider_external_urls"
    venueProviderId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue_provider.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    venueProvider: sa_orm.Mapped["VenueProvider"] = sa_orm.relationship(
        "VenueProvider", foreign_keys=[venueProviderId], back_populates="externalUrls"
    )

    # Ticketing urls
    bookingExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    cancelExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)
    # Notification url
    notificationExternalUrl: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text(), nullable=True)

    __table_args__ = (
        sa.CheckConstraint(
            '("bookingExternalUrl" IS NOT NULL AND "cancelExternalUrl" IS NOT NULL) OR ("bookingExternalUrl" IS NULL AND "cancelExternalUrl" IS NULL)',
            name="check_ticketing_external_urls_both_set_or_null",
        ),
        sa.CheckConstraint(
            '"bookingExternalUrl" IS NOT NULL OR "notificationExternalUrl" IS NOT NULL',
            name="check_at_least_one_of_the_external_url_is_set",
        ),
    )


class VenueProvider(PcObject, Model, DeactivableMixin):
    """Stores specific sync settings for a Venue, and whether it is active"""

    __tablename__ = "venue_provider"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("venue.id"), nullable=False)

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship("Venue", foreign_keys=[venueId])

    providerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("provider.id"), index=True, nullable=False
    )

    provider: sa_orm.Mapped["Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="venueProviders"
    )

    venueIdAtOfferProvider: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(70), nullable=True)

    # external URLs
    externalUrls: sa_orm.Mapped["VenueProviderExternalUrls"] = sa_orm.relationship(
        "VenueProviderExternalUrls", uselist=False, back_populates="venueProvider", cascade="all,delete"
    )

    # This column is unused by our code but by the data team
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )

    lastSyncDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    # describe if synchronised offers are available for duo booking or not
    isDuoOffers: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(sa.Boolean, nullable=True)

    isFromAllocineProvider = sa_orm.column_property(
        sa.exists(
            sa.select(Provider.id)
            .where(sa.and_(Provider.id == providerId, Provider.localClass == "AllocineStocks"))
            .correlate_except(Provider)
        )
    )

    isFromCinemaProvider = sa_orm.column_property(
        sa.exists(sa.select(Provider.id))
        .where(
            sa.and_(
                Provider.id == providerId,
                Provider.localClass.in_(provider_constants.CINEMA_PROVIDER_NAMES),
            )
        )
        .correlate_except(Provider)
    )

    __mapper_args__ = {
        "polymorphic_on": sa.case(
            (isFromAllocineProvider, "allocine_venue_provider"),
            else_="venue_provider",
        ),
        "polymorphic_identity": "venue_provider",
    }

    __table_args__ = (
        # FIXME (ghaliela, 2024-04-05): after migrating to postgres 15, we can use the following constraint
        # with `NULLS NOT DISTINCT` to replace the index below 'unique_venue_provider_index_null_venue_id_at_provider'
        sa.UniqueConstraint(
            "venueId",
            "providerId",
            "venueIdAtOfferProvider",
            name="unique_venue_provider",
        ),
        sa.Index(
            "unique_venue_provider_index_null_venue_id_at_provider",
            "venueId",
            "providerId",
            unique=True,
            postgresql_where=venueIdAtOfferProvider.is_(None),
        ),
    )

    @staticmethod
    def restize_integrity_error(error: sa_exc.IntegrityError) -> tuple[str, str]:
        if "unique_venue_provider" in str(error.orig):
            return ("global", "Votre lieu est déjà lié à cette source")
        return PcObject.restize_integrity_error(error)

    @property
    def hasTicketingService(self) -> bool:
        return bool(self.externalUrls and self.externalUrls.bookingExternalUrl and self.externalUrls.cancelExternalUrl)


class CinemaProviderPivot(PcObject, Model):
    """Stores whether a Venue has requested to be synced with a Provider"""

    __tablename__ = "cinema_provider_pivot"
    venueId = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("venue.id"), index=False, nullable=False, unique=True)

    venue: sa_orm.Mapped["Venue | None"] = sa_orm.relationship(
        Venue, foreign_keys=[venueId], back_populates="cinemaProviderPivot", uselist=False
    )

    providerId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=False)

    provider: sa_orm.Mapped["Provider"] = sa_orm.relationship(
        "Provider", foreign_keys=[providerId], back_populates="cinemaProviderPivots"
    )
    CDSCinemaDetails: sa_orm.Mapped["CDSCinemaDetails | None"] = sa_orm.relationship(
        "CDSCinemaDetails", back_populates="cinemaProviderPivot", uselist=False
    )
    BoostCinemaDetails: sa_orm.Mapped["BoostCinemaDetails | None"] = sa_orm.relationship(
        "BoostCinemaDetails", back_populates="cinemaProviderPivot", uselist=False
    )
    CGRCinemaDetails: sa_orm.Mapped["CGRCinemaDetails | None"] = sa_orm.relationship(
        "CGRCinemaDetails", back_populates="cinemaProviderPivot", uselist=False
    )
    EMSCinemaDetails: sa_orm.Mapped["EMSCinemaDetails | None"] = sa_orm.relationship(
        "EMSCinemaDetails", back_populates="cinemaProviderPivot", uselist=False
    )
    idAtProvider: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint(
            "venueId",
            "providerId",
            name="unique_pivot_venue_provider",
        ),
        sa.UniqueConstraint(
            "providerId",
            "idAtProvider",
            name="unique_provider_id_at_provider",
        ),
    )


class CDSCinemaDetails(PcObject, Model):
    """Stores info on the specific login details of a cinema synced with CDS"""

    __tablename__ = "cds_cinema_details"
    cinemaProviderPivotId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )

    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = sa_orm.relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId], back_populates="CDSCinemaDetails", uselist=False
    )
    cinemaApiToken: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)

    accountId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)


class AllocineVenueProvider(VenueProvider):
    __tablename__ = "allocine_venue_provider"
    __mapper_args__ = {"polymorphic_identity": "allocine_venue_provider"}

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("venue_provider.id"), primary_key=True)
    isDuo: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, default=True, server_default=sa.true(), nullable=False
    )
    quantity: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    internalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)
    price: sa_orm.Mapped[decimal.Decimal] = sa_orm.mapped_column(
        sa.Numeric(10, 2), sa.CheckConstraint("price >= 0", name="check_price_is_not_negative"), nullable=False
    )


@dataclass
class VenueProviderCreationPayload:
    isDuo: bool | None = None
    price: decimal.Decimal | None = None
    quantity: int | None = None
    venueIdAtOfferProvider: str | None = None


class AllocinePivot(PcObject, Model):
    __tablename__ = "allocine_pivot"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id"), index=False, nullable=False, unique=True
    )

    venue: sa_orm.Mapped["Venue"] = sa_orm.relationship(Venue, foreign_keys=[venueId], back_populates="allocinePivot")

    theaterId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(20), nullable=False, unique=True)

    internalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)


class AllocineTheater(PcObject, Model):
    __tablename__ = "allocine_theater"
    siret: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(14), nullable=True, unique=True)

    theaterId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(20), nullable=False, unique=True)

    internalId: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)


class LocalProviderEventType(enum.Enum):
    SyncError = "SyncError"

    SyncPartStart = "SyncPartStart"
    SyncPartEnd = "SyncPartEnd"

    SyncStart = "SyncStart"
    SyncEnd = "SyncEnd"


class LocalProviderEvent(PcObject, Model):
    __tablename__ = "local_provider_event"
    providerId: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, sa.ForeignKey("provider.id"), nullable=False)
    provider: sa_orm.Mapped["Provider"] = sa_orm.relationship("Provider", foreign_keys=[providerId])
    date: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    type: sa_orm.Mapped[LocalProviderEventType] = sa_orm.mapped_column(sa.Enum(LocalProviderEventType), nullable=False)
    payload: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.String(50), nullable=True)


class BoostCinemaDetails(PcObject, Model):
    """Stores info on the specific login details of a cinema synced with Boost"""

    __tablename__ = "boost_cinema_details"
    cinemaProviderPivotId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )
    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = sa_orm.relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId], back_populates="BoostCinemaDetails", uselist=False
    )
    cinemaUrl: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, nullable=False
    )  # including http:// or https:// and trailing /
    token: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    tokenExpirationDate: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)


class CGRCinemaDetails(PcObject, Model):
    """Stores info on the specific login details of a cinema synced with CGR"""

    __tablename__ = "cgr_cinema_details"
    cinemaProviderPivotId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )
    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = sa_orm.relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId], back_populates="CGRCinemaDetails", uselist=False
    )
    cinemaUrl: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    numCinema: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)
    password: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)


class EMSCinemaDetails(PcObject, Model):
    """Stores info on the specific login details of a cinema synced with EMS"""

    __tablename__ = "ems_cinema_details"
    cinemaProviderPivotId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("cinema_provider_pivot.id"), index=False, nullable=True, unique=True
    )
    cinemaProviderPivot: sa_orm.Mapped["CinemaProviderPivot | None"] = sa_orm.relationship(
        CinemaProviderPivot, foreign_keys=[cinemaProviderPivotId], back_populates="EMSCinemaDetails", uselist=False
    )
    lastVersion: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, default=0, nullable=False)

    @property
    def last_version_as_isoformat(self) -> str:
        return datetime.datetime.fromtimestamp(self.lastVersion).isoformat()
