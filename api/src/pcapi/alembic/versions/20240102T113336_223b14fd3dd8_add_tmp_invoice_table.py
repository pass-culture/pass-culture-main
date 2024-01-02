"""Add tmp_invoice table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "223b14fd3dd8"
down_revision = "ec0f52ada8fa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tmp_invoice",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("date", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("venueBankAccountLinkId", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["venueBankAccountLinkId"],
            ["venue_bank_account_link.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        op.f("ix_tmp_invoice_venueBankAccountLinkId"), "tmp_invoice", ["venueBankAccountLinkId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_tmp_invoice_venueBankAccountLinkId"), table_name="tmp_invoice")
    op.drop_table("tmp_invoice")
