"""delete_ff_force_phone_validation
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4054f720ac9f"
down_revision = "090834b497b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM feature where name = 'FORCE_PHONE_VALIDATION'")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES ('FORCE_PHONE_VALIDATION', 'Forcer l étape de validation du téléphone pour devenir bénéficiaire', false)
    """
    )
