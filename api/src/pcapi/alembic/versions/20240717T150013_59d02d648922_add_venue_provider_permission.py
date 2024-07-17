"""Add `venue_provider_permission` table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "59d02d648922"
down_revision = "e0d7e16bcbaa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "venue_provider_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueProviderId", sa.BigInteger(), nullable=False),
        sa.Column("resource", sa.Text(), nullable=False),
        sa.Column("permission", sa.Enum("READ", "WRITE", name="permissionenum"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "venueProviderId", "resource", "permission", name="unique_venue_provider_resource_permission"
        ),
    )


def downgrade() -> None:
    op.drop_table("venue_provider_permission")
    op.execute("DROP TYPE IF EXISTS permissionenum")
