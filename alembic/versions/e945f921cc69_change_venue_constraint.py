"""change_venue_constraint

Revision ID: e945f921cc69
Revises: de36871d256e
Create Date: 2019-06-20 13:07:07.348459

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e945f921cc69'
down_revision = 'de36871d256e'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('check_is_virtual_xor_has_address', 'venue')
    op.create_check_constraint(
        constraint_name='check_is_virtual_xor_has_address',
        table_name='venue',
        condition="""
        (
            "isVirtual" IS TRUE
            AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
        )
        OR
        (
            "isVirtual" IS FALSE
            AND siret is NOT NULL
            AND ("postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
        )
        OR
        (
            "isVirtual" IS FALSE
            AND (siret is NULL and comment is NOT NULL)
            AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
        )
        """
    )


def downgrade():
    op.drop_constraint('check_is_virtual_xor_has_address', 'venue')
    op.execute("""
        UPDATE venue SET address = '' WHERE siret IS NOT NULL AND address IS NULL;
    """)
    op.create_check_constraint(
        constraint_name='check_is_virtual_xor_has_address',
        table_name='venue',
        condition="""
        (
            "isVirtual" IS TRUE
            AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
        )
        OR
        (
            "isVirtual" IS FALSE
            AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
        )
        """
)
