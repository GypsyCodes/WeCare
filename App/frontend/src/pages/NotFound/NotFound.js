import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/dashboard');
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center text-center">
        <Col lg={6}>
          <div className="not-found-content">
            {/* 404 Illustration */}
            <div className="mb-5">
              <div className="error-code">404</div>
              <div className="error-illustration">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
            </div>

            {/* Error Message */}
            <h1 className="mb-3">Página não encontrada</h1>
            <p className="lead text-muted mb-4">
              Oops! A página que você está procurando não existe ou foi removida.
            </p>
            <p className="text-muted mb-4">
              Verifique o endereço digitado ou use os botões abaixo para navegar.
            </p>

            {/* Action Buttons */}
            <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
              <Button 
                variant="primary" 
                size="lg"
                onClick={handleGoHome}
                className="px-4"
              >
                <i className="fas fa-home me-2"></i>
                Ir para o Dashboard
              </Button>
              <Button 
                variant="outline-secondary" 
                size="lg"
                onClick={handleGoBack}
                className="px-4"
              >
                <i className="fas fa-arrow-left me-2"></i>
                Voltar
              </Button>
            </div>

            {/* Help Links */}
            <div className="mt-5 pt-4 border-top">
              <p className="mb-2">
                <strong>Links úteis:</strong>
              </p>
              <div className="d-flex flex-wrap justify-content-center gap-4">
                <Button 
                  variant="link" 
                  className="p-0"
                  onClick={() => navigate('/escalas')}
                >
                  <i className="fas fa-calendar-alt me-1"></i>
                  Escalas
                </Button>
                <Button 
                  variant="link" 
                  className="p-0"
                  onClick={() => navigate('/checkins')}
                >
                  <i className="fas fa-clock me-1"></i>
                  Check-ins
                </Button>
                <Button 
                  variant="link" 
                  className="p-0"
                  onClick={() => navigate('/usuarios')}
                >
                  <i className="fas fa-users me-1"></i>
                  Usuários
                </Button>
                <Button 
                  variant="link" 
                  className="p-0"
                  onClick={() => navigate('/relatorios')}
                >
                  <i className="fas fa-chart-bar me-1"></i>
                  Relatórios
                </Button>
              </div>
            </div>
          </div>
        </Col>
      </Row>

      <style jsx>{`
        .error-code {
          font-size: 8rem;
          font-weight: 900;
          color: #6c757d;
          line-height: 1;
          margin-bottom: 1rem;
        }
        
        .error-illustration {
          font-size: 4rem;
          color: #ffc107;
          margin-bottom: 2rem;
        }
        
        .not-found-content {
          animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @media (max-width: 576px) {
          .error-code {
            font-size: 5rem;
          }
          
          .error-illustration {
            font-size: 3rem;
          }
        }
      `}</style>
    </Container>
  );
};

export default NotFound; 