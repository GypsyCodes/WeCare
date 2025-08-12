import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, InputGroup } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

const Relatorios = () => {
  const { user } = useAuth();
  const [relatorios, setRelatorios] = useState([]);
  const [filteredRelatorios, setFilteredRelatorios] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadRelatorios();
  }, []);

  useEffect(() => {
    filterRelatorios();
  }, [searchTerm, relatorios]);

  const loadRelatorios = async () => {
    try {
      setIsLoading(true);
      // TODO: Implementar chamada para API
      // const response = await api.get('/relatorios');
      // setRelatorios(response.data);
      
      // Dados mock para demonstração
      setRelatorios([
        {
          id: 1,
          nome: 'Relatório de Check-ins - Janeiro 2024',
          tipo: 'Check-ins',
          periodo: '01/01/2024 - 31/01/2024',
          autor: 'Admin Sistema',
          dataGeracao: '2024-01-31T23:59:00',
          status: 'disponivel',
          tamanho: '2.3 MB'
        },
        {
          id: 2,
          nome: 'Relatório de Escalas - Dezembro 2023',
          tipo: 'Escalas',
          periodo: '01/12/2023 - 31/12/2023',
          autor: 'Maria Silva',
          dataGeracao: '2024-01-01T09:00:00',
          status: 'disponivel',
          tamanho: '1.8 MB'
        },
        {
          id: 3,
          nome: 'Relatório de Usuários Ativos',
          tipo: 'Usuários',
          periodo: '01/01/2024 - 15/01/2024',
          autor: 'João Santos',
          dataGeracao: '2024-01-15T14:30:00',
          status: 'processando',
          tamanho: '-'
        }
      ]);
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterRelatorios = () => {
    let filtered = relatorios;
    
    if (searchTerm) {
      filtered = filtered.filter(rel =>
        rel.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rel.tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rel.autor.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredRelatorios(filtered);
  };

  const handleShowModal = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const getStatusBadge = (status) => {
    const variants = {
      'disponivel': 'success',
      'processando': 'warning',
      'erro': 'danger',
      'expirado': 'secondary'
    };
    const labels = {
      'disponivel': 'Disponível',
      'processando': 'Processando',
      'erro': 'Erro',
      'expirado': 'Expirado'
    };
    return <Badge bg={variants[status] || 'secondary'}>{labels[status]}</Badge>;
  };

  const getTipoIcon = (tipo) => {
    const icons = {
      'Check-ins': 'fas fa-clock',
      'Escalas': 'fas fa-calendar-alt',
      'Usuários': 'fas fa-users',
      'Geral': 'fas fa-chart-line',
      'Financeiro': 'fas fa-dollar-sign'
    };
    return icons[tipo] || 'fas fa-file-alt';
  };

  const tiposRelatorio = [
    { value: 'checkins', label: 'Check-ins', icon: 'fas fa-clock' },
    { value: 'escalas', label: 'Escalas', icon: 'fas fa-calendar-alt' },
    { value: 'usuarios', label: 'Usuários', icon: 'fas fa-users' },
    { value: 'geral', label: 'Relatório Geral', icon: 'fas fa-chart-line' }
  ];

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
              <h1>Relatórios</h1>
              <p className="text-muted">Gere e visualize relatórios do sistema</p>
            </div>
            <Button variant="primary" onClick={handleShowModal}>
              <i className="fas fa-plus me-2"></i>
              Novo Relatório
            </Button>
          </div>
        </Col>
      </Row>

      {/* Cards de Tipos de Relatório */}
      <Row className="mb-4">
        {tiposRelatorio.map(tipo => (
          <Col md={3} key={tipo.value}>
            <Card 
              className="text-center h-100 report-type-card" 
              style={{ cursor: 'pointer' }}
              onClick={handleShowModal}
            >
              <Card.Body>
                <i className={`${tipo.icon} fa-3x text-primary mb-3`}></i>
                <h5>{tipo.label}</h5>
                <p className="text-muted">
                  Gerar relatório de {tipo.label.toLowerCase()}
                </p>
                <Button variant="outline-primary" size="sm">
                  <i className="fas fa-chart-bar me-2"></i>
                  Gerar
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Barra de Pesquisa */}
      <Row className="mb-4">
        <Col md={8}>
          <InputGroup>
            <InputGroup.Text>
              <i className="fas fa-search"></i>
            </InputGroup.Text>
            <Form.Control
              placeholder="Buscar relatórios por nome, tipo ou autor..."
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
                <i className="fas fa-file-alt me-2"></i>
                Histórico de Relatórios
              </h5>
            </Card.Header>
            <Card.Body>
              {filteredRelatorios.length > 0 ? (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Relatório</th>
                      <th>Tipo</th>
                      <th>Período</th>
                      <th>Autor</th>
                      <th>Data Geração</th>
                      <th>Tamanho</th>
                      <th>Status</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRelatorios.map(rel => (
                      <tr key={rel.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <i className={`${getTipoIcon(rel.tipo)} fa-2x text-primary me-3`}></i>
                            <div>
                              <div className="fw-bold">{rel.nome}</div>
                              <small className="text-muted">ID: {rel.id}</small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <Badge bg="info">{rel.tipo}</Badge>
                        </td>
                        <td>{rel.periodo}</td>
                        <td>{rel.autor}</td>
                        <td>
                          {new Date(rel.dataGeracao).toLocaleDateString('pt-BR')}{' '}
                          {new Date(rel.dataGeracao).toLocaleTimeString('pt-BR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </td>
                        <td>{rel.tamanho}</td>
                        <td>{getStatusBadge(rel.status)}</td>
                        <td>
                          {rel.status === 'disponivel' && (
                            <>
                              <Button
                                variant="outline-primary"
                                size="sm"
                                className="me-2"
                                title="Baixar"
                              >
                                <i className="fas fa-download"></i>
                              </Button>
                              <Button
                                variant="outline-success"
                                size="sm"
                                className="me-2"
                                title="Visualizar"
                              >
                                <i className="fas fa-eye"></i>
                              </Button>
                            </>
                          )}
                          {rel.status === 'processando' && (
                            <div className="spinner-border spinner-border-sm text-warning" role="status">
                              <span className="visually-hidden">Processando...</span>
                            </div>
                          )}
                          <Button 
                            variant="outline-danger" 
                            size="sm"
                            title="Excluir"
                          >
                            <i className="fas fa-trash"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-chart-bar fa-3x text-muted mb-3"></i>
                  <h5>Nenhum relatório encontrado</h5>
                  <p className="text-muted">
                    {searchTerm ? 
                      'Nenhum relatório corresponde aos termos de busca' :
                      'Clique em "Novo Relatório" para gerar seu primeiro relatório'
                    }
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal para Novo Relatório */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Gerar Novo Relatório</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Relatório</Form.Label>
              <Form.Select>
                <option value="">Selecione o tipo de relatório</option>
                <option value="checkins">Check-ins</option>
                <option value="escalas">Escalas</option>
                <option value="usuarios">Usuários</option>
                <option value="geral">Relatório Geral</option>
              </Form.Select>
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Data Início</Form.Label>
                  <Form.Control
                    type="date"
                    defaultValue="2024-01-01"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Data Fim</Form.Label>
                  <Form.Control
                    type="date"
                    defaultValue={new Date().toISOString().split('T')[0]}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Filtros Específicos</Form.Label>
              <Row>
                <Col md={6}>
                  <Form.Select className="mb-2">
                    <option value="">Todos os setores</option>
                    <option value="uti">UTI</option>
                    <option value="pediatria">Pediatria</option>
                    <option value="cardiologia">Cardiologia</option>
                    <option value="emergencia">Emergência</option>
                  </Form.Select>
                </Col>
                <Col md={6}>
                  <Form.Select>
                    <option value="">Todos os turnos</option>
                    <option value="manha">Manhã</option>
                    <option value="tarde">Tarde</option>
                    <option value="noite">Noite</option>
                  </Form.Select>
                </Col>
              </Row>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Formato de Saída</Form.Label>
              <div>
                <Form.Check
                  inline
                  type="radio"
                  id="pdf-format"
                  name="formato"
                  label="PDF"
                  defaultChecked
                />
                <Form.Check
                  inline
                  type="radio"
                  id="excel-format"
                  name="formato"
                  label="Excel"
                />
                <Form.Check
                  inline
                  type="radio"
                  id="csv-format"
                  name="formato"
                  label="CSV"
                />
              </div>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Nome do Relatório</Form.Label>
              <Form.Control
                type="text"
                placeholder="Digite um nome para o relatório (opcional)"
              />
              <Form.Text className="text-muted">
                Se não especificado, será gerado automaticamente baseado no tipo e período
              </Form.Text>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Cancelar
          </Button>
          <Button variant="primary" disabled={generating}>
            {generating ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Gerando...
              </>
            ) : (
              <>
                <i className="fas fa-chart-bar me-2"></i>
                Gerar Relatório
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Relatorios; 