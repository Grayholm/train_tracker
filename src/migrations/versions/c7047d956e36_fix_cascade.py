"""fix cascade

Revision ID: c7047d956e36
Revises: 025701d52ce5
Create Date: 2025-11-07 02:24:10.370096

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7047d956e36"
down_revision: Union[str, Sequence[str], None] = "025701d52ce5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("workout_exercises_workout_id_fkey"),
        "workout_exercises",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "workout_exercises",
        "workouts",
        ["workout_id"],
        ["id"],
        ondelete="CASCADE",
    )



def downgrade() -> None:
    op.drop_constraint(None, "workout_exercises", type_="foreignkey")
    op.create_foreign_key(
        op.f("workout_exercises_workout_id_fkey"),
        "workout_exercises",
        "workouts",
        ["workout_id"],
        ["id"],
    )

