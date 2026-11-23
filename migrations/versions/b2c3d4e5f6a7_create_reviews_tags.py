from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = '351571be2630'

branch_labels = None
depends_on = None


def upgrade() -> None:

    # CREATE REVIEWS TABLE

    op.create_table(
        'reviews',

        sa.Column('uid', sa.UUID(), nullable=False),

        sa.Column('rating', sa.Integer(), nullable=False),

        sa.Column('review_text', sa.String(), nullable=False),

        sa.Column('user_uid', sa.UUID(), nullable=True),

        sa.Column('book_uid', sa.UUID(), nullable=True),

        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),

        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),

        sa.ForeignKeyConstraint(
            ['user_uid'],
            ['users.uid']
        ),

        sa.ForeignKeyConstraint(
            ['book_uid'],
            ['books.uid']
        ),

        sa.PrimaryKeyConstraint('uid')
    )

    # CREATE TAGS TABLE

    op.create_table(
        'tags',

        sa.Column('uid', sa.UUID(), nullable=False),

        sa.Column('name', sa.String(), nullable=False),

        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),

        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),

        sa.PrimaryKeyConstraint('uid')
    )


def downgrade() -> None:

    op.drop_table('tags')
    op.drop_table('reviews')