import axios from 'axios';

// Configuração base do axios
const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar respostas e erros
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error.response?.data || error);
  }
);

const apiService = {
  // Autenticação
  login: async (credentials) => {
    return api.post('/auth/login', {
      email: credentials.email,
      senha: credentials.senha
    });
  },

  // Usuários
  getUsuarios: async () => {
    return api.get('/usuarios/');
  },

  getUsuario: async (id) => {
    return api.get(`/usuarios/${id}`);
  },

  createUsuario: async (userData) => {
    return api.post('/usuarios/', userData);
  },

  updateUsuario: async (id, userData) => {
    return api.put(`/usuarios/${id}`, userData);
  },

  deleteUsuario: async (id) => {
    return api.delete(`/usuarios/${id}`);
  },

  // Escalas
  getEscalas: async () => {
    return api.get('/escalas/');
  },

  getEscala: async (id) => {
    return api.get(`/escalas/${id}`);
  },

  createEscala: async (escalaData) => {
    return api.post('/escalas/', escalaData);
  },

  updateEscala: async (id, escalaData) => {
    return api.put(`/escalas/${id}`, escalaData);
  },

  deleteEscala: async (id) => {
    return api.delete(`/escalas/${id}`);
  },

  // Check-ins
  getCheckins: async () => {
    return api.get('/checkins/');
  },

  getCheckin: async (id) => {
    return api.get(`/checkins/${id}`);
  },

  createCheckin: async (checkinData) => {
    return api.post('/checkins/', checkinData);
  },

  // Documentos
  getDocumentos: async () => {
    return api.get('/documentos/');
  },

  getDocumento: async (id) => {
    return api.get(`/documentos/${id}`);
  },

  uploadDocumento: async (formData) => {
    return api.post('/documentos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  deleteDocumento: async (id) => {
    return api.delete(`/documentos/${id}`);
  },

  // Relatórios
  getRelatorios: async (params) => {
    return api.get('/relatorios/', { params });
  },

  downloadRelatorio: async (tipo, params) => {
    return api.get(`/relatorios/${tipo}`, {
      params,
      responseType: 'blob',
    });
  },

  // Dashboard
  getDashboardStats: async () => {
    return api.get('/dashboard/stats');
  },

  // Perfil do usuário atual
  getCurrentUser: async () => {
    return api.get('/auth/me');
  },

  updateProfile: async (userData) => {
    return api.put('/auth/me', userData);
  },

  changePassword: async (passwordData) => {
    return api.put('/auth/change-password', passwordData);
  },
};

export default apiService; 