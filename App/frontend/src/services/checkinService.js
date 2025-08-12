import apiService from './api';

/**
 * Serviço para gerenciamento de check-ins
 * Integração com APIs reais do backend
 */
class CheckinService {
  
  // ==========================================
  // CRUD DE CHECK-INS
  // ==========================================

  /**
   * Listar check-ins com filtros e paginação
   */
  async listar(params = {}) {
    try {
      const response = await apiService.get('/checkins', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-ins');
    }
  }

  /**
   * Buscar check-in por ID
   */
  async buscarPorId(id) {
    try {
      const response = await apiService.get(`/checkins/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-in');
    }
  }

  /**
   * Realizar check-in
   */
  async realizarCheckin(dadosCheckin) {
    try {
      const response = await apiService.post('/checkins', dadosCheckin);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao realizar check-in');
    }
  }

  /**
   * Atualizar check-in
   */
  async atualizar(id, dadosCheckin) {
    try {
      const response = await apiService.put(`/checkins/${id}`, dadosCheckin);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao atualizar check-in');
    }
  }

  // ==========================================
  // CHECK-INS POR CONTEXTO
  // ==========================================

  /**
   * Buscar check-ins por usuário
   */
  async buscarPorUsuario(usuarioId, params = {}) {
    try {
      const response = await apiService.get(`/checkins/usuario/${usuarioId}`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-ins do usuário');
    }
  }

  /**
   * Buscar check-ins por escala
   */
  async buscarPorEscala(escalaId) {
    try {
      const response = await apiService.get(`/checkins/escala/${escalaId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-ins da escala');
    }
  }

  /**
   * Buscar check-ins por estabelecimento
   */
  async buscarPorEstabelecimento(estabelecimentoId, params = {}) {
    try {
      const response = await apiService.get(`/checkins/estabelecimento/${estabelecimentoId}`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-ins do estabelecimento');
    }
  }

  /**
   * Buscar check-ins do dia atual
   */
  async buscarCheckinsHoje(estabelecimentoId = null) {
    const hoje = new Date().toISOString().split('T')[0];
    const params = { data_inicio: hoje, data_fim: hoje };
    
    if (estabelecimentoId) {
      params.estabelecimento_id = estabelecimentoId;
    }
    
    return this.listar(params);
  }

  /**
   * Buscar check-ins pendentes (escalas sem check-in)
   */
  async buscarCheckinsPendentes(estabelecimentoId = null) {
    try {
      const params = estabelecimentoId ? { estabelecimento_id: estabelecimentoId } : {};
      const response = await apiService.get('/checkins/pendentes', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar check-ins pendentes');
    }
  }

  // ==========================================
  // FUNCIONALIDADES DE GEOLOCALIZAÇÃO
  // ==========================================

  /**
   * Obter localização atual do usuário
   */
  async obterLocalizacaoAtual() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocalização não suportada pelo navegador'));
        return;
      }

      const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000
      };

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
          });
        },
        (error) => {
          let mensagem = 'Erro ao obter localização';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              mensagem = 'Permissão de localização negada';
              break;
            case error.POSITION_UNAVAILABLE:
              mensagem = 'Localização indisponível';
              break;
            case error.TIMEOUT:
              mensagem = 'Tempo limite para obter localização excedido';
              break;
          }
          
