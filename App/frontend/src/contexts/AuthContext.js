import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Verificar se o token é válido na inicialização
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (token) {
          // Verificar se o token ainda é válido e obter dados do usuário
          const response = await api.get('/auth/me');
          setUser(response.data);
        }
      } catch (error) {
        console.error('Erro ao inicializar autenticação:', error);
        // Token inválido, remover
        logout();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, [token]);

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', {
        email: credentials.email,
        senha: credentials.senha
      });
      const { access_token, user: userData } = response.data;
      
      // Armazenar token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    // O redirecionamento será feito pelo interceptor do api
  };

  const updateUser = (userData) => {
    setUser(prevUser => ({ ...prevUser, ...userData }));
  };

  // Verificar permissões
  const hasPermission = (requiredRole) => {
    if (!user) return false;
    
    const roles = {
      'Administrador': 3,
      'Supervisor': 2,
      'Socio': 1
    };
    
    const userLevel = roles[user.perfil] || 0;
    const requiredLevel = roles[requiredRole] || 0;
    
    return userLevel >= requiredLevel;
  };

  // Atualizar perfil
  const updateProfile = async (userData) => {
    try {
      const response = await api.put('/auth/me', userData);
      const updatedUser = response.data;
      setUser(updatedUser);
      return updatedUser;
    } catch (error) {
      throw error;
    }
  };

  // Alterar senha
  const changePassword = async (passwordData) => {
    try {
      await api.put('/auth/change-password', passwordData);
    } catch (error) {
      throw error;
    }
  };

  const value = {
    user,
    loading,
    login,
    logout,
    updateUser,
    hasPermission,
    updateProfile,
    changePassword,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 