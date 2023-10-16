"""link tables iris_france and user
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d42246a7f9ba"
down_revision = "f81aecdc3793"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.add_column("user", sa.Column("irisFranceId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_user_irisFranceId"), "user", ["irisFranceId"], unique=False)
    op.create_foreign_key(
        "user_iris_france_fk", "user", "iris_france", ["irisFranceId"], ["id"], postgresql_not_valid=True
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_constraint("user_iris_france_fk", "user", type_="foreignkey")
    op.drop_index(op.f("ix_user_irisFranceId"), table_name="user")
    op.drop_column("user", "irisFranceId")
