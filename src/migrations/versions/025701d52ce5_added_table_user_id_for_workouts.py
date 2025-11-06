"""added table user_id for workouts

Revision ID: 025701d52ce5
Revises: c3c2a0fb2efd
Create Date: 2025-11-07 01:24:31.890421

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "025701d52ce5"
down_revision: Union[str, Sequence[str], None] = "c3c2a0fb2efd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "workouts", sa.Column("user_id", sa.Integer(), nullable=False)
    )
    op.create_foreign_key(None, "workouts", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "workouts", type_="foreignkey")
    op.drop_column("workouts", "user_id")

