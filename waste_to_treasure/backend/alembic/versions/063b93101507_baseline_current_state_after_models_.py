"""baseline: current state after models reorganization

This is a baseline migration created to sync Alembic with the current database state
after the previous migration files were removed during Cognito integration.

Revision ID: 063b93101507
Revises: 
Create Date: 2025-11-07 13:17:23.602987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '063b93101507'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
