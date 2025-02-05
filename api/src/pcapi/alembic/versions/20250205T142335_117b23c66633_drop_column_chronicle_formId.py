"""drom column chronicle.formId"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "117b23c66633"
down_revision = "8e97f8429b91"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ix_chronicle_formId", "chronicle", type_="unique")
    op.drop_column("chronicle", "formId")


def downgrade() -> None:
    op.add_column("chronicle", sa.Column("formId", sa.TEXT(), autoincrement=False, nullable=False))
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint("ix_chronicle_formId", "chronicle", ["formId"])
