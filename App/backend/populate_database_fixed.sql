-- ==========================================
-- SCRIPT CORRIGIDO PARA POPULAR BANCO DE DADOS
-- Sistema We Care - Dados Mock para Enfermeiros
-- ==========================================

-- Limpar dados existentes de forma segura (DELETE em ordem correta)
DELETE FROM escala_usuarios WHERE escala_id > 0;
DELETE FROM escala_supervisores WHERE escala_id > 0;
DELETE FROM estabelecimento_profissionais WHERE estabelecimento_id > 0;
DELETE FROM transferencias_plantao WHERE id > 0;
DELETE FROM logs WHERE id > 1; -- Manter log do admin
DELETE FROM documentos WHERE id > 0;
DELETE FROM checkins WHERE id > 0;
DELETE FROM escalas WHERE id > 0;
DELETE FROM estabelecimentos WHERE id > 0;
-- Manter apenas o usuário admin na tabela usuarios
DELETE FROM usuarios WHERE id > 1;

-- ==========================================
-- 1. USUÁRIOS (Administradores, Supervisores e Enfermeiros)
-- ==========================================

-- Senha padrão para todos: hash de "123456"
-- $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG

-- SUPERVISORES DE ENFERMAGEM
INSERT INTO usuarios (nome, email, senha_hash, perfil, status, created_at) VALUES
('Enfº Coord. Carlos Mendes', 'carlos.mendes@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Supervisor', 'Ativo', NOW()),
('Enfª Coord. Ana Paula Silva', 'ana.silva@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Supervisor', 'Ativo', NOW()),
('Enfº Coord. Roberto Santos', 'roberto.santos@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Supervisor', 'Ativo', NOW());

-- ENFERMEIROS SÓCIOS
INSERT INTO usuarios (nome, email, senha_hash, perfil, status, created_at) VALUES
('Enfª Maria Silva', 'maria.silva@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº João Santos', 'joao.santos@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfª Ana Costa', 'ana.costa@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº Carlos Lima', 'carlos.lima@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfª Fernanda Rocha', 'fernanda.rocha@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº Roberto Mendes', 'roberto.mendes@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfª Patricia Gomes', 'patricia.gomes@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº Lucas Oliveira', 'lucas.oliveira@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfª Juliana Ferreira', 'juliana.ferreira@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº Rafael Almeida', 'rafael.almeida@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfª Camila Dias', 'camila.dias@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW()),
('Enfº Bruno Martins', 'bruno.martins@wecare.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewBQJhixbNDUFFCG', 'Socio', 'Ativo', NOW());

-- ==========================================
-- 2. ESTABELECIMENTOS (Hospitais e Clínicas)
-- ==========================================

INSERT INTO estabelecimentos (nome, endereco, latitude, longitude, raio_checkin, ativo, created_at) VALUES
('Hospital Santa Casa', 'Rua das Flores, 123 - Centro, São Paulo - SP', -23.5505200, -46.6333090, 100, TRUE, NOW()),
('Clínica São José', 'Av. Paulista, 456 - Bela Vista, São Paulo - SP', -23.5618000, -46.6565000, 50, TRUE, NOW()),
('UPA Central', 'Rua Central, 789 - Vila Mariana, São Paulo - SP', -23.5489000, -46.6388000, 75, TRUE, NOW()),
('Hospital das Clínicas', 'Av. Dr. Enéas de Carvalho Aguiar, 255 - Cerqueira César, São Paulo - SP', -23.5556700, -46.6696200, 120, TRUE, NOW()),
('Hospital Albert Einstein', 'Av. Albert Einstein, 627 - Morumbi, São Paulo - SP', -23.5984000, -46.7119000, 150, TRUE, NOW()),
('Clínica Vida Nova', 'Rua Augusta, 1234 - Consolação, São Paulo - SP', -23.5551000, -46.6620000, 80, TRUE, NOW()),
('Hospital Regional Norte', 'Av. Inajar de Souza, 1500 - Freguesia do Ó, São Paulo - SP', -23.4834000, -46.7297000, 90, TRUE, NOW());

-- ==========================================
-- 3. ASSOCIAÇÃO ESTABELECIMENTO-ENFERMEIROS
-- ==========================================

-- Distribuir enfermeiros pelos estabelecimentos
INSERT INTO estabelecimento_profissionais (estabelecimento_id, usuario_id, ativo, created_at) VALUES
-- Hospital Santa Casa (id: 1)
(1, 5, TRUE, NOW()),  -- Enfª Maria Silva
(1, 6, TRUE, NOW()),  -- Enfº João Santos
(1, 8, TRUE, NOW()),  -- Enfº Carlos Lima
(1, 9, TRUE, NOW()),  -- Enfª Fernanda Rocha
(1, 10, TRUE, NOW()), -- Enfº Roberto Mendes

-- Clínica São José (id: 2)
(2, 7, TRUE, NOW()),  -- Enfª Ana Costa
(2, 11, TRUE, NOW()), -- Enfª Patricia Gomes
(2, 12, TRUE, NOW()), -- Enfº Lucas Oliveira
(2, 13, TRUE, NOW()), -- Enfª Juliana Ferreira

-- UPA Central (id: 3)
(3, 14, TRUE, NOW()), -- Enfº Rafael Almeida
(3, 15, TRUE, NOW()), -- Enfª Camila Dias
(3, 16, TRUE, NOW()); -- Enfº Bruno Martins

-- ==========================================
-- 4. ESCALAS DE PLANTÃO (SEM SETORES)
-- ==========================================

-- Escalas para esta semana e próximas semanas
INSERT INTO escalas (data_inicio, data_fim, hora_inicio, hora_fim, usuario_id, estabelecimento_id, status, created_at) VALUES

-- HOJE - Plantões diurnos e noturnos
(CURDATE(), CURDATE(), '07:00', '19:00', 5, 1, 'Confirmado', NOW()),
(CURDATE(), CURDATE(), '07:00', '19:00', 8, 1, 'Confirmado', NOW()),
(CURDATE(), CURDATE(), '07:00', '19:00', 9, 1, 'Confirmado', NOW()),
(CURDATE(), CURDATE(), '12:00', '18:00', 10, 1, 'Confirmado', NOW()),
(CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 DAY), '19:00', '07:00', 6, 1, 'Confirmado', NOW()),

