"""adding long_url to engagement

Revision ID: 1ebd5c23446f
Revises: 71d4524bf1c0
Create Date: 2024-11-21 11:48:15.998445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ebd5c23446f'
down_revision = '71d4524bf1c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('engagements', sa.Column('long_url', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('engagements', 'long_url')
    # ### end Alembic commands ###