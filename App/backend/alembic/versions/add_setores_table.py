"""add setores table

Revision ID: add_setores_table
Revises: 19cd0b3623a9
Create Date: 2025-07-31 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_setores_table'
down_revision = '19cd0b3623a9'
branch_labels = None
depends_on = None


def upgrade():
    # Create setores table
    op.create_table('setores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on nome
    op.create_index('ix_setores_nome', 'setores', ['nome'], unique=True)
    
    # Insert default setores
    op.execute("""
        INSERT INTO setores (nome, descricao, ativo) VALUES
        ('UTI', 'Unidade de Terapia Intensiva', true),
        ('UTI NEONATAL', 'Unidade de Terapia Intensiva Neonatal', true),
        ('UTI PEDIÁTRICA', 'Unidade de Terapia Intensiva Pediátrica', true),
        ('UTI CARDIOVASCULAR', 'Unidade de Terapia Intensiva Cardiovascular', true),
        ('UTI NEUROLÓGICA', 'Unidade de Terapia Intensiva Neurológica', true),
        ('UTI RESPIRATÓRIA', 'Unidade de Terapia Intensiva Respiratória', true),
        ('UTI TRAUMA', 'Unidade de Terapia Intensiva Trauma', true),
        ('UTI QUEIMADOS', 'Unidade de Terapia Intensiva Queimados', true),
        ('UTI INFECTOLOGIA', 'Unidade de Terapia Intensiva Infectologia', true),
        ('UTI TRANSPLANTE', 'Unidade de Terapia Intensiva Transplante', true),
        ('UTI GERIÁTRICA', 'Unidade de Terapia Intensiva Geriátrica', true),
        ('UTI ONCOLÓGICA', 'Unidade de Terapia Intensiva Oncológica', true),
        ('UTI PÓS-OPERATÓRIO', 'Unidade de Terapia Intensiva Pós-Operatório', true),
        ('UTI CIRÚRGICA', 'Unidade de Terapia Intensiva Cirúrgica', true),
        ('UTI CLÍNICA', 'Unidade de Terapia Intensiva Clínica', true),
        ('UTI MISTA', 'Unidade de Terapia Intensiva Mista', true),
        ('UTI CORONARIANA', 'Unidade de Terapia Intensiva Coronariana', true),
        ('UTI RESPIRATÓRIA ADULTO', 'Unidade de Terapia Intensiva Respiratória Adulto', true),
        ('UTI RESPIRATÓRIA PEDIÁTRICA', 'Unidade de Terapia Intensiva Respiratória Pediátrica', true),
        ('UTI NEUROCIRÚRGICA', 'Unidade de Terapia Intensiva Neurocirúrgica', true)
    """)


def downgrade():
    # Drop setores table
    op.drop_index('ix_setores_nome', table_name='setores')
    op.drop_table('setores') 