"""delete "offer_id" foreign key on "opening_hours" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0fea3fa4c699"
down_revision = "b870a92839fa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("opening_hours_offerId_fkey"), "opening_hours", type_="foreignkey")


def downgrade() -> None:
    op.create_foreign_key(
        "opening_hours_offerId_fkey",
        "opening_hours",
        "offer",
        ["offerId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute('ALTER TABLE "opening_hours" VALIDATE CONSTRAINT "opening_hours_offerId_fkey"')
