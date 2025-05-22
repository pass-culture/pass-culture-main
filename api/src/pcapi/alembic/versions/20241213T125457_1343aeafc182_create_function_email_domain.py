"""create SQL function: email_domain"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1343aeafc182"
down_revision = "741084b8cec2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            """
            CREATE OR REPLACE FUNCTION public.email_domain(text)
                RETURNS text
                LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT AS
            $$
                SELECT substring($1 from '@(.*)$')
            $$
            ;
            """
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""DROP FUNCTION IF EXISTS public.email_domain;""")
