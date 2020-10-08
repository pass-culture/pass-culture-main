"""Normalize beneficiary import

Revision ID: 2920fd4ec916
Revises: 7906543b4e96
Create Date: 2019-07-19 08:23:50.213592

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import func, ForeignKey

# revision identifiers, used by Alembic.
revision = '2920fd4ec916'
down_revision = '7906543b4e96'
branch_labels = None
depends_on = None

previous_values = ('DUPLICATE', 'CREATED', 'ERROR', 'REJECTED')
new_values = ('DUPLICATE', 'CREATED', 'ERROR', 'REJECTED', 'RETRY')
previous_enum = sa.Enum(*previous_values, name='importstatus')
temporary_enum = sa.Enum(*new_values, name='tmp_importstatus')
new_enum = sa.Enum(*new_values, name='importstatus')


def upgrade():
    op.create_table(
        'beneficiary_import_status',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('status', temporary_enum, nullable=False),
        sa.Column('date', sa.DateTime, nullable=False, server_default=func.now()),
        sa.Column('detail', sa.VARCHAR(255), nullable=True),
        sa.Column('beneficiaryImportId', sa.BigInteger, ForeignKey('beneficiary_import.id'), nullable=False),
        sa.Column('authorId', sa.BigInteger, ForeignKey('user.id'), nullable=True),
        sa.Column('demarcheSimplifieeApplicationId', sa.BigInteger, nullable=False)
    )

    op.execute("""
    ALTER TABLE beneficiary_import
    ALTER COLUMN status
    TYPE tmp_importstatus
    USING status::text::tmp_importstatus
    ;
    """)

    op.execute("""
    INSERT INTO
        beneficiary_import_status("beneficiaryImportId", status, date, detail, "demarcheSimplifieeApplicationId")
    SELECT
        id, status, date, detail, "demarcheSimplifieeApplicationId"
    FROM
        beneficiary_import
    ;
    """)

    op.execute("""
    UPDATE beneficiary_import_status a
    SET "beneficiaryImportId" = (
        SELECT MIN(b."beneficiaryImportId")
        FROM beneficiary_import_status b
        WHERE a."demarcheSimplifieeApplicationId" = b."demarcheSimplifieeApplicationId"
    )
    ;
    """)

    op.execute("""
    DELETE FROM beneficiary_import
    WHERE id NOT IN (SELECT DISTINCT "beneficiaryImportId" FROM beneficiary_import_status)
    ;
    """)

    op.drop_column('beneficiary_import_status', 'demarcheSimplifieeApplicationId')

    op.drop_column('beneficiary_import', 'status')
    op.drop_column('beneficiary_import', 'date')
    op.drop_column('beneficiary_import', 'detail')

    previous_enum.drop(op.get_bind(), checkfirst=False)
    new_enum.create(op.get_bind(), checkfirst=False)

    op.execute("""
    ALTER TABLE beneficiary_import_status
    ALTER COLUMN status
    TYPE importstatus
    USING status::text::importstatus
    """)

    temporary_enum.drop(op.get_bind(), checkfirst=False)

    op.create_unique_constraint(
        'uniq_beneficiary_import_demarcheSimplifieeApplicationId',
        'beneficiary_import', ['demarcheSimplifieeApplicationId']
    )


def downgrade():
    op.drop_constraint('uniq_beneficiary_import_demarcheSimplifieeApplicationId', 'beneficiary_import')

    temporary_enum.create(op.get_bind(), checkfirst=False)

    op.add_column('beneficiary_import', sa.Column('status', temporary_enum, nullable=True))
    op.add_column('beneficiary_import', sa.Column('date', sa.DateTime, nullable=True, server_default=func.now()))
    op.add_column('beneficiary_import', sa.Column('detail', sa.VARCHAR(255), nullable=True))

    op.execute("""
    ALTER TABLE beneficiary_import_status
    ALTER COLUMN status
    TYPE tmp_importstatus
    USING status::text::tmp_importstatus
    ;
    """)

    op.execute("""
    INSERT INTO
        beneficiary_import(status, date, detail, "beneficiaryId", "demarcheSimplifieeApplicationId")
    SELECT
        bis.status,
        bis.date,
        bis.detail,
        bi."beneficiaryId",
        bi."demarcheSimplifieeApplicationId"
    FROM
        beneficiary_import_status as bis
    JOIN
        beneficiary_import as bi
    ON
        bis."beneficiaryImportId" = bi.id     
    ;
    """)

    op.drop_table('beneficiary_import_status')

    op.execute("""
    DELETE FROM beneficiary_import
    WHERE status IS NULL
    ;
    """)

    op.alter_column('beneficiary_import', 'status', nullable=False)
    op.alter_column('beneficiary_import', 'date', nullable=False)

    op.execute("""
    ALTER TABLE beneficiary_import
    ALTER COLUMN status
    TYPE importstatus
    USING status::text::importstatus
    ;
    """)
    temporary_enum.drop(op.get_bind(), checkfirst=False)
