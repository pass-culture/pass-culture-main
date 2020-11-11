"""create_and_migrate_allocine_venue_provider

Revision ID: 03f3f93489ab
Revises: 771cab29d46e
Create Date: 2020-02-25 09:55:50.597831

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.sql import expression


# revision identifiers, used by Alembic.
revision = "03f3f93489ab"
down_revision = "771cab29d46e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "allocine_venue_provider",
        sa.Column("id", sa.BigInteger, ForeignKey("venue_provider.id"), primary_key=True),
        sa.Column("isDuo", sa.Boolean, nullable=False, server_default=expression.false()),
        sa.Column("available", sa.Integer, nullable=True),
    )

    op.drop_constraint("venue_provider_price_rule_venueProviderId_fkey", "venue_provider_price_rule")
    op.alter_column("venue_provider_price_rule", "venueProviderId", new_column_name="allocineVenueProviderId")

    op.rename_table("venue_provider_price_rule", "allocine_venue_provider_price_rule")
    op.drop_constraint("venue_provider_price_rule_pkey", "allocine_venue_provider_price_rule")
    op.create_primary_key("allocine_venue_provider_price_rule_pkey", "allocine_venue_provider_price_rule", ["id"])
    op.execute("ALTER SEQUENCE venue_provider_price_rule_id_seq" " RENAME TO allocine_venue_provider_price_rule_id_seq")

    op.execute(
        """ 
        INSERT INTO allocine_venue_provider (id, available, "isDuo") 
            (SELECT venue_provider.id, NULL, FALSE FROM venue_provider 
            JOIN provider ON venue_provider."providerId" = provider.id AND provider."localClass" = 'AllocineStocks');
     """
    )

    op.create_foreign_key(
        "allocine_venue_provider_price_rule_allocineVenueProviderId_fkey",
        "allocine_venue_provider_price_rule",
        "allocine_venue_provider",
        ["allocineVenueProviderId"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "allocine_venue_provider_price_rule_allocineVenueProviderId_fkey", "allocine_venue_provider_price_rule"
    )
    op.alter_column("allocine_venue_provider_price_rule", "allocineVenueProviderId", new_column_name="venueProviderId")
    op.create_foreign_key(
        "venue_provider_price_rule_venueProviderId_fkey",
        "allocine_venue_provider_price_rule",
        "venue_provider",
        ["venueProviderId"],
        ["id"],
    )
    op.rename_table("allocine_venue_provider_price_rule", "venue_provider_price_rule")
    op.drop_table("allocine_venue_provider")
    op.drop_constraint("allocine_venue_provider_price_rule_pkey", "venue_provider_price_rule")
    op.create_primary_key("venue_provider_price_rule_pkey", "venue_provider_price_rule", ["id"])
    op.execute("ALTER SEQUENCE allocine_venue_provider_price_rule_id_seq" " RENAME TO venue_provider_price_rule_id_seq")
