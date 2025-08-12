import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Tab, Tabs } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

const Profile = () => {
  const { user, updateProfile } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [formData, setFormData] = useState({
    nome: user?.nome || '',
    email: user?.email || '',
    telefone: user?.telefone || '',
    perfil: user?.perfil || '',
    setor: user?.setor || ''
  });
  const [passwordData, setPasswordData] = useState({
    senhaAtual: '',
    novaSenha: '',
    confirmarSenha: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage({ type: '', text: '' });

    try {
      // TODO: Implementar chamada para API
      // await updateProfile(formData);
      
      // Simulação de sucesso
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage({ type: 'success', text: 'Perfil atualizado com sucesso!' });
      setIsEditing(false);
    } catch (error) {
      setMessage({ type: 'danger', text: 'Erro ao atualizar perfil. Tente novamente.' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (passwordData.novaSenha !== passwordData.confirmarSenha) {
      setMessage({ type: 'danger', text: 'As senhas não coincidem.' });
      return;
    }
    
    if (passwordData.novaSenha.length < 6) {
      setMessage({ type: 'danger', text: 'A nova senha deve ter pelo menos 6 caracteres.' });
      return;
    }

    setIsSaving(true);
    setMessage({ type: '', text: '' });

    try {
      // TODO: Implementar chamada para API
      // await changePassword(passwordData);
      
      // Simulação de sucesso
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage({ type: 'success', text: 'Senha alterada com sucesso!' });
      setPasswordData({ senhaAtual: '', novaSenha: '', confirmarSenha: '' });
    } catch (error) {
      setMessage({ type: 'danger', text: 'Erro ao alterar senha. Verifique a senha atual.' });
    } finally {
      setIsSaving(false);
    }
  };

  const getPerfilIcon = (perfil) => {
    const icons = {
      'Médico': 'fas fa-user-md',
      'Enfermeira': 'fas fa-user-nurse',
      'Técnica': 'fas fa-user-cog',
      'Admin': 'fas fa-user-shield'
    };
    return icons[perfil] || 'fas fa-user';
  };

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h1>Meu Perfil</h1>
          <p className="text-muted">Gerencie suas informações pessoais e configurações</p>
        </Col>
      </Row>

      {message.text && (
        <Row className="mb-4">
          <Col>
            <Alert variant={message.type} dismissible onClose={() => setMessage({ type: '', text: '' })}>
              <i className={`fas ${message.type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2`}></i>
              {message.text}
            </Alert>
          </Col>
        </Row>
      )}

      <Row>
        <Col lg={4}>
          {/* Card do Usuário */}
          <Card className="mb-4">
            <Card.Body className="text-center">
              <div className="mb-3">
                <i className={`${getPerfilIcon(user?.perfil)} fa-5x text-primary`}></i>
              </div>
              <h4>{user?.nome}</h4>
              <p className="text-muted">{user?.perfil}</p>
              <p className="small">
                <i className="fas fa-building me-2"></i>
                {user?.setor}
              </p>
              <p className="small">
                <i className="fas fa-envelope me-2"></i>
                {user?.email}
              </p>
              <Button
                variant={isEditing ? "secondary" : "primary"}
                onClick={() => setIsEditing(!isEditing)}
                disabled={isSaving}
              >
                {isEditing ? (
                  <>
                    <i className="fas fa-times me-2"></i>
                    Cancelar
                  </>
                ) : (
                  <>
                    <i className="fas fa-edit me-2"></i>
                    Editar Perfil
                  </>
                )}
              </Button>
            </Card.Body>
          </Card>

          {/* Card de Configurações Rápidas */}
          <Card>
            <Card.Header>
              <h6 className="mb-0">
                <i className="fas fa-cog me-2"></i>
                Configurações Rápidas
              </h6>
            </Card.Header>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span>Tema</span>
                <Button
                  variant={theme === 'light' ? 'outline-warning' : 'outline-light'}
                  size="sm"
                  onClick={toggleTheme}
                >
                  <i className={`fas ${theme === 'light' ? 'fa-moon' : 'fa-sun'} me-2`}></i>
                  {theme === 'light' ? 'Escuro' : 'Claro'}
                </Button>
              </div>
              <div className="d-flex justify-content-between align-items-center">
                <span>Notificações</span>
                <Form.Check type="switch" id="notifications" defaultChecked />
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          <Tabs defaultActiveKey="profile" className="mb-3">
            <Tab eventKey="profile" title="Informações Pessoais">
              <Card>
                <Card.Body>
                  <Form onSubmit={handleSaveProfile}>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Nome Completo</Form.Label>
                          <Form.Control
                            type="text"
                            name="nome"
                            value={formData.nome}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>E-mail</Form.Label>
                          <Form.Control
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Telefone</Form.Label>
                          <Form.Control
                            type="tel"
                            name="telefone"
                            value={formData.telefone}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            placeholder="(00) 00000-0000"
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Perfil</Form.Label>
                          <Form.Control
                            type="text"
                            value={formData.perfil}
                            disabled
                            className="bg-light"
                          />
                          <Form.Text className="text-muted">
                            O perfil só pode ser alterado pelo administrador
                          </Form.Text>
                        </Form.Group>
                      </Col>
                    </Row>

                    <Form.Group className="mb-3">
                      <Form.Label>Setor</Form.Label>
                      <Form.Control
                        type="text"
                        value={formData.setor}
                        disabled
                        className="bg-light"
                      />
                      <Form.Text className="text-muted">
                        O setor só pode ser alterado pelo administrador
                      </Form.Text>
                    </Form.Group>

                    {isEditing && (
                      <div className="d-flex gap-2">
                        <Button
                          type="submit"
                          variant="success"
                          disabled={isSaving}
                        >
                          {isSaving ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              Salvando...
                            </>
                          ) : (
                            <>
                              <i className="fas fa-save me-2"></i>
                              Salvar Alterações
                            </>
                          )}
                        </Button>
                        <Button
                          type="button"
                          variant="secondary"
                          onClick={() => setIsEditing(false)}
                          disabled={isSaving}
                        >
                          Cancelar
                        </Button>
                      </div>
                    )}
                  </Form>
                </Card.Body>
              </Card>
            </Tab>

            <Tab eventKey="security" title="Segurança">
              <Card>
                <Card.Body>
                  <h5 className="mb-3">Alterar Senha</h5>
                  <Form onSubmit={handleChangePassword}>
                    <Form.Group className="mb-3">
                      <Form.Label>Senha Atual</Form.Label>
                      <Form.Control
                        type="password"
                        name="senhaAtual"
                        value={passwordData.senhaAtual}
                        onChange={handlePasswordChange}
                        required
                      />
                    </Form.Group>

                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Nova Senha</Form.Label>
                          <Form.Control
                            type="password"
                            name="novaSenha"
                            value={passwordData.novaSenha}
                            onChange={handlePasswordChange}
                            minLength="6"
                            required
                          />
                        </Form.Group>
                      </Col>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Confirmar Nova Senha</Form.Label>
                          <Form.Control
                            type="password"
                            name="confirmarSenha"
                            value={passwordData.confirmarSenha}
                            onChange={handlePasswordChange}
                            minLength="6"
                            required
                          />
                        </Form.Group>
                      </Col>
                    </Row>

                    <Button
                      type="submit"
                      variant="warning"
                      disabled={isSaving}
                    >
                      {isSaving ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Alterando...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-key me-2"></i>
                          Alterar Senha
                        </>
                      )}
                    </Button>
                  </Form>

                  <hr className="my-4" />

                  <h5 className="mb-3">Informações de Sessão</h5>
                  <div className="row">
                    <div className="col-sm-6">
                      <p className="mb-1"><strong>Último Login:</strong></p>
                      <p className="text-muted">15/01/2024 às 08:30</p>
                    </div>
                    <div className="col-sm-6">
                      <p className="mb-1"><strong>Dispositivo:</strong></p>
                      <p className="text-muted">Chrome em Windows</p>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Tab>

            <Tab eventKey="activity" title="Atividade Recente">
              <Card>
                <Card.Body>
                  <h5 className="mb-3">Últimas Atividades</h5>
                  <div className="activity-list">
                    <div className="d-flex align-items-center mb-3">
                      <i className="fas fa-sign-in-alt text-success me-3"></i>
                      <div>
                        <div>Login realizado</div>
                        <small className="text-muted">15/01/2024 às 08:30</small>
                      </div>
                    </div>
                    <div className="d-flex align-items-center mb-3">
                      <i className="fas fa-edit text-primary me-3"></i>
                      <div>
                        <div>Perfil atualizado</div>
                        <small className="text-muted">14/01/2024 às 16:45</small>
                      </div>
                    </div>
                    <div className="d-flex align-items-center mb-3">
                      <i className="fas fa-clock text-info me-3"></i>
                      <div>
                        <div>Check-in registrado</div>
                        <small className="text-muted">14/01/2024 às 08:00</small>
                      </div>
                    </div>
                    <div className="d-flex align-items-center">
                      <i className="fas fa-file-alt text-warning me-3"></i>
                      <div>
                        <div>Relatório gerado</div>
                        <small className="text-muted">13/01/2024 às 17:30</small>
                      </div>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </Tab>
          </Tabs>
        </Col>
      </Row>
    </Container>
  );
};

export default Profile; 