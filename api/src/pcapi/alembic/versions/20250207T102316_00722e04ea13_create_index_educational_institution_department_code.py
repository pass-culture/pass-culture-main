"""Create index on educational_institution department code"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "00722e04ea13"
down_revision = "117b23c66633"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        # Tested on staging: 58 seconds
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_educational_institution_department_code" ON educational_institution
            USING btree (postal_code_to_department_code("postalCode"));
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_educational_institution_department_code",
            table_name="educational_institution",
            postgresql_concurrently=True,
            if_exists=True,
        )
