import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, InputGroup, ProgressBar } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

const Documentos = () => {
  const { user } = useAuth();
  const [documentos, setDocumentos] = useState([]);
  const [filteredDocumentos, setFilteredDocumentos] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocumentos();
  }, []);

  useEffect(() => {
    filterDocumentos();
  }, [searchTerm, documentos]);

  const loadDocumentos = async () => {
    try {
      setIsLoading(true);
      // TODO: Implementar chamada para API
      // const response = await api.get('/documentos');
      // setDocumentos(response.data);
      
      // Dados mock para demonstração
      setDocumentos([
        {
          id: 1,
          nome: 'Protocolo UTI - Janeiro 2024',
          tipo: 'Protocolo',
          categoria: 'Procedimento',
          tamanho: '2.5 MB',
          autor: 'Dr. João Silva',
          dataUpload: '2024-01-15T10:30:00',
          status: 'ativo'
        },
        {
          id: 2,
          nome: 'Manual de Emergência',
          tipo: 'Manual',
          categoria: 'Documentação',
          tamanho: '5.8 MB',
          autor: 'Enfª Maria Costa',
          dataUpload: '2024-01-14T14:20:00',
          status: 'ativo'
        },
        {
          id: 3,
          nome: 'Relatório Mensal - Dezembro',
          tipo: 'Relatório',
          categoria: 'Gestão',
          tamanho: '1.2 MB',
          autor: 'Admin Sistema',
          dataUpload: '2024-01-10T09:15:00',
          status: 'arquivado'
        }
      ]);
    } catch (error) {
      console.error('Erro ao carregar documentos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterDocumentos = () => {
    let filtered = documentos;
    
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.autor.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredDocumentos(filtered);
  };

  const handleShowModal = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const getStatusBadge = (status) => {
    const variants = {
      'ativo': 'success',
      'arquivado': 'warning',
      'inativo': 'secondary'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const getTipoIcon = (tipo) => {
    const icons = {
      'Protocolo': 'fas fa-clipboard-list',
      'Manual': 'fas fa-book',
      'Relatório': 'fas fa-chart-line',
      'Formulário': 'fas fa-file-alt',
      'Política': 'fas fa-gavel'
    };
    return icons[tipo] || 'fas fa-file';
  };

  const formatFileSize = (size) => {
    return size;
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
              <h1>Documentos</h1>
              <p className="text-muted">Gerencie documentos, protocolos e manuais</p>
            </div>
            <Button variant="primary" onClick={handleShowModal}>
              <i className="fas fa-plus me-2"></i>
              Novo Documento
            </Button>
          </div>
        </Col>
      </Row>

      {/* Estatísticas Rápidas */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-file-alt fa-2x text-primary mb-2"></i>
              <h4>{documentos.filter(d => d.status === 'ativo').length}</h4>
              <small className="text-muted">Documentos Ativos</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-archive fa-2x text-warning mb-2"></i>
              <h4>{documentos.filter(d => d.status === 'arquivado').length}</h4>
              <small className="text-muted">Arquivados</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-clipboard-list fa-2x text-success mb-2"></i>
              <h4>{documentos.filter(d => d.tipo === 'Protocolo').length}</h4>
              <small className="text-muted">Protocolos</small>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <i className="fas fa-book fa-2x text-info mb-2"></i>
              <h4>{documentos.filter(d => d.tipo === 'Manual').length}</h4>
              <small className="text-muted">Manuais</small>
            </Card.Body>
          </Card>
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
              placeholder="Buscar documentos por nome, tipo, categoria ou autor..."
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
                <i className="fas fa-folder-open me-2"></i>
                Biblioteca de Documentos
              </h5>
            </Card.Header>
            <Card.Body>
              {filteredDocumentos.length > 0 ? (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Documento</th>
                      <th>Tipo</th>
                      <th>Categoria</th>
                      <th>Autor</th>
                      <th>Tamanho</th>
                      <th>Data Upload</th>
                      <th>Status</th>
                      <th>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDocumentos.map(doc => (
                      <tr key={doc.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            <i className={`${getTipoIcon(doc.tipo)} fa-2x text-primary me-3`}></i>
                            <div>
                              <div className="fw-bold">{doc.nome}</div>
                              <small className="text-muted">ID: {doc.id}</small>
                            </div>
                          </div>
                        </td>
                        <td>
                          <Badge bg="info">{doc.tipo}</Badge>
                        </td>
                        <td>{doc.categoria}</td>
                        <td>{doc.autor}</td>
                        <td>{doc.tamanho}</td>
                        <td>
                          {new Date(doc.dataUpload).toLocaleDateString('pt-BR')}{' '}
                          {new Date(doc.dataUpload).toLocaleTimeString('pt-BR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </td>
                        <td>{getStatusBadge(doc.status)}</td>
                        <td>
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
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="me-2"
                            title="Editar"
                          >
                            <i className="fas fa-edit"></i>
                          </Button>
                          <Button 
                            variant="outline-danger" 
                            size="sm"
                            title="Arquivar"
                          >
                            <i className="fas fa-archive"></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              ) : (
                <div className="text-center py-4">
                  <i className="fas fa-folder-open fa-3x text-muted mb-3"></i>
                  <h5>Nenhum documento encontrado</h5>
                  <p className="text-muted">
                    {searchTerm ? 
                      'Nenhum documento corresponde aos termos de busca' :
                      'Clique em "Novo Documento" para fazer upload do primeiro documento'
                    }
                  </p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal para Upload de Documento */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Novo Documento</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Arquivo</Form.Label>
              <Form.Control
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
              />
              <Form.Text className="text-muted">
                Formatos aceitos: PDF, Word, Excel, PowerPoint (máx. 10MB)
              </Form.Text>
            </Form.Group>
            
            {uploading && (
              <div className="mb-3">
                <ProgressBar animated now={45} label="Enviando... 45%" />
              </div>
            )}

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nome do Documento</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Digite o nome do documento"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tipo</Form.Label>
                  <Form.Select>
                    <option value="">Selecione o tipo</option>
                    <option value="Protocolo">Protocolo</option>
                    <option value="Manual">Manual</option>
                    <option value="Relatório">Relatório</option>
                    <option value="Formulário">Formulário</option>
                    <option value="Política">Política</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Categoria</Form.Label>
                  <Form.Select>
                    <option value="">Selecione a categoria</option>
                    <option value="Procedimento">Procedimento</option>
                    <option value="Documentação">Documentação</option>
                    <option value="Gestão">Gestão</option>
                    <option value="Treinamento">Treinamento</option>
                    <option value="Segurança">Segurança</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Autor</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Nome do autor"
                    defaultValue={user?.nome || ''}
                  />
                </Form.Group>
              </Col>
            </Row>
            
            <Form.Group className="mb-3">
              <Form.Label>Descrição</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Breve descrição do documento (opcional)"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Cancelar
          </Button>
          <Button variant="primary" disabled={uploading}>
            {uploading ? 'Enviando...' : 'Upload Documento'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Documentos; 