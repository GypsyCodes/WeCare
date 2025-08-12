import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Form, InputGroup, Modal, Alert, Spinner } from 'react-bootstrap';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Checkins.css';

// Fix para ícones do Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const Checkins = () => {
  const { user } = useAuth();
  const [checkins, setCheckins] = useState([]);
  const [escalas, setEscalas] = useState([]);
  const [estabelecimentos, setEstabelecimentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCheckinModal, setShowCheckinModal] = useState(false);
  const [selectedEscala, setSelectedEscala] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [checkinLoading, setCheckinLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterEstabelecimento, setFilterEstabelecimento] = useState('');

  useEffect(() => {
    loadData();
    getCurrentLocation();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Carregar dados em paralelo
      const [checkinsResponse, escalasResponse, estabelecimentosResponse] = await Promise.all([
        api.get('/checkins'),
        api.get('/escalas'),
        api.get('/estabelecimentos')
      ]);
      
      setCheckins(checkinsResponse.data.checkins || checkinsResponse.data || []);
      setEscalas(escalasResponse.data.escalas || escalasResponse.data || []);
      setEstabelecimentos(estabelecimentosResponse.data.estabelecimentos || estabelecimentosResponse.data || []);
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setError('Erro ao carregar dados. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocalização não suportada pelo navegador');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setLocationError(null);
      },
      (error) => {
        console.error('Erro ao obter localização:', error);
        setLocationError('Erro ao obter localização. Verifique as permissões.');
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutos
      }
    );
  };

  const handleCheckin = async (escala) => {
    if (!userLocation) {
      setLocationError('Localização não disponível. Aguarde...');
      getCurrentLocation();
      return;
    }

    setSelectedEscala(escala);
    setShowCheckinModal(true);
  };

  const confirmCheckin = async () => {
    if (!selectedEscala || !userLocation) return;

    try {
      setCheckinLoading(true);
      
      const checkinData = {
        escala_id: selectedEscala.id,
        gps_lat: userLocation.lat,
        gps_long: userLocation.lng,
        status: 'Realizado',
        observacoes: ''
      };

      await api.post('/checkins', checkinData);
      
      // Recarregar dados
      await loadData();
      
      setShowCheckinModal(false);
      setSelectedEscala(null);
      
    } catch (error) {
      console.error('Erro ao realizar check-in:', error);
      setError('Erro ao realizar check-in. Tente novamente.');
    } finally {
      setCheckinLoading(false);
    }
  };

  const validateLocation = (escala) => {
    if (!userLocation || !escala.estabelecimento) return false;
    
    const estabelecimento = estabelecimentos.find(e => e.id === escala.estabelecimento_id);
    if (!estabelecimento) return false;
    
    const distance = calculateDistance(
      userLocation.lat,
      userLocation.lng,
      estabelecimento.latitude,
      estabelecimento.longitude
    );
    
    return distance <= estabelecimento.raio_checkin;
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371e3; // Raio da Terra em metros
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;

    const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c; // Distância em metros
  };

  const getStatusBadge = (status) => {
    const variants = {
      'Realizado': 'success',
      'Ausente': 'danger',
      'Fora de Local': 'warning'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const getEstabelecimentoNome = (id) => {
    const estabelecimento = estabelecimentos.find(e => e.id === id);
    return estabelecimento ? estabelecimento.nome : 'N/A';
  };

  const getEscalasHoje = () => {
    if (!escalas || !Array.isArray(escalas)) return [];
    const hoje = new Date().toISOString().split('T')[0];
    return escalas.filter(escala => {
      const escalaDate = new Date(escala.data_inicio).toISOString().split('T')[0];
      return escalaDate === hoje && escala.status === 'Confirmado';
    });
  };

  const getEscalasSemCheckin = () => {
    const escalasHoje = getEscalasHoje();
    if (!checkins || !Array.isArray(checkins)) return escalasHoje;
    return escalasHoje.filter(escala => {
      return !checkins.some(checkin => checkin.escala_id === escala.id);
    });
  };

  const filteredCheckins = checkins && Array.isArray(checkins) ? checkins.filter(checkin => {
    if (filterStatus && checkin.status !== filterStatus) return false;
    if (filterEstabelecimento) {
      const escala = escalas && Array.isArray(escalas) ? escalas.find(e => e.id === checkin.escala_id) : null;
      if (!escala || escala.estabelecimento_id !== parseInt(filterEstabelecimento)) return false;
    }
    return true;
  }) : [];

  if (loading) {
    return (
      <div className="checkins-loading">
        <Container fluid>
          <Row className="justify-content-center">
            <Col md={6} className="text-center">
              <Spinner animation="border" role="status" className="mb-3">
                <span className="visually-hidden">Carregando...</span>
              </Spinner>
              <h4>Carregando check-ins...</h4>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }

  if (error) {
    return (
      <div className="checkins-error">
        <Container fluid>
          <Row className="justify-content-center">
            <Col md={6} className="text-center">
              <Alert variant="danger">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
              </Alert>
              <Button 
                variant="primary"
                onClick={loadData}
              >
                <i className="fas fa-redo me-2"></i>
                Tentar Novamente
              </Button>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }

  return (
    <div className="checkins">
      <Container fluid>
        {/* Header */}
        <Row className="mb-4">
          <Col>
            <h1 className="checkins-title">
              <i className="fas fa-map-marker-alt me-3"></i>
              Check-ins com GPS
            </h1>
            <p className="text-muted">
              Realize check-ins com validação de localização
            </p>
          </Col>
        </Row>

        {/* Status da Localização */}
        {locationError && (
          <Row className="mb-4">
            <Col>
              <Alert variant="warning">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {locationError}
                <Button 
                  variant="outline-warning" 
                  size="sm" 
                  className="ms-3"
                  onClick={getCurrentLocation}
                >
                  <i className="fas fa-sync-alt me-1"></i>
                  Tentar Novamente
                </Button>
              </Alert>
            </Col>
          </Row>
        )}

        {userLocation && (
          <Row className="mb-4">
            <Col>
              <Alert variant="success">
                <i className="fas fa-check-circle me-2"></i>
                Localização obtida: {userLocation.lat.toFixed(6)}, {userLocation.lng.toFixed(6)}
              </Alert>
            </Col>
          </Row>
        )}

        {/* Escalas Pendentes */}
        <Row className="mb-4">
          <Col>
            <Card className="pending-card">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-clock me-2"></i>
                  Escalas Pendentes de Check-in
                </h5>
              </Card.Header>
              <Card.Body>
                {getEscalasSemCheckin().length > 0 ? (
                  <Row>
                    {getEscalasSemCheckin().map(escala => {
                      const estabelecimento = estabelecimentos.find(e => e.id === escala.estabelecimento_id);
                      const isLocationValid = validateLocation(escala);
                      
                      return (
                        <Col md={6} lg={4} key={escala.id} className="mb-3">
                          <Card className={`escala-card ${isLocationValid ? 'location-valid' : 'location-invalid'}`}>
                            <Card.Body>
                              <div className="escala-header">
                                <h6>{estabelecimento?.nome}</h6>
                                <Badge bg={isLocationValid ? 'success' : 'warning'}>
                                  {isLocationValid ? 'Localização OK' : 'Fora do Raio'}
                                </Badge>
                              </div>
                              <div className="escala-details">
                                <p><strong>Horário:</strong> {escala.hora_inicio} - {escala.hora_fim}</p>
                                <p><strong>Setor:</strong> {escala.setor || 'Não informado'}</p>
                                {estabelecimento && (
                                  <p><strong>Raio:</strong> {estabelecimento.raio_checkin}m</p>
                                )}
                              </div>
                              <Button 
                                variant={isLocationValid ? 'success' : 'warning'}
                                onClick={() => handleCheckin(escala)}
                                disabled={!isLocationValid}
                                className="w-100"
                              >
                                <i className="fas fa-check me-2"></i>
                                {isLocationValid ? 'Realizar Check-in' : 'Fora do Local'}
                              </Button>
                            </Card.Body>
                          </Card>
                        </Col>
                      );
                    })}
                  </Row>
                ) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-check-circle fa-3x mb-3"></i>
                    <p>Nenhuma escala pendente de check-in</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Mapa */}
        <Row className="mb-4">
          <Col>
            <Card className="map-card">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-map me-2"></i>
                  Mapa de Localização
                </h5>
              </Card.Header>
              <Card.Body>
                {userLocation ? (
                  <MapContainer 
                    center={[userLocation.lat, userLocation.lng]} 
                    zoom={15} 
                    style={{ height: '400px', width: '100%' }}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    
                    {/* Marcador da localização do usuário */}
                    <Marker position={[userLocation.lat, userLocation.lng]}>
                      <Popup>
                        <strong>Sua Localização</strong><br />
                        {userLocation.lat.toFixed(6)}, {userLocation.lng.toFixed(6)}
                      </Popup>
                    </Marker>
                    
                    {/* Marcadores dos estabelecimentos */}
                    {estabelecimentos && Array.isArray(estabelecimentos) ? estabelecimentos.map(estabelecimento => (
                      <div key={estabelecimento.id}>
                        <Marker position={[estabelecimento.latitude, estabelecimento.longitude]}>
                          <Popup>
                            <strong>{estabelecimento.nome}</strong><br />
                            {estabelecimento.endereco}<br />
                            Raio: {estabelecimento.raio_checkin}m
                          </Popup>
                        </Marker>
                        <Circle
                          center={[estabelecimento.latitude, estabelecimento.longitude]}
                          radius={estabelecimento.raio_checkin}
                          pathOptions={{ color: 'blue', fillColor: 'blue', fillOpacity: 0.1 }}
                        />
                      </div>
                    )) : null}
                  </MapContainer>
                ) : (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-map fa-3x mb-3"></i>
                    <p>Aguardando localização...</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Histórico de Check-ins */}
        <Row>
          <Col>
            <Card>
              <Card.Header>
                <div className="d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">
                    <i className="fas fa-history me-2"></i>
                    Histórico de Check-ins
                  </h5>
                  <div className="d-flex gap-2">
                    <Form.Select 
                      value={filterStatus} 
                      onChange={(e) => setFilterStatus(e.target.value)}
                      style={{ width: 'auto' }}
                    >
                      <option value="">Todos os Status</option>
                      <option value="Realizado">Realizado</option>
                      <option value="Ausente">Ausente</option>
                      <option value="Fora de Local">Fora de Local</option>
                    </Form.Select>
                    <Form.Select 
                      value={filterEstabelecimento} 
                      onChange={(e) => setFilterEstabelecimento(e.target.value)}
                      style={{ width: 'auto' }}
                    >
                      <option value="">Todos os Estabelecimentos</option>
                      {estabelecimentos && Array.isArray(estabelecimentos) ? estabelecimentos.map(est => (
                        <option key={est.id} value={est.id}>{est.nome}</option>
                      )) : null}
                    </Form.Select>
                  </div>
                </div>
              </Card.Header>
              <Card.Body>
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Data/Hora</th>
                      <th>Estabelecimento</th>
                      <th>Setor</th>
                      <th>Localização</th>
                      <th>Status</th>
                      <th>Observações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCheckins.map(checkin => {
                      const escala = escalas.find(e => e.id === checkin.escala_id);
                      return (
                        <tr key={checkin.id}>
                          <td>{new Date(checkin.data_hora).toLocaleString('pt-BR')}</td>
                          <td>{getEstabelecimentoNome(escala?.estabelecimento_id)}</td>
                          <td>{escala?.setor || '-'}</td>
                          <td>
                            {checkin.gps_lat && checkin.gps_long ? (
                              <small>
                                {checkin.gps_lat.toFixed(4)}, {checkin.gps_long.toFixed(4)}
                              </small>
                            ) : (
                              <span className="text-muted">Não registrado</span>
                            )}
                          </td>
                          <td>{getStatusBadge(checkin.status)}</td>
                          <td>{checkin.observacoes || '-'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
                
                {filteredCheckins.length === 0 && (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-history fa-3x mb-3"></i>
                    <p>Nenhum check-in encontrado</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Modal de Confirmação de Check-in */}
        <Modal show={showCheckinModal} onHide={() => setShowCheckinModal(false)}>
          <Modal.Header closeButton>
            <Modal.Title>
              <i className="fas fa-check-circle me-2"></i>
              Confirmar Check-in
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {selectedEscala && (
              <div>
                <p><strong>Estabelecimento:</strong> {getEstabelecimentoNome(selectedEscala.estabelecimento_id)}</p>
                <p><strong>Horário:</strong> {selectedEscala.hora_inicio} - {selectedEscala.hora_fim}</p>
                <p><strong>Setor:</strong> {selectedEscala.setor || 'Não informado'}</p>
                <p><strong>Sua Localização:</strong> {userLocation?.lat.toFixed(6)}, {userLocation?.lng.toFixed(6)}</p>
                
                {validateLocation(selectedEscala) ? (
                  <Alert variant="success">
                    <i className="fas fa-check-circle me-2"></i>
                    Localização válida! Você está dentro do raio permitido.
                  </Alert>
                ) : (
                  <Alert variant="warning">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    Atenção: Você está fora do raio permitido para este estabelecimento.
                  </Alert>
                )}
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowCheckinModal(false)}>
              Cancelar
            </Button>
            <Button 
              variant="success" 
              onClick={confirmCheckin}
              disabled={checkinLoading || !validateLocation(selectedEscala)}
            >
              {checkinLoading ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Processando...
                </>
              ) : (
                <>
                  <i className="fas fa-check me-2"></i>
                  Confirmar Check-in
                </>
              )}
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    </div>
  );
};

export default Checkins; 