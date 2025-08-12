import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, InputGroup } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

const Usuarios = () => {
  const { user } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [filteredUsuarios, setFilteredUsuarios] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedUsuario, setSelectedUsuario] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadUsuarios();
  }, []);

  useEffect(() => {
    filterUsuarios();
  }, [searchTerm, usuarios]);

  const loadUsuarios = async () => {
    try {
      setIsLoading(true);
      // TODO: Implementar chamada para API
      // const response = await api.get('/usuarios');
      // setUsuarios(response.data);
      
      // Dados mock para demonstração
      setUsuarios([
        {
          id: 1,
          nome: 'Maria Silva',
          email: 'maria.silva@hospital.com',
          perfil: 'Enfermeira',
          setor: 'UTI',
          status: 'ativo',
          ultimoLogin: '2024-01-15T10:30:00'
        },
        {
          id: 2,
          nome: 'João Santos',
          email: 'joao.santos@hospital.com',
          perfil: 'Médico',
          setor: 'Pediatria',
          status: 'ativo',
          ultimoLogin: '2024-01-15T08:15:00'
        },
        {
          id: 3,
          nome: 'Ana Costa',
          email: 'ana.costa@hospital.com',
          perfil: 'Técnica',
          setor: 'Emergência',
          status: 'inativo',
          ultimoLogin: '2024-01-10T14:20:00'
        }
      ]);
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterUsuarios = () => {
    let filtered = usuarios;
    
    if (searchTerm) {
      filtered = filtered.filter(usuario =>
        usuario.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        usuario.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        usuario.perfil.toLowerCase().includes(searchTerm.toLowerCase()) ||
        usuario.setor.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredUsuarios(filtered);
  };

  const handleShowModal = (usuario = null) => {
    setSelectedUsuario(usuario);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedUsuario(null);
  };

  const getStatusBadge = (status) => {
    const variants = {
      'ativo': 'success',
      'inativo': 'danger',
      'pendente': 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
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

  if (isLoading) {
    return (
      <Container>
        <div className="text-center py-5">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Carregando...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1>Usuários</h1>
              <p className="text-muted">Gerencie os usuários do sistema</p>
            </div>
            <Button variant="primary" onClick={() => handleShowModal()}>
              <i className="fas fa-plus me-2"></i>
              Novo Usuário
            </Button>
          </div>
        </Col>
      </Row>

      {/* Barra de Pesquisa */}
      <Row className="mb-4">
        <Col md={8}>
          <InputGroup>
            <InputGroup.Text>
              <i className="fas fa-search"></i>
            </InputGroup.Text>
            <Form.Control
              placeholder="Buscar por nome, e-mail, perfil ou setor..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-users me-2"></i>
                Lista de Usuários
              </h5>
            </Card.Header>
            <Card.Body>
              {filteredUsuarios.length > 0 ? (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Usuário</th>
                      <th>E-mail</th>
                      <th>Perfil</th>
                      <th>Setor</th>
                      <th>Último Login</th>
                      <th>Status</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsuarios.map(usuario => (
                      <tr key={usuario.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <i className={`${getPerfilIcon(usuario.perfil)} fa-2x text-primary me-3`}></i>
                            <div>
                              <div className="fw-bold">{usuario.nome}</div>
                              <small className="text-muted">ID: {usuario.id}</small>
                            </div>
                          </div>
                        </td>
                        <td>{usuario.email}</td>
                        <td>
                          <Badge bg="info">{usuario.perfil}</Badge>
                        </td>
                        <td>{usuario.setor}</td>
                        <td>
                          {new Date(usuario.ultimoLogin).toLocaleDateString('pt-BR')}{' '}
                          {new Date(usuario.ultimoLogin).toLocaleTimeString('pt-BR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </td>
                        <td>{getStatusBadge(usuario.status)}</td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-2"
                            onClick={() => handleShowModal(usuario)}
                          >
                            <i className="fas fa-edit"></i>
                          </Button>
                          <Button variant="outline-danger" size="sm">
                            <i className="fas fa-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-users fa-3x text-muted mb-3"></i>
                  <h5>Nenhum usuário encontrado</h5>
                  <p className="text-muted">
                    {searchTerm ? 
                      'Nenhum usuário corresponde aos termos de busca' :
                      'Clique em "Novo Usuário" para adicionar o primeiro usuário'
                    }
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal para Novo/Editar Usuário */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedUsuario ? 'Editar Usuário' : 'Novo Usuário'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nome Completo</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Digite o nome completo"
                    defaultValue={selectedUsuario?.nome || ''}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>E-mail</Form.Label>
                  <Form.Control
                    type="email"
                    placeholder="Digite o e-mail"
                    defaultValue={selectedUsuario?.email || ''}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Perfil</Form.Label>
                  <Form.Select defaultValue={selectedUsuario?.perfil || ''}>
                    <option value="">Selecione o perfil</option>
                    <option value="Médico">Médico</option>
                    <option value="Enfermeira">Enfermeira</option>
                    <option value="Técnica">Técnica</option>
                    <option value="Admin">Administrador</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Setor</Form.Label>
                  <Form.Select defaultValue={selectedUsuario?.setor || ''}>
                    <option value="">Selecione o setor</option>
                    <option value="UTI">UTI</option>
                    <option value="Pediatria">Pediatria</option>
                    <option value="Cardiologia">Cardiologia</option>
                    <option value="Emergência">Emergência</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            {!selectedUsuario && (
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Senha</Form.Label>
                    <Form.Control
                      type="password"
                      placeholder="Digite a senha"
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Confirmar Senha</Form.Label>
                    <Form.Control
                      type="password"
                      placeholder="Confirme a senha"
                    />
                  </Form.Group>
                </Col>
              </Row>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Cancelar
          </Button>
          <Button variant="primary">
            {selectedUsuario ? 'Salvar Alterações' : 'Criar Usuário'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Usuarios; 