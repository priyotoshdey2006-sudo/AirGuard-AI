"""Add functional geography GiST index on aqi_records for metric ST_DWithin queries.

Revision ID: 003_functional_geog_index
Revises: 002_spatial
Create Date: 2026-11-21 22:35:00.000000
"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_functional_geog_index"
down_revision: Union[str, None] = "002_spatial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute(
            "CREATE INDEX IF NOT EXISTS idx_aqi_records_geom_geog "
            "ON aqi_records USING gist (cast(geom as geography));"
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("DROP INDEX IF EXISTS idx_aqi_records_geom_geog;")
