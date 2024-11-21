"""Add ondelete CASCADE to engagements.link_id

Revision ID: 71d4524bf1c0
Revises: f5e3b7138578
Create Date: 2024-11-20 17:50:42.227350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71d4524bf1c0'
down_revision = 'f5e3b7138578'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('engagements_link_id_fkey', 'engagements', type_='foreignkey')
    op.create_foreign_key(None, 'engagements', 'links', ['link_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'engagements', type_='foreignkey')
    op.create_foreign_key('engagements_link_id_fkey', 'engagements', 'links', ['link_id'], ['id'])
    # ### end Alembic commands ###
