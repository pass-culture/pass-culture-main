"""Remove administrative from venue type"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ded99f0acd9e"
down_revision = "62d5ff24ee22"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""UPDATE venue SET "venueTypeCode" = 'OTHER' WHERE "venueTypeCode" = 'ADMINISTRATIVE';""")


def downgrade() -> None:
    pass
