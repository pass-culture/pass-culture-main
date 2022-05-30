"""link_collectiveOffers_EducationalInstitution
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c3f40e7f77a"
down_revision = "e3aae72aab7f"
branch_labels = None
depends_on = None


FOREIGN_KEY_NAME = "collective_offer_educational_institution_fkey"


def upgrade() -> None:
    op.add_column("collective_offer", sa.Column("institutionId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_collective_offer_institutionId"), "collective_offer", ["institutionId"], unique=False)
    op.create_foreign_key(FOREIGN_KEY_NAME, "collective_offer", "educational_institution", ["institutionId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(FOREIGN_KEY_NAME, "collective_offer", type_="foreignkey")
    op.drop_index(op.f("ix_collective_offer_institutionId"), table_name="collective_offer")
    op.drop_column("collective_offer", "institutionId")
