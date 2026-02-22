"""Add pipeline execution tracking models

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2024-01-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e7f8a9b0c1d2'  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Import UUID type
    from sqlalchemy.dialects.postgresql import UUID
    
    # Create pipeline_runs table
    op.create_table(
        'pipeline_runs',
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('pipeline_id', sa.Integer(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('state', sa.Enum('INIT', 'QUEUED', 'RUNNING', 'PARTIAL_FAIL', 'RETRY', 
                                   'HARD_FAIL', 'HALTED', 'COMPLETED', 'CANCELLED', 
                                   name='pipelinerunstate'), nullable=False),
        sa.Column('current_step', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('config_snapshot', sa.JSON(), nullable=False),
        sa.Column('user_assets', sa.JSON(), nullable=True),
        sa.Column('execution_policy', sa.JSON(), nullable=True),
        sa.Column('outputs', sa.JSON(), nullable=True),
        sa.Column('artifacts', sa.JSON(), nullable=True),
        sa.Column('total_failures', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('celery_task_id', sa.String(), nullable=True),
        sa.Column('run_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('run_id'),
        sa.ForeignKeyConstraint(['pipeline_id'], ['pipelines.id'], )
    )
    
    # Create indexes
    op.create_index(op.f('ix_pipeline_runs_run_id'), 'pipeline_runs', ['run_id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_pipeline_id'), 'pipeline_runs', ['pipeline_id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_user_id'), 'pipeline_runs', ['user_id'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_state'), 'pipeline_runs', ['state'], unique=False)
    op.create_index(op.f('ix_pipeline_runs_celery_task_id'), 'pipeline_runs', ['celery_task_id'], unique=False)
    
    # Create pipeline_run_steps table
    op.create_table(
        'pipeline_run_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('step_name', sa.String(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('state', sa.Enum('PENDING', 'START', 'SUCCESS', 'FAIL', 'RETRY', 
                                   'SKIPPED', 'TIMEOUT', name='stepstate'), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('input_summary', sa.JSON(), nullable=True),
        sa.Column('output_summary', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_type', sa.String(), nullable=True),
        sa.Column('step_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['run_id'], ['pipeline_runs.run_id'], )
    )
    
    # Create indexes
    op.create_index(op.f('ix_pipeline_run_steps_run_id'), 'pipeline_run_steps', ['run_id'], unique=False)
    
    # Create pipeline_events table
    op.create_table(
        'pipeline_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.String(), nullable=False),
        sa.Column('run_id', sa.String(), nullable=False),
        sa.Column('pipeline_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.Enum('PIPELINE_CREATED', 'PIPELINE_STARTED', 'PIPELINE_COMPLETED', 
                                        'PIPELINE_FAILED', 'PIPELINE_HALTED', 'PIPELINE_CANCELLED',
                                        'STEP_START', 'STEP_SUCCESS', 'STEP_FAIL', 'STEP_RETRY', 
                                        'STEP_SKIP', 'STEP_TIMEOUT',
                                        'AGENT_INVOKED', 'AGENT_COMPLETED', 'AGENT_ERROR',
                                        'STATE_TRANSITION', 'QUALITY_CHECK', 
                                        'RETRY_LIMIT_REACHED', 'FAILURE_LIMIT_REACHED',
                                        name='eventtype'), nullable=False),
        sa.Column('level', sa.Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 
                                   name='loglevel'), nullable=False),
        sa.Column('step_name', sa.String(), nullable=True),
        sa.Column('agent_name', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('previous_state', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('event_metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['run_id'], ['pipeline_runs.run_id'], )
    )
    
    # Create indexes
    op.create_index(op.f('ix_pipeline_events_event_id'), 'pipeline_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_pipeline_events_run_id'), 'pipeline_events', ['run_id'], unique=False)
    op.create_index(op.f('ix_pipeline_events_pipeline_id'), 'pipeline_events', ['pipeline_id'], unique=False)
    op.create_index(op.f('ix_pipeline_events_timestamp'), 'pipeline_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_pipeline_events_event_type'), 'pipeline_events', ['event_type'], unique=False)
    
    # Create research_contexts table
    op.create_table(
        'research_contexts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('research_id', sa.String(), nullable=False),
        sa.Column('topic', sa.String(), nullable=False),
        sa.Column('depth', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('context_pack', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('source_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_research_contexts_research_id'), 'research_contexts', ['research_id'], unique=True)
    op.create_index(op.f('ix_research_contexts_topic'), 'research_contexts', ['topic'], unique=False)
    op.create_index(op.f('ix_research_contexts_expires_at'), 'research_contexts', ['expires_at'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_research_contexts_expires_at'), table_name='research_contexts')
    op.drop_index(op.f('ix_research_contexts_topic'), table_name='research_contexts')
    op.drop_index(op.f('ix_research_contexts_research_id'), table_name='research_contexts')
    op.drop_table('research_contexts')
    
    op.drop_index(op.f('ix_pipeline_events_event_type'), table_name='pipeline_events')
    op.drop_index(op.f('ix_pipeline_events_timestamp'), table_name='pipeline_events')
    op.drop_index(op.f('ix_pipeline_events_pipeline_id'), table_name='pipeline_events')
    op.drop_index(op.f('ix_pipeline_events_run_id'), table_name='pipeline_events')
    op.drop_index(op.f('ix_pipeline_events_event_id'), table_name='pipeline_events')
    op.drop_table('pipeline_events')
    
    op.drop_index(op.f('ix_pipeline_run_steps_run_id'), table_name='pipeline_run_steps')
    op.drop_table('pipeline_run_steps')
    
    op.drop_index(op.f('ix_pipeline_runs_celery_task_id'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_state'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_user_id'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_pipeline_id'), table_name='pipeline_runs')
    op.drop_index(op.f('ix_pipeline_runs_run_id'), table_name='pipeline_runs')
    op.drop_table('pipeline_runs')
    
    # Drop enums
    sa.Enum(name='loglevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='eventtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='stepstate').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='pipelinerunstate').drop(op.get_bind(), checkfirst=True)
