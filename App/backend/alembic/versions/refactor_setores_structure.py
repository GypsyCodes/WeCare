"""refactor setores structure

Revision ID: refactor_setores_structure
Revises: 19cd0b3623a9
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'refactor_setores_structure'
down_revision = '19cd0b3623a9'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Adicionar estabelecimento_id na tabela setores (se não existir)
    connection = op.get_bind()
    
    # Verificar se a coluna estabelecimento_id já existe
    result = connection.execute(text("SHOW COLUMNS FROM setores LIKE 'estabelecimento_id'"))
    if not result.fetchone():
        op.add_column('setores', sa.Column('estabelecimento_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_setores_estabelecimento_id'), 'setores', ['estabelecimento_id'], unique=False)
        op.create_foreign_key('fk_setores_estabelecimento_id', 'setores', 'estabelecimentos', ['estabelecimento_id'], ['id'], ondelete='CASCADE')
    
    # 2. Remover unique constraint do nome do setor (agora pode ter nomes iguais em estabelecimentos diferentes)
    # Verificar se o índice existe antes de tentar removê-lo
    result = connection.execute(text("SHOW INDEX FROM setores WHERE Key_name = 'ix_setores_nome'"))
    if result.fetchone():
        op.drop_index('ix_setores_nome', table_name='setores')
    op.create_index(op.f('ix_setores_nome'), 'setores', ['nome'], unique=False)
    
    # 3. Adicionar a nova coluna setor_id na tabela escala_usuarios (se não existir)
    result = connection.execute(text("SHOW COLUMNS FROM escala_usuarios LIKE 'setor_id'"))
    if not result.fetchone():
        op.add_column('escala_usuarios', sa.Column('setor_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_escala_usuarios_setor_id'), 'escala_usuarios', ['setor_id'], unique=False)
        op.create_foreign_key('fk_escala_usuarios_setor_id', 'escala_usuarios', 'setores', ['setor_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # 1. Remover coluna setor_id
    connection = op.get_bind()
    result = connection.execute(text("SHOW COLUMNS FROM escala_usuarios LIKE 'setor_id'"))
    if result.fetchone():
        op.drop_constraint('fk_escala_usuarios_setor_id', 'escala_usuarios', type_='foreignkey')
        op.drop_index(op.f('ix_escala_usuarios_setor_id'), table_name='escala_usuarios')
        op.drop_column('escala_usuarios', 'setor_id')
    
    # 2. Restaurar unique constraint no nome do setor
    result = connection.execute(text("SHOW INDEX FROM setores WHERE Key_name = 'ix_setores_nome'"))
    if result.fetchone():
        op.drop_index(op.f('ix_setores_nome'), table_name='setores')
    op.create_index('ix_setores_nome', 'setores', ['nome'], unique=True)
    
    # 3. Remover estabelecimento_id da tabela setores
    result = connection.execute(text("SHOW COLUMNS FROM setores LIKE 'estabelecimento_id'"))
    if result.fetchone():
        op.drop_constraint('fk_setores_estabelecimento_id', 'setores', type_='foreignkey')
        op.drop_index(op.f('ix_setores_estabelecimento_id'), table_name='setores')
        op.drop_column('setores', 'estabelecimento_id') 