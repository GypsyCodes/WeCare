import api from './api';

const setorService = {
    // Listar todos os setores
    listar: async (params = {}) => {
        try {
            const response = await api.get('/setores/', { params });
            return response.data;
        } catch (error) {
            console.error('Erro ao listar setores:', error);
            throw error;
        }
    },

    // Listar apenas setores ativos
    listarAtivos: async () => {
        try {
            const response = await api.get('/setores/?ativo=true');
            return response.data;
        } catch (error) {
            console.error('Erro ao listar setores ativos:', error);
            throw error;
        }
    },

    // Listar setores por estabelecimento
    listarPorEstabelecimento: async (estabelecimentoId) => {
        try {
            const response = await api.get(`/escalas/setores/disponiveis?estabelecimento_id=${estabelecimentoId}`);
            return response.data;
        } catch (error) {
            console.error('Erro ao listar setores por estabelecimento:', error);
            throw error;
        }
    },

    // Obter setor por ID
    obterPorId: async (id) => {
        try {
            const response = await api.get(`/setores/${id}`);
            return response.data;
        } catch (error) {
            console.error('Erro ao obter setor:', error);
            throw error;
        }
    },

    // Criar novo setor
    criar: async (setorData) => {
        try {
            const response = await api.post('/setores/', setorData);
            return response.data;
        } catch (error) {
            console.error('Erro ao criar setor:', error);
            throw error;
        }
    },

    // Atualizar setor
    atualizar: async (id, setorData) => {
        try {
            const response = await api.put(`/setores/${id}`, setorData);
            return response.data;
        } catch (error) {
            console.error('Erro ao atualizar setor:', error);
            throw error;
        }
    },

    // Deletar setor
    deletar: async (id) => {
        try {
            const response = await api.delete(`/setores/${id}`);
            return response.data;
        } catch (error) {
            console.error('Erro ao deletar setor:', error);
            throw error;
        }
    }
};

export default setorService; 