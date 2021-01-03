"""empty message

Revision ID: 33b1a33d824e
Revises: e095df5e326b
Create Date: 2020-11-13 07:58:54.417302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33b1a33d824e'
down_revision = 'e095df5e326b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###