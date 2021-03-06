"""empty message

Revision ID: 448eb611b0e3
Revises: a26e71289bb5
Create Date: 2020-11-13 07:09:17.464019

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '448eb611b0e3'
down_revision = 'a26e71289bb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
