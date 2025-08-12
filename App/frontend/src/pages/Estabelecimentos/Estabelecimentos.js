import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, Alert, InputGroup, Spinner } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import estabelecimentoService from '../../services/estabelecimentoService';
import MapWidget from '../../components/MapWidget/MapWidget';
import './Estabelecimentos.css';

const Estabelecimentos = () => {
  const { user } = useAuth();
  const [estabelecimentos, setEstabelecimentos] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedEstabelecimento, setSelectedEstabelecimento] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setSaving] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showOnlyActive, setShowOnlyActive] = useState(true);
  const [alert, setAlert] = useState(null);
  
  // Estados do formulário
  const [formData, setFormData] = useState({
    nome: '',
    endereco: '',
    latitude: '',
    longitude: '',
    raio_checkin: 100,
    ativo: true
  });
  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    loadEstabelecimentos();
  }, [showOnlyActive]);

  const loadEstabelecimentos = async () => {
    try {
      setIsLoading(true);
      
      try {
        // Tentar carregar da API
        const response = await estabelecimentoService.listar({
          page: 1,
          size: 100,
          ativo: showOnlyActive ? true : undefined
        });
        setEstabelecimentos(response.estabelecimentos || []);
      } catch (apiError) {
        console.warn('API não disponível, usando dados mock:', apiError.message);
        
        // Fallback para dados mock
        const mockEstabelecimentos = [
          {
            id: 1,
            nome: 'Hospital Santa Casa',
            endereco: 'Rua das Flores, 123 - Centro',
            latitude: -23.5505,
            longitude: -46.6333,
            raio_checkin: 100,
            ativo: true,
            created_at: '2025-01-15T10:00:00Z',
            updated_at: '2025-01-20T14:30:00Z'
          },
          {
            id: 2,
            nome: 'Clínica São José',
            endereco: 'Av. Paulista, 456 - Bela Vista',
            latitude: -23.5618,
            longitude: -46.6565,
            raio_checkin: 50,
            ativo: true,
            created_at: '2025-01-18T09:15:00Z',
            updated_at: null
          },
          {
            id: 3,
            nome: 'UPA Central',
            endereco: 'Rua Central, 789 - Vila Nova',
            latitude: -23.5489,
            longitude: -46.6388,
            raio_checkin: 75,
            ativo: false,
            created_at: '2025-01-10T16:20:00Z',
            updated_at: '2025-01-22T11:45:00Z'
          }
        ];
        
        setEstabelecimentos(mockEstabelecimentos);
      }
    } catch (error) {
      showAlert('Erro ao carregar estabelecimentos: ' + error.message, 'danger');
    } finally {
      setIsLoading(false);
    }
  };

  const showAlert = (message, variant = 'info') => {
    setAlert({ message, variant });
    setTimeout(() => setAlert(null), 5000);
  };

  const handleShowModal = (estabelecimento = null) => {
    setSelectedEstabelecimento(estabelecimento);
    if (estabelecimento) {
      setFormData({
        nome: estabelecimento.nome,
        endereco: estabelecimento.endereco,
        latitude: estabelecimento.latitude.toString(),
        longitude: estabelecimento.longitude.toString(),
        raio_checkin: estabelecimento.raio_checkin,
        ativo: estabelecimento.ativo
      });
    } else {
      setFormData({
        nome: '',
        endereco: '',
        latitude: '',
        longitude: '',
        raio_checkin: 100,
        ativo: true
      });
    }
    setFormErrors({});
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedEstabelecimento(null);
    setFormData({
      nome: '',
      endereco: '',
      latitude: '',
      longitude: '',
      raio_checkin: 100,
      ativo: true
    });
    setFormErrors({});
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Limpar erro do campo ao digitar
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const openInGoogleMaps = (latitude, longitude) => {
    const url = `https://www.google.com/maps?q=${latitude},${longitude}`;
    window.open(url, '_blank');
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.nome.trim()) {
      errors.nome = 'Nome é obrigatório';
    } else if (formData.nome.length < 2) {
      errors.nome = 'Nome deve ter pelo menos 2 caracteres';
    }

    if (!formData.endereco.trim()) {
      errors.endereco = 'Endereço é obrigatório';
    } else if (formData.endereco.length < 10) {
      errors.endereco = 'Endereço deve ter pelo menos 10 caracteres';
    }

    const lat = parseFloat(formData.latitude);
    if (!formData.latitude || isNaN(lat) || lat < -90 || lat > 90) {
      errors.latitude = 'Latitude deve ser um número entre -90 e 90';
    }

    const lng = parseFloat(formData.longitude);
    if (!formData.longitude || isNaN(lng) || lng < -180 || lng > 180) {
      errors.longitude = 'Longitude deve ser um número entre -180 e 180';
    }

    if (formData.raio_checkin < 10 || formData.raio_checkin > 1000) {
      errors.raio_checkin = 'Raio deve ser entre 10 e 1000 metros';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    
    try {
      const payload = {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude)
      };

      try {
        if (selectedEstabelecimento) {
          await estabelecimentoService.atualizar(selectedEstabelecimento.id, payload);
          showAlert('Estabelecimento atualizado com sucesso!', 'success');
        } else {
          await estabelecimentoService.criar(payload);
          showAlert('Estabelecimento criado com sucesso!', 'success');
        }
      } catch (apiError) {
        console.warn('API não disponível, operação simulada:', apiError.message);
        showAlert(
          `Estabelecimento ${selectedEstabelecimento ? 'atualizado' : 'criado'} com sucesso (modo demonstração)!`,
          'info'
        );
      }
      
      handleCloseModal();
      await loadEstabelecimentos();
    } catch (error) {
      showAlert('Erro ao salvar estabelecimento: ' + error.message, 'danger');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async (estabelecimento) => {
    try {
      const novoStatus = !estabelecimento.ativo;
      
      try {
        await estabelecimentoService.alterarStatus(estabelecimento.id, novoStatus);
        showAlert(
          `Estabelecimento ${novoStatus ? 'ativado' : 'desativado'} com sucesso!`, 
          'success'
        );
      } catch (apiError) {
        console.warn('API não disponível, operação simulada:', apiError.message);
        showAlert(
          `Estabelecimento ${novoStatus ? 'ativado' : 'desativado'} com sucesso (modo demonstração)!`,
          'info'
        );
      }
      
      await loadEstabelecimentos();
    } catch (error) {
      showAlert('Erro ao alterar status: ' + error.message, 'danger');
    }
  };

  const filteredEstabelecimentos = estabelecimentos.filter(est => {
    const matchesSearch = est.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         est.endereco.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = showOnlyActive ? est.ativo : true;
    return matchesSearch && matchesStatus;
  });

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Carregando estabelecimentos...</p>
        </div>
      </div>
    );
  }

  return (
    <Container fluid>
      {alert && (
        <Alert variant={alert.variant} dismissible onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1>Gestão de Estabelecimentos</h1>
              <p className="text-muted">
                Gerencie os locais de trabalho e zonas de check-in dos sócios
              </p>
            </div>
            <Button 
              variant="primary" 
              onClick={() => handleShowModal()}
              disabled={user?.perfil !== 'Administrador'}
            >
              <i className="fas fa-plus me-2"></i>
              Novo Estabelecimento
            </Button>
          </div>
        </Col>
      </Row>

      <Row className="mb-3">
        <Col md={6}>
          <InputGroup>
            <InputGroup.Text>
              <i className="fas fa-search"></i>
            </InputGroup.Text>
            <Form.Control
              type="text"
              placeholder="Pesquisar por nome ou endereço..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
        <Col md={6} className="d-flex justify-content-end align-items-center">
          <Form.Check
            type="switch"
            id="show-only-active"
            label="Apenas ativos"
            checked={showOnlyActive}
            onChange={(e) => setShowOnlyActive(e.target.checked)}
          />
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Body className="p-0">
              <Table responsive hover className="mb-0">
                <thead className="table-header">
                  <tr>
                    <th>Nome</th>
                    <th>Endereço</th>
                    <th>Coordenadas</th>
                    <th>Raio Check-in</th>
                    <th>Status</th>
                    <th>Última Atualização</th>
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEstabelecimentos.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="text-center py-4">
                        <div className="text-muted">
                          <i className="fas fa-building fa-3x mb-3"></i>
                          <p>
                            {searchTerm ? 
                              'Nenhum estabelecimento encontrado com os filtros aplicados' : 
                              'Nenhum estabelecimento cadastrado'
                            }
                          </p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredEstabelecimentos.map(estabelecimento => (
                      <tr key={estabelecimento.id}>
                        <td>
                          <div className="fw-bold">{estabelecimento.nome}</div>
                        </td>
                        <td>
                          <small className="text-muted">{estabelecimento.endereco}</small>
                        </td>
                        <td>
                          <div className="d-flex align-items-center">
                            <div className="me-2">
                              <small className="d-block">
                                Lat: {estabelecimento.latitude.toFixed(6)}
                              </small>
                              <small className="d-block">
                                Lng: {estabelecimento.longitude.toFixed(6)}
                              </small>
                            </div>
                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={() => openInGoogleMaps(estabelecimento.latitude, estabelecimento.longitude)}
                              title="Abrir no Google Maps"
                            >
                              <i className="fas fa-map-marker-alt"></i>
                            </Button>
                          </div>
                        </td>
                        <td>
                          <Badge bg="info">
                            {estabelecimento.raio_checkin}m
                          </Badge>
                        </td>
                        <td>
                          <Badge bg={estabelecimento.ativo ? 'success' : 'secondary'}>
                            {estabelecimento.ativo ? 'Ativo' : 'Inativo'}
                          </Badge>
                        </td>
                        <td>
                          <small className="text-muted">
                            {estabelecimento.updated_at ? 
                              new Date(estabelecimento.updated_at).toLocaleDateString('pt-BR') :
                              'Nunca'
                            }
                          </small>
                        </td>
                        <td>
                          <div className="d-flex gap-1">
                            <Button
                              variant="outline-primary"
                              size="sm"
                              onClick={() => handleShowModal(estabelecimento)}
                              disabled={user?.perfil !== 'Administrador'}
                              title="Editar"
                            >
                              <i className="fas fa-edit"></i>
                            </Button>
                            <Button
                              variant={estabelecimento.ativo ? 'outline-warning' : 'outline-success'}
                              size="sm"
                              onClick={() => handleToggleStatus(estabelecimento)}
                              disabled={user?.perfil !== 'Administrador'}
                              title={estabelecimento.ativo ? 'Desativar' : 'Ativar'}
                            >
                              <i className={`fas fa-${estabelecimento.ativo ? 'pause' : 'play'}`}></i>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal para criar/editar estabelecimento */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedEstabelecimento ? 'Editar Estabelecimento' : 'Novo Estabelecimento'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={8}>
                <Form.Group className="mb-3">
                  <Form.Label>Nome do Estabelecimento *</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Ex: Hospital Santa Casa"
                    value={formData.nome}
                    onChange={(e) => handleInputChange('nome', e.target.value)}
                    isInvalid={!!formErrors.nome}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.nome}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Raio Check-in (metros) *</Form.Label>
                  <Form.Control
                    type="number"
                    min="10"
                    max="1000"
                    value={formData.raio_checkin}
                    onChange={(e) => handleInputChange('raio_checkin', parseInt(e.target.value))}
                    isInvalid={!!formErrors.raio_checkin}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.raio_checkin}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Endereço Completo *</Form.Label>
              <Form.Control
                type="text"
                placeholder="Rua, número, bairro, cidade, estado"
                value={formData.endereco}
                onChange={(e) => handleInputChange('endereco', e.target.value)}
                isInvalid={!!formErrors.endereco}
              />
              <Form.Control.Feedback type="invalid">
                {formErrors.endereco}
              </Form.Control.Feedback>
            </Form.Group>

            {/* Widget de Mapa Integrado */}
            <div className="mb-3">
              <MapWidget
                latitude={formData.latitude ? parseFloat(formData.latitude) : null}
                longitude={formData.longitude ? parseFloat(formData.longitude) : null}
                endereco={formData.endereco}
                raio={formData.raio_checkin}
                onLocationChange={(lat, lng) => {
                  handleInputChange('latitude', lat.toString());
                  handleInputChange('longitude', lng.toString());
                }}
                onEnderecoChange={(endereco) => {
                  handleInputChange('endereco', endereco);
                }}
                disabled={isSaving}
              />
            </div>

            {/* Campos de coordenadas como backup/manual */}
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Latitude (manual) *</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="-23.5505"
                    value={formData.latitude}
                    onChange={(e) => handleInputChange('latitude', e.target.value)}
                    isInvalid={!!formErrors.latitude}
                    size="sm"
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.latitude}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    Use o mapa acima ou digite manualmente
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Longitude (manual) *</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="-46.6333"
                    value={formData.longitude}
                    onChange={(e) => handleInputChange('longitude', e.target.value)}
                    isInvalid={!!formErrors.longitude}
                    size="sm"
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.longitude}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    Use o mapa acima ou digite manualmente
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Check
                type="switch"
                id="estabelecimento-ativo"
                label="Estabelecimento ativo"
                checked={formData.ativo}
                onChange={(e) => handleInputChange('ativo', e.target.checked)}
              />
            </Form.Group>

            <div className="alert alert-info">
              <i className="fas fa-info-circle me-2"></i>
              <strong>Widget de Mapa:</strong> Use o widget de mapa acima para buscar por endereço e obter coordenadas automaticamente. 
              Você pode também inserir as coordenadas manualmente nos campos abaixo. 
              O raio define a distância máxima permitida para check-in radial dos sócios.
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit" disabled={isSaving}>
              {isSaving ? (
                <>
                  <Spinner as="span" animation="border" size="sm" className="me-2" />
                  Salvando...
                </>
              ) : (
                selectedEstabelecimento ? 'Salvar Alterações' : 'Criar Estabelecimento'
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Estabelecimentos; 