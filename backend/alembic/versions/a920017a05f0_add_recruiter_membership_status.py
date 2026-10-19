"""add recruiter membership status

Revision ID: a920017a05f0
Revises: 3ef6d78695e5
Create Date: 2026-10-16 17:10:54.536012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a920017a05f0'
down_revision: Union[str, Sequence[str], None] = '3ef6d78695e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    membership_status = sa.Enum(
        "PENDING",
        "ACTIVE",
        "REJECTED",
        name="membershipstatus",
    )

    # Create the PostgreSQL enum type before adding the column.
    membership_status.create(op.get_bind(), checkfirst=True)

    # Add the column with a temporary database default so existing
    # rows receive a valid status.
    op.add_column(
        "recruiter_companies",
        sa.Column(
            "status",
            membership_status,
            nullable=False,
            server_default="PENDING",
        ),
    )

    # Remove the database default after the column is populated.
    op.alter_column(
        "recruiter_companies",
        "status",
        existing_type=membership_status,
        existing_nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    membership_status = sa.Enum(
        "PENDING",
        "ACTIVE",
        "REJECTED",
        name="membershipstatus",
    )

    op.drop_column("recruiter_companies", "status")

    # Drop the enum only after its column has been removed.
    membership_status.drop(op.get_bind(), checkfirst=True)

