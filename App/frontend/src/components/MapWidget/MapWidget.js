import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Form, Alert, Spinner, InputGroup, Badge } from 'react-bootstrap';
import './MapWidget.css';

const MapWidget = ({ 
  latitude, 
  longitude, 
  endereco, 
  raio = 100,
  onLocationChange,
  onEnderecoChange,
  disabled = false 
}) => {
  const [isLoadingGeocoding, setIsLoadingGeocoding] = useState(false);
  const [geocodingError, setGeocodingError] = useState(null);
  const [mapUrl, setMapUrl] = useState('');
  const [showMap, setShowMap] = useState(false);
  const [tempEndereco, setTempEndereco] = useState(endereco || '');
  const mapRef = useRef(null);

  // Atualizar URL do mapa quando coordenadas mudarem
  useEffect(() => {
    if (latitude && longitude) {
      const zoom = 15;
      // Usar OpenStreetMap em iframe simples
      const mapUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${longitude-0.01},${latitude-0.01},${longitude+0.01},${latitude+0.01}&layer=mapnik&marker=${latitude},${longitude}`;
      setMapUrl(mapUrl);
      setShowMap(true);
    }
  }, [latitude, longitude]);

  // Buscar coordenadas por endereço usando Nominatim (OpenStreetMap)
  const buscarCoordenadas = async (endereco) => {
    if (!endereco || endereco.trim().length < 10) {
      setGeocodingError('Endereço deve ter pelo menos 10 caracteres');
      return;
    }

    setIsLoadingGeocoding(true);
    setGeocodingError(null);

    try {
      // Usar Nominatim (OpenStreetMap) - Gratuito e sem API key
      const geocodingUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(endereco + ' Brasil')}&limit=1&addressdetails=1`;
      
      const response = await fetch(geocodingUrl, {
        headers: {
          'User-Agent': 'WeCare-App/1.0' // Requerido pelo Nominatim
        }
      });
      
      if (!response.ok) {
        throw new Error('Erro na busca de endereço');
      }
      
      const data = await response.json();

      if (data && data.length > 0) {
        const result = data[0];
        const lat = parseFloat(result.lat);
        const lng = parseFloat(result.lon);

        if (onLocationChange) {
          onLocationChange(lat, lng);
        }

        // Formatar endereço retornado
        const enderecoFormatado = result.display_name || endereco;
        if (onEnderecoChange) {
          onEnderecoChange(enderecoFormatado);
        }

        setTempEndereco(enderecoFormatado);
        setGeocodingError(null);
      } else {
        setGeocodingError('Endereço não encontrado. Verifique se o endereço está correto e inclui cidade/estado.');
      }
    } catch (error) {
      console.error('Erro ao buscar coordenadas:', error);
      setGeocodingError('Erro ao buscar coordenadas. Verifique sua conexão e tente novamente.');
    } finally {
      setIsLoadingGeocoding(false);
    }
  };

  // Obter localização atual do usuário
  const obterLocalizacaoAtual = async () => {
    setIsLoadingGeocoding(true);
    
    try {
      if (!navigator.geolocation) {
        throw new Error('Geolocalização não é suportada neste navegador');
      }

      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        });
      });

      const { latitude: lat, longitude: lng } = position.coords;
      
      if (onLocationChange) {
        onLocationChange(lat, lng);
      }

      // Buscar endereço da localização atual
      await buscarEndereco(lat, lng);
      
    } catch (error) {
      let message = 'Erro ao obter localização: ';
      if (error.code === 1) {
        message += 'Permissão negada pelo usuário';
      } else if (error.code === 2) {
        message += 'Localização indisponível';
      } else if (error.code === 3) {
        message += 'Tempo esgotado';
      } else {
        message += error.message;
      }
      setGeocodingError(message);
    } finally {
      setIsLoadingGeocoding(false);
    }
  };

  // Buscar endereço por coordenadas (reverse geocoding)
  const buscarEndereco = async (lat, lng) => {
    try {
      const reverseUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`;
      
      const response = await fetch(reverseUrl, {
        headers: {
          'User-Agent': 'WeCare-App/1.0'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data && data.display_name) {
          const endereco = data.display_name;
          setTempEndereco(endereco);
          
          if (onEnderecoChange) {
            onEnderecoChange(endereco);
          }
        }
      }
    } catch (error) {
      console.error('Erro ao buscar endereço:', error);
    }
  };

  // Abrir no Google Maps
  const abrirNoGoogleMaps = () => {
    if (latitude && longitude) {
      const url = `https://www.google.com/maps?q=${latitude},${longitude}&zoom=16`;
      window.open(url, '_blank');
    }
  };

  // Abrir no OpenStreetMap
  const abrirNoOpenStreetMap = () => {
    if (latitude && longitude) {
      const url = `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}&zoom=16`;
      window.open(url, '_blank');
    }
  };

  // Copiar coordenadas
  const copiarCoordenadas = async () => {
    if (latitude && longitude) {
      const coords = `${latitude}, ${longitude}`;
      try {
        await navigator.clipboard.writeText(coords);
        // TODO: Mostrar toast de sucesso
        console.log('Coordenadas copiadas:', coords);
      } catch (error) {
        console.error('Erro ao copiar coordenadas:', error);
      }
    }
  };

  // Calcular área do círculo do raio
  const calcularArea = (raio) => {
    const area = Math.PI * Math.pow(raio, 2);
    return area > 10000 ? `${(area / 10000).toFixed(1)} hectares` : `${area.toFixed(0)} m²`;
  };

  return (
    <Card className="map-widget">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <div className="d-flex align-items-center">
          <i className="fas fa-map-marked-alt me-2 text-white"></i>
          <span className="fw-bold">Localização & Mapa</span>
        </div>
        {latitude && longitude && (
          <div className="d-flex gap-2">
            <Button
              variant="outline-light"
              size="sm"
              onClick={copiarCoordenadas}
              title="Copiar coordenadas"
            >
              <i className="fas fa-copy"></i>
            </Button>
            <Button
              variant="outline-light"
              size="sm"
              onClick={abrirNoOpenStreetMap}
              title="Abrir no OpenStreetMap"
            >
              <i className="fas fa-map"></i>
            </Button>
            <Button
              variant="outline-light"
              size="sm"
              onClick={abrirNoGoogleMaps}
              title="Abrir no Google Maps"
            >
              <i className="fas fa-external-link-alt"></i>
            </Button>
          </div>
        )}
      </Card.Header>

      <Card.Body>
        {/* Busca por endereço */}
        <Form.Group className="mb-3">
          <Form.Label className="d-flex align-items-center">
            <i className="fas fa-search me-2"></i>
            Buscar por Endereço
          </Form.Label>
          <InputGroup>
            <Form.Control
              type="text"
              placeholder="Digite o endereço completo (ex: Rua das Flores, 123, São Paulo, SP)..."
              value={tempEndereco}
              onChange={(e) => setTempEndereco(e.target.value)}
              disabled={disabled || isLoadingGeocoding}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  buscarCoordenadas(tempEndereco);
                }
              }}
            />
            <Button
              variant="primary"
              onClick={() => buscarCoordenadas(tempEndereco)}
              disabled={disabled || isLoadingGeocoding || !tempEndereco.trim()}
            >
              {isLoadingGeocoding ? (
                <Spinner as="span" animation="border" size="sm" />
              ) : (
                <i className="fas fa-search"></i>
              )}
            </Button>
          </InputGroup>
          <Form.Text className="text-muted">
            Digite um endereço completo incluindo cidade e estado para melhores resultados
          </Form.Text>
        </Form.Group>

        {/* Botão para obter localização atual */}
        <div className="mb-3">
          <Button
            variant="outline-success"
            onClick={obterLocalizacaoAtual}
            disabled={disabled || isLoadingGeocoding}
            className="w-100"
          >
            {isLoadingGeocoding ? (
              <>
                <Spinner as="span" animation="border" size="sm" className="me-2" />
                Obtendo localização...
              </>
            ) : (
              <>
                <i className="fas fa-crosshairs me-2"></i>
                Usar Minha Localização Atual
              </>
            )}
          </Button>
        </div>

        {/* Erro de geocoding */}
        {geocodingError && (
          <Alert variant="warning" className="mb-3">
            <i className="fas fa-exclamation-triangle me-2"></i>
            {geocodingError}
          </Alert>
        )}

        {/* Coordenadas atuais */}
        {latitude && longitude && (
          <div className="coordinates-info mb-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="fw-bold text-success">
                <i className="fas fa-crosshairs me-2"></i>
                Coordenadas Encontradas
              </span>
              <Badge bg="success" className="d-flex align-items-center">
                <i className="fas fa-check-circle me-1"></i>
                Válido
              </Badge>
            </div>
            
            <div className="row">
              <div className="col-6">
                <small className="text-muted d-block">Latitude</small>
                <code className="coordinate-value">{latitude.toFixed(8)}</code>
              </div>
              <div className="col-6">
                <small className="text-muted d-block">Longitude</small>
                <code className="coordinate-value">{longitude.toFixed(8)}</code>
              </div>
            </div>

            {/* Informações do raio */}
            <div className="radius-info mt-3 p-2 bg-light rounded">
              <div className="row">
                <div className="col-4">
                  <small className="text-muted d-block">Raio Check-in</small>
                  <span className="fw-bold text-info">{raio}m</span>
                </div>
                <div className="col-4">
                  <small className="text-muted d-block">Área Cobertura</small>
                  <span className="fw-bold text-info">{calcularArea(raio)}</span>
                </div>
                <div className="col-4">
                  <small className="text-muted d-block">Diâmetro</small>
                  <span className="fw-bold text-info">{raio * 2}m</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mapa incorporado */}
        {showMap && mapUrl && (
          <div className="map-container">
            <div className="map-header mb-2">
              <span className="text-muted">
                <i className="fas fa-map me-2"></i>
                Visualização do Local
              </span>
            </div>
            <div className="map-iframe-container">
              <iframe
                ref={mapRef}
                src={mapUrl}
                width="100%"
                height="300"
                style={{ border: 0, borderRadius: '8px' }}
                allowFullScreen=""
                loading="lazy"
                title="Mapa do Estabelecimento"
              />
              
              {/* Indicador do raio de check-in */}
              <div className="radius-overlay">
                <div 
                  className="radius-circle"
                  style={{
                    width: `${Math.min(raio / 3, 120)}px`,
                    height: `${Math.min(raio / 3, 120)}px`,
                  }}
                >
                  <div className="radius-label">
                    Raio: {raio}m
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dicas de uso */}
        <div className="usage-tips mt-3">
          <Alert variant="info" className="small mb-0">
            <i className="fas fa-lightbulb me-2"></i>
            <strong>Dicas:</strong>
            <ul className="mb-0 mt-1 ps-3">
              <li>Digite o endereço completo incluindo cidade e estado</li>
              <li>Use "Minha Localização Atual" para GPS automático</li>
              <li>O círculo no mapa representa a área de check-in permitida</li>
              <li>Clique nos botões para abrir em mapas externos</li>
              <li>Use o botão copiar para salvar as coordenadas</li>
            </ul>
          </Alert>
        </div>
      </Card.Body>
    </Card>
  );
};

export default MapWidget; 