          reject(new Error(mensagem));
        },
        options
      );
    });
  }

  /**
   * Validar se localização está dentro do raio permitido
   */
  validarRaio(lat1, lon1, lat2, lon2, raioPermitido) {
    const distancia = this.calcularDistancia(lat1, lon1, lat2, lon2);
    return {
      valido: distancia <= raioPermitido,
      distancia: Math.round(distancia),
      raioPermitido
    };
  }

  /**
   * Calcular distância entre duas coordenadas (Haversine)
   */
  calcularDistancia(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Raio da Terra em metros
    const dLat = this.toRadians(lat2 - lat1);
    const dLon = this.toRadians(lon2 - lon1);
    
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Converter graus para radianos
   */
  toRadians(degrees) {
    return degrees * (Math.PI / 180);
  }

  /**
   * Obter endereço através de geocodificação reversa
   */
  async obterEndereco(latitude, longitude) {
    try {
      // Usar serviço de geocodificação (Nominatim OpenStreetMap)
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'WeCareSistema/1.0'
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Erro na geocodificação');
      }
      
      const data = await response.json();
      return data.display_name || `${latitude}, ${longitude}`;
      
    } catch (error) {
      console.warn('Erro ao obter endereço:', error);
      return `${latitude}, ${longitude}`;
    }
  }

  // ==========================================
  // CHECK-IN AUTOMÁTICO/INTELIGENTE
  // ==========================================

  /**
   * Realizar check-in automático com validações
   */
  async checkinAutomatico(escalaId) {
    try {
      // 1. Obter localização atual
      const localizacao = await this.obterLocalizacaoAtual();
      
      // 2. Obter dados da escala
      const escala = await apiService.get(`/escalas/${escalaId}`);
      const estabelecimento = escala.data.estabelecimento;
      
      // 3. Validar raio
      const validacaoRaio = this.validarRaio(
        localizacao.latitude,
        localizacao.longitude,
        estabelecimento.latitude,
        estabelecimento.longitude,
        estabelecimento.raio_checkin
      );
      
      // 4. Obter endereço
      const endereco = await this.obterEndereco(
        localizacao.latitude,
        localizacao.longitude
      );
      
      // 5. Preparar dados do check-in
      const dadosCheckin = {
        escala_id: escalaId,
        gps_lat: localizacao.latitude,
        gps_long: localizacao.longitude,
        endereco: endereco,
        status: validacaoRaio.valido ? 'Realizado' : 'Fora de Local',
        observacoes: validacaoRaio.valido 
          ? `Check-in realizado automaticamente (${validacaoRaio.distancia}m do estabelecimento)`
          : `Check-in fora do raio permitido (${validacaoRaio.distancia}m de distância, máximo ${validacaoRaio.raioPermitido}m)`
      };
      
      // 6. Realizar check-in
      const resultado = await this.realizarCheckin(dadosCheckin);
      
      return {
        ...resultado,
        validacaoRaio,
        localizacao,
        endereco
      };
      
    } catch (error) {
      throw this.handleError(error, 'Erro no check-in automático');
    }
  }

  /**
   * Verificar se check-in é permitido (janela de tempo)
   */
  podeRealizarCheckin(escala) {
    const agora = new Date();
    const dataEscala = new Date(escala.data_inicio + 'T' + escala.hora_inicio);
    
    // Permitir check-in até 15 minutos antes do horário
    const janelaInicio = new Date(dataEscala.getTime() - 15 * 60 * 1000);
    
    // Permitir check-in até 30 minutos após o horário
    const janelaFim = new Date(dataEscala.getTime() + 30 * 60 * 1000);
    
    return {
      permitido: agora >= janelaInicio && agora <= janelaFim,
      janelaInicio,
      janelaFim,
      agora
    };
  }

  // ==========================================
  // RELATÓRIOS E ESTATÍSTICAS
  // ==========================================

  /**
   * Obter estatísticas de check-ins
   */
  async obterEstatisticas(params = {}) {
    try {
      const response = await apiService.get('/checkins/stats', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar estatísticas');
    }
  }

  /**
   * Exportar check-ins
   */
  async exportar(formato = 'csv', filtros = {}) {
    try {
      const response = await apiService.get('/checkins/export', {
        params: { formato, ...filtros },
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `checkins_${new Date().toISOString().split('T')[0]}.${formato}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      throw this.handleError(error, 'Erro ao exportar check-ins');
    }
  }

  // ==========================================
  // UTILITÁRIOS
  // ==========================================

  /**
   * Processar check-ins para exibição
   */
  processarCheckinsParaExibicao(checkins) {
    return checkins.map(checkin => ({
      ...checkin,
      // Formatação para compatibilidade
      socio: checkin.usuario?.nome || 'N/A',
      estabelecimento: checkin.escala?.estabelecimento?.nome || 'N/A',
      setor: checkin.escala?.setor || 'N/A',
      horaCheckin: this.formatarDataHora(checkin.data_hora),
      statusColor: this.obterCorPorStatus(checkin.status),
      distanciaFormatada: checkin.distancia ? `${checkin.distancia}m` : 'N/A'
    }));
  }

  /**
   * Obter cor baseada no status
   */
  obterCorPorStatus(status) {
    const cores = {
      'Realizado': '#429E17',
      'Ausente': '#dc3545',
      'Fora de Local': '#ffc107'
    };
    return cores[status] || '#6c757d';
  }

  /**
   * Formatar data e hora
   */
  formatarDataHora(dataHora) {
    return new Date(dataHora).toLocaleString('pt-BR');
  }

  /**
   * Formatar apenas hora
   */
  formatarHora(dataHora) {
    return new Date(dataHora).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // ==========================================
  // TRATAMENTO DE ERROS
  // ==========================================

  /**
   * Tratar erros da API
   */
  handleError(error, mensagemPadrao) {
    console.error('CheckinService Error:', error);
    
    if (error.response) {
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
          return new Error('Check-in ou escala não encontrado');
        case 409:
          return new Error('Check-in já realizado para esta escala');
        case 422:
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
      return new Error('Erro de conexão com o servidor');
    } else {
      return new Error(mensagemPadrao);
    }
  }
}

// Exportar instância única
const checkinService = new CheckinService();
export default checkinService; 