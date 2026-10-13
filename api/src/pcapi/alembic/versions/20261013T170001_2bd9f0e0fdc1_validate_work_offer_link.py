"""Validate the direct work offer link after deployment."""

from alembic import op


# pre/post deployment: post
revision = "2bd9f0e0fdc1"
down_revision = "b6291d40c5a7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE work VALIDATE CONSTRAINT work_offer_id_fkey")


def downgrade() -> None:
    op.drop_constraint("work_offer_id_fkey", "work", type_="foreignkey")
    op.create_foreign_key(
        "work_offer_id_fkey",
        "work",
        "offer",
        ["offer_id"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )
