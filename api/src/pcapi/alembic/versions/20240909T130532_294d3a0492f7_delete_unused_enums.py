"""Delete unused enums : eventtype, featuretoggle, studentlevels, thingtype"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "294d3a0492f7"
down_revision = "d0a81150dd8d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("DROP TYPE IF EXISTS eventtype;")
    op.execute("DROP TYPE IF EXISTS featuretoggle;")
    op.execute("DROP TYPE IF EXISTS thingtype;")


def downgrade() -> None:
    # Theses commands has been copied from schema_init.sql
    op.execute(
        """
        CREATE TYPE public.eventtype AS ENUM (
            'Workshop',
            'MovieScreening',
            'Meeting',
            'Game',
            'SchoolHelp',
            'StreetPerformance',
            'Other',
            'BookReading',
            'CircusAndMagic',
            'DancePerformance',
            'Comedy',
            'Concert',
            'Combo',
            'Youth',
            'Musical',
            'Theater',
            'GuidedVisit',
            'FreeVisit'
        );"""
    )
    op.execute(
        """
        CREATE TYPE public.featuretoggle AS ENUM (
            'SEARCH_ALGOLIA',
            'SYNCHRONIZE_ALGOLIA',
            'SYNCHRONIZE_ALLOCINE',
            'SYNCHRONIZE_TITELIVE_PRODUCTS',
            'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
            'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
            'UPDATE_BOOKING_USED',
            'BOOKINGS_V2',
            'API_SIRENE_AVAILABLE'
        );"""
    )
    op.execute(
        """
        CREATE TYPE public.thingtype as ENUM (
            'Article',
            'AudioObject',
            'Blog',
            'Book',
            'BookSeries',
            'BroadcastService',
            'BusTrip',
            'CableOrSatelliteService',
            'Clip',
            'Course',
            'CreativeWorkSeason',
            'CreativeWorkSeries',
            'DataDownload',
            'Episode',
            'FoodService',
            'Game',
            'ImageObject',
            'Map',
            'MediaObject',
            'Movie',
            'MovieClip',
            'MovieSeries',
            'MusicAlbum',
            'MusicComposition',
            'MusicRecording',
            'MusicVideoObject',
            'NewsArticle',
            'Painting',
            'PaymentCard',
            'Periodical',
            'Photograph',
            'Product',
            'ProgramMembership',
            'PublicationIssue',
            'PublicationVolume',
            'RadioClip',
            'RadioEpisode',
            'RadioSeason',
            'RadioSeries',
            'Report',
            'ScholarlyArticle',
            'Sculpture',
            'Service',
            'TaxiService',
            'TechArticle',
            'Ticket',
            'TVClip',
            'TVEpisode',
            'TVSeason',
            'TVSeries',
            'VideoGame',
            'VideoGameClip',
            'VideoGameSeries',
            'VideoObject',
            'VisualArtwork'
        );"""
    )
