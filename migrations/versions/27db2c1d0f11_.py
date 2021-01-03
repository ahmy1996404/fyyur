"""empty message

Revision ID: 27db2c1d0f11
Revises: 2f4a63301636
Create Date: 2020-11-12 10:12:28.834026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27db2c1d0f11'
down_revision = '2f4a63301636'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###