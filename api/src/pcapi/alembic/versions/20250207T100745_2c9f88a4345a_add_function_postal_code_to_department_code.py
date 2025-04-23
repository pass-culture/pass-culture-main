"""Create function postal_code_to_department_code"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2c9f88a4345a"
down_revision = "a534059325fe"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE OR REPLACE FUNCTION public.postal_code_to_department_code(text)
                RETURNS text
                LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
            $$
                SELECT CASE
                    WHEN ($1 = '97133') THEN '977'
                    WHEN ($1 = '97150') THEN '978'
                    WHEN (CAST(SUBSTRING($1 FROM 1 FOR 2) AS INTEGER) >= 97) THEN SUBSTRING($1 FROM 1 FOR 3)
                    ELSE SUBSTRING($1 FROM 1 FOR 2)
                END
            $$
            ;
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""DROP FUNCTION IF EXISTS public.postal_code_to_department_code;""")
