"""add_informations_to_educational_deposit

Revision ID: bb84cb0e65c2
Revises: d37e6052a854
Create Date: 2021-07-01 09:41:08.822112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb84cb0e65c2"
down_revision = "d37e6052a854"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("educational_deposit", sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False))
    op.add_column(
        "educational_deposit", sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
    )
    op.add_column("educational_deposit", sa.Column("isFinal", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("educational_deposit", "isFinal")
    op.drop_column("educational_deposit", "dateCreated")
    op.drop_column("educational_deposit", "amount")
