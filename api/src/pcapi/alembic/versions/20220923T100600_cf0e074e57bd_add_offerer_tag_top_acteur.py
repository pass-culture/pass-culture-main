"""add_offerer_tag_top_acteur
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cf0e074e57bd"
down_revision = "685f32d7cb22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO offerer_tag (name, label, description)
        VALUES ('top-acteur', 'Top Acteur', 'Acteur prioritaire dans les objectifs d''acquisition')
        ON CONFLICT (name) DO UPDATE SET label='Top Acteur', description='Acteur prioritaire dans les objectifs d''acquisition'
        """
    )


def downgrade() -> None:
    pass
