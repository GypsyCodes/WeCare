import api from './api';

/**
 * Serviço para gerenciamento de escalas de enfermeiros
 * Integração com APIs reais do backend
 */
class EscalaService {
  
  // ==========================================
  // CRUD DE ESCALAS
  // ==========================================

  /**
   * Listar escalas com filtros e paginação
   */
  async listar(params = {}) {
    try {
      const response = await api.get('/escalas', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar escalas');
    }
  }

  /**
   * Buscar escala por ID
   */
  async buscarPorId(id) {
    try {
      const response = await api.get(`/escalas/${id}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar escala');
    }
  }

  /**
   * Criar nova escala
   */
  async criar(dadosEscala) {
    try {
      const response = await api.post('/escalas', dadosEscala);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao criar escala');
    }
  }

  /**
   * Atualizar escala existente
   */
  async atualizar(id, dadosEscala) {
    try {
      const response = await api.put(`/escalas/${id}`, dadosEscala);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao atualizar escala');
    }
  }

  /**
   * Excluir escala
   */
  async excluir(id) {
    try {
      await api.delete(`/escalas/${id}`);
      return { success: true };
    } catch (error) {
      throw this.handleError(error, 'Erro ao excluir escala');
    }
  }

  /**
   * Atribuir usuário a uma escala
   */
  async atribuirUsuario(atribuicaoData) {
    try {
      const response = await api.post(`/escalas/${atribuicaoData.escala_id}/atribuir-usuario`, {
        usuario_id: atribuicaoData.usuario_id,
        setor_id: atribuicaoData.setor_id
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao atribuir usuário à escala');
    }
  }

  /**
   * Obter usuários de uma escala
   */
  async getUsuariosEscala(escalaId) {
    try {
      const response = await api.get(`/escalas/${escalaId}/usuarios`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar usuários da escala');
    }
  }

  /**
   * Adicionar usuário à escala
   */
  async adicionarUsuario(escalaId, usuarioId, setorId) {
    try {
      const response = await api.post(`/escalas/${escalaId}/usuarios`, {
        usuario_id: usuarioId,
        setor_id: setorId
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao adicionar usuário à escala');
    }
  }

  /**
   * Remover usuário da escala
   */
  async removerUsuario(escalaId, usuarioId) {
    try {
      const response = await api.delete(`/escalas/${escalaId}/usuarios/${usuarioId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao remover usuário da escala');
    }
  }

  /**
   * Atualizar setor do usuário na escala
   */
  async atualizarSetorUsuario(escalaId, usuarioId, novoSetorId) {
    try {
      const response = await api.put(`/escalas/${escalaId}/usuarios/${usuarioId}`, {
        setor_id: novoSetorId
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao atualizar setor do usuário');
    }
  }

  /**
   * Método alias para deletar (compatibilidade)
   */
  async deletar(id) {
    return this.excluir(id);
  }

  /**
   * Enviar notificação WhatsApp para uma escala
   */
  async enviarNotificacao(escalaId) {
    try {
      const response = await api.post(`/escalas/${escalaId}/enviar-notificacao`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao enviar notificação WhatsApp');
    }
  }

  /**
   * Alterar status da escala
   */
  async alterarStatus(id, status) {
    try {
      const response = await api.put(`/escalas/${id}/status`, { status });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao alterar status da escala');
    }
  }

  // ==========================================
  // CONSULTAS ESPECÍFICAS PARA AGENDA
  // ==========================================

  /**
   * Buscar escalas por período (para agenda)
   */
  async buscarPorPeriodo(dataInicio, dataFim, estabelecimentoId = null) {
    try {
      const params = {
        data_inicio: dataInicio,
        data_fim: dataFim
      };
      
      if (estabelecimentoId) {
        params.estabelecimento_id = estabelecimentoId;
      }
      
      const response = await api.get('/escalas/periodo', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar escalas do período');
    }
  }

  /**
   * Buscar view de calendário
   */
  async buscarCalendario(dataInicio, dataFim, usuarioId = null) {
    try {
      const params = {
        start_date: dataInicio,
        end_date: dataFim
      };
      
      if (usuarioId) {
        params.usuario_id = usuarioId;
      }
      
      const response = await api.get('/escalas/calendar', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar calendário de escalas');
    }
  }

  /**
   * Buscar estatísticas das escalas
   */
  async buscarEstatisticas(dataInicio, dataFim, usuarioId = null) {
    try {
      const params = {
        start_date: dataInicio,
        end_date: dataFim
      };
      
      if (usuarioId) {
        params.usuario_id = usuarioId;
      }
      
      const response = await api.get('/escalas/stats/summary', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar estatísticas das escalas');
    }
  }

  /**
   * Buscar escalas do dia atual
   */
  async buscarEscalasHoje(estabelecimentoId = null) {
    const hoje = new Date().toISOString().split('T')[0];
    return this.buscarPorPeriodo(hoje, hoje, estabelecimentoId);
  }

  /**
   * Buscar escalas da semana atual
   */
  async buscarEscalasSemana(estabelecimentoId = null) {
    const hoje = new Date();
    const inicioDaSemana = new Date(hoje);
    inicioDaSemana.setDate(hoje.getDate() - hoje.getDay());
    
    const fimDaSemana = new Date(inicioDaSemana);
    fimDaSemana.setDate(inicioDaSemana.getDate() + 6);
    
    return this.buscarPorPeriodo(
      inicioDaSemana.toISOString().split('T')[0],
      fimDaSemana.toISOString().split('T')[0],
      estabelecimentoId
    );
  }

  /**
   * Buscar escalas por usuário
   */
  async buscarPorUsuario(usuarioId, params = {}) {
    try {
      const response = await api.get(`/escalas/usuario/${usuarioId}`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar escalas do usuário');
    }
  }

  /**
   * Buscar escalas por estabelecimento
   */
  async buscarPorEstabelecimento(estabelecimentoId, params = {}) {
    try {
      const response = await api.get(`/escalas/estabelecimento/${estabelecimentoId}`, { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar escalas do estabelecimento');
    }
  }

  // ==========================================
  // TRANSFERÊNCIAS DE PLANTÃO
  // ==========================================

  /**
   * Solicitar transferência de plantão
   */
  async solicitarTransferencia(escalaId, dadosTransferencia) {
    try {
      const response = await api.post(`/escalas/${escalaId}/transferir`, dadosTransferencia);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao solicitar transferência');
    }
  }

  /**
   * Listar transferências pendentes
   */
  async listarTransferenciasPendentes() {
    try {
      const response = await api.get('/transferencias?status=Pendente');
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar transferências pendentes');
    }
  }

  /**
   * Aprovar transferência
   */
  async aprovarTransferencia(transferenciaId, observacoes = '') {
    try {
      const response = await api.put(`/transferencias/${transferenciaId}/aprovar`, {
        observacoes
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao aprovar transferência');
    }
  }

  /**
   * Rejeitar transferência
   */
  async rejeitarTransferencia(transferenciaId, motivo) {
    try {
      const response = await api.put(`/transferencias/${transferenciaId}/rejeitar`, {
        motivo
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao rejeitar transferência');
    }
  }

  // ==========================================
  // RELATÓRIOS E ESTATÍSTICAS
  // ==========================================

  /**
   * Obter estatísticas das escalas
   */
  async obterEstatisticas(params = {}) {
    try {
      const response = await api.get('/escalas/stats', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Erro ao carregar estatísticas');
    }
  }

  /**
   * Exportar escalas
   */
  async exportar(formato = 'csv', filtros = {}) {
    try {
      const response = await api.get('/escalas/export', {
        params: { formato, ...filtros },
        responseType: 'blob'
      });
      
      // Criar download do arquivo
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `escalas_${new Date().toISOString().split('T')[0]}.${formato}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      throw this.handleError(error, 'Erro ao exportar escalas');
    }
  }

  // ==========================================
  // UTILITÁRIOS PARA FRONTEND
  // ==========================================

  /**
   * Processar escalas para exibição na agenda
   */
  processarEscalasParaAgenda(escalas) {
    return escalas.map(escala => ({
      ...escala,
      // Adicionar propriedades para renderização
      cor: this.obterCorPorStatus(escala.status),
      isMultiDias: escala.data_inicio !== escala.data_fim,
      isPlantao24h: escala.hora_inicio === escala.hora_fim,
      isNoturno: this.isPlantaoNoturno(escala.hora_inicio, escala.hora_fim),
      duracaoHoras: this.calcularDuracaoHoras(escala.hora_inicio, escala.hora_fim),
      // Formatação para compatibilidade com frontend
      socio: escala.usuarios_atribuidos && escala.usuarios_atribuidos.length > 0 ? escala.usuarios_atribuidos[0].usuario?.nome || 'N/A' : 'N/A',
      estabelecimento: escala.estabelecimento?.nome || 'N/A',
      horaInicio: escala.hora_inicio,
      horaFim: escala.hora_fim,
      dataInicio: escala.data_inicio,
      dataFim: escala.data_fim,
      estabelecimentoId: escala.estabelecimento_id,
      setor: escala.setor || 'Enfermagem' // Padrão para enfermeiros
    }));
  }

  /**
   * Obter cor baseada no status
   */
  obterCorPorStatus(status) {
    const cores = {
      'Confirmado': '#429E17',
      'Pendente': '#ffc107',
      'Ausente': '#dc3545'
    };
    return cores[status] || '#6c757d';
  }

  /**
   * Verificar se é plantão noturno
   */
  isPlantaoNoturno(horaInicio, horaFim) {
    const inicio = parseInt(horaInicio.split(':')[0]);
    const fim = parseInt(horaFim.split(':')[0]);
    
    // Plantão noturno: inicia após 18h ou termina antes das 8h
    return inicio >= 18 || fim <= 8 || fim < inicio;
  }

  /**
   * Calcular duração do plantão em horas
   */
  calcularDuracaoHoras(horaInicio, horaFim) {
    const [inicioH, inicioM] = horaInicio.split(':').map(Number);
    const [fimH, fimM] = horaFim.split(':').map(Number);
    
    let inicioMinutos = inicioH * 60 + inicioM;
    let fimMinutos = fimH * 60 + fimM;
    
    // Se fim < início, é overnight
    if (fimMinutos < inicioMinutos) {
      fimMinutos += 24 * 60; // Adicionar 24h
    }
    
    return Math.round((fimMinutos - inicioMinutos) / 60 * 10) / 10;
  }

  /**
   * Validar dados da escala
   */
  validarEscala(dados) {
    const erros = [];
    
    if (!dados.usuario_id) {
      erros.push('Enfermeiro é obrigatório');
    }
    
    if (!dados.estabelecimento_id) {
      erros.push('Estabelecimento é obrigatório');
    }
    
    if (!dados.data_inicio) {
      erros.push('Data de início é obrigatória');
    }
    
    if (!dados.data_fim) {
      erros.push('Data de fim é obrigatória');
    }
    
    if (!dados.hora_inicio) {
      erros.push('Hora de início é obrigatória');
    }
    
    if (!dados.hora_fim) {
      erros.push('Hora de fim é obrigatória');
    }
    
    // Validar datas
    if (dados.data_inicio && dados.data_fim) {
      const dataInicio = new Date(dados.data_inicio);
      const dataFim = new Date(dados.data_fim);
      
      if (dataFim < dataInicio) {
        erros.push('Data de fim não pode ser anterior à data de início');
      }
    }
    
    return erros;
  }

  /**
   * Formatar horário para exibição
   */
  formatarHorario(hora) {
    return hora.substring(0, 5); // HH:MM
  }

  /**
   * Formatar data para exibição
   */
  formatarData(data) {
    return new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');
  }

  /**
   * Obter tipos de plantão disponíveis para enfermeiros
   */
  obterTiposPlantao() {
    return [
      {
        value: 'diurno',
        label: 'Diurno (12h)',
        horaInicio: '07:00',
        horaFim: '19:00'
      },
      {
        value: 'noturno', 
        label: 'Noturno (12h)',
        horaInicio: '19:00',
        horaFim: '07:00'
      },
      {
        value: 'integral',
        label: 'Plantão 24h',
        horaInicio: '08:00',
        horaFim: '08:00'
      },
      {
        value: 'personalizado',
        label: 'Personalizado',
        horaInicio: '',
        horaFim: ''
      }
    ];
  }

  /**
   * Obter setores disponíveis (simplificado para enfermeiros)
   */
  obterSetores() {
    return [
      'Enfermagem Geral',
      'UTI',
      'Emergência', 
      'Pediatria'
    ];
  }

  // ==========================================
  // TRATAMENTO DE ERROS
  // ==========================================

  /**
   * Tratar erros da API
   */
  handleError(error, mensagemPadrao) {
    console.error('EscalaService Error:', error);
    
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
          return new Error('Escala não encontrada');
        case 409:
          return new Error('Conflito de horário ou recurso já existente');
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
const escalaService = new EscalaService();
export default escalaService; 