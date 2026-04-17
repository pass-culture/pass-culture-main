"""Add "offerId" foreign key constraint to "cultural_outreach" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "76687ea6ef2c"
down_revision = "b69574766fe3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "cultural_outreach_offerId_fkey",
        "cultural_outreach",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("cultural_outreach_offerId_fkey", "cultural_outreach", type_="foreignkey")
