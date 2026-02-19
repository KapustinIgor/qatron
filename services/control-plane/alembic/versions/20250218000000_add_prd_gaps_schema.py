"""Add service tokens, suite/feature/dataset updates for PRD gaps.

Revision ID: 20250218000000
Revises:
Create Date: 2025-02-18

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250218000000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Service tokens table
    op.create_table(
        "service_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_service_tokens_organization_id"), "service_tokens", ["organization_id"], unique=False)
    op.create_index(op.f("ix_service_tokens_project_id"), "service_tokens", ["project_id"], unique=False)
    op.create_index(op.f("ix_service_tokens_token_hash"), "service_tokens", ["token_hash"], unique=True)
    op.create_index(op.f("ix_service_tokens_is_active"), "service_tokens", ["is_active"], unique=False)

    # 2. Suites: add require_dataset_health
    op.add_column("suites", sa.Column("require_dataset_health", sa.Boolean(), nullable=True, server_default=sa.false()))

    # 3. Scenarios: add scenario_type and examples
    op.add_column("scenarios", sa.Column("scenario_type", sa.String(50), nullable=True, server_default="scenario"))
    op.add_column("scenarios", sa.Column("examples", sa.Text(), nullable=True))

    # 4. Steps: add order and data_table
    op.add_column("steps", sa.Column("order", sa.Integer(), nullable=True, server_default=sa.text("0")))
    op.add_column("steps", sa.Column("data_table", sa.Text(), nullable=True))
    # Ensure order is not null for new rows
    op.alter_column("steps", "order", existing_type=sa.Integer(), nullable=False, server_default=sa.text("0"))

    # 5. Dataset versions: add storage_path and expectations
    op.add_column("dataset_versions", sa.Column("storage_path", sa.String(500), nullable=True))
    op.add_column("dataset_versions", sa.Column("expectations", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("dataset_versions", "expectations")
    op.drop_column("dataset_versions", "storage_path")
    op.drop_column("steps", "data_table")
    op.drop_column("steps", "order")
    op.drop_column("scenarios", "examples")
    op.drop_column("scenarios", "scenario_type")
    op.drop_column("suites", "require_dataset_health")
    op.drop_index(op.f("ix_service_tokens_is_active"), table_name="service_tokens")
    op.drop_index(op.f("ix_service_tokens_token_hash"), table_name="service_tokens")
    op.drop_index(op.f("ix_service_tokens_project_id"), table_name="service_tokens")
    op.drop_index(op.f("ix_service_tokens_organization_id"), table_name="service_tokens")
    op.drop_table("service_tokens")
