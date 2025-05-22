"""Add index on EducationalInstitution (type name city) concat"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "04caadcaa652"
down_revision = "6be778edb2f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_educational_institution_type_name_city" ON public.educational_institution
            USING gin (("institutionType" || ' ' || "name" || ' ' || "city") gin_trgm_ops);
        """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
    op.execute("BEGIN")


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index(
        index_name="ix_educational_institution_type_name_city",
        table_name="educational_institution",
        postgresql_concurrently=True,
        if_exists=True,
    )
    op.execute("BEGIN")
