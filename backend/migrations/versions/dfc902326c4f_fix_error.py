"""fix error

Revision ID: dfc902326c4f
Revises: 8781ec1e77a4
Create Date: 2025-06-18 23:52:56.687072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfc902326c4f'
down_revision = '8781ec1e77a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('order_ibfk_4'), type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['user_id'], ondelete='SET NULL')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(batch_op.f('order_ibfk_4'), 'user', ['user_id'], ['user_id'])

    # ### end Alembic commands ###