-- Outros estabelecimentos - HOJE
(CURDATE(), CURDATE(), '08:00', '20:00', 7, 2, 'Pendente', NOW()),
(CURDATE(), CURDATE(), '14:00', '22:00', 11, 2, 'Pendente', NOW()),
(CURDATE(), CURDATE(), '06:00', '18:00', 14, 3, 'Confirmado', NOW()),

-- AMANHÃ - Plantões 24h e normais
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00', '08:00', 7, 2, 'Pendente', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY), '07:00', '19:00', 12, 4, 'Confirmado', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00', '16:00', 15, 3, 'Confirmado', NOW()),

-- SEMANA ATUAL - Diversos plantões
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 2 DAY), '07:00', '19:00', 13, 2, 'Pendente', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), '19:00', '07:00', 16, 3, 'Confirmado', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), '12:00', '20:00', 9, 5, 'Confirmado', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 4 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY), '06:00', '14:00', 11, 5, 'Pendente', NOW()),

-- PRÓXIMA SEMANA
(DATE_ADD(CURDATE(), INTERVAL 7 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), '07:00', '19:00', 5, 1, 'Pendente', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 8 DAY), DATE_ADD(CURDATE(), INTERVAL 8 DAY), '08:00', '16:00', 8, 1, 'Pendente', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 9 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), '19:00', '07:00', 6, 1, 'Pendente', NOW()),
(DATE_ADD(CURDATE(), INTERVAL 10 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), '14:00', '22:00', 7, 2, 'Pendente', NOW());

-- ==========================================
-- 5. MÚLTIPLOS USUÁRIOS POR ESCALA
-- ==========================================

-- Associar múltiplos usuários às escalas existentes
INSERT INTO escala_usuarios (escala_id, usuario_id, setor, created_at) VALUES
-- Escala 1 (HOJE - Hospital Santa Casa)
(1, 5, 'UTI', NOW()),              -- Enfª Maria Silva - UTI
(1, 8, 'Enfermaria', NOW()),       -- Enfº Carlos Lima - Enfermaria

-- Escala 2 (HOJE - Hospital Santa Casa)
(2, 9, 'Emergência', NOW()),       -- Enfª Fernanda Rocha - Emergência
(2, 10, 'Cirurgia', NOW()),        -- Enfº Roberto Mendes - Cirurgia

-- Escala 3 (HOJE - Hospital Santa Casa)
(3, 6, 'UTI', NOW()),              -- Enfº João Santos - UTI

-- Escala 4 (HOJE - Hospital Santa Casa)
(4, 11, 'Ambulatório', NOW()),     -- Enfª Patricia Gomes - Ambulatório

-- Escala 6 (HOJE - Clínica São José)
(6, 7, 'Enfermaria', NOW()),       -- Enfª Ana Costa - Enfermaria
(6, 12, 'Ambulatório', NOW()),     -- Enfº Lucas Oliveira - Ambulatório

