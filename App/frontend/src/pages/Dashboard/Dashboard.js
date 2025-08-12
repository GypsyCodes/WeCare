import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Alert, Spinner } from 'react-bootstrap';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './Dashboard.css';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    escalasHoje: 0,
    checkinsPendentes: 0,
    usuariosAtivos: 0,
    estabelecimentos: 0,
    alertas: []
  });
  const [chartData, setChartData] = useState({
    checkinsSemana: { labels: [], data: [] },
    escalasMes: { labels: [], data: [] },
    usuariosPorPerfil: { labels: [], data: [] }
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Carregar estatísticas gerais
      const statsResponse = await api.get('/relatorios/dashboard-stats');
      setStats(statsResponse.data);
      
      // Carregar dados para gráficos
      const [checkinsResponse, escalasResponse, usuariosResponse] = await Promise.all([
        api.get('/relatorios/checkins-semana'),
        api.get('/relatorios/escalas-mes'),
        api.get('/relatorios/usuarios-perfil')
      ]);
      
      setChartData({
        checkinsSemana: checkinsResponse.data,
        escalasMes: escalasResponse.data,
        usuariosPorPerfil: usuariosResponse.data
      });
      
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      setError('Erro ao carregar dados do dashboard. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const checkinsChartData = {
    labels: chartData.checkinsSemana.labels,
    datasets: [
      {
        label: 'Check-ins Realizados',
        data: chartData.checkinsSemana.data,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      }
    ]
  };

  const escalasChartData = {
    labels: chartData.escalasMes.labels,
    datasets: [
      {
        label: 'Escalas Confirmadas',
        data: chartData.escalasMes.data,
        backgroundColor: 'rgba(54, 162, 235, 0.8)',
      }
    ]
  };

  const usuariosChartData = {
    labels: chartData.usuariosPorPerfil.labels,
    datasets: [
      {
        data: chartData.usuariosPorPerfil.data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
        ],
      }
    ]
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <Container fluid>
          <Row className="justify-content-center">
            <Col md={6} className="text-center">
              <Spinner animation="border" role="status" className="mb-3">
                <span className="visually-hidden">Carregando...</span>
              </Spinner>
              <h4>Carregando dashboard...</h4>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <Container fluid>
          <Row className="justify-content-center">
            <Col md={6} className="text-center">
              <Alert variant="danger">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
              </Alert>
              <button 
                className="btn btn-primary"
                onClick={loadDashboardData}
              >
                <i className="fas fa-redo me-2"></i>
                Tentar Novamente
              </button>
            </Col>
          </Row>
        </Container>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <Container fluid>
        {/* Header */}
        <Row className="mb-4">
          <Col>
            <h1 className="dashboard-title">
              {getGreeting()}, {user?.nome}!
            </h1>
            <p className="text-muted">
              Bem-vindo ao sistema We Care - {new Date().toLocaleDateString('pt-BR')}
            </p>
          </Col>
        </Row>

        {/* Alertas */}
        {stats.alertas && Array.isArray(stats.alertas) && stats.alertas.length > 0 && (
          <Row className="mb-4">
            <Col>
              {stats.alertas.map(alerta => (
                <Alert 
                  key={alerta.id} 
                  variant={alerta.tipo === 'warning' ? 'warning' : 'info'}
                  className="mb-2"
                >
                  <i className={`fas ${alerta.tipo === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'} me-2`}></i>
                  {alerta.mensagem}
                </Alert>
              ))}
            </Col>
          </Row>
        )}

        {/* Cards de Estatísticas */}
        <Row className="mb-4">
          <Col md={3}>
            <Card className="stat-card text-center h-100">
              <Card.Body>
                <div className="stat-icon text-primary">
                  <i className="fas fa-calendar-day"></i>
                </div>
                <h3 className="stat-number">{stats.escalasHoje}</h3>
                <p className="text-muted mb-0">Escalas Hoje</p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="stat-card text-center h-100">
              <Card.Body>
                <div className="stat-icon text-warning">
                  <i className="fas fa-clock"></i>
                </div>
                <h3 className="stat-number">{stats.checkinsPendentes}</h3>
                <p className="text-muted mb-0">Check-ins Pendentes</p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="stat-card text-center h-100">
              <Card.Body>
                <div className="stat-icon text-success">
                  <i className="fas fa-users"></i>
                </div>
                <h3 className="stat-number">{stats.usuariosAtivos}</h3>
                <p className="text-muted mb-0">Usuários Ativos</p>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={3}>
            <Card className="stat-card text-center h-100">
              <Card.Body>
                <div className="stat-icon text-info">
                  <i className="fas fa-hospital"></i>
                </div>
                <h3 className="stat-number">{stats.estabelecimentos}</h3>
                <p className="text-muted mb-0">Estabelecimentos</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Gráficos */}
        <Row className="mb-4">
          <Col lg={8}>
            <Card className="chart-card h-100">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-chart-line me-2"></i>
                  Check-ins da Semana
                </h5>
              </Card.Header>
              <Card.Body>
                {chartData.checkinsSemana.data.length > 0 ? (
                  <Line 
                    data={checkinsChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                    height={300}
                  />
                ) : (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-chart-line fa-3x mb-3"></i>
                    <p>Nenhum dado de check-in disponível</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
          
          <Col lg={4}>
            <Card className="chart-card h-100">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-chart-pie me-2"></i>
                  Usuários por Perfil
                </h5>
              </Card.Header>
              <Card.Body>
                {chartData.usuariosPorPerfil.data.length > 0 ? (
                  <Doughnut 
                    data={usuariosChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                    height={300}
                  />
                ) : (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-chart-pie fa-3x mb-3"></i>
                    <p>Nenhum dado de usuários disponível</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Gráfico de Escalas */}
        <Row>
          <Col>
            <Card className="chart-card">
              <Card.Header>
                <h5 className="mb-0">
                  <i className="fas fa-chart-bar me-2"></i>
                  Escalas do Mês
                </h5>
              </Card.Header>
              <Card.Body>
                {chartData.escalasMes.data.length > 0 ? (
                  <Bar 
                    data={escalasChartData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                        },
                      },
                    }}
                    height={250}
                  />
                ) : (
                  <div className="text-center text-muted py-5">
                    <i className="fas fa-chart-bar fa-3x mb-3"></i>
                    <p>Nenhum dado de escalas disponível</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Dashboard; 