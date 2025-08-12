import React, { useState } from 'react';
import { Navbar, Nav, Container, Offcanvas, Button } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [showSidebar, setShowSidebar] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar);
  };

  const toggleSidebarExpanded = () => {
    setSidebarExpanded(!sidebarExpanded);
  };

  const closeSidebar = () => {
    setShowSidebar(false);
  };

  const menuItems = [
    { path: '/dashboard', icon: 'fas fa-tachometer-alt', label: 'Dashboard' },
    { path: '/escalas', icon: 'fas fa-calendar-alt', label: 'Escalas' },
    { path: '/estabelecimentos', icon: 'fas fa-building', label: 'Estabelecimentos' },
    { path: '/checkins', icon: 'fas fa-clock', label: 'Check-ins' },
    { path: '/usuarios', icon: 'fas fa-users', label: 'Usuários' },
    { path: '/documentos', icon: 'fas fa-file-alt', label: 'Documentos' },
    { path: '/relatorios', icon: 'fas fa-chart-bar', label: 'Relatórios' },
  ];

  return (
    <div className="layout">
      {/* Top Navigation Bar */}
      <Navbar bg="primary" variant="dark" expand="lg" fixed="top" className="top-navbar">
        <Container fluid>
          <Button
            variant="outline-light"
            className="me-3 d-lg-none sidebar-toggle"
            onClick={toggleSidebar}
          >
            <i className="fas fa-bars"></i>
          </Button>
          
          <Navbar.Brand href="/dashboard" className="d-flex align-items-center">
            <i className="fas fa-heart-pulse me-2"></i>
            We Care
          </Navbar.Brand>

          <Nav className="ms-auto d-flex align-items-center">
            {/* Theme Toggle */}
            <Button
              variant="outline-light"
              size="sm"
              onClick={toggleTheme}
              className="me-3"
              title={`Mudar para tema ${theme === 'light' ? 'escuro' : 'claro'}`}
            >
              <i className={`fas ${theme === 'light' ? 'fa-moon' : 'fa-sun'}`}></i>
            </Button>

            {/* User Menu */}
            <Nav.Link as="div" className="text-white d-flex align-items-center">
              <i className="fas fa-user-circle me-2"></i>
              <span className="me-3">{user?.nome || 'Usuário'}</span>
            </Nav.Link>

            <LinkContainer to="/profile">
              <Nav.Link className="text-white me-2">
                <i className="fas fa-cog"></i>
              </Nav.Link>
            </LinkContainer>

            <Button
              variant="outline-light"
              size="sm"
              onClick={handleLogout}
              title="Sair"
            >
              <i className="fas fa-sign-out-alt"></i>
            </Button>
          </Nav>
        </Container>
      </Navbar>

      <div className="layout-container">
        {/* Desktop Sidebar - Discreto */}
        <div className={`sidebar d-none d-lg-block ${sidebarExpanded ? 'expanded' : ''}`}>
          <div className="sidebar-content">
            {/* Toggle Button */}
            <div className="sidebar-toggle-btn">
              <Button
                variant="outline-primary"
                size="sm"
                onClick={toggleSidebarExpanded}
                className="toggle-btn"
                title={sidebarExpanded ? "Recolher menu" : "Expandir menu"}
              >
                <i className={`fas ${sidebarExpanded ? 'fa-chevron-left' : 'fa-chevron-right'}`}></i>
              </Button>
            </div>

            <Nav className="flex-column sidebar-nav">
              {menuItems.map((item) => (
                <LinkContainer key={item.path} to={item.path}>
                  <Nav.Link 
                    className={`sidebar-nav-link ${location.pathname === item.path ? 'active' : ''}`}
                    title={!sidebarExpanded ? item.label : ''}
                  >
                    <i className={`${item.icon} sidebar-icon`}></i>
                    {sidebarExpanded && <span className="sidebar-label">{item.label}</span>}
                  </Nav.Link>
                </LinkContainer>
              ))}
            </Nav>
          </div>
        </div>

        {/* Mobile Sidebar */}
        <Offcanvas show={showSidebar} onHide={closeSidebar} placement="start">
          <Offcanvas.Header closeButton>
            <Offcanvas.Title>
              <i className="fas fa-heart-pulse me-2 text-primary"></i>
              We Care
            </Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body>
            <Nav className="flex-column">
              {menuItems.map((item) => (
                <LinkContainer key={item.path} to={item.path}>
                  <Nav.Link className="mobile-nav-link" onClick={closeSidebar}>
                    <i className={`${item.icon} me-3`}></i>
                    {item.label}
                  </Nav.Link>
                </LinkContainer>
              ))}
            </Nav>
          </Offcanvas.Body>
        </Offcanvas>

        {/* Main Content */}
        <main className={`main-content ${sidebarExpanded ? 'sidebar-expanded' : ''}`}>
          <div className="content-wrapper">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout; 