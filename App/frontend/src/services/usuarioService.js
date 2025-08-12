import api from './api';

/**
 * Serviço para gerenciamento de usuários
 * Integração com APIs reais do backend
 */
class UsuarioService {
  
  // ==========================================
  // CRUD DE USUÁRIOS
  // ==========================================

  /**
   * Listar usuários com paginação e filtros
   */
  async listar(params = {}) {
    try {
      const response = await api.get('/usuarios', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar usuários');
    }
  }

  /**
   * Buscar usuário por ID
   */
  async buscarPorId(id) {
    try {
      const response = await api.get(`/usuarios/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar usuário');
    }
  }

  /**
   * Criar novo usuário
   */
  async criar(dadosUsuario) {
    try {
      const response = await api.post('/usuarios', dadosUsuario);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao criar usuário');
    }
  }

  /**
   * Atualizar usuário existente
   */
  async atualizar(id, dadosUsuario) {
    try {
      const response = await api.put(`/usuarios/${id}`, dadosUsuario);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao atualizar usuário');
    }
  }

  /**
   * Excluir usuário
   */
  async excluir(id) {
    try {
      await api.delete(`/usuarios/${id}`);
      return { success: true };
    } catch (error) {
      throw this.handleError(error, 'Erro ao excluir usuário');
    }
  }

  /**
   * Alterar status do usuário (ativar/desativar)
   */
  async alterarStatus(id, status) {
    try {
      const response = await api.put(`/usuarios/${id}/status`, { status });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao alterar status do usuário');
    }
  }

  // ==========================================
  // GERENCIAMENTO DE SENHAS
  // ==========================================

  /**
   * Gerar token de registro para usuário
   */
  async gerarTokenRegistro(id) {
    try {
      const response = await api.post(`/usuarios/${id}/generate-token`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao gerar token de registro');
    }
  }

  /**
   * Alterar senha do usuário
   */
  async alterarSenha(id, dadosSenha) {
    try {
      const response = await api.put(`/usuarios/${id}/change-password`, dadosSenha);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao alterar senha');
    }
  }

  /**
   * Redefinir senha do usuário (admin)
   */
  async redefinirSenha(id) {
    try {
      const response = await api.post(`/usuarios/${id}/reset-password`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao redefinir senha');
    }
  }

  // ==========================================
  // PERFIS E ESTABELECIMENTOS
  // ==========================================

  /**
   * Listar perfis disponíveis
   */
  async listarPerfis() {
    return [
      { value: 'Administrador', label: 'Administrador' },
      { value: 'Supervisor', label: 'Supervisor' },
      { value: 'Socio', label: 'Sócio' }
    ];
  }

  /**
   * Associar usuário a estabelecimentos
   */
  async associarEstabelecimentos(usuarioId, estabelecimentosIds) {
    try {
      const response = await api.post(`/usuarios/${usuarioId}/estabelecimentos`, {
        estabelecimentos: estabelecimentosIds
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao associar estabelecimentos');
    }
  }

  /**
   * Listar estabelecimentos do usuário
   */
  async listarEstabelecimentosUsuario(usuarioId) {
    try {
      const response = await api.get(`/usuarios/${usuarioId}/estabelecimentos`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar estabelecimentos do usuário');
    }
  }

  // ==========================================
  // ESTATÍSTICAS E RELATÓRIOS
  // ==========================================

  /**
   * Obter estatísticas dos usuários
   */
  async obterEstatisticas() {
    try {
      const response = await api.get('/usuarios/stats');
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar estatísticas');
    }
  }

  /**
   * Exportar usuários para CSV/Excel
   */
  async exportar(formato = 'csv', filtros = {}) {
    try {
      const response = await api.get('/usuarios/export', {
        params: { formato, ...filtros },
        responseType: 'blob'
      });
      
      // Criar download do arquivo
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `usuarios_${new Date().toISOString().split('T')[0]}.${formato}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      throw this.handleError(error, 'Erro ao exportar usuários');
    }
  }

  // ==========================================
  // UTILITÁRIOS
  // ==========================================

  /**
   * Validar CPF
   */
  validarCPF(cpf) {
    // Remove caracteres não numéricos
    cpf = cpf.replace(/\D/g, '');
    
    // Verifica se tem 11 dígitos
    if (cpf.length !== 11) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validação do primeiro dígito verificador
    let soma = 0;
    for (let i = 0; i < 9; i++) {
      soma += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let resto = 11 - (soma % 11);
    let dv1 = resto >= 10 ? 0 : resto;
    
    if (parseInt(cpf.charAt(9)) !== dv1) return false;
    
    // Validação do segundo dígito verificador
    soma = 0;
    for (let i = 0; i < 10; i++) {
      soma += parseInt(cpf.charAt(i)) * (11 - i);
    }
    resto = 11 - (soma % 11);
    let dv2 = resto >= 10 ? 0 : resto;
    
    return parseInt(cpf.charAt(10)) === dv2;
  }

  /**
   * Formatar CPF para exibição
   */
  formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  }

  /**
   * Validar email
   */
  validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  /**
   * Gerar senha aleatória
   */
  gerarSenhaAleatoria(tamanho = 8) {
    const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%';
    let senha = '';
    for (let i = 0; i < tamanho; i++) {
      senha += caracteres.charAt(Math.floor(Math.random() * caracteres.length));
    }
    return senha;
  }

  /**
   * Obter cor do avatar baseada no nome
   */
  obterCorAvatar(nome) {
    const cores = [
      '#429E17', '#2D6E0A', '#17a2b8', '#6f42c1', 
      '#e83e8c', '#fd7e14', '#20c997', '#6610f2'
    ];
    
    let hash = 0;
    for (let i = 0; i < nome.length; i++) {
      hash = nome.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    return cores[Math.abs(hash) % cores.length];
  }

  /**
   * Obter iniciais do nome para avatar
   */
  obterIniciais(nome) {
    return nome
      .split(' ')
      .map(palavra => palavra.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  // ==========================================
  // TRATAMENTO DE ERROS
  // ==========================================

  /**
   * Tratar erros da API
   */
  handleError(error, mensagemPadrao) {
    console.error('UsuarioService Error:', error);
    
    if (error.response) {
      // Erro da API
      const status = error.response.status;
      const data = error.response.data;
      
      switch (status) {
        case 400:
          return new Error(data.detail || 'Dados inválidos');
        case 401:
          return new Error('Não autorizado');
        case 403:
          return new Error('Sem permissão para esta ação');
        case 404:
          return new Error('Usuário não encontrado');
        case 409:
          return new Error('CPF ou email já cadastrado');
        case 422:
          // Erros de validação
          if (data.detail && Array.isArray(data.detail)) {
            const mensagens = data.detail.map(err => err.msg).join(', ');
            return new Error(`Erro de validação: ${mensagens}`);
          }
          return new Error(data.detail || 'Dados inválidos');
        case 500:
          return new Error('Erro interno do servidor');
        default:
          return new Error(data.detail || mensagemPadrao);
      }
    } else if (error.request) {
      // Erro de rede
      return new Error('Erro de conexão com o servidor');
    } else {
      // Erro interno
      return new Error(mensagemPadrao);
    }
  }
}

// Exportar instância única
const usuarioService = new UsuarioService();
export default usuarioService; 