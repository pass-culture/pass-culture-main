"""add_profile_page_feature

Revision ID: 979af719f2f7
Revises: 4475df545cae
Create Date: 2020-09-01 08:11:35.662128

"""
import enum

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "979af719f2f7"
down_revision = "4475df545cae"
branch_labels = None
depends_on = None


class FeatureToggle(enum.Enum):
    WEBAPP_PROFILE_PAGE = "Permettre l affichage de la page profil (route dédiée + navbar)"


def upgrade():
    old_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
        "SAVE_SEEN_OFFERS",
        "API_SIRENE_AVAILABLE",
        "CLEAN_DISCOVERY_VIEW",
        "WEBAPP_HOMEPAGE",
    )

    new_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
        "SAVE_SEEN_OFFERS",
        "BOOKINGS_V2",
        "API_SIRENE_AVAILABLE",
        "CLEAN_DISCOVERY_VIEW",
        "WEBAPP_HOMEPAGE",
        "WEBAPP_PROFILE_PAGE",
    )

    previous_enum = sa.Enum(*old_values, name="featuretoggle")
    new_enum = sa.Enum(*new_values, name="featuretoggle")

    temporary_enum = sa.Enum(*new_values, name="tmp_featuretoggle")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle" " USING name::text::tmp_featuretoggle")

    previous_enum.drop(op.get_bind(), checkfirst=False)

    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle" " USING name::text::featuretoggle")

    op.execute(
        """
                    INSERT INTO feature (name, description, "isActive")
                    VALUES ('%s', '%s', TRUE);
                    """
        % (FeatureToggle.WEBAPP_PROFILE_PAGE.name, FeatureToggle.WEBAPP_PROFILE_PAGE.value)
    )

    temporary_enum.drop(op.get_bind(), checkfirst=False)


def downgrade():
    old_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
        "SAVE_SEEN_OFFERS",
        "BOOKINGS_V2",
        "API_SIRENE_AVAILABLE",
        "CLEAN_DISCOVERY_VIEW",
        "WEBAPP_HOMEPAGE",
        "WEBAPP_PROFILE_PAGE",
    )

    new_values = (
        "WEBAPP_SIGNUP",
        "DEGRESSIVE_REIMBURSEMENT_RATE",
        "QR_CODE",
        "FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE",
        "SEARCH_ALGOLIA",
        "SEARCH_LEGACY",
        "BENEFICIARIES_IMPORT",
        "SYNCHRONIZE_ALGOLIA",
        "SYNCHRONIZE_ALLOCINE",
        "SYNCHRONIZE_BANK_INFORMATION",
        "SYNCHRONIZE_LIBRAIRES",
        "SYNCHRONIZE_TITELIVE",
        "SYNCHRONIZE_TITELIVE_PRODUCTS",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION",
        "SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS",
        "UPDATE_DISCOVERY_VIEW",
        "UPDATE_BOOKING_USED",
        "RECOMMENDATIONS_WITH_DISCOVERY_VIEW",
        "RECOMMENDATIONS_WITH_DIGITAL_FIRST",
        "RECOMMENDATIONS_WITH_GEOLOCATION",
        "NEW_RIBS_UPLOAD",
        "SAVE_SEEN_OFFERS",
        "API_SIRENE_AVAILABLE",
        "CLEAN_DISCOVERY_VIEW",
        "WEBAPP_HOMEPAGE",
    )

    op.execute("DELETE FROM feature WHERE name = '%s'" % FeatureToggle.WEBAPP_PROFILE_PAGE.name)

    previous_enum = sa.Enum(*old_values, name="featuretoggle")
    new_enum = sa.Enum(*new_values, name="featuretoggle")

    temporary_enum = sa.Enum(*new_values, name="tmp_featuretoggle")
    temporary_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE tmp_featuretoggle" " USING name::text::tmp_featuretoggle")

    previous_enum.drop(op.get_bind(), checkfirst=False)

    new_enum.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle" " USING name::text::featuretoggle")

    temporary_enum.drop(op.get_bind(), checkfirst=False)
