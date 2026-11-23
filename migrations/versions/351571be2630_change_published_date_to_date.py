from alembic import op
import sqlalchemy as sa

revision = '351571be2630'
down_revision = '0aabcdcc7cf4'

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.alter_column(
        'books',
        'published_date',
        existing_type=sa.VARCHAR(),
        type_=sa.Date(),
        existing_nullable=False,
        postgresql_using='published_date::date'
    )


def downgrade() -> None:

    op.alter_column(
        'books',
        'published_date',
        existing_type=sa.Date(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using='published_date::text'
    )