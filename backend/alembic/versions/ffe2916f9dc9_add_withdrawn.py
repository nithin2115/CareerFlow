"""add withdrawn

Revision ID: ffe2916f9dc9
Revises: 51c3041c84c1
Create Date: 2026-10-22 14:02:36.271661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffe2916f9dc9'
down_revision: Union[str, Sequence[str], None] = '51c3041c84c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute(
        "ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'WITHDRAWN'"
    )


def downgrade() -> None:
    # PostgreSQL does not directly support removing an enum value.
    # Keep WITHDRAWN in the database during downgrade.
    pass
