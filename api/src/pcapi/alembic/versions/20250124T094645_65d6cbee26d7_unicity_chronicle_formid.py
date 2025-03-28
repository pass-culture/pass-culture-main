"""enforce formId unicity for chronicles"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "65d6cbee26d7"
down_revision = "704367eff1d5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
DELETE FROM
    chronicle as c
WHERE
    -- delete when more than one is present
    c."formId" IN (
        SELECT
            form_id
        FROM (
            SELECT
                "formId" AS form_id,
                count(id) AS count_id
            FROM
                chronicle
            GROUP BY
                "formId"
        ) AS count_sub WHERE count_id>1
    )
    -- keep one from delete
    AND c.id != (
        SELECT
            id
        FROM
            chronicle
        WHERE
            "formId"=c."formId"
        ORDER BY id
        LIMIT 1
    )
"""
    )
    # the lock is not a problem if we deactivate ENABLE_CHRONICLES_SYNC
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute("select 1 -- squawk:ignore-next-statement")
        op.create_unique_constraint("ix_chronicle_formId", "chronicle", ["formId"])
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_constraint("ix_chronicle_formId", "chronicle", type_="unique")
