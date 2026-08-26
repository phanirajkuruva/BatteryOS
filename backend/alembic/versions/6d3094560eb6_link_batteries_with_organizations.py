"""link batteries with organizations

Revision ID: 6d3094560eb6
Revises: 4bb86fb8485a
Create Date: 2026-08-25 19:00:19.647885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d3094560eb6'
down_revision: Union[str, Sequence[str], None] = '4bb86fb8485a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add the new column as nullable first
    op.add_column(
        "batteries",
        sa.Column("organization_id", sa.Integer(), nullable=True)
    )

    # Step 2: Assign existing batteries to Organization ID = 1
    op.execute("""
        UPDATE batteries
        SET organization_id = 1
    """)

    # Step 3: Make the column NOT NULL
    op.alter_column(
        "batteries",
        "organization_id",
        nullable=False
    )

    # Step 4: Create Foreign Key
    op.create_foreign_key(
        "fk_batteries_organization",
        "batteries",
        "organizations",
        ["organization_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_batteries_organization",
        "batteries",
        type_="foreignkey"
    )

    op.drop_column("batteries", "organization_id")