"""scheduler state persistence (B1)

Adds scheduler_source_status and scheduler_heartbeat tables so the
dedicated cara-scheduler worker service (Render background worker, see
render.yaml) can persist per-source refresh state and a runner heartbeat
to Postgres, where the web service reads them via
utils/scheduler_state_store.py.

Revision ID: b1schedulerstate
Revises: fa2d1f01156f
Create Date: 2026-05-22

The matching utils/scheduler_state_store.py also runs CREATE TABLE
IF NOT EXISTS as a safety net at first use, so a worker process can
boot against a fresh database even if alembic has not yet been run.
This migration is the authoritative declaration; the safety net just
prevents a chicken-and-egg deadlock on the very first deploy.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'b1schedulerstate'
down_revision: Union[str, Sequence[str], None] = 'fa2d1f01156f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _existing_tables() -> set:
    """Tables already present in the target database.

    The app also creates these tables via db.create_all() at startup, and
    utils/scheduler_state_store.py runs CREATE TABLE IF NOT EXISTS as a
    safety net. So by the time this migration runs the tables may already
    exist; guard each create/drop to stay idempotent on both fresh and
    already-populated databases.
    """
    return set(inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    existing = _existing_tables()
    if 'scheduler_source_status' not in existing:
        op.create_table(
            'scheduler_source_status',
            sa.Column('source_id', sa.String(length=64), nullable=False),
            sa.Column('last_refresh', sa.DateTime(), nullable=True),
            sa.Column('next_refresh', sa.DateTime(), nullable=True),
            sa.Column('last_attempt', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(length=16), nullable=False, server_default='pending'),
            sa.Column('last_error', sa.Text(), nullable=True),
            sa.Column('refresh_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('in_progress', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.PrimaryKeyConstraint('source_id'),
        )
    if 'scheduler_heartbeat' not in existing:
        op.create_table(
            'scheduler_heartbeat',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('runner_id', sa.String(length=128), nullable=True),
            sa.Column('last_beat_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.PrimaryKeyConstraint('id'),
        )


def downgrade() -> None:
    existing = _existing_tables()
    if 'scheduler_heartbeat' in existing:
        op.drop_table('scheduler_heartbeat')
    if 'scheduler_source_status' in existing:
        op.drop_table('scheduler_source_status')
