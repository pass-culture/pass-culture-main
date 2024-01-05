"""Delete providable mixin from venue provider"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "10b54017d02a"
down_revision = "cbd4d45e39f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("venue_provider", "dateModifiedAtLastProvider")
    op.drop_column("venue_provider", "lastProviderId")
    op.drop_column("venue_provider", "fieldsUpdated")
    op.drop_column("venue_provider", "idAtProviders")


def downgrade() -> None:
    op.add_column(
        "venue_provider", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True)
    )
    op.add_column(
        "venue_provider",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column("venue_provider", sa.Column("lastProviderId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column(
        "venue_provider",
        sa.Column("dateModifiedAtLastProvider", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "venue_provider_lastProviderId_fkey", "venue_provider", "provider", ["lastProviderId"], ["id"]
    )
    op.create_unique_constraint("venue_provider_idAtProviders_key", "venue_provider", ["idAtProviders"])
