"""Add retailer, category attributes, condition, is_archived to Item

Revision ID: 472adf64f560
Revises: 8ecf2ca615a3
Create Date: 2026-08-25 14:33:09.507840

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '472adf64f560'
down_revision = '8ecf2ca615a3'
branch_labels = None
depends_on = None

item_condition_enum = postgresql.ENUM(
    'new', 'like_new', 'good', 'fair', name='itemcondition'
)


def upgrade():
    # Postgres needs the enum TYPE created explicitly before a column can
    # use it — batch_alter_table's add_column doesn't do this automatically.
    item_condition_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('retailer', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('size', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('material', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('color', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('dimensions', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('storage_capacity', sa.String(length=50), nullable=True))
        batch_op.add_column(
            sa.Column(
                'condition',
                postgresql.ENUM('new', 'like_new', 'good', 'fair', name='itemcondition', create_type=False),
                nullable=True,
            )
        )
        # server_default backfills existing rows to False; dropped right
        # after since the model only needs a Python-side default going
        # forward, not a permanent DB-level one.
        batch_op.add_column(
            sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.alter_column('is_archived', server_default=None)


def downgrade():
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_column('is_archived')
        batch_op.drop_column('condition')
        batch_op.drop_column('storage_capacity')
        batch_op.drop_column('dimensions')
        batch_op.drop_column('color')
        batch_op.drop_column('material')
        batch_op.drop_column('size')
        batch_op.drop_column('retailer')

    item_condition_enum.drop(op.get_bind(), checkfirst=True)
