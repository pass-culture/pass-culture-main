"""add "venueId" foreign key constraint to "ProAdvice" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9252f2f14ae9"
down_revision = "293141b3c2a9"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "pro_advice_venueId_fkey",
        "pro_advice",
        "venue",
        ["venueId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )
    op.execute("COMMIT")
    op.execute("BEGIN")
    op.execute('ALTER TABLE "pro_advice" VALIDATE CONSTRAINT "pro_advice_venueId_fkey"')


def downgrade() -> None:
    op.drop_constraint("pro_advice_venueId_fkey", "pro_advice", type_="foreignkey")
