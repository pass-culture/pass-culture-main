"""Offerer delete unused columns."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "cd2fcba2f97f"
down_revision = "84144a86ec2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("offerer", "dateModifiedAtLastProvider")
    op.drop_column("offerer", "thumbCount")
    op.drop_column("offerer", "idAtProviders")
    op.drop_column("offerer", "lastProviderId")
    op.drop_column("offerer", "fieldsUpdated")


def downgrade() -> None:
    op.add_column(
        "offerer",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column("offerer", sa.Column("lastProviderId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("offerer", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True))
    op.add_column("offerer", sa.Column("thumbCount", sa.INTEGER(), autoincrement=False, nullable=False, default=0))
    op.add_column(
        "offerer", sa.Column("dateModifiedAtLastProvider", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
    )
    op.create_foreign_key("offerer_lastProviderId_fkey", "offerer", "provider", ["lastProviderId"], ["id"])
    op.create_unique_constraint("offerer_idAtProviders_key", "offerer", ["idAtProviders"])
