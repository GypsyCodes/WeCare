-- ==========================================
-- SCRIPT PARA ADICIONAR TABELA ESCALA_USUARIOS
-- Sistema We Care - Múltiplos usuários por escala
-- ==========================================

-- Criar tabela para relacionamento múltiplos usuários por escala
CREATE TABLE IF NOT EXISTS escala_usuarios (
    id SERIAL PRIMARY KEY,
    escala_id INTEGER NOT NULL REFERENCES escalas(id) ON DELETE CASCADE,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    setor VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE NOW(),
    
    -- Índices para performance
    INDEX idx_escala_usuarios_escala_id (escala_id),
    INDEX idx_escala_usuarios_usuario_id (usuario_id),
    
    -- Constraint para evitar usuário duplicado na mesma escala
    UNIQUE KEY unique_escala_usuario (escala_id, usuario_id)
);

-- Verificar se tabela foi criada
SELECT 
    'TABELA escala_usuarios criada com sucesso!' as status,
    COUNT(*) as registros_existentes
FROM escala_usuarios;

-- Mostrar estrutura da tabela
DESCRIBE escala_usuarios;

-- ==========================================
-- SCRIPT FINALIZADO
-- ========================================== 