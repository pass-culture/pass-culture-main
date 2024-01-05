"""Delete ProvidableMixin columns on Venue table."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cbd4d45e39f0"
down_revision = "2b2059710c60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("venue", "lastProviderId")
    op.drop_column("venue", "idAtProviders")
    op.drop_column("venue", "dateModifiedAtLastProvider")
    op.drop_column("venue", "fieldsUpdated")


def downgrade() -> None:
    op.add_column(
        "venue",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "venue", sa.Column("dateModifiedAtLastProvider", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
    )
    op.add_column("venue", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True))
    op.add_column("venue", sa.Column("lastProviderId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key("venue_lastProviderId_fkey", "venue", "provider", ["lastProviderId"], ["id"])
    op.create_unique_constraint("venue_idAtProviders_key", "venue", ["idAtProviders"])
