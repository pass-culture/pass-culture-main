"""Create new tag: siren-caduc (applied from the code)
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9ed959b8d025"
down_revision = "98681bf3c6b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO offerer_tag (name, label, description)
        VALUES ('siren-caduc', 'SIREN caduc', 'Structure inactive d''après l''INSEE')
        ON CONFLICT (name) DO UPDATE SET label='SIREN caduc', description='Structure inactive d''après l''INSEE'
        """
    )


def downgrade() -> None:
    pass
