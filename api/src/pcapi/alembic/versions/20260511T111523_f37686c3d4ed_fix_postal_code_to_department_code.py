"""Fix SQL function postal_code_to_department_code"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f37686c3d4ed"
down_revision = "734b78b841f2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.postal_code_to_department_code(text) RETURNS text
        LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
            AS $_$
                SELECT CASE
                    WHEN ($1 = '97133') THEN '977'
                    WHEN ($1 = '97150') THEN '978'
                    WHEN (CAST(SUBSTRING($1 FROM 1 FOR 2) AS INTEGER) >= 97) THEN SUBSTRING($1 FROM 1 FOR 3)
                     WHEN (SUBSTRING($1 FROM 1 FOR 3) IN ('202', '206')) THEN '2B'
                     WHEN (SUBSTRING($1 FROM 1 FOR 2) = '20') THEN '2A'
                    ELSE SUBSTRING($1 FROM 1 FOR 2)
                END
            $_$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.postal_code_to_department_code(text) RETURNS text
        LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
            AS $_$
                SELECT CASE
                    WHEN ($1 = '97133') THEN '977'
                    WHEN ($1 = '97150') THEN '978'
                    WHEN (CAST(SUBSTRING($1 FROM 1 FOR 2) AS INTEGER) >= 97) THEN SUBSTRING($1 FROM 1 FOR 3)
                    ELSE SUBSTRING($1 FROM 1 FOR 2)
                END
            $_$;
        """
    )
