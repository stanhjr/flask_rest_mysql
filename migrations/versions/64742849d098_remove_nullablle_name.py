"""remove nullablle name

Revision ID: 64742849d098
Revises: 1a6335135935
Create Date: 2022-04-08 12:12:07.799150

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '64742849d098'
down_revision = '1a6335135935'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'name',
               existing_type=mysql.VARCHAR(collation='utf8_unicode_ci', length=128),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'name',
               existing_type=mysql.VARCHAR(collation='utf8_unicode_ci', length=128),
               nullable=False)
    # ### end Alembic commands ###
