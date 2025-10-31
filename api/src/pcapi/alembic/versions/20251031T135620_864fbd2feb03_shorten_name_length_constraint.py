"""Shorten "name" column length constraint in "highlight" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "864fbd2feb03"
down_revision = "c23249637c33"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "highlight_name_check",
        table_name="highlight",
        type_="check",
        if_exists=True,
    )
    op.create_check_constraint(
        "highlight_name_check",
        table_name="highlight",
        condition="length(name) <= 60",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "highlight_name_check",
        table_name="highlight",
        type_="check",
        if_exists=True,
    )
    op.create_check_constraint(
        "highlight_name_check",
        table_name="highlight",
        condition="length(name) <= 200",
        postgresql_not_valid=True,
    )
