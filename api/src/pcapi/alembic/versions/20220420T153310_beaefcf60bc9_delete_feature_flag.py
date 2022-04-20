"""delete_feature_flag ALLOW_EMPTY_USER_PROFILING
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "beaefcf60bc9"
down_revision = "c588425fe807"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("delete from feature where name = 'ALLOW_EMPTY_USER_PROFILING'")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES ('ALLOW_EMPTY_USER_PROFILING', 'Autorise les inscriptions de bénéficiaires sans USER_PROFILING', false)
        """
    )
