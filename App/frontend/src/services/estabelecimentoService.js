import api from './api';

/**
 * Serviço para gerenciar estabelecimentos
 */
class EstabelecimentoService {
  
  /**
   * Listar todos os estabelecimentos
   * @param {Object} params - Parâmetros de filtro
   * @param {number} params.page - Página atual
   * @param {number} params.size - Itens por página
   * @param {string} params.search - Termo de busca
   * @param {boolean} params.ativo - Filtrar apenas ativos
   * @returns {Promise<Object>} Lista paginada de estabelecimentos
   */
  async listar(params = {}) {
    try {
      const response = await api.get('/estabelecimentos', { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao listar estabelecimentos:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Buscar estabelecimento por ID
   * @param {number} id - ID do estabelecimento
   * @returns {Promise<Object>} Dados do estabelecimento
   */
  async buscarPorId(id) {
    try {
      const response = await api.get(`/estabelecimentos/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Criar novo estabelecimento
   * @param {Object} estabelecimentoData - Dados do estabelecimento
   * @param {string} estabelecimentoData.nome - Nome do estabelecimento
   * @param {string} estabelecimentoData.endereco - Endereço completo
   * @param {number} estabelecimentoData.latitude - Coordenada latitude
   * @param {number} estabelecimentoData.longitude - Coordenada longitude
   * @param {number} estabelecimentoData.raio_checkin - Raio de check-in em metros
   * @param {boolean} estabelecimentoData.ativo - Status ativo/inativo
   * @returns {Promise<Object>} Estabelecimento criado
   */
  async criar(estabelecimentoData) {
    try {
      // Validar dados obrigatórios
      this.validarDados(estabelecimentoData);
      
      const response = await api.post('/estabelecimentos', estabelecimentoData);
      return response.data;
    } catch (error) {
      console.error('Erro ao criar estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Atualizar estabelecimento existente
   * @param {number} id - ID do estabelecimento
   * @param {Object} estabelecimentoData - Dados para atualização
   * @returns {Promise<Object>} Estabelecimento atualizado
   */
  async atualizar(id, estabelecimentoData) {
    try {
      // Validar dados obrigatórios (exceto campos opcionais na atualização)
      this.validarDados(estabelecimentoData, false);
      
      const response = await api.put(`/estabelecimentos/${id}`, estabelecimentoData);
      return response.data;
    } catch (error) {
      console.error('Erro ao atualizar estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Desativar/ativar estabelecimento
   * @param {number} id - ID do estabelecimento
   * @param {boolean} ativo - Novo status
   * @returns {Promise<Object>} Estabelecimento atualizado
   */
  async alterarStatus(id, ativo) {
    try {
      const response = await api.put(`/estabelecimentos/${id}`, { ativo });
      return response.data;
    } catch (error) {
      console.error('Erro ao alterar status do estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Excluir estabelecimento (soft delete)
   * @param {number} id - ID do estabelecimento
   * @returns {Promise<Object>} Resposta da operação
   */
  async excluir(id) {
    try {
      const response = await api.delete(`/estabelecimentos/${id}`);
      return response.data;
    } catch (error) {
      console.error('Erro ao excluir estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Buscar escalas de um estabelecimento
   * @param {number} id - ID do estabelecimento
   * @param {Object} params - Parâmetros de filtro
   * @param {string} params.data_inicio - Data início (YYYY-MM-DD)
   * @param {string} params.data_fim - Data fim (YYYY-MM-DD)
   * @returns {Promise<Object>} Escalas do estabelecimento
   */
  async buscarEscalas(id, params = {}) {
    try {
      const response = await api.get(`/estabelecimentos/${id}/escalas`, { params });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar escalas do estabelecimento:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Validar se as coordenadas estão dentro de um raio
   * @param {number} lat1 - Latitude do ponto 1
   * @param {number} lon1 - Longitude do ponto 1  
   * @param {number} lat2 - Latitude do ponto 2
   * @param {number} lon2 - Longitude do ponto 2
   * @param {number} raio - Raio em metros
   * @returns {boolean} Se está dentro do raio
   */
  validarRaio(lat1, lon1, lat2, lon2, raio) {
    const R = 6371e3; // Raio da Terra em metros
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    const distancia = R * c; // em metros

    return distancia <= raio;
  }

  /**
   * Obter localização atual do usuário
   * @param {Object} options - Opções de geolocalização
   * @returns {Promise<Object>} Coordenadas {latitude, longitude}
   */
  obterLocalizacaoAtual(options = {}) {
    const defaultOptions = {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 60000,
      ...options
    };

    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalização não é suportada neste navegador'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          let message = 'Erro ao obter localização: ';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              message += 'Permissão negada pelo usuário';
              break;
            case error.POSITION_UNAVAILABLE:
              message += 'Localização indisponível';
              break;
            case error.TIMEOUT:
              message += 'Tempo esgotado';
              break;
            default:
              message += 'Erro desconhecido';
              break;
          }
          reject(new Error(message));
        },
        defaultOptions
      );
    });
  }

  /**
   * Validar dados do estabelecimento
   * @param {Object} data - Dados para validar
   * @param {boolean} isCreate - Se é operação de criação
   */
  validarDados(data, isCreate = true) {
    const errors = [];

    if (isCreate || data.nome !== undefined) {
      if (!data.nome || data.nome.trim().length < 2) {
        errors.push('Nome deve ter pelo menos 2 caracteres');
      }
    }

    if (isCreate || data.endereco !== undefined) {
      if (!data.endereco || data.endereco.trim().length < 10) {
        errors.push('Endereço deve ter pelo menos 10 caracteres');
      }
    }

    if (isCreate || data.latitude !== undefined) {
      if (typeof data.latitude !== 'number' || data.latitude < -90 || data.latitude > 90) {
        errors.push('Latitude deve ser um número entre -90 e 90');
      }
    }

    if (isCreate || data.longitude !== undefined) {
      if (typeof data.longitude !== 'number' || data.longitude < -180 || data.longitude > 180) {
        errors.push('Longitude deve ser um número entre -180 e 180');
      }
    }

    if (isCreate || data.raio_checkin !== undefined) {
      if (typeof data.raio_checkin !== 'number' || data.raio_checkin < 10 || data.raio_checkin > 1000) {
        errors.push('Raio de check-in deve ser entre 10 e 1000 metros');
      }
    }

    if (errors.length > 0) {
      throw new Error(errors.join('; '));
    }
  }

  /**
   * Tratar erros da API
   * @param {Error} error - Erro da requisição
   * @returns {Error} Erro tratado
   */
  handleError(error) {
    if (error.response) {
      // Erro de resposta da API
      const { status, data } = error.response;
      
      if (status === 400) {
        return new Error(data.detail || 'Dados inválidos');
      } else if (status === 401) {
        return new Error('Não autorizado');
      } else if (status === 403) {
        return new Error('Acesso negado');
      } else if (status === 404) {
        return new Error('Estabelecimento não encontrado');
      } else if (status === 422) {
        const errors = data.detail?.map(err => err.msg).join('; ') || 'Dados inválidos';
        return new Error(errors);
      } else if (status >= 500) {
        return new Error('Erro interno do servidor');
      }
      
      return new Error(data.detail || 'Erro na requisição');
    } else if (error.request) {
      // Erro de rede
      return new Error('Erro de conexão com o servidor');
    } else {
      // Erro local
      return error;
    }
  }
}

// Instância singleton do serviço
const estabelecimentoService = new EstabelecimentoService();
export default estabelecimentoService; 