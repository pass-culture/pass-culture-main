"""Delete unused sql functions and operator"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7d4b6b018c02"
down_revision = "083db307ac0e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""DROP OPERATOR IF EXISTS public.- (jsonb, jsonb) ;""")
    op.execute("""DROP FUNCTION IF EXISTS public.jsonb_subtract (jsonb, jsonb) ;""")
    op.execute("""DROP FUNCTION IF EXISTS public.jsonb_change_key_name (jsonb, text, text) ;""")


def downgrade() -> None:
    op.execute("""
    CREATE FUNCTION public.jsonb_change_key_name(data jsonb, old_key text, new_key text) RETURNS jsonb
        LANGUAGE sql IMMUTABLE
        AS $$
        SELECT ('{'||string_agg(to_json(CASE WHEN key = old_key THEN new_key ELSE key END)||':'||value, ',')||'}')::jsonb
        FROM (
            SELECT *
            FROM jsonb_each(data)
        ) t;
    $$;
    """)

    op.execute("""
    CREATE FUNCTION public.jsonb_subtract(arg1 jsonb, arg2 jsonb) RETURNS jsonb
        LANGUAGE sql
        AS $$
    SELECT
    COALESCE(json_object_agg(key, value), '{}')::jsonb
    FROM
    jsonb_each(arg1)
    WHERE
    (arg1 -> key) <> (arg2 -> key) OR (arg2 -> key) IS NULL
    $$;
    """)

    op.execute("""
        CREATE OPERATOR public.- (
            FUNCTION = public.jsonb_subtract,
            LEFTARG = jsonb,
            RIGHTARG = jsonb
        );
            """)
