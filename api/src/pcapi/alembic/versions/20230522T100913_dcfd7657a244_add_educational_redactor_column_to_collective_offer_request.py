"""Add educationalRedactorId to collective_offer_request table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dcfd7657a244"
down_revision = "692bba538fb3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer_request", sa.Column("educationalRedactorId", sa.BigInteger(), nullable=False))
    op.create_foreign_key(
        "ix_collective_offer_request_educationalRedactorId",
        "collective_offer_request",
        "educational_redactor",
        ["educationalRedactorId"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "ix_collective_offer_request_educationalRedactorId", "collective_offer_request", type_="foreignkey"
    )
    op.drop_column("collective_offer_request", "educationalRedactorId")
