"""Modify the constraint on venue requiring a siret or a comment"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "762d470e2aa9"
down_revision = "19faaa413a12"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "check_has_siret_xor_comment_xor_isVirtual",
        table_name="venue",
    )
    op.execute(sa.text("""UPDATE venue SET comment = 'Lieu virtuel' WHERE "isVirtual" = true;"""))
    op.create_check_constraint(
        "check_has_siret_or_comment",
        table_name="venue",
        condition=sa.text("(siret IS NOT NULL) OR (comment IS NOT NULL)"),
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_has_siret_or_comment",
        table_name="venue",
    )
    op.execute(sa.text("""UPDATE venue SET comment = NULL WHERE "isVirtual" = true;"""))
    op.create_check_constraint(
        "check_has_siret_xor_comment_xor_isVirtual",
        table_name="venue",
        condition=sa.text("""
            (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
            OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
            OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
        """),
        postgresql_not_valid=True,
    )
