""" example de migration qui ne passe pas le lint avec une expression ignorée
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "3c9e910de34d"
down_revision = "23e2d3b322ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("-- squawk:ignore-next-statement")
    op.execute("commit")  # the rule transaction-nesting should not activate
    op.add_column("stock", sa.Column("venueId", sa.BigInteger(), nullable=False))
    op.create_index(op.f("ix_stock_venueId"), "stock", ["venueId"], unique=False)
    op.create_foreign_key(None, "stock", "venue", ["venueId"], ["id"])


def downgrade() -> None:
    op.drop_constraint("constraint_name", "stock", type_="foreignkey")
    op.drop_index(op.f("ix_stock_venueId"), table_name="stock")
    op.drop_column("stock", "venueId")