-- Escala 7 (HOJE - Clínica São José)
(7, 13, 'UTI', NOW()),             -- Enfª Juliana Ferreira - UTI

-- Escala 8 (HOJE - UPA Central)
(8, 14, 'Emergência', NOW()),      -- Enfº Rafael Almeida - Emergência
(8, 15, 'UTI', NOW()),             -- Enfª Camila Dias - UTI

-- Escala 9 (24h - Clínica São José)
(9, 16, 'Enfermaria', NOW()),      -- Enfº Bruno Martins - Enfermaria

-- Escala 10 (AMANHÃ - Hospital das Clínicas)
(10, 5, 'Cirurgia', NOW()),        -- Enfª Maria Silva - Cirurgia
(10, 7, 'UTI', NOW()),             -- Enfª Ana Costa - UTI

-- Escala 11 (AMANHÃ - UPA Central)
(11, 15, 'Emergência', NOW()),     -- Enfª Camila Dias - Emergência

-- Escala 12 (Próximos dias)
(12, 13, 'Enfermaria', NOW()),     -- Enfª Juliana Ferreira - Enfermaria
(12, 16, 'Ambulatório', NOW()),    -- Enfº Bruno Martins - Ambulatório

-- Escala 13 (Próximos dias)
(13, 9, 'UTI', NOW()),             -- Enfª Fernanda Rocha - UTI

-- Escala 14 (Próximos dias)
(14, 11, 'Emergência', NOW()),     -- Enfª Patricia Gomes - Emergência
(14, 14, 'Cirurgia', NOW()),       -- Enfº Rafael Almeida - Cirurgia

-- Escala 15 (Próxima semana)
(15, 8, 'Enfermaria', NOW()),      -- Enfº Carlos Lima - Enfermaria

-- Escala 16 (Próxima semana)
(16, 6, 'UTI', NOW()),             -- Enfº João Santos - UTI
(16, 12, 'Ambulatório', NOW()),    -- Enfº Lucas Oliveira - Ambulatório

-- Escala 17 (Próxima semana)
(17, 10, 'Emergência', NOW()),     -- Enfº Roberto Mendes - Emergência

-- Escala 18 (Próxima semana)
(18, 7, 'Enfermaria', NOW());      -- Enfª Ana Costa - Enfermaria

-- ==========================================
-- 6. SUPERVISORES DE ESCALAS
-- ==========================================

-- Associar supervisores às escalas
INSERT INTO escala_supervisores (escala_id, supervisor_id, created_at) VALUES
(1, 2, NOW()), (2, 2, NOW()), (3, 2, NOW()), (4, 2, NOW()), (5, 2, NOW()),
(6, 3, NOW()), (7, 3, NOW()), (8, 3, NOW()), (9, 3, NOW()), (10, 3, NOW()),
(11, 4, NOW()), (12, 4, NOW()), (13, 4, NOW()), (14, 4, NOW()), (15, 4, NOW());

-- ==========================================
-- 7. CHECK-INS DE EXEMPLO
-- ==========================================

INSERT INTO checkins (usuario_id, escala_id, data_hora, gps_lat, gps_long, status, endereco, observacoes, created_at) VALUES
(5, 1, CONCAT(CURDATE(), ' 06:58:00'), -23.5505200, -46.6333090, 'Realizado', 'Rua das Flores, 123 - Centro, São Paulo - SP', 'Check-in realizado no horário', NOW()),
(8, 2, CONCAT(CURDATE(), ' 07:02:00'), -23.5505200, -46.6333090, 'Realizado', 'Rua das Flores, 123 - Centro, São Paulo - SP', NULL, NOW()),
(9, 3, CONCAT(CURDATE(), ' 06:55:00'), -23.5505200, -46.6333090, 'Realizado', 'Rua das Flores, 123 - Centro, São Paulo - SP', NULL, NOW()),
(10, 4, CONCAT(CURDATE(), ' 11:58:00'), -23.5505200, -46.6333090, 'Realizado', 'Rua das Flores, 123 - Centro, São Paulo - SP', NULL, NOW()),
(7, 6, CONCAT(CURDATE(), ' 07:55:00'), -23.5618000, -46.6565000, 'Realizado', 'Av. Paulista, 456 - Bela Vista, São Paulo - SP', NULL, NOW()),
(14, 8, CONCAT(CURDATE(), ' 05:58:00'), -23.5489000, -46.6388000, 'Realizado', 'Rua Central, 789 - Vila Mariana, São Paulo - SP', NULL, NOW()),
(11, 7, CONCAT(CURDATE(), ' 14:05:00'), -23.5650000, -46.6700000, 'Fora de Local', 'Rua Distante, 999 - Local Incorreto', 'Check-in realizado fora do raio permitido', NOW());

