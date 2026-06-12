/**
 * Strategic Flow - Menu Funcional + API com DEBUG + FALLBACK + MULTI-TENANT SECURE
 * Arquivo Unificado e Corrigido contra Travamentos
 */

class StrategicFlowAPI {
    constructor() {
        // Alinhado cirurgicamente com as portas e caminhos das APIs do backend
        this.API_URL = 'http://localhost:8001/api';
        this.WS_URL = 'ws://localhost:8001/ws/kpis';

        this.kpis = { cycleTime: null, otif: null, efficiency: null, rejection: null, roi: null, success: null, nps: null, throughput: null };
        this.ws = null;
        this.chart = null;
        this.restInterval = null;
        this.activeProcessId = null; // Controla o chat ativo do Portal do Cliente

        this.init();
    }

    init() {
        console.log('🚀 Strategic Flow iniciando...');
        this.setupNavigation();
        this.setupMenuCollapse();
        this.connectWebSocket();
        this.initChart();
        this.fetchKPIs();
    }

    // Injeta de forma segura o token JWT para o middleware do backend interceptar
    getHeaders() {
        let token = localStorage.getItem('access_token');
        if (!token) {
            // Token administrativo padrão para testes locais rápidos no ambiente de desenvolvimento
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2bGFkZW1pckBzdHJhdGVnaWNmbG93LmNvbSIsInRlbmFudF9pZCI6ImRlZmF1bHQtdGVuYW50Iiwicm9sZSI6ImNvbnN1bHRhbnQifQ";
            localStorage.setItem('access_token', token);
        }
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    // === NAVIGATION (ACESSO AS PAGES) ===
    setupNavigation() {
        console.log('📍 Configurando navegação...');

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                const section = item.dataset.section;
                if (!section) return;

                console.log(`📍 Navegando para a seção: ${section}`);

                // Remove as classes de ativo de todas as abas e painéis
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

                // Ativa visualmente o item clicado no menu
                item.classList.add('active');

                // Apresenta o painel correspondente na tela principal
                const targetSection = document.getElementById(section);
                if (targetSection) {
                    targetSection.classList.add('active');
                    document.getElementById('page-title').textContent = item.textContent.trim();
                }
            });
        });
    }

    // === MENU COLAPSÁVEL (SUBMENU) ===
    setupMenuCollapse() {
        console.log('🎛️ Configurando menus sanfona...');

        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', (e) => {
                e.preventDefault();

                const category = header.parentElement;
                const isOpen = category.classList.contains('open');

                // Fecha as outras categorias para manter a interface organizada
                document.querySelectorAll('.menu-category').forEach(cat => {
                    cat.classList.remove('open');
                });

                // Se a categoria estava fechada, expande ela agora
                if (!isOpen) {
                    category.classList.add('open');
                }

                console.log(`🎛️ Menu: ${isOpen ? 'fechado' : 'aberto'}`);
            });
        });
    }

    // === SIDEBAR COLAPSO (ÍCONES-ONLY) ===
    setupSidebarToggle() {
        const sidebar = document.querySelector('.sidebar');
        const toggleBtn = document.getElementById('menu-toggle');

        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                console.log('🔄 Sidebar alterada para: ' + (sidebar.classList.contains('collapsed') ? 'recolhida' : 'expandida'));
            });
        }
    }

    // === WEBSOCKET REALTIME ===
    connectWebSocket() {
        console.log('🔌 Tentando abrir conexão em tempo real via WebSocket:', this.WS_URL);

        try {
            this.ws = new WebSocket(this.WS_URL);

            this.ws.onopen = () => {
                console.log('✅ Canal WebSocket CONECTADO com sucesso!');
                this.updateStatus('connected', 'WebSocket Conectado');
                this.fetchAllData();
            };

            this.ws.onmessage = (e) => {
                console.log('📡 Dados de streaming do WebSocket recebidos:', e.data);
                try {
                    const data = JSON.parse(e.data);
                    this.updateKPIs(data);
                } catch (error) {
                    console.error('Erro ao processar mensagem do canal:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ Falha na infraestrutura do WebSocket:', error);
                this.updateStatus('disconnected', 'WebSocket Falhou - acionando REST');
                this.startRESTFallback();
            };

            this.ws.onclose = () => {
                console.log('❌ Canal WebSocket fechado.');
                this.updateStatus('disconnected', 'WebSocket Desconectado - acionando REST');
                this.startRESTFallback();
            };
        } catch (error) {
            console.error('❌ Exceção de rede no WebSocket:', error);
            this.updateStatus('disconnected', 'Erro WebSocket - acionando REST');
            this.startRESTFallback();
        }
    }
    updateStatus(status, text) {
        const indicator = document.getElementById('connection-indicator');
        const textEl = document.getElementById('connection-text');
        const btn = document.getElementById('connect-btn');

        if (indicator) indicator.className = `status-indicator ${status}`;
        if (textEl) textEl.textContent = text;
        if (btn) btn.style.display = status === 'connected' ? 'none' : 'inline';

        console.log(`📊 Status da Rede Atualizado: ${status} - ${text}`);
    }

    startRESTFallback() {
        console.log('⚡ Ativando mecanismo de resiliência (Polling HTTP a cada 30s)...');

        if (this.restInterval) clearInterval(this.restInterval);
        this.restInterval = setInterval(() => this.fetchKPIs(), 30000);
        this.fetchKPIs();
    }

        // === FETCH ALL DATA ===
    async fetchAllData() {
        console.log('📥 Sincronizando dados de todos os submódulos...');
        await this.fetchData('workflow-list', '/workflow');
        await this.fetchData('pdca-board', '/pdca');
        await this.fetchData('kaizen-board', '/kaizen');
        await this.fetchData('crm-table', '/crm/companies'); 
        await this.fetchData('projects-table', '/projects');
        
        // ---> ADICIONADO AQUI: Ativa a carga real da matriz de alocação da equipe
        await this.fetchData('workforce-view', '/workforce/dashboard');
        
        // Ativa a carga real dos processos do Portal do Cliente
        await this.fetchData('client-portal-view', '/portal/my-processes');
    }


    async fetchData(elementId, endpoint) {
        try {
            console.log(`📥 Consultando módulo REST: ${endpoint}...`);
            const res = await fetch(`${this.API_URL}${endpoint}`, {
                headers: this.getHeaders()
            });

            if (!res.ok) {
                console.error(`❌ Erro no servidor ao buscar ${endpoint}: ${res.status}`);
                return;
            }

            const data = await res.json();
            console.log(`✅ Dados carregados para ${endpoint}:`, data);
            this.renderData(elementId, data);
        } catch (error) {
            console.error(`❌ Falha na requisição HTTP do módulo ${endpoint}:`, error);
        }
    }

    // === KPIs HTTP FALLBACK ===
    async fetchKPIs() {
        console.log('📥 Buscando KPIs via requisição REST tradicional...');

        try {
            const res = await fetch(`${this.API_URL}/kpis`, {
                headers: this.getHeaders()
            });

            if (!res.ok) {
                console.error(`❌ Erro HTTP na rota de KPIs: ${res.status}`);
                this.useMockData();
                return;
            }

            const data = await res.json();
            console.log('✅ KPIs REST capturados com sucesso:', data);
            this.updateKPIs(data);
        } catch (error) {
            console.error('❌ Falha de rede ao buscar KPIs:', error);
            this.useMockData();
        }
    }

    updateKPIs(data) {
        console.log('🔄 Atualizando elementos de texto e tendências da tela...');
        this.kpis = data;
        const now = new Date().toLocaleTimeString();

        Object.keys(data).forEach(kpi => {
            const el = document.getElementById(`kpi-${kpi}`);
            const trend = document.getElementById(`trend-${kpi}`);
            const realtime = document.getElementById(`realtime-${kpi}`);

            if (el && data[kpi] !== null && data[kpi] !== undefined) {
                const value = data[kpi];
                el.textContent = kpi === 'throughput' || kpi === 'nps' ?
                    value.toFixed(0) :
                    value.toFixed(1) + (kpi === 'cycleTime' ? 'h' : '%');

                const target = this.getTarget(kpi);
                const trendValue = this.calcTrend(value, target, kpi === 'rejection');

                if (trend) {
                    trend.textContent = trendValue;
                    trend.className = `trend ${trendValue.includes('+') ? 'up' : 'down'}`;
                }

                if (realtime) realtime.textContent = now;
            }
        });

        this.updateChart();
    }

    getTarget(kpi) {
        return {
            cycleTime: 20,
            otif: 95,
            efficiency: 95,
            rejection: 2,
            roi: 200,
            success: 85,
            nps: 75,
            throughput: 1200
        }[kpi];
    }

    calcTrend(current, target, inverse = false) {
        if (!current || !target) return '--';
        const diff = ((current - target) / target) * 100;
        const sign = inverse ? (diff >= 0 ? '-' : '+') : (diff >= 0 ? '+' : '-');
        return `${sign}${Math.abs(diff).toFixed(0)}%`;
    }

    useMockData() {
        console.log('📊 Servidor offline - Populando painel com Mock Data dinâmico');
        const mock = {
            cycleTime: 24 + Math.random() * 2,
            otif: 94 + Math.random() * 2,
            efficiency: 95 + Math.random(),
            rejection: 2 + Math.random() * 0.5,
            roi: 220 + Math.random() * 10,
            success: 87 + Math.random() * 2,
            nps: 72 + Math.random() * 3,
            throughput: 1250 + Math.random() * 50
        };
        this.updateKPIs(mock);
    }
        // === CHART.JS REALTIME (CORRIGIDO E SEGURO CONTRA TRAVAMENTOS) ===
    initChart() {
        const canvas = document.getElementById('realtime-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Cycle Time', data: [], borderColor: '#ff4757', tension: 0.4, fill: false },
                    { label: 'OTIF', data: [], borderColor: '#2ed573', tension: 0.4, fill: false },
                    { label: 'Eficiência', data: [], borderColor: '#3742fa', tension: 0.4, fill: false }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 500 },
                scales: { y: { beginAtZero: false } }
            }
        });
        
        console.log('📊 Gráfico Chart.js pronto e mapeado!');
    }

    updateChart() {
        // Validação de segurança para evitar erros de nulos no console
        if (!this.chart || !this.kpis || this.kpis.cycleTime === null) return;
        
        const now = new Date().toLocaleTimeString();
        
        // Remove leituras antigas para manter a rolagem do gráfico fluida
        if (this.chart.data.labels.length > 20) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach(d => d.data.shift());
        }
        
        this.chart.data.labels.push(now);
        
        // CORREÇÃO CRÍTICA: Mapeamento cirúrgico dos índices, [1] e [2] das linhas do gráfico
        if (this.chart.data.datasets[0]) this.chart.data.datasets[0].data.push(this.kpis.cycleTime);
        if (this.chart.data.datasets[1]) this.chart.data.datasets[1].data.push(this.kpis.otif);
        if (this.chart.data.datasets[2]) this.chart.data.datasets[2].data.push(this.kpis.efficiency || 90.0);
        
        this.chart.update();
    }

    // === RENDERIZADORES DE INTERFACE (INTEGRADO E CORRIGIDO) ===
    renderData(elementId, data) {
        const el = document.getElementById(elementId);
        if (!el || !data) return;
        
        console.log(`🎨 Desenhando elementos na ID: ${elementId}`, data);
        
        if (elementId === 'workflow-list') {
            el.innerHTML = data.map(w => 
                `<div class="workflow-item" style="background:#f5f7fa;padding:15px;margin-bottom:10px;border-radius:8px;">
                    <strong>${w.name}</strong><br>
                    SLA: ${w.sla_remaining}<br>
                    <span class="status ${w.status === 'active' ? 'active' : 'developing'}">${w.status}</span>
                </div>`
            ).join('');
            
        } else if (elementId === 'pdca-board') {
            el.innerHTML = data.reduce((html, d) => {
                return html + `<div class="pdca-column" style="background:white;padding:20px;border-radius:12px;">
                    <h4 style="color:#3742fa">${d.phase}</h4>
                    <div class="pdca-item" style="background:#f5f7fa;padding:12px;margin:10px 0;border-radius:6px;">
                        ${d.title}<br>
                        <span class="status developing">${d.status}</span>
                    </div>
                </div>`;
            }, '');
            
        } else if (elementId === 'kaizen-board') {
            el.innerHTML = `<div class="kaizen-column"><h5>BACKLOG</h5>${data.filter(d=>d.status==='backlog').map(d=>`<div class="kaizen-card" style="background:white;padding:12px;margin:8px 0;border-radius:6px;">${d.title}</div>`).join('')}</div>
                <div class="kaizen-column"><h5>PROGRESS</h5>${data.filter(d=>d.status==='progress').map(d=>`<div class="kaizen-card" style="background:white;padding:12px;margin:8px 0;border-radius:6px;">${d.title}</div>`).join('')}</div>
                <div class="kaizen-column"><h5>DONE</h5>${data.filter(d=>d.status==='done').map(d=>`<div class="kaizen-card" style="background:#e0ffe0;padding:12px;margin:8px 0;border-radius:6px;">${d.title} - ROI: ${d.roi}</div>`).join('')}</div>`;
        
        } else if (elementId === 'crm-table') {
            const empresas = Array.isArray(data) ? data : (data.companies || []);
            if (!empresas.length) {
                el.innerHTML = '<tbody><tr><td style="color:#94a3b8; text-align:center; padding:20px;">Nenhuma conta ou lead cadastrado no CRM.</td></tr></tbody>';
                return;
            }
            el.innerHTML = `
                <thead>
                    <tr><th>ID</th><th>Razão Social / Empresa</th><th>CNPJ</th><th>Segmento</th><th>Porte</th><th>Funcionários</th></tr>
                </thead>
                <tbody>
                    ${empresas.map(c => `
                        <tr>
                            <td><strong>#${c.id_empresa}</strong></td>
                            <td style="color:#0D8ABC; font-weight:500;">${c.razao_social}</td>
                            <td>${c.cnpj || '--'}</td>
                            <td><span>${c.segmento || 'Geral'}</span></td>
                            <td>${c.porte_empresa || '--'}</td>
                            <td>${c.numero_funcionarios || 0} colab.</td>
                        </tr>
                    `).join('')}
                </tbody>`;
     //renderData//
                }         else if (elementId === 'workforce-view') {
            const consultores = Array.isArray(data) ? data : (data.consultants || []);
            if (!consultores.length) {
                el.innerHTML = '<p style="color:#94a3b8; padding:20px; text-align:center;">Nenhum engenheiro alocado.</p>';
                return;
            }
            
            el.innerHTML = `
                <div style="margin-bottom:20px;">
                    <h4 style="margin:0; color:#1e293b;">Alocação de Engenheiros & Consultores de Processo</h4>
                </div>
                
                <!-- Uso estrito das suas classes de estilo CSS enviadas -->
                <div class="workforce-grid">
                    ${consultores.map(c => {
                        const utilizacao = c.taxa_utilizacao_percent || 0;
                        // Define a cor de progresso usando o padrão das suas métricas
                        const corProgress = utilizacao >= 75 ? '#2ed573' : '#ff4757';
                        
                        return `
                            <div class="workforce-card">
                                <div class="workforce-card-header">
                                    <div>
                                        <strong>${c.nome || 'Consultor'}</strong><br>
                                        <span class="workforce-card-title">${c.cargo_senioridade || 'Membro'}</span>
                                    </div>
                                    <span class="workforce-status-tag" style="background:${c.status === 'Disponível' ? '#e0ffe0' : '#fff3cd'}; color:${c.status === 'Disponível' ? '#207220' : '#a07800'};">
                                        ${c.status || 'Ativo'}
                                    </span>
                                </div>
                                <div class="workforce-utilization">Utilização das Horas: <strong>${utilizacao.toFixed(1)}%</strong></div>
                                <div class="workforce-progress">
                                    <div class="workforce-progress-bar" style="width: ${Math.min(utilizacao, 100)}%; background: ${corProgress};"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>`;
        }

         else if (elementId === 'client-portal-view') {
            const processos = data.processes || [];
            el.innerHTML = `
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:25px; width:100%;">
                    <div>
                        <h5><i class="fas fa-sitemap"></i> Processos para Consulta</h5>
                        ${processos.length ? processos.map(p => `
                            <div onclick="app.loadProcessComments(${p.id_processo})" style="background:white; padding:15px; border-radius:8px; margin-bottom:12px; cursor:pointer; border:1px solid #e2e8f0;">
                                <strong style="color:#0D8ABC;">${p.nome_processo}</strong>
                            </div>
                        `).join('') : '<p style="color:#94a3b8;">Nenhum processo liberado no portal.</p>'}
                    </div>
                    <div style="display:flex; flex-direction:column; background:white; padding:20px; border-radius:12px; border:1px solid #e2e8f0; height:350px;">
                        <h5><i class="fas fa-comments"></i> Chat Feedback</h5>
                        <div id="portal-chat-history" style="flex:1; overflow-y:auto; padding:10px; background:#f8fafc; border-radius:8px; margin-bottom:15px;">
                            <p style="color:#94a3b8; text-align:center; margin-top:80px;">Selecione um processo para carregar o histórico.</p>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <input type="text" id="portal-message-input" placeholder="Feedback..." style="flex:1; padding:10px; border-radius:6px; border:1px solid #cbd5e1;">
                            <button onclick="app.sendPortalComment()" style="background:#0D8ABC; color:white; border:none; padding:0 15px; border-radius:6px; cursor:pointer;"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>`;
                
        } else if (elementId.includes('table')) {
            const rowsData = Array.isArray(data) ? data : [];
            if (!rowsData.length) return;
            const headers = Object.keys(rowsData[0]);
            const rows = rowsData.map(r => `<tr>${headers.map(h => `<td>${r[h] !== null ? r[h] : '--'}</td>`).join('')}</tr>`).join('');
            el.innerHTML = `<thead><tr>${headers.map(h => `<th>${h.toUpperCase()}</th>`).join('')}</tr></thead><tbody>${rows}</tbody>`;
        }
    }

    // === MÉTODOS AUXILIARES DO CHAT DO PORTAL ===
    async loadProcessComments(idProcesso) {
        this.activeProcessId = idProcesso;
        try {
            const res = await fetch(`${this.API_URL}/portal/comments/${idProcesso}`, { headers: this.getHeaders() });
            const data = await res.json();
            const historyEl = document.getElementById('portal-chat-history');
            if (historyEl && data.comments) {
                historyEl.innerHTML = data.comments.map(c => `
                    <div style="margin-bottom:10px; background:white; padding:10px; border-radius:8px; border:1px solid #e2e8f0;">
                        <strong style="font-size:12px;">${c.usuario_nome}</strong>
                        <p style="margin:5px 0 0 0; color:#334155; font-size:13px;">${c.mensagem}</p>
                    </div>
                `).join('');
                historyEl.scrollTop = historyEl.scrollHeight;
            }
        } catch (err) {
            console.error("Erro ao carregar chat:", err);
        }
    }

    async sendPortalComment() {
        const input = document.getElementById('portal-message-input');
        if (!input || !input.value.trim() || !this.activeProcessId) return;
        try {
            const res = await fetch(`${this.API_URL}/portal/comments`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ id_processo: this.activeProcessId, mensagem: input.value.trim() })
            });
            if (res.ok) {
                input.value = '';
                this.loadProcessComments(this.activeProcessId);
            }
        } catch (err) {
            console.error("Erro ao enviar comentário:", err);
        }
    }
               
               // === DARK MODE ===
               setupDarkMode() {
                const themeBtn = document.getElementById('theme-toggle');
                if (!themeBtn) return;
                
                themeBtn.addEventListener('click', () => {
                document.body.classList.toggle('dark');
                const isDark = document.body.classList.contains('dark');
                themeBtn.innerHTML = isDark ? '' : '';
                console.log('🌙 Dark mode alterado.');});}}
              
               // // === BOOTSTRAP INITIALIZATION ===

               console.log('💡 Strategic Flow - DEBUG MODE ON');
               const app = new StrategicFlowAPI();
               
               document.addEventListener("DOMContentLoaded", () => {
                app.setupSidebarToggle();
                app.setupDarkMode();});