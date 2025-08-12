import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Calendar, Users, Plus, Copy, Clock, MapPin, X, Edit3, Trash2, Save, Filter, Menu, Eye, Settings, ChevronLeft, ChevronRight } from 'react-feather';
import { toast } from 'react-toastify';
import { useAuth } from '../../contexts/AuthContext';
import escalaService from '../../services/escalaService';
import usuarioService from '../../services/usuarioService';
import estabelecimentoService from '../../services/estabelecimentoService';
import setorService from '../../services/setorService';
import './Escalas.css';

const Escalas = () => {
    // Hook de autenticação
    const { user, hasPermission } = useAuth();
    
    // Estados principais
    const [currentDate, setCurrentDate] = useState(new Date());
    const [selectedUser, setSelectedUser] = useState(null);
    const [expandedWeek, setExpandedWeek] = useState(null);
    const [showEscalaModal, setShowEscalaModal] = useState(false);
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [editMode, setEditMode] = useState(false);

    const [selectedEscala, setSelectedEscala] = useState(null);
    
    // Estados de filtros
    const [filtroEstabelecimento, setFiltroEstabelecimento] = useState('');
    
    // Estados do formulário
    const [escalaForm, setEscalaForm] = useState({
        tipo: 'regular',
        data: '',
        horaInicio: '07:00',
        horaFim: '19:00',
        estabelecimentoId: '',
        diasSemana: [],
        escalasIrregulares: []
    });

    // Estados dos dados
    const [usuarios, setUsuarios] = useState([]);
    const [estabelecimentos, setEstabelecimentos] = useState([]);
    const [escalas, setEscalas] = useState([]);
    const [setores, setSetores] = useState([]);
    const [filtroSetor, setFiltroSetor] = useState('');
    
    // Estados para o novo sistema de setores e profissionais
    const [showSetorManager, setShowSetorManager] = useState(false);
    const [showProfessionalSelector, setShowProfessionalSelector] = useState(false);
    const [selectedSetor, setSelectedSetor] = useState(null);
    const [setorProfissionais, setSetorProfissionais] = useState({}); // {setorId: [profissionais]}
    const [setorForm, setSetorForm] = useState({
        nome: '',
        descricao: ''
    });
    
    // Estados da sidebar retrátil
    const [sidebarVisible, setSidebarVisible] = useState(false);
    const [sidebarMode, setSidebarMode] = useState('usuarios'); // 'usuarios' | 'setores'
    
    // Estados para drag & drop
    const [draggedUser, setDraggedUser] = useState(null);
    const [draggedOver, setDraggedOver] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    
    // Estados para copiar/colar
    const [copiedEscala, setCopiedEscala] = useState(null);
    
    // Estados para painel de edição central
    const [showEditPanel, setShowEditPanel] = useState(false);
    const [editingEscala, setEditingEscala] = useState(null);
    
    // Estados para widget flutuante de usuários
    const [showUserSelector, setShowUserSelector] = useState(false);
    const [userSearchTerm, setUserSearchTerm] = useState('');
    const [filteredUsers, setFilteredUsers] = useState([]);
    
    // Estados para plantões atípicos
    const [showAtypicalModal, setShowAtypicalModal] = useState(false);
    const [atypicalShifts, setAtypicalShifts] = useState([]);
    
    // Estados para múltiplos usuários por escala (agora integrado nas escalas)
    
    // Estados de estatísticas
    const [checkinStats, setCheckinStats] = useState({
        realizados: 0,
        pendentes: 0,
        total: 0,
        percentualRealizados: 0
    });
    
    const [notificacoes, setNotificacoes] = useState([
        { id: 1, tipo: 'checkin', mensagem: 'Check-in pendente para João Silva', urgente: false },
        { id: 2, tipo: 'escala', mensagem: 'Nova escala atribuída', urgente: true }
    ]);

    // Refs para intervalos
    const notificationIntervalRef = useRef();
    const statsIntervalRef = useRef();

    // Cores para usuários
    const userColors = [
        '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336',
        '#00BCD4', '#795548', '#607D8B', '#E91E63', '#3F51B5'
    ];

    // Carregar dados iniciais
    useEffect(() => {
        loadInitialData();
        setupIntervals();
        
        return () => {
            clearInterval(notificationIntervalRef.current);
            clearInterval(statsIntervalRef.current);
        };
    }, []);

    const loadSetoresPorEstabelecimento = async (estabelecimentoId) => {
        try {
            if (estabelecimentoId) {
                const setoresData = await setorService.listarPorEstabelecimento(estabelecimentoId);
                setSetores(setoresData || []);
            } else {
                setSetores([]);
            }
        } catch (error) {
            console.error('Erro ao carregar setores por estabelecimento:', error);
            setSetores([]);
        }
    };

    const loadInitialData = async () => {
        try {
            // Carregar usuários
            const usuariosResponse = await usuarioService.listar({ 
                page: 1, 
                per_page: 50, 
                perfil: 'Socio' 
            });
            const usuarios = usuariosResponse.users || usuariosResponse.usuarios || [];
            console.log('Usuários carregados:', usuarios);

            // Carregar estabelecimentos
            const estabelecimentosResponse = await estabelecimentoService.listar({
                page: 1,
                per_page: 50
            });
            const estabelecimentos = estabelecimentosResponse.estabelecimentos || [];

            // Calcular intervalo de datas para o mês atual
            const hoje = new Date();
            const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
            const fimMes = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0);
            
            const dataInicio = inicioMes.toISOString().split('T')[0];
            const dataFim = fimMes.toISOString().split('T')[0];

            // Carregar escalas do mês atual
            const calendarioEscalas = await escalaService.buscarCalendario(dataInicio, dataFim);
            
            // Processar escalas para formato do frontend
            const escalasFormatadas = [];
            if (calendarioEscalas && Array.isArray(calendarioEscalas)) {
                console.log('Calendário escalas recebido:', calendarioEscalas);
            calendarioEscalas.forEach(dia => {
                    console.log('Processando dia:', dia);
                    if (dia.escalas && Array.isArray(dia.escalas)) {
                dia.escalas.forEach(escala => {
                            console.log('Processando escala:', escala);
                    escalasFormatadas.push({
                        id: escala.id,
                                data: escala.data_inicio, // Usar data_inicio da escala
                        horaInicio: escala.hora_inicio,
                        horaFim: escala.hora_fim,
                        estabelecimento: escala.estabelecimento,
                                status: escala.status,
                                usuarios_atribuidos: escala.usuarios_atribuidos || []
                    });
                });
                    }
            });
            }
            
            console.log('Escalas formatadas:', escalasFormatadas);

            setUsuarios(usuarios);
            setEstabelecimentos(estabelecimentos);
            setEscalas(escalasFormatadas);
            
            if (estabelecimentos.length > 0) {
                setFiltroEstabelecimento(estabelecimentos[0].id);
                // Carregar setores do primeiro estabelecimento
                await loadSetoresPorEstabelecimento(estabelecimentos[0].id);
            }
            
            // Carregar setores (serão carregados por estabelecimento quando necessário)
            setSetores([]);
            
            // Carregar estatísticas reais
            try {
                const stats = await escalaService.buscarEstatisticas(dataInicio, dataFim);
                const totalEscalas = stats.total_escalas || 0;
                const realizadas = stats.confirmadas || 0;
                const pendentes = stats.pendentes || 0;
                const percentual = totalEscalas > 0 ? Math.round((realizadas / totalEscalas) * 100) : 0;
                
                setCheckinStats({
                    realizados: realizadas,
                    pendentes: pendentes,
                    total: totalEscalas,
                    percentualRealizados: percentual
                });
            } catch (statsError) {
                console.warn('Erro ao carregar estatísticas, usando fallback:', statsError);
                // Fallback para dados locais
                const totalEscalas = escalasFormatadas.length;
                const escalasRealizadas = escalasFormatadas.filter(e => e.status === 'CONFIRMADO').length;
                const escalasPendentes = escalasFormatadas.filter(e => e.status === 'PENDENTE').length;
                const percentual = totalEscalas > 0 ? Math.round((escalasRealizadas / totalEscalas) * 100) : 0;
                
                setCheckinStats({
                    realizados: escalasRealizadas,
                    pendentes: escalasPendentes,
                    total: totalEscalas,
                    percentualRealizados: percentual
                });
            }
            
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            toast.error('Erro ao carregar dados');
            
            // Fallback para dados mock em caso de erro
            const mockUsuarios = [
                { id: 1, nome: 'João Doutor', perfil: 'SOCIO', setor: 'UTI' },
                { id: 2, nome: 'Maria Silva', perfil: 'SOCIO', setor: 'Emergência' }
            ];
            const mockEstabelecimentos = [
                { id: 1, nome: 'Hospital São Lucas' }
            ];
            
            setUsuarios(mockUsuarios);
            setEstabelecimentos(mockEstabelecimentos);
            setEscalas([]);
            if (mockEstabelecimentos.length > 0) {
                setFiltroEstabelecimento(mockEstabelecimentos[0].id);
            }
        }
    };

    const setupIntervals = () => {
        // Atualizar estatísticas a cada 30 segundos
        statsIntervalRef.current = setInterval(() => {
            setCheckinStats(prev => {
                // Simular pequenas variações nas estatísticas
                const novoPercentual = Math.max(80, Math.min(95, prev.percentualRealizados + (Math.random() * 4 - 2)));
                const novosRealizados = Math.floor((prev.total * novoPercentual) / 100);
                const novosPendentes = prev.total - novosRealizados;
                
                return {
                    ...prev,
                    realizados: novosRealizados,
                    pendentes: novosPendentes,
                    percentualRealizados: Math.round(novoPercentual)
                };
            });
        }, 30000);

        // Atualizar notificações a cada 60 segundos
        notificationIntervalRef.current = setInterval(() => {
            // Simular novas notificações ocasionalmente
            if (Math.random() < 0.3) {
                setNotificacoes(prev => [
                    ...prev.slice(-4), // Manter apenas as últimas 4
                    {
                        id: Date.now(),
                        tipo: Math.random() > 0.5 ? 'checkin' : 'escala',
                        mensagem: Math.random() > 0.5 ? 'Check-in realizado com sucesso' : 'Nova escala disponível',
                        urgente: Math.random() < 0.2
                    }
                ]);
            }
        }, 60000);
    };

    // Funções de navegação do calendário
    const changeMonth = (direction) => {
        setCurrentDate(prev => {
            const newDate = new Date(prev);
            newDate.setMonth(prev.getMonth() + direction);
            
            // Recarregar dados do novo mês
            loadMonthData(newDate);
            
            return newDate;
        });
    };

    // Carregar dados de um mês específico
    const loadMonthData = async (date) => {
        try {
            const inicioMes = new Date(date.getFullYear(), date.getMonth(), 1);
            const fimMes = new Date(date.getFullYear(), date.getMonth() + 1, 0);
            
            const dataInicio = inicioMes.toISOString().split('T')[0];
            const dataFim = fimMes.toISOString().split('T')[0];

            // Carregar escalas do mês
            const calendarioEscalas = await escalaService.buscarCalendario(dataInicio, dataFim);
            
            // Processar escalas
            const escalasFormatadas = [];
            if (calendarioEscalas && Array.isArray(calendarioEscalas)) {
            calendarioEscalas.forEach(dia => {
                    if (dia.escalas && Array.isArray(dia.escalas)) {
                dia.escalas.forEach(escala => {
                    escalasFormatadas.push({
                        id: escala.id,
                        data: escala.data_inicio,
                        horaInicio: escala.hora_inicio,
                        horaFim: escala.hora_fim,
                        estabelecimento: escala.estabelecimento,
                                status: escala.status,
                                usuarios_atribuidos: escala.usuarios_atribuidos || []
                    });
                });
                    }
            });
            }

            setEscalas(escalasFormatadas);
            
            // Atualizar estatísticas
            try {
                const stats = await escalaService.buscarEstatisticas(dataInicio, dataFim);
                const totalEscalas = stats.total_escalas || 0;
                const realizadas = stats.confirmadas || 0;
                const pendentes = stats.pendentes || 0;
                const percentual = totalEscalas > 0 ? Math.round((realizadas / totalEscalas) * 100) : 0;
                
                setCheckinStats({
                    realizados: realizadas,
                    pendentes: pendentes,
                    total: totalEscalas,
                    percentualRealizados: percentual
                });
            } catch (statsError) {
                // Fallback para estatísticas locais
                const totalEscalas = escalasFormatadas.length;
                const escalasRealizadas = escalasFormatadas.filter(e => e.status === 'CONFIRMADO').length;
                const escalasPendentes = escalasFormatadas.filter(e => e.status === 'PENDENTE').length;
                const percentual = totalEscalas > 0 ? Math.round((escalasRealizadas / totalEscalas) * 100) : 0;
                
                setCheckinStats({
                    realizados: escalasRealizadas,
                    pendentes: escalasPendentes,
                    total: totalEscalas,
                    percentualRealizados: percentual
                });
            }
            
        } catch (error) {
            console.error('Erro ao carregar dados do mês:', error);
            toast.error('Erro ao carregar dados do mês');
        }
    };

    const getCalendarWeeks = () => {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        
        const firstDay = new Date(year, month, 1);
        
        // Encontrar o domingo da semana que contém o primeiro dia do mês
        const startDate = new Date(firstDay);
        const dayOfWeek = firstDay.getDay(); // 0 = domingo, 1 = segunda, etc.
        startDate.setDate(startDate.getDate() - dayOfWeek);
        
        console.log(`Gerando calendário para ${year}-${month + 1}`);
        console.log(`Primeiro dia do mês: ${firstDay.toDateString()}`);
        console.log(`Dia da semana: ${dayOfWeek} (0=domingo, 1=segunda, etc.)`);
        console.log(`Data de início: ${startDate.toDateString()}`);
        
        const weeks = [];
        
        // Gerar 5 semanas (35 dias)
        for (let weekIndex = 0; weekIndex < 5; weekIndex++) {
            const week = [];
            for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
                const dayOffset = (weekIndex * 7) + dayIndex;
                const currentDate = new Date(startDate.getTime() + (dayOffset * 24 * 60 * 60 * 1000));
                week.push(currentDate);
            }
            
            // Debug da semana
            console.log(`Semana ${weekIndex}:`, week.map(day => `${day.getDate()}/${day.getMonth() + 1} (${day.toLocaleDateString('pt-BR', { weekday: 'short' })})`));
            weeks.push(week);
        }
        
        return weeks;
    };

    // Funções de interação
    const selectUser = (user) => {
        setSelectedUser(user);
    };

    const toggleWeek = (weekIndex) => {
        setExpandedWeek(expandedWeek === weekIndex ? null : weekIndex);
    };

    const openCreateEscala = (day) => {
        // Formatar data de forma local para evitar problemas de fuso horário
        const year = day.getFullYear();
        const month = String(day.getMonth() + 1).padStart(2, '0');
        const date = String(day.getDate()).padStart(2, '0');
        const formattedDate = `${year}-${month}-${date}`;
        
        console.log(`Criando escala para: ${day.toDateString()} -> ${formattedDate}`);
        
        setEscalaForm(prev => ({
            ...prev,
            data: formattedDate,
            estabelecimentoId: filtroEstabelecimento || ''
        }));
        setShowEscalaModal(true);
    };

    const showEscalaDetails = (escala) => {
        if (!escala) return;
        
        setSelectedEscala(escala);
        
        // Se é admin, abrir painel de edição, se não, apenas visualização
        if (hasPermission('Administrador') || hasPermission('Supervisor')) {
            // Carregar profissionais dos setores para a escala
            const profissionaisPorSetor = {};
            if (escala.usuarios_atribuidos && Array.isArray(escala.usuarios_atribuidos)) {
                escala.usuarios_atribuidos.forEach(usuarioEscala => {
                    if (usuarioEscala.setor_id) {
                        if (!profissionaisPorSetor[usuarioEscala.setor_id]) {
                            profissionaisPorSetor[usuarioEscala.setor_id] = [];
                        }
                        const usuario = usuarios.find(u => u.id === usuarioEscala.usuario_id);
                        if (usuario) {
                            profissionaisPorSetor[usuarioEscala.setor_id].push(usuario);
                        }
                    }
                });
            }
            setSetorProfissionais(profissionaisPorSetor);
            
            setEditingEscala(escala);
            setShowEditPanel(true);
        } else {
            setShowDetailsModal(true);
        }
    };

    // Função para múltiplos usuários por escala
    const getEscalaUsuarios = (escalaId) => {
        const escala = escalas.find(e => e.id === escalaId);
        return escala ? escala.usuarios_atribuidos || [] : [];
    };

    // Função para drag & drop
    const handleDragStart = (user) => {
        setDraggedUser(user);
        setIsDragging(true);
    };

    const handleDragEnd = () => {
        setDraggedUser(null);
        setIsDragging(false);
        setDraggedOver(null);
    };

    const handleDragOver = (e, escalaId) => {
        e.preventDefault();
        setDraggedOver(escalaId);
    };

    const handleDrop = async (e, escala) => {
        e.preventDefault();
        
        if (!draggedUser || !escala) return;
        
        try {
            // Se não há setores disponíveis, mostrar erro
            if (setores.length === 0) {
                toast.error('Nenhum setor disponível. Crie um setor primeiro.');
                return;
            }
            
            // Usar o primeiro setor disponível (ou implementar seleção)
            const setorId = setores[0].id;
            
            // Adicionar usuário à escala
            await adicionarUsuarioAEscala(escala.id, draggedUser.id, setorId);
            
            toast.success(`${draggedUser.nome} adicionado à escala`);
            loadInitialData(); // Recarregar dados
        } catch (error) {
            toast.error('Erro ao adicionar usuário à escala');
        }
        
        handleDragEnd();
    };

    // Funções para gerenciar setores
    const openSetorManager = () => {
        setShowSetorManager(true);
    };

    const closeSetorManager = () => {
        setShowSetorManager(false);
        setSetorForm({ nome: '', descricao: '' });
    };

    const handleSetorFormChange = (field, value) => {
        setSetorForm(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const criarSetor = async () => {
        try {
            if (!setorForm.nome.trim()) {
                toast.error('Nome do setor é obrigatório');
                return;
            }

            await setorService.criar({
                nome: setorForm.nome.toUpperCase(),
                descricao: setorForm.descricao,
                estabelecimento_id: parseInt(filtroEstabelecimento)
            });

            toast.success('Setor criado com sucesso!');
            closeSetorManager();
            
            // Recarregar setores do estabelecimento atual
            await loadSetoresPorEstabelecimento(filtroEstabelecimento);
        } catch (error) {
            console.error('Erro ao criar setor:', error);
            toast.error('Erro ao criar setor');
        }
    };

    // Funções para seleção de profissionais por setor
    const openProfessionalSelector = (setor) => {
        setSelectedSetor(setor);
        setShowProfessionalSelector(true);
    };

    const closeProfessionalSelector = () => {
        setShowProfessionalSelector(false);
        setSelectedSetor(null);
        
        // Atualizar a escala em edição com os setores e profissionais
        if (editingEscala) {
            const setoresComProfissionais = setores.filter(setor => 
                setorProfissionais[setor.id] && setorProfissionais[setor.id].length > 0
            );
            
            setEditingEscala(prev => ({
                ...prev,
                setores: setoresComProfissionais
            }));
        }
    };

    const adicionarProfissionalAoSetor = (setorId, profissional) => {
        setSetorProfissionais(prev => ({
            ...prev,
            [setorId]: [...(prev[setorId] || []), profissional]
        }));
    };

    const removerProfissionalDoSetor = (setorId, profissionalId) => {
        setSetorProfissionais(prev => ({
            ...prev,
            [setorId]: (prev[setorId] || []).filter(p => p.id !== profissionalId)
        }));
    };

    // Função para solicitar setor (mantida para compatibilidade)
    const solicitarSetor = () => {
        return new Promise((resolve) => {
            if (setores.length === 0) {
                resolve(null);
                return;
            }
            const setorId = setores[0]?.id;
            resolve(setorId);
        });
    };

    // Função para adicionar usuário à escala
    const adicionarUsuarioAEscala = async (escalaId, usuarioId, setorId) => {
        try {
            await escalaService.adicionarUsuario(escalaId, usuarioId, setorId);
            
            // Encontrar o setor pelo ID
            const setor = setores.find(s => s.id === setorId);
            
            // Atualizar estado local das escalas
            setEscalas(prev => prev.map(escala => {
                if (escala.id === escalaId) {
                    return {
                        ...escala,
                        usuarios_atribuidos: [...(escala.usuarios_atribuidos || []), { 
                            usuario_id: usuarioId, 
                            setor_id: setorId,
                            setor: setor,
                            usuario: usuarios.find(u => u.id === usuarioId)
                        }]
                    };
                }
                return escala;
            }));
        } catch (error) {
            throw error;
        }
    };

    // Função para remover usuário da escala
    const removerUsuarioDaEscala = async (escalaId, usuarioId) => {
        try {
            await escalaService.removerUsuario(escalaId, usuarioId);
            
            // Atualizar estado local das escalas
            setEscalas(prev => prev.map(escala => {
                if (escala.id === escalaId) {
                    return {
                        ...escala,
                        usuarios_atribuidos: (escala.usuarios_atribuidos || []).filter(u => u.usuario_id !== usuarioId)
                    };
                }
                return escala;
            }));
            
            toast.success('Usuário removido da escala');
        } catch (error) {
            toast.error('Erro ao remover usuário da escala');
        }
    };

    // Função copiar escala
    const copiarEscala = (escala) => {
        setCopiedEscala({
            ...escala,
            usuarios_atribuidos: escala.usuarios_atribuidos || []
        });
        toast.info('Escala copiada');
    };

    // Função colar escala
    const colarEscala = async (data) => {
        if (!copiedEscala) {
            toast.warning('Nenhuma escala copiada');
            return;
        }
        
        try {
            const novaEscala = {
                ...copiedEscala,
                data: data.toISOString().split('T')[0],
                id: undefined // Para criar nova
            };
            
            const escalaCreated = await escalaService.criar(novaEscala);
            
            // Adicionar usuários copiados
            for (const usuario of copiedEscala.usuarios_atribuidos || []) {
                await adicionarUsuarioAEscala(escalaCreated.id, usuario.usuario_id, usuario.setor_id || usuario.setor);
            }
            
            toast.success('Escala colada com sucesso');
            loadInitialData();
        } catch (error) {
            toast.error('Erro ao colar escala');
        }
    };

    // Função para toggle da sidebar
    const toggleSidebar = () => {
        setSidebarVisible(!sidebarVisible);
    };

    // Função para validar conflitos
    const validarConflitos = (usuarioId, data, horaInicio, horaFim) => {
        const conflitos = escalas.filter(escala => {
            if (escala.data !== data) return false;
            
            const usuarios = escala.usuarios_atribuidos || [];
            if (!usuarios.some(u => u.usuario_id === usuarioId)) return false;
            
            // Verificar sobreposição de horários
            return !(horaFim <= escala.horaInicio || horaInicio >= escala.horaFim);
        });
        
        return conflitos;
    };

    // Funções do widget de seleção de usuários
    const openUserSelector = () => {
        setUserSearchTerm('');
        setFilteredUsers(usuarios);
        setShowUserSelector(true);
    };

    const closeUserSelector = () => {
        setShowUserSelector(false);
        setUserSearchTerm('');
        setFilteredUsers([]);
    };

    const handleUserSearch = (searchTerm) => {
        setUserSearchTerm(searchTerm);
        
        if (!searchTerm.trim()) {
            setFilteredUsers(usuarios);
            return;
        }
        
        const filtered = usuarios.filter(usuario =>
            usuario.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
            usuario.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            usuario.perfil.toLowerCase().includes(searchTerm.toLowerCase())
        );
        
        setFilteredUsers(filtered);
    };

    const selectUserFromWidget = async (usuario) => {
        if (!editingEscala) return;
        
        const setor = await solicitarSetor();
        if (setor) {
            await adicionarUsuarioAEscala(editingEscala.id, usuario.id, setor);
            closeUserSelector();
        }
    };

    // Funções do formulário
    const handleFormChange = (field, value) => {
        setEscalaForm(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleDiaSemanaToggle = (dia) => {
        setEscalaForm(prev => ({
            ...prev,
            diasSemana: prev.diasSemana.includes(dia)
                ? prev.diasSemana.filter(d => d !== dia)
                : [...prev.diasSemana, dia]
        }));
    };

    const addEscalaIrregular = () => {
        const novaEscala = {
            id: Date.now(),
            data: '',
            horaInicio: '07:00',
            horaFim: '19:00',
            setor: ''
        };
        
        setEscalaForm(prev => ({
            ...prev,
            escalasIrregulares: [...prev.escalasIrregulares, novaEscala]
        }));
    };

    const removeEscalaIrregular = (id) => {
        setEscalaForm(prev => ({
            ...prev,
            escalasIrregulares: prev.escalasIrregulares.filter(e => e.id !== id)
        }));
    };

    const handleSubmitEscala = async () => {
        try {
            // Preparar dados para API
            const dadosEscala = {
                data_inicio: escalaForm.data,
                data_fim: escalaForm.data, // Para escalas simples, data_fim = data_inicio
                hora_inicio: escalaForm.horaInicio,
                hora_fim: escalaForm.horaFim,
                estabelecimento_id: parseInt(escalaForm.estabelecimentoId),
                observacoes: ''
            };

            // Criar escala via API
            const escalaResponse = await escalaService.criar(dadosEscala);
            
            // Converter para formato do frontend
            const novaEscala = {
                id: escalaResponse.id,
                data: escalaResponse.data_inicio, // Usar data_inicio do backend
                horaInicio: escalaResponse.hora_inicio,
                horaFim: escalaResponse.hora_fim,
                estabelecimento: escalaResponse.estabelecimento,
                status: escalaResponse.status,
                usuarios_atribuidos: []
            };
            
            console.log('Escala criada:', novaEscala);
            console.log('Data da escala:', novaEscala.data);

            setEscalas(prev => {
                const novasEscalas = [...prev, novaEscala];
                
                // Atualizar estatísticas
                const totalEscalas = novasEscalas.length;
                const escalasRealizadas = novasEscalas.filter(e => e.status === 'CONFIRMADO').length;
                const escalasPendentes = novasEscalas.filter(e => e.status === 'PENDENTE').length;
                const percentual = totalEscalas > 0 ? Math.round((escalasRealizadas / totalEscalas) * 100) : 0;
                
                setCheckinStats({
                    realizados: escalasRealizadas,
                    pendentes: escalasPendentes,
                    total: totalEscalas,
                    percentualRealizados: percentual
                });
                
                return novasEscalas;
            });
            
            // Limpar formulário
            setEscalaForm({
                tipo: 'regular',
                data: '',
                horaInicio: '07:00',
                horaFim: '19:00',
                estabelecimentoId: filtroEstabelecimento || '',
                diasSemana: [],
                escalasIrregulares: []
            });
            
            setShowEscalaModal(false);
            toast.success('Escala criada com sucesso!');
            
        } catch (error) {
            console.error('Erro ao criar escala:', error);
            const errorMessage = error.message || 'Erro ao criar escala';
            toast.error(errorMessage);
        }
    };

    // Funções auxiliares
    const getDayEscalas = (date) => {
        // Formatar data de referência de forma local
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const referenceDate = `${year}-${month}-${day}`;
        
        console.log(`Procurando escalas para: ${date.toDateString()} (${referenceDate})`);
        console.log('Todas as escalas disponíveis:', escalas.map(e => ({ id: e.id, data: e.data, horaInicio: e.horaInicio, horaFim: e.horaFim })));
        
        let filteredEscalas = escalas.filter(escala => {
            // Comparar datas usando formato YYYY-MM-DD
            const match = escala.data === referenceDate;
            if (match) {
                console.log(`Match encontrado: escala ${escala.id} com data ${escala.data} para dia ${referenceDate}`);
            }
            return match;
        });
        
        // Aplicar filtro de setor se selecionado
        if (filtroSetor) {
            filteredEscalas = filteredEscalas.filter(escala => {
                const usuarios = escala.usuarios_atribuidos || [];
                return usuarios.some(usuario => {
                    if (usuario.setor_id) {
                        return usuario.setor_id.toString() === filtroSetor.toString();
                    }
                    // Fallback para dados antigos
                    if (usuario.setor && typeof usuario.setor === 'object') {
                        return usuario.setor.id.toString() === filtroSetor.toString();
                    }
                    return false;
                });
            });
        }
        
        // Debug temporário
        if (filteredEscalas.length > 0) {
            console.log(`Escalas encontradas para ${date.toDateString()} (${referenceDate}):`, filteredEscalas);
        }
        
        return filteredEscalas;
    };

    const hasEscalas = (date) => {
        return getDayEscalas(date).length > 0;
    };

    const isToday = (date) => {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    };

    const isOtherMonth = (date) => {
        return date.getMonth() !== currentDate.getMonth();
    };

    const getUserColor = (userId) => {
        return userColors[userId % userColors.length];
    };

    const getInitials = (name) => {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    };

    const formatTime = (time) => {
        return time.substring(0, 5);
    };



    const isOvernight = (startTime, endTime) => {
        const [startHours] = startTime.split(':').map(Number);
        const [endHours] = endTime.split(':').map(Number);
        return endHours < startHours;
    };

    // Renderização dos componentes
    const renderUserAvatar = (user) => {
        const color = getUserColor(user.id);
        const isSelected = selectedUser?.id === user.id;
        
        return (
            <div
                key={user.id}
                className={`user-avatar ${isSelected ? 'selected' : ''}`}
                style={{ backgroundColor: color }}
                onClick={() => selectUser(user)}
                title={user.nome}
            >
                {getInitials(user.nome)}
            </div>
        );
    };

    const renderCalendarDay = (date, weekIndex, dayIndex) => {
        const dayEscalas = getDayEscalas(date);
        const hasSchedule = hasEscalas(date);
        const today = isToday(date);
        const otherMonth = isOtherMonth(date);
        
        return (
            <div
                key={dayIndex}
                className={`calendar-day ${otherMonth ? 'other-month' : ''} ${today ? 'today' : ''} ${hasSchedule ? 'has-schedule' : ''} ${selectedUser && dayEscalas.some(e => e.usuarios_atribuidos && e.usuarios_atribuidos.some(u => u.usuario_id === selectedUser.id)) ? 'highlighted' : ''}`}
            >
                <span className="day-number">{date.getDate()}</span>
                
                {!otherMonth && editMode && hasPermission('Supervisor') && (
                    <>
                        <button
                            className="create-escala-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                openCreateEscala(date);
                            }}
                            title="Criar nova escala"
                        >
                            <Plus size={12} />
                        </button>
                        
                        {hasSchedule && (
                            <button
                                className="copy-escala-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    const escalasDoDia = getDayEscalas(date);
                                    if (escalasDoDia.length > 0) {
                                        copiarEscala(escalasDoDia[0]);
                                    }
                                }}
                                title="Copiar escala"
                            >
                                <Copy size={10} />
                            </button>
                        )}
                        
                        {copiedEscala && !hasSchedule && (
                            <button
                                className="paste-escala-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    colarEscala(date);
                                }}
                                title="Colar escala"
                            >
                                📋
                            </button>
                        )}
                    </>
                )}
            </div>
        );
    };

    const renderWeekTimeline = (week, weekIndex) => {
        const weekEscalas = week.flatMap(day => getDayEscalas(day));
        
        return (
            <div className="week-timeline-dashboard">
                {/* Header dos dias */}
                <div className="timeline-header">
                    {week.map((day, dayIndex) => {
                        const today = isToday(day);
                        const otherMonth = isOtherMonth(day);
                        const hasSchedule = hasEscalas(day);
                        
                        return (
                            <div 
                                key={`${day.getTime()}-${dayIndex}`} 
                                className={`timeline-day-header ${otherMonth ? 'other-month' : ''} ${today ? 'today' : ''} ${hasSchedule ? 'has-schedule' : ''}`}
                            >
                                <div className="day-number">{day.getDate()}</div>
                                <div className="day-name">{day.toLocaleDateString('pt-BR', { weekday: 'short' })}</div>
                            </div>
                        );
                    })}
                </div>
                
                {/* Dashboard Timeline */}
                <div className="timeline-dashboard">
                    <div className="timeline-container">
                        {/* Linhas de horário de fundo */}
                        <div className="timeline-hours-bg">
                            {Array.from({ length: 24 }, (_, hour) => (
                                <div key={hour} className="hour-line">
                                    <span className="hour-label">{hour.toString().padStart(2, '0')}h</span>
                                </div>
                            ))}
                        </div>
                        
                        {/* Colunas dos dias com escalas */}
                        <div className="timeline-columns">
                            {week.map((day, dayIndex) => {
                                const dayEscalas = getDayEscalas(day);
                                
                                // Debug específico para cada dia
                                if (dayEscalas.length > 0) {
                                    console.log(`Timeline - Dia ${day.getDate()}/${day.getMonth() + 1}:`, dayEscalas.map(e => `${e.horaInicio}-${e.horaFim}`));
                                }
                                
                                return (
                                    <div key={`${day.getTime()}-${dayIndex}`} className="timeline-day-column">
                                        {/* Escalas do dia */}
                                        {dayEscalas.map(escala => {
                                            const startHour = parseInt(escala.horaInicio.split(':')[0]);
                                            const startMinute = parseInt(escala.horaInicio.split(':')[1]);
                                            const endHour = parseInt(escala.horaFim.split(':')[0]);
                                            const endMinute = parseInt(escala.horaFim.split(':')[1]);
                                            
                                            // Calcular posição e altura
                                            const top = (startHour + startMinute / 60) * 25; // 25px por hora (consistente com CSS atual)
                                            const duration = (endHour + endMinute / 60) - (startHour + startMinute / 60);
                                            const height = Math.max(duration * 25, 20); // Mínimo 20px
                                            
                                            // Renderizar múltiplos usuários se houver
                                            const usuarios = escala.usuarios_atribuidos || [];
                                            
                                            if (usuarios.length === 0) {
                                                // Escala sem usuários atribuídos
                                            return (
                                                <div
                                                    key={escala.id}
                                                        className={`schedule-card empty ${draggedOver === escala.id ? 'drag-over' : ''}`}
                                                    style={{
                                                        top: `${top}px`,
                                                        height: `${height}px`,
                                                            backgroundColor: '#f0f0f0',
                                                            border: '2px dashed #ccc'
                                                        }}
                                                        onClick={() => showEscalaDetails(escala)}
                                                        onDragOver={(e) => handleDragOver(e, escala.id)}
                                                        onDrop={(e) => handleDrop(e, escala)}
                                                    >
                                                        <div className="schedule-content">
                                                            <div className="schedule-info">
                                                                <div className="schedule-name">Escala Vazia</div>
                                                                <div className="schedule-time">
                                                                    {formatTime(escala.horaInicio)} - {formatTime(escala.horaFim)}
                                                                </div>
                                                                <div className="schedule-sector">Arraste um profissional</div>
                                                            </div>
                                                            {(hasPermission('Administrador') || hasPermission('Supervisor')) && (
                                                                <button
                                                                    className="schedule-delete-btn"
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        if (window.confirm('Tem certeza que deseja excluir esta escala? Esta ação não pode ser desfeita.')) {
                                                                            escalaService.excluir(escala.id)
                                                                                .then(() => {
                                                                                    toast.success('Escala excluída com sucesso');
                                                                                    loadInitialData();
                                                                                })
                                                                                .catch((error) => {
                                                                                    console.error('Erro ao excluir:', error);
                                                                                    toast.error('Erro ao excluir escala');
                                                                                });
                                                                        }
                                                                    }}
                                                                    style={{
                                                                        position: 'absolute',
                                                                        top: '2px',
                                                                        right: '2px',
                                                                        background: 'rgba(220, 53, 69, 0.9)',
                                                                        color: 'white',
                                                                        border: 'none',
                                                                        borderRadius: '50%',
                                                                        width: '16px',
                                                                        height: '16px',
                                                                        fontSize: '10px',
                                                                        cursor: 'pointer',
                                                                        display: 'flex',
                                                                        alignItems: 'center',
                                                                        justifyContent: 'center',
                                                                        zIndex: 20
                                                                    }}
                                                                    title="Excluir escala"
                                                                >
                                                                    ×
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                );
                                            }
                                            
                                            // Renderizar cada usuário da escala
                                            return usuarios.map((usuarioEscala, index) => (
                                                <div
                                                    key={`${escala.id}-${usuarioEscala.usuario_id}`}
                                                    className={`schedule-card ${draggedOver === escala.id ? 'drag-over' : ''}`}
                                                    style={{
                                                        top: `${top + (index * 15)}px`,
                                                        height: `${Math.max(height - (index * 8), 18)}px`,
                                                        backgroundColor: getUserColor(usuarioEscala.usuario_id),
                                                        zIndex: 10 - index
                                                    }}
                                                    onClick={() => showEscalaDetails(escala)}
                                                    onDragOver={(e) => handleDragOver(e, escala.id)}
                                                    onDrop={(e) => handleDrop(e, escala)}
                                                >
                                                    <div className="schedule-content">
                                                        <div className="schedule-avatar">
                                                            {usuarioEscala.usuario?.nome ? getInitials(usuarioEscala.usuario.nome) : getInitials('Usuário')}
                                                        </div>
                                                        <div className="schedule-info">
                                                            <div className="schedule-name">
                                                                {usuarioEscala.usuario?.nome ? usuarioEscala.usuario.nome.split(' ')[0] : 'Usuário'}
                                                            </div>
                                                            <div className="schedule-time">
                                                                {formatTime(escala.horaInicio)} - {formatTime(escala.horaFim)}
                                                            </div>
                                                            {usuarioEscala.setor && (
                                                                <div className="schedule-sector">
                                                                    {typeof usuarioEscala.setor === 'string' ? usuarioEscala.setor : usuarioEscala.setor.nome}
                                                                </div>
                                                            )}
                                                        </div>
                                                        {(hasPermission('Administrador') || hasPermission('Supervisor')) && (
                                                            <button
                                                                className="schedule-delete-btn"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    if (window.confirm('Tem certeza que deseja excluir esta escala? Esta ação não pode ser desfeita.')) {
                                                                        escalaService.excluir(escala.id)
                                                                            .then(() => {
                                                                                toast.success('Escala excluída com sucesso');
                                                                                loadInitialData();
                                                                            })
                                                                            .catch((error) => {
                                                                                console.error('Erro ao excluir:', error);
                                                                                toast.error('Erro ao excluir escala');
                                                                            });
                                                                    }
                                                                }}
                                                                style={{
                                                                    position: 'absolute',
                                                                    top: '2px',
                                                                    right: '2px',
                                                                    background: 'rgba(220, 53, 69, 0.9)',
                                                                    color: 'white',
                                                                    border: 'none',
                                                                    borderRadius: '50%',
                                                                    width: '16px',
                                                                    height: '16px',
                                                                    fontSize: '10px',
                                                                    cursor: 'pointer',
                                                                    display: 'flex',
                                                                    alignItems: 'center',
                                                                    justifyContent: 'center',
                                                                    zIndex: 20
                                                                }}
                                                                title="Excluir escala"
                                                            >
                                                                ×
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>
                                            ));
                                        })}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="escalas-container">
            {/* Sidebar Retrátil */}
            <div className={`sidebar-retratil ${sidebarVisible ? 'visible' : ''}`}>
                <div className="sidebar-content">
                    <div className="sidebar-header">
                        <div className="sidebar-tabs">
                            <button 
                                className={`sidebar-tab ${sidebarMode === 'usuarios' ? 'active' : ''}`}
                                onClick={() => setSidebarMode('usuarios')}
                            >
                                <Users size={16} />
                                Usuários
                            </button>
                            <button 
                                className={`sidebar-tab ${sidebarMode === 'setores' ? 'active' : ''}`}
                                onClick={() => setSidebarMode('setores')}
                            >
                                <Filter size={16} />
                                Setores
                            </button>
                        </div>
                        <button className="sidebar-close" onClick={() => setSidebarVisible(false)}>
                            <X size={16} />
                        </button>
                    </div>
                    
                    {sidebarMode === 'usuarios' && (
                        <div className="sidebar-usuarios">
                            <div className="sidebar-section-title">
                                Profissionais {isDragging ? '(arraste para escala)' : ''}
                            </div>
                            <div className="usuarios-list">
                                {usuarios.map(usuario => (
                                    <div 
                                        key={usuario.id}
                                        className={`usuario-item ${selectedUser?.id === usuario.id ? 'selected' : ''}`}
                                        draggable={hasPermission('Administrador') || hasPermission('Supervisor')}
                                        onDragStart={() => handleDragStart(usuario)}
                                        onDragEnd={handleDragEnd}
                                        onClick={() => setSelectedUser(selectedUser?.id === usuario.id ? null : usuario)}
                                    >
                                        <div 
                                            className="user-avatar"
                                            style={{ backgroundColor: getUserColor(usuario.id) }}
                                        >
                                            {getInitials(usuario.nome)}
                                        </div>
                                        <div className="usuario-info">
                                            <div className="usuario-nome">{usuario.nome}</div>
                                            <div className="usuario-perfil">{usuario.perfil}</div>
                                        </div>
                                        {(hasPermission('Administrador') || hasPermission('Supervisor')) && (
                                            <div className="drag-indicator">⋮⋮</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    
                    {sidebarMode === 'setores' && (
                        <div className="sidebar-setores">
                            <div className="sidebar-section-title">Filtrar por Setor</div>
                            <div className="setores-list">
                                <div 
                                    className={`setor-item ${!filtroSetor ? 'active' : ''}`}
                                    onClick={() => setFiltroSetor('')}
                                >
                                    <div className="setor-color all-sectors"></div>
                                    <span>Todos os Setores</span>
                                </div>
                                {setores.map((setor, index) => (
                                    <div 
                                        key={setor.id}
                                                                        className={`setor-item ${filtroSetor === setor.id ? 'active' : ''}`}
                                onClick={() => setFiltroSetor(setor.id)}
                                    >
                                        <div 
                                            className="setor-color"
                                            style={{ backgroundColor: userColors[index % userColors.length] }}
                                        ></div>
                                        <span>{setor.nome}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Overlay para fechar sidebar */}
            {sidebarVisible && <div className="sidebar-overlay" onClick={() => setSidebarVisible(false)}></div>}

            {/* Header */}
            <div className="escalas-header">
                <div className="header-title-section">
                    <button 
                        className="btn-sidebar-toggle"
                        onClick={toggleSidebar}
                        title="Abrir painel de usuários"
                    >
                        <Menu size={20} />
                    </button>
                    <h1>Gestão de Escalas</h1>
                    {hasPermission('Supervisor') && (
                        <button 
                            className={`btn-create-escala ${editMode ? 'active' : ''}`}
                            onClick={() => {
                                if (editMode) {
                                    setShowEscalaModal(true);
                                } else {
                                    setEditMode(true);
                                }
                            }}
                            title={editMode ? "Criar nova escala" : "Entrar no modo de edição"}
                        >
                            <Plus size={16} />
                            {editMode ? 'Nova Escala' : 'Criar Escalas'}
                        </button>
                    )}
                    {editMode && hasPermission('Supervisor') && (
                        <button 
                            className="btn-exit-edit"
                            onClick={() => setEditMode(false)}
                            title="Sair do modo de edição"
                        >
                            ✕ Sair
                        </button>
                    )}
                    {hasPermission('Supervisor') && (
                        <button 
                            className="btn-create-escala"
                            onClick={openSetorManager}
                            title="Gerenciar Setores"
                        >
                            <Settings size={16} />
                            Setores
                        </button>
                    )}
                </div>
                <div className="header-controls">
                    <div className="month-navigation">
                        <button 
                            className="month-nav-btn"
                            onClick={() => changeMonth(-1)}
                        >
                            ‹
                        </button>
                        <div className="month-title">
                            {currentDate.toLocaleDateString('pt-BR', { 
                                month: 'long', 
                                year: 'numeric' 
                            })}
                        </div>
                        <button 
                            className="month-nav-btn"
                            onClick={() => changeMonth(1)}
                        >
                            ›
                        </button>
                    </div>
                    <select 
                        className="filter-select"
                        value={filtroEstabelecimento}
                        onChange={(e) => {
                            setFiltroEstabelecimento(e.target.value);
                            loadSetoresPorEstabelecimento(e.target.value);
                        }}
                    >
                        {estabelecimentos.map(est => (
                            <option key={est.id} value={est.id}>{est.nome}</option>
                        ))}
                    </select>
                    <select 
                        className="filter-select"
                        value={filtroSetor}
                        onChange={(e) => setFiltroSetor(e.target.value)}
                    >
                        <option value="">Todos os Setores</option>
                        {setores.map(setor => (
                            <option key={setor.id} value={setor.id}>{setor.nome}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Main Content */}
            <div className="calendar-main-grid">
                {/* Sidebar com Sócios */}
                <div className="users-sidebar">
                    <div className="sidebar-title">SÓCIOS</div>
                    <div className="users-list">
                        {usuarios.map(renderUserAvatar)}
                    </div>
                </div>

                {/* Calendário Principal */}
                <div className="calendar-panel">
                    <div className="calendar-grid">
                        {/* Cabeçalho dos dias da semana */}
                        <div className="weekday-headers">
                            {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(day => (
                                <div key={day} className="weekday-header">{day}</div>
                            ))}
                        </div>

                        {/* Semanas do calendário */}
                        <div className="calendar-weeks">
                            {getCalendarWeeks().map((week, weekIndex) => (
                                <div key={weekIndex} className="calendar-week">
                                    {expandedWeek === weekIndex ? (
                                        <div 
                                            className="week-expanded"
                                            onClick={() => toggleWeek(weekIndex)}
                                        >
                                            {renderWeekTimeline(week, weekIndex)}
                                        </div>
                                    ) : (
                                        <div 
                                            className="week-days"
                                            onClick={() => toggleWeek(weekIndex)}
                                        >
                                            {week.map((day, dayIndex) => 
                                                renderCalendarDay(day, weekIndex, dayIndex)
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Widgets Laterais */}
                <div className="widgets-sidebar">
                    <div className="widget-section">
                        <div className="checkin-widget">
                            <div className="widget-title">
                                <Clock size={16} />
                                Status dos Check-ins
                            </div>
                            <div className="checkin-info">
                                <div className="checkin-stats">
                                    <div className="stat-item realized">
                                        <div>
                                            <div className="stat-value">{checkinStats.realizados}</div>
                                            <div className="stat-label">Realizados</div>
                                        </div>
                                    </div>
                                    <div className="stat-item pending">
                                        <div>
                                            <div className="stat-value">{checkinStats.pendentes}</div>
                                            <div className="stat-label">Pendentes</div>
                                        </div>
                                    </div>
                                </div>
                                <div className="progress-bar">
                                    <div 
                                        className="progress-fill"
                                        style={{ width: `${checkinStats.percentualRealizados}%` }}
                                    ></div>
                                    <span className="progress-text">{checkinStats.percentualRealizados}% Concluído</span>
                                </div>
                            </div>
                        </div>



                        <div className="stats-widget">
                            <div className="widget-title">
                                <Users size={16} />
                                Estatísticas
                            </div>
                            <div className="stats-content">
                                <div className="stat-card">
                                    <div className="stat-number">{escalas.length}</div>
                                    <div className="stat-label">Total de Escalas</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-number">{usuarios.length}</div>
                                    <div className="stat-label">Profissionais Ativos</div>
                                </div>
                                <div className="stat-card">
                                    <div className="stat-number">{escalas.filter(e => isOvernight(e.horaInicio, e.horaFim)).length}</div>
                                    <div className="stat-label">Plantões Noturnos</div>
                                </div>
                            </div>
                            
                            <div className="notifications-section">
                                <h4>Notificações</h4>
                                <div className="notifications-list">
                                    {notificacoes.length > 0 ? (
                                        notificacoes.map(notif => (
                                            <div key={notif.id} className={`notification-item ${notif.urgente ? 'urgente' : ''}`}>
                                                {notif.mensagem}
                                            </div>
                                        ))
                                    ) : (
                                        <div className="no-notifications">
                                            Nenhuma notificação
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>





            {/* Modal de Criação de Escala */}
            {showEscalaModal && (
                <div className="modal-overlay show" onClick={() => setShowEscalaModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="modal-title">
                                <Plus size={20} />
                                Nova Escala
                            </div>
                            <button 
                                className="close-button"
                                onClick={() => setShowEscalaModal(false)}
                            >
                                ×
                            </button>
                        </div>

                        <form className="escala-form" onSubmit={(e) => { e.preventDefault(); handleSubmitEscala(); }}>
                            <div className="form-group">
                                <label className="form-label">
                                    <Calendar size={16} />
                                    Tipo de Escala
                                </label>
                                <div className="radio-group">
                                    <label className="radio-option">
                                        <input
                                            type="radio"
                                            name="tipo"
                                            value="regular"
                                            checked={escalaForm.tipo === 'regular'}
                                            onChange={(e) => handleFormChange('tipo', e.target.value)}
                                        />
                                        Regular
                                    </label>
                                    <label className="radio-option">
                                        <input
                                            type="radio"
                                            name="tipo"
                                            value="irregular"
                                            checked={escalaForm.tipo === 'irregular'}
                                            onChange={(e) => handleFormChange('tipo', e.target.value)}
                                        />
                                        Irregular
                                    </label>
                                </div>
                            </div>

                            {escalaForm.tipo === 'regular' ? (
                                <>
                                    <div className="form-group">
                                        <label className="form-label">
                                            <Calendar size={16} />
                                            Data
                                        </label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            value={escalaForm.data ? new Date(escalaForm.data).toLocaleDateString('pt-BR', {
                                                day: '2-digit',
                                                month: '2-digit',
                                                year: 'numeric'
                                            }) : ''}
                                            readOnly
                                            style={{ backgroundColor: '#f8f9fa' }}
                                            required
                                        />
                                    </div>

                                    <div className="form-row">
                                        <div className="form-group">
                                            <label className="form-label">
                                                <Clock size={16} />
                                                Hora Início
                                            </label>
                                            <input
                                                type="time"
                                                className="form-input"
                                                value={escalaForm.horaInicio}
                                                onChange={(e) => handleFormChange('horaInicio', e.target.value)}
                                                required
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">
                                                <Clock size={16} />
                                                Hora Fim
                                            </label>
                                            <input
                                                type="time"
                                                className="form-input"
                                                value={escalaForm.horaFim}
                                                onChange={(e) => handleFormChange('horaFim', e.target.value)}
                                                required
                                            />
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="form-group">
                                        <label className="form-label">
                                            <Calendar size={16} />
                                            Dias da Semana
                                        </label>
                                        <div className="dias-semana-grid">
                                            {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map((dia, index) => (
                                                <button
                                                    key={dia}
                                                    type="button"
                                                    className={`dia-button ${escalaForm.diasSemana.includes(index) ? 'selected' : ''}`}
                                                    onClick={() => handleDiaSemanaToggle(index)}
                                                >
                                                    {dia}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">
                                            <Clock size={16} />
                                            Escalas Irregulares
                                        </label>
                                        <div className="escalas-irregulares-list">
                                            {escalaForm.escalasIrregulares.map((escala, index) => (
                                                <div key={escala.id} className="escala-irregular-item">
                                                    <div className="escala-irregular-header">
                                                        <span className="escala-number">Escala {index + 1}</span>
                                                        <button
                                                            type="button"
                                                            className="remove-button"
                                                            onClick={() => removeEscalaIrregular(escala.id)}
                                                        >
                                                            ×
                                                        </button>
                                                    </div>
                                                    <div className="form-row">
                                                        <input
                                                            type="text"
                                                            className="form-input"
                                                            value={escala.data ? new Date(escala.data).toLocaleDateString('pt-BR', {
                                                                day: '2-digit',
                                                                month: '2-digit',
                                                                year: 'numeric'
                                                            }) : ''}
                                                            readOnly
                                                            style={{ backgroundColor: '#f8f9fa' }}
                                                            placeholder="Data"
                                                        />
                                                        <input
                                                            type="time"
                                                            className="form-input"
                                                            value={escala.horaInicio}
                                                            onChange={(e) => {
                                                                const newEscalas = [...escalaForm.escalasIrregulares];
                                                                newEscalas[index].horaInicio = e.target.value;
                                                                handleFormChange('escalasIrregulares', newEscalas);
                                                            }}
                                                        />
                                                        <input
                                                            type="time"
                                                            className="form-input"
                                                            value={escala.horaFim}
                                                            onChange={(e) => {
                                                                const newEscalas = [...escalaForm.escalasIrregulares];
                                                                newEscalas[index].horaFim = e.target.value;
                                                                handleFormChange('escalasIrregulares', newEscalas);
                                                            }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                className="btn-secondary"
                                                onClick={addEscalaIrregular}
                                            >
                                                <Plus size={16} />
                                                Adicionar Escala Irregular
                                            </button>
                                        </div>
                                    </div>
                                </>
                            )}

                            <div className="form-group">
                                <label className="form-label">
                                    <MapPin size={16} />
                                    Estabelecimento
                                </label>
                                <select
                                    className="form-select"
                                    value={escalaForm.estabelecimentoId}
                                    onChange={(e) => handleFormChange('estabelecimentoId', e.target.value)}
                                    required
                                >
                                    <option value="">Selecione um estabelecimento</option>
                                    {estabelecimentos.map(estabelecimento => (
                                        <option key={estabelecimento.id} value={estabelecimento.id}>
                                            {estabelecimento.nome}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="modal-footer">
                                <button
                                    type="button"
                                    className="btn-secondary"
                                    onClick={() => setShowEscalaModal(false)}
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="btn-primary"
                                >
                                    Criar Escala
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Detalhes da Escala */}
            {showDetailsModal && selectedEscala && (
                <div className="modal-overlay show" onClick={() => setShowDetailsModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="modal-title">
                                <Calendar size={20} />
                                Detalhes da Escala
                            </div>
                            <button 
                                className="close-button"
                                onClick={() => setShowDetailsModal(false)}
                            >
                                ×
                            </button>
                        </div>

                        <div className="escala-info">
                            <div className="info-row">
                                <span className="info-label">Horário:</span>
                                <span className="info-value">
                                    {formatTime(selectedEscala.horaInicio)} - {formatTime(selectedEscala.horaFim)}
                                </span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">Estabelecimento:</span>
                                <span className="info-value">{selectedEscala.estabelecimento?.nome || 'Não definido'}</span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">Data:</span>
                                <span className="info-value">
                                    {new Date(selectedEscala.data).toLocaleDateString('pt-BR', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric'
                                    })}
                                </span>
                            </div>
                            <div className="info-row">
                                <span className="info-label">Status:</span>
                                <span className="info-value">{selectedEscala.status}</span>
                            </div>
                            
                            {selectedEscala.usuarios_atribuidos && selectedEscala.usuarios_atribuidos.length > 0 && (
                                <>
                                    <div className="info-row">
                                        <span className="info-label">Profissionais:</span>
                                    </div>
                                    {selectedEscala.usuarios_atribuidos.map((usuarioEscala, index) => (
                                        <div key={index} className="info-row nested">
                                            <span className="info-value">
                                                • {usuarioEscala.usuario?.nome || 'Usuário não definido'} 
                                                {usuarioEscala.setor && ` - ${usuarioEscala.setor}`}
                                            </span>
                                        </div>
                                    ))}
                                </>
                            )}
                        </div>

                        <div className="modal-footer">
                            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <button
                                type="button"
                                className="btn-secondary"
                                onClick={() => setShowDetailsModal(false)}
                            >
                                Fechar
                            </button>
                                {(hasPermission('Administrador') || hasPermission('Supervisor')) && (
                                    <button
                                        type="button"
                                        className="btn-delete"
                                        onClick={async () => {
                                            if (window.confirm('Tem certeza que deseja excluir esta escala? Esta ação não pode ser desfeita.')) {
                                                try {
                                                    await escalaService.excluir(selectedEscala.id);
                                                    toast.success('Escala excluída com sucesso');
                                                    setShowDetailsModal(false);
                                                    loadInitialData();
                                                } catch (error) {
                                                    console.error('Erro ao excluir:', error);
                                                    toast.error('Erro ao excluir escala');
                                                }
                                            }
                                        }}
                                        style={{ 
                                            backgroundColor: '#dc3545', 
                                            color: 'white',
                                            border: 'none',
                                            padding: '8px 16px',
                                            borderRadius: '4px',
                                            cursor: 'pointer',
                                            fontSize: '14px'
                                        }}
                                    >
                                        Excluir Escala
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Painel de Edição Central (Administrador) */}
            {showEditPanel && editingEscala && (
                <div className="edit-panel-overlay">
                    <div className="edit-panel-central">
                        <div className="edit-panel-header">
                            <h3>
                                <Edit3 size={18} />
                                Editar Escala - {new Date(editingEscala.data).toLocaleDateString('pt-BR', {
                                    day: '2-digit',
                                    month: '2-digit',
                                    year: 'numeric'
                                })}
                            </h3>
                            <button 
                                className="close-btn"
                                onClick={() => setShowEditPanel(false)}
                            >
                                <X size={18} />
                            </button>
                        </div>
                        
                        <div className="edit-panel-content">
                            {/* Informações Básicas */}
                            <div className="edit-section">
                                <h4>Informações da Escala</h4>
                                <div className="form-group">
                                    <label>Data:</label>
                                    <input 
                                        type="text" 
                                        value={new Date(editingEscala.data).toLocaleDateString('pt-BR', {
                                            day: '2-digit',
                                            month: '2-digit',
                                            year: 'numeric'
                                        })}
                                        readOnly
                                        style={{ backgroundColor: '#f8f9fa' }}
                                    />
                                </div>
                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Início:</label>
                                        <input 
                                            type="time" 
                                            value={editingEscala.horaInicio}
                                            onChange={(e) => setEditingEscala({...editingEscala, horaInicio: e.target.value})}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Fim:</label>
                                        <input 
                                            type="time" 
                                            value={editingEscala.horaFim}
                                            onChange={(e) => setEditingEscala({...editingEscala, horaFim: e.target.value})}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Setores da Escala */}
                            <div className="edit-section">
                                <h4>Setores da Escala</h4>
                                <div style={{ marginBottom: 12 }}>
                                                        <select 
                                        className="form-select"
                                        value={''}
                                        onChange={e => {
                                            const setorId = e.target.value;
                                            if (!setorId) return;
                                            // Adiciona setor ao estado local da escala
                                            setEditingEscala(prev => ({
                                                                    ...prev,
                                                setores: [...(prev.setores || []), setores.find(s => s.id === parseInt(setorId))]
                                                                }));
                                                            }}
                                                        >
                                        <option value="">Adicionar Setor...</option>
                                        {setores.filter(s => !(editingEscala.setores || []).some(sel => sel.id === s.id)).map(setor => (
                                            <option key={setor.id} value={setor.id}>{setor.nome}</option>
                                                            ))}
                                                        </select>
                                                    </div>
                                <div className="setores-blocos">
                                    {(editingEscala.setores || []).map(setor => (
                                        <div key={setor.id} className="setor-bloco">
                                            <div className="setor-bloco-header">
                                                <strong>{setor.nome}</strong>
                                                <button onClick={() => setEditingEscala(prev => ({
                                                    ...prev,
                                                    setores: (prev.setores || []).filter(s => s.id !== setor.id)
                                                }))} style={{ marginLeft: 8 }}>Remover</button>
                                            </div>
                                            <div>
                                                <button onClick={() => openProfessionalSelector(setor)}>
                                                    Adicionar Profissionais
                                                    </button>
                                                </div>
                                            <div className="assigned-professionals-grid">
                                                {(setorProfissionais[setor.id] || []).map(profissional => (
                                                    <div key={profissional.id} className="assigned-professional">
                                                        <div className="professional-avatar small" style={{ backgroundColor: getUserColor(profissional.id) }}>
                                                            {getInitials(profissional.nome)}
                                </div>
                                                        <div className="professional-details">
                                                            <div className="name">{profissional.nome}</div>
                            </div>
                                                        <button className="remove-professional" onClick={() => removerProfissionalDoSetor(setor.id, profissional.id)}>
                                                            <X size={12} />
                                    </button>
                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="edit-panel-footer">
                            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <button 
                                className="btn-save"
                                onClick={async () => {
                                    try {
                                            // Salvar a escala básica
                                        await escalaService.atualizar(editingEscala.id, editingEscala);
                                            
                                            // Salvar os profissionais dos setores
                                            for (const setor of editingEscala.setores || []) {
                                                const profissionaisDoSetor = setorProfissionais[setor.id] || [];
                                                for (const profissional of profissionaisDoSetor) {
                                                    await escalaService.adicionarUsuario(editingEscala.id, profissional.id, setor.id);
                                                }
                                            }
                                            
                                        toast.success('Escala atualizada');
                                        setShowEditPanel(false);
                                            setSetorProfissionais({}); // Limpar estado dos profissionais
                                        loadInitialData();
                                    } catch (error) {
                                            console.error('Erro ao atualizar:', error);
                                        toast.error('Erro ao atualizar');
                                    }
                                }}
                            >
                                Salvar
                            </button>
                                <button 
                                    className="btn-cancel"
                                    onClick={() => {
                                        setShowEditPanel(false);
                                        setSetorProfissionais({}); // Limpar estado dos profissionais
                                    }}
                                >
                                Cancelar
                            </button>
                                <button 
                                    className="btn-delete"
                                    onClick={async () => {
                                        if (window.confirm('Tem certeza que deseja excluir esta escala? Esta ação não pode ser desfeita.')) {
                                            try {
                                                await escalaService.excluir(editingEscala.id);
                                                toast.success('Escala excluída com sucesso');
                                                setShowEditPanel(false);
                                                setSetorProfissionais({});
                                                loadInitialData();
                                            } catch (error) {
                                                console.error('Erro ao excluir:', error);
                                                toast.error('Erro ao excluir escala');
                                            }
                                        }
                                    }}
                                    style={{ 
                                        backgroundColor: '#dc3545', 
                                        color: 'white',
                                        border: 'none',
                                        padding: '8px 16px',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        fontSize: '14px'
                                    }}
                                >
                                    Excluir Escala
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Widget Flutuante de Seleção de Usuários */}
            {showUserSelector && (
                <div className="user-selector-overlay">
                    <div className="user-selector-widget">
                        <div className="user-selector-header">
                            <h4>
                                <Users size={18} />
                                Selecionar Profissional
                            </h4>
                            <button 
                                className="close-btn"
                                onClick={closeUserSelector}
                            >
                                <X size={16} />
                            </button>
                        </div>
                        
                        <div className="user-selector-search">
                            <input
                                type="text"
                                placeholder="Buscar por nome, email ou perfil..."
                                value={userSearchTerm}
                                onChange={(e) => handleUserSearch(e.target.value)}
                                className="search-input"
                                autoFocus
                            />
                            <div className="search-results-count">
                                {filteredUsers.length} de {usuarios.length} profissionais
                            </div>
                        </div>
                        
                        <div className="user-selector-list">
                            {filteredUsers.filter(usuario => {
                                // Não mostrar usuários já atribuídos à escala
                                return !getEscalaUsuarios(editingEscala?.id || 0).some(eu => eu.usuario_id === usuario.id);
                            }).map(usuario => (
                                <div 
                                    key={usuario.id}
                                    className="user-selector-item"
                                    onClick={() => selectUserFromWidget(usuario)}
                                >
                                    <div 
                                        className="user-avatar"
                                        style={{ backgroundColor: getUserColor(usuario.id) }}
                                    >
                                        {getInitials(usuario.nome)}
                                    </div>
                                    <div className="user-details">
                                        <div className="user-name">{usuario.nome}</div>
                                        <div className="user-email">{usuario.email}</div>
                                        <div className="user-profile">{usuario.perfil}</div>
                                    </div>
                                    <div className="add-user-btn">
                                        <Plus size={16} />
                                    </div>
                                </div>
                            ))}
                            
                            {filteredUsers.filter(usuario => {
                                return !getEscalaUsuarios(editingEscala?.id || 0).some(eu => eu.usuario_id === usuario.id);
                            }).length === 0 && (
                                <div className="no-users-found">
                                    {userSearchTerm ? 
                                        `Nenhum profissional encontrado para "${userSearchTerm}"` : 
                                        'Todos os profissionais já estão atribuídos a esta escala'
                                    }
                                </div>
                            )}
                        </div>
                        
                        <div className="user-selector-footer">
                            <small>Clique em um profissional para adicioná-lo à escala</small>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de Gerenciamento de Setores */}
            {showSetorManager && (
                <div className="modal-overlay show" onClick={closeSetorManager}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <div className="modal-title">
                                <Settings size={20} />
                                Gerenciar Setores
                            </div>
                            <button 
                                className="close-button"
                                onClick={closeSetorManager}
                            >
                                <X size={20} />
                            </button>
                        </div>
                        
                        <div className="escala-form">
                            <div className="form-group">
                                <label className="form-label">Nome do Setor</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={setorForm.nome}
                                    onChange={(e) => handleSetorFormChange('nome', e.target.value)}
                                    placeholder="Ex: UTI, EMERGÊNCIA"
                                />
                            </div>
                            
                            <div className="form-group">
                                <label className="form-label">Descrição</label>
                                <textarea
                                    className="form-input"
                                    value={setorForm.descricao}
                                    onChange={(e) => handleSetorFormChange('descricao', e.target.value)}
                                    placeholder="Descrição do setor"
                                    rows={3}
                                />
                            </div>
                        </div>
                        
                        <div className="modal-footer">
                            <button 
                                className="btn-primary"
                                onClick={criarSetor}
                            >
                                Criar Setor
                            </button>
                            <button 
                                className="btn-secondary"
                                onClick={closeSetorManager}
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Sidebar de Seleção de Profissionais por Setor */}
            {showProfessionalSelector && selectedSetor && (
                <>
                    <div className="sidebar-overlay" onClick={closeProfessionalSelector}></div>
                    <div className="professional-selector-sidebar">
                    <div className="professional-selector-content">
                        <div className="professional-selector-header">
                            <div className="professional-selector-title">
                                <Users size={20} />
                                Selecionar Profissionais - {selectedSetor.nome}
                            </div>
                            <button 
                                className="professional-selector-close"
                                onClick={closeProfessionalSelector}
                            >
                                <X size={20} />
                            </button>
                        </div>
                        
                        <div className="professional-selector-body">
                            <div className="available-professionals-sidebar">
                                <h4>Profissionais Disponíveis</h4>
                                {usuarios.map(usuario => (
                                    <div 
                                        key={usuario.id}
                                        className="available-professional-sidebar"
                                        onClick={() => adicionarProfissionalAoSetor(selectedSetor.id, usuario)}
                                    >
                                        <div 
                                            className="professional-avatar"
                                            style={{ backgroundColor: getUserColor(usuario.id) }}
                                        >
                                            {getInitials(usuario.nome)}
                                        </div>
                                        <div className="professional-info">
                                            <div className="professional-name">{usuario.nome}</div>
                                            <div className="professional-email">{usuario.email}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            
                            <div className="selected-professionals-sidebar">
                                <h4>Profissionais Selecionados</h4>
                                {(setorProfissionais[selectedSetor.id] || []).map(profissional => (
                                    <div key={profissional.id} className="selected-professional-sidebar">
                                        <div 
                                            className="professional-avatar small"
                                            style={{ backgroundColor: getUserColor(profissional.id) }}
                                        >
                                            {getInitials(profissional.nome)}
                                        </div>
                                        <div className="professional-details">
                                            <div className="name">{profissional.nome}</div>
                                        </div>
                                        <button 
                                            className="remove-professional"
                                            onClick={() => removerProfissionalDoSetor(selectedSetor.id, profissional.id)}
                                        >
                                            <X size={12} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        <div className="professional-selector-footer">
                            <button 
                                className="btn-primary"
                                onClick={closeProfessionalSelector}
                            >
                                Confirmar Seleção
                            </button>
                            <button 
                                className="btn-secondary"
                                onClick={closeProfessionalSelector}
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
                </>
            )}
        </div>
    );
};

export default Escalas;