-- ==========================================
-- 8. DOCUMENTOS DE EXEMPLO
-- ==========================================

INSERT INTO documentos (usuario_id, nome_arquivo, tipo_documento, arquivo_path, tamanho_bytes, mimetype, created_at) VALUES
(5, 'coren_maria_silva.pdf', 'COREN', '/uploads/documents/coren_maria_silva.pdf', 256000, 'application/pdf', NOW()),
(5, 'certificado_especializacao_maria.pdf', 'Certificado', '/uploads/documents/certificado_especializacao_maria.pdf', 512000, 'application/pdf', NOW()),
(6, 'rg_joao_santos.jpg', 'RG', '/uploads/documents/rg_joao_santos.jpg', 128000, 'image/jpeg', NOW()),
(7, 'diploma_enfermagem_ana_costa.pdf', 'Diploma', '/uploads/documents/diploma_enfermagem_ana_costa.pdf', 1024000, 'application/pdf', NOW()),
(8, 'coren_carlos_lima.pdf', 'COREN', '/uploads/documents/coren_carlos_lima.pdf', 345000, 'application/pdf', NOW()),
(9, 'certificado_uti_fernanda_rocha.pdf', 'Certificado', '/uploads/documents/certificado_uti_fernanda_rocha.pdf', 678000, 'application/pdf', NOW());

-- ==========================================
-- 9. LOGS DE EXEMPLO
-- ==========================================

INSERT INTO logs (usuario_id, acao, descricao, ip_address, user_agent, dados_extras, created_at) VALUES
(1, 'LOGIN', 'Login realizado com sucesso', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '{"method": "POST", "endpoint": "/auth/login"}', NOW()),
(2, 'CREATE_ESCALA', 'Nova escala criada - Escala (ID: 1)', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '{"recurso": "Escala", "recurso_id": 1}', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(3, 'UPDATE_USER', 'Usuário atualizado - Usuario (ID: 5)', '192.168.1.101', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '{"recurso": "Usuario", "recurso_id": 5}', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
(5, 'CREATE_CHECKIN', 'Check-in realizado - Checkin (ID: 1)', '192.168.1.105', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15', '{"recurso": "Checkin", "recurso_id": 1, "location_valid": true}', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(8, 'UPLOAD_DOCUMENTO', 'Documento enviado - Documento (ID: 1)', '192.168.1.108', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '{"recurso": "Documento", "recurso_id": 1, "tipo_documento": "COREN"}', DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(4, 'GENERATE_REPORT', 'Relatório de escalas gerado', '192.168.1.104', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '{"report_type": "escalas", "period": "weekly"}', DATE_SUB(NOW(), INTERVAL 6 HOUR));

-- ==========================================
-- 10. TRANSFERÊNCIAS DE PLANTÃO
-- ==========================================

INSERT INTO transferencias_plantao (escala_original_id, usuario_origem_id, usuario_destino_id, motivo, status, aprovado_por_id, data_aprovacao, observacoes, created_at) VALUES
(15, 5, 8, 'Emergência familiar - não posso comparecer no plantão', 'Aprovado', 2, DATE_SUB(NOW(), INTERVAL 2 DAY), 'Transferência aprovada pelo supervisor Carlos Mendes', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(16, 9, 11, 'Viagem de trabalho em outra cidade', 'Pendente', NULL, NULL, 'Aguardando aprovação do supervisor', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(17, 6, 10, 'Problema de saúde - atestado médico', 'Aprovado', 3, NOW(), 'Transferência aprovada com apresentação de atestado', DATE_SUB(NOW(), INTERVAL 5 HOUR));

-- ==========================================
-- 11. VERIFICAÇÃO DOS DADOS
-- ==========================================

SELECT 'USUARIOS' as Tabela, COUNT(*) as Total FROM usuarios
UNION ALL
SELECT 'ESTABELECIMENTOS', COUNT(*) FROM estabelecimentos
UNION ALL
SELECT 'ESCALAS', COUNT(*) FROM escalas
UNION ALL
SELECT 'CHECKINS', COUNT(*) FROM checkins
UNION ALL
SELECT 'DOCUMENTOS', COUNT(*) FROM documentos
UNION ALL
SELECT 'LOGS', COUNT(*) FROM logs;

-- Estatísticas por perfil
SELECT perfil, COUNT(*) as quantidade FROM usuarios GROUP BY perfil ORDER BY quantidade DESC;

-- Estatísticas por status de escala
SELECT status, COUNT(*) as quantidade FROM escalas GROUP BY status ORDER BY quantidade DESC; 