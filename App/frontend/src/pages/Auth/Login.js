import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [credentials, setCredentials] = useState({ email: '', senha: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(credentials);
      navigate('/dashboard');
    } catch (err) {
      setError('Email ou senha inválidos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">🏥</div>
          <h1 className="login-title">We Care</h1>
          <p className="login-subtitle">Soluções em Saúde</p>
                  </div>
        <div className="login-body">
          {error && <div className="alert alert-danger">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                      type="email"
                className="form-control"
                placeholder="Digite seu email"
                value={credentials.email}
                onChange={(e) => setCredentials({...credentials, email: e.target.value})}
                      required
                    />
            </div>
            <div className="form-group">
              <label className="form-label">Senha</label>
              <input
                type="password"
                className="form-control"
                        placeholder="Digite sua senha"
                value={credentials.senha}
                onChange={(e) => setCredentials({...credentials, senha: e.target.value})}
                        required
                      />
            </div>
            <button 
                    type="submit"
              className="btn-login"
              disabled={loading}
                  >
              {loading && <span className="loading-spinner"></span>}
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
                </div>
            </div>
    </div>
  );
};

export default Login; 