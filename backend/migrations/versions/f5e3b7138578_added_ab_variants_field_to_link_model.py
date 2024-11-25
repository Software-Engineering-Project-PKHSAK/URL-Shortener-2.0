"""Added ab_variants field to Link model

Revision ID: f5e3b7138578
Revises: 11f0783fbad5
Create Date: 2024-11-20 01:47:43.589398

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5e3b7138578'
down_revision = '11f0783fbad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('links', sa.Column('ab_variants', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('links', 'ab_variants')
    # ### end Alembic commands ###