import React, { useState, useEffect, useRef } from 'react';
import { Badge, Dropdown, ListGroup, Button, Modal, Form } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import './NotificationCenter.css';

const NotificationCenter = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showModal, setShowModal] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    if (user) {
      loadNotifications();
      connectWebSocket();
    }

    return () => {
      if (websocket) {
        websocket.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [user]);

  const connectWebSocket = () => {
    if (!user) return;

    const token = localStorage.getItem('token');
    const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
      
      // Subscribe to notification types
      ws.send(JSON.stringify({
        type: 'subscribe',
        notification_types: ['checkin_pending', 'escala_confirmed', 'document_processed', 'system_alert', 'maintenance']
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
      
      // Attempt to reconnect after 5 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    setWebsocket(ws);
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'notification':
        // Add new notification to the list
        setNotifications(prev => [data.notification, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // Show toast notification
        showToastNotification(data.notification);
        break;
      
      case 'connection':
        console.log('Connected to notification system');
        break;
      
      case 'subscription_confirmed':
        console.log('Subscribed to notifications:', data.notification_types);
        break;
      
      case 'pong':
        // Handle ping-pong for connection health
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const showToastNotification = (notification) => {
    // Create a toast notification
    const toast = document.createElement('div');
    toast.className = `notification-toast notification-toast-${notification.prioridade}`;
    toast.innerHTML = `
      <div class="toast-header">
        <strong>${notification.titulo}</strong>
        <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
      </div>
      <div class="toast-body">
        ${notification.mensagem}
      </div>
    `;
    
    document.body.appendChild(toast);
    
    // Remove toast after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 5000);
  };

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/notificacoes');
      setNotifications(response.data);
      
      // Count unread notifications
      const unread = response.data.filter(n => !n.lida).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.put(`/notificacoes/${notificationId}/read`);
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => 
          n.id === notificationId ? { ...n, lida: true } : n
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.put('/notificacoes/mark-all-read');
      
      // Update local state
      setNotifications(prev => 
        prev.map(n => ({ ...n, lida: true }))
      );
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await api.delete(`/notificacoes/${notificationId}`);
      
      // Update local state
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      
      // Update unread count if notification was unread
      const notification = notifications.find(n => n.id === notificationId);
      if (notification && !notification.lida) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const handleNotificationClick = (notification) => {
    if (!notification.lida) {
      markAsRead(notification.id);
    }
    
    setSelectedNotification(notification);
    setShowModal(true);
  };

  const getNotificationIcon = (tipo) => {
    const icons = {
      'checkin_pending': 'fas fa-clock text-warning',
      'escala_confirmed': 'fas fa-calendar-check text-success',
      'document_processed': 'fas fa-file-alt text-info',
      'system_alert': 'fas fa-exclamation-triangle text-danger',
      'maintenance': 'fas fa-tools text-warning'
    };
    return icons[tipo] || 'fas fa-bell text-secondary';
  };

  const getNotificationPriorityColor = (prioridade) => {
    const colors = {
      'low': 'secondary',
      'normal': 'primary',
      'high': 'danger'
    };
    return colors[prioridade] || 'primary';
  };

  const formatNotificationTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `${diffMins} min atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays} dias atrás`;
    
    return date.toLocaleDateString('pt-BR');
  };

  return (
    <>
      <Dropdown align="end" className="notification-dropdown">
        <Dropdown.Toggle variant="link" className="notification-toggle">
          <i className="fas fa-bell"></i>
          {unreadCount > 0 && (
            <Badge 
              bg="danger" 
              className="notification-badge"
              pill
            >
              {unreadCount > 99 ? '99+' : unreadCount}
            </Badge>
          )}
          <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}></div>
        </Dropdown.Toggle>

        <Dropdown.Menu className="notification-menu">
          <div className="notification-header">
            <h6 className="mb-0">Notificações</h6>
            <div className="notification-actions">
              {unreadCount > 0 && (
                <Button 
                  size="sm" 
                  variant="outline-primary"
                  onClick={markAllAsRead}
                >
                  Marcar todas como lidas
                </Button>
              )}
            </div>
          </div>

          <div className="notification-list">
            {loading ? (
              <div className="text-center py-3">
                <div className="spinner-border spinner-border-sm" role="status">
                  <span className="visually-hidden">Carregando...</span>
                </div>
              </div>
            ) : notifications.length === 0 ? (
              <div className="text-center py-3 text-muted">
                <i className="fas fa-bell-slash fa-2x mb-2"></i>
                <p>Nenhuma notificação</p>
              </div>
            ) : (
              <ListGroup variant="flush">
                {notifications.slice(0, 10).map(notification => (
                  <ListGroup.Item 
                    key={notification.id}
                    className={`notification-item ${!notification.lida ? 'unread' : ''}`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="notification-content">
                      <div className="notification-icon">
                        <i className={getNotificationIcon(notification.tipo)}></i>
                      </div>
                      <div className="notification-details">
                        <div className="notification-title">
                          {notification.titulo}
                          {!notification.lida && (
                            <Badge 
                              bg={getNotificationPriorityColor(notification.prioridade)}
                              size="sm"
                              className="ms-2"
                            >
                              {notification.prioridade}
                            </Badge>
                          )}
                        </div>
                        <div className="notification-message">
                          {notification.mensagem}
                        </div>
                        <div className="notification-time">
                          {formatNotificationTime(notification.data_criacao)}
                        </div>
                      </div>
                      <div className="notification-actions">
                        <Button
                          size="sm"
                          variant="outline-danger"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                        >
                          <i className="fas fa-trash"></i>
                        </Button>
                      </div>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
          </div>

          {notifications.length > 10 && (
            <div className="notification-footer">
              <Button 
                variant="link" 
                size="sm"
                onClick={() => setShowModal(true)}
              >
                Ver todas as notificações
              </Button>
            </div>
          )}
        </Dropdown.Menu>
      </Dropdown>

      {/* Notification Detail Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className={`${getNotificationIcon(selectedNotification?.tipo)} me-2`}></i>
            {selectedNotification?.titulo}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedNotification && (
            <div>
              <div className="notification-detail-meta">
                <Badge bg={getNotificationPriorityColor(selectedNotification.prioridade)}>
                  {selectedNotification.prioridade}
                </Badge>
                <span className="text-muted ms-2">
                  {formatNotificationTime(selectedNotification.data_criacao)}
                </span>
              </div>
              
              <div className="notification-detail-message">
                {selectedNotification.mensagem}
              </div>
              
              {selectedNotification.dados_adicional && Object.keys(selectedNotification.dados_adicional).length > 0 && (
                <div className="notification-detail-data">
                  <h6>Informações Adicionais:</h6>
                  <pre className="bg-light p-3 rounded">
                    {JSON.stringify(selectedNotification.dados_adicional, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Fechar
          </Button>
          {selectedNotification && !selectedNotification.lida && (
            <Button 
              variant="primary"
              onClick={() => {
                markAsRead(selectedNotification.id);
                setShowModal(false);
              }}
            >
              Marcar como lida
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default NotificationCenter; 