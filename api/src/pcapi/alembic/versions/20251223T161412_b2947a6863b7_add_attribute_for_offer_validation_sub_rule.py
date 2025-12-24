"""add two new filters attribute for offer_validation_sub_rule"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b2947a6863b7"
down_revision = "b1aca0fa5857"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE IF NOT EXISTS 'AUTHOR';")
    op.execute("ALTER TYPE offer_validation_attribute ADD VALUE IF NOT EXISTS 'PUBLISHER';")


def downgrade() -> None:
    op.execute("ALTER TYPE offer_validation_attribute RENAME TO offer_validation_attribute_old")
    op.execute("""
        CREATE TYPE offer_validation_attribute AS ENUM (
            'CLASS_NAME',
            'NAME',
            'DESCRIPTION',
            'SIREN',
            'CATEGORY_ID',
            'SUBCATEGORY_ID',
            'WITHDRAWAL_DETAILS',
            'MAX_PRICE',
            'PRICE',
            'PRICE_DETAIL',
            'SHOW_SUB_TYPE',
            'ID',
            'TEXT',
            'FORMATS'
        );
    """)
    op.execute("ALTER TABLE offer_validation_sub_rule ADD COLUMN attribute_tmp text;")
    op.execute('UPDATE offer_validation_sub_rule SET attribute_tmp="attribute"::text;')
    op.execute('ALTER TABLE offer_validation_sub_rule DROP COLUMN "attribute";')
    op.execute("ALTER TABLE offer_validation_sub_rule ADD COLUMN attribute offer_validation_attribute;")
    op.execute('UPDATE offer_validation_sub_rule SET "attribute"=attribute_tmp::offer_validation_attribute;')
    op.execute('ALTER TABLE offer_validation_sub_rule ALTER COLUMN "attribute" SET NOT NULL;')
    op.execute('ALTER TABLE offer_validation_sub_rule DROP COLUMN "attribute_tmp";')
    op.execute("DROP TYPE IF EXISTS offer_validation_attribute_old")
