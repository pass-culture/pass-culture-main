"""Drop CGR encryptedPassword column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e7f8b2b66df7"
down_revision = "d158e4b24ff2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("cgr_cinema_details", "encryptedPassword")


def downgrade() -> None:
    op.add_column("cgr_cinema_details", sa.Column("encryptedPassword", sa.TEXT(), autoincrement=False, nullable=True))
    op.execute("""update cgr_cinema_details set "encryptedPassword" = "password" """)
    op.alter_column("cgr_cinema_details", "encryptedPassword", existing_type=sa.TEXT(), nullable=False)
