"""Add offerer_invitation table"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6d60c6c70ac3"
down_revision = "405f222670b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offerer_invitation",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("offererId", "email", name="unique_offerer_invitation"),
    )
    op.create_index(op.f("ix_offerer_invitation_offererId"), "offerer_invitation", ["offererId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_offerer_invitation_offererId"), table_name="offerer_invitation")
    op.drop_table("offerer_invitation")
