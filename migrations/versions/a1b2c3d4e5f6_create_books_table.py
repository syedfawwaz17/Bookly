from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'd69b834ce02e'

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        'books',

        sa.Column('uid', sa.UUID(), nullable=False),

        sa.Column('title', sa.String(), nullable=False),

        sa.Column('author', sa.String(), nullable=False),

        sa.Column('publisher', sa.String(), nullable=False),

        sa.Column('published_date', sa.String(), nullable=False),

        sa.Column('page_count', sa.Integer(), nullable=False),

        sa.Column('language', sa.String(), nullable=False),

        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),

        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),

        sa.PrimaryKeyConstraint('uid')
    )


def downgrade() -> None:

    op.drop_table('books')