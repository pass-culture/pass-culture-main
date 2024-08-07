"""Drop `venue_provider_permission` table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "03013c06a0ac"
down_revision = "227228152465"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute('DROP TABLE IF EXISTS "venue_provider_permission"')
    op.execute("DROP TYPE IF EXISTS permissionenum")


def downgrade() -> None:
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
    op.create_foreign_key(
        "venue_provider_permission_venueProviderId_fkey",
        "venue_provider_permission",
        "venue_provider",
        ["venueProviderId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute(
        'ALTER TABLE "venue_provider_permission" VALIDATE CONSTRAINT "venue_provider_permission_venueProviderId_fkey"'
    )
