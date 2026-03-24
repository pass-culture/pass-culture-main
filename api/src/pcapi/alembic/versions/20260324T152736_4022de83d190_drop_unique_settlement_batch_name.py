"""Drop unique constraint on settlement_batch.name"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4022de83d190"
down_revision = "3b3ffca589b5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint(op.f("settlement_batch_name_key"), "settlement_batch", type_="unique", if_exists=True)


def downgrade() -> None:
    # Table not used in production yet => no need to re-create unique constraint
    pass
