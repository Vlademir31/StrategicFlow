/**
 * Strategic Flow - Menu Funcional + API com DEBUG + FALLBACK
 */

class StrategicFlowAPI {
    constructor() {
        this.API_URL = 'http://localhost:8001/api';
        this.WS_URL = 'ws://localhost:8001/ws/kpis';
        
        this.kpis = { cycleTime: null, otif: null, efficiency: null, rejection: null, roi: null, success: null, nps: null, throughput: null };
        this.ws = null;
        this.chart = null;
        this.restInterval = null;
        
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

    // === NAVIGATION (ACES S PAGES) ===
    setupNavigation() {
        console.log('📍 Configurando navegação...');
        
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                const section = item.dataset.section;
                if (!section) return;
                
                console.log(`📍 Navigation to: ${section}`);
                
                // Remove active de todos
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                
                // Add active no item clicado
                item.classList.add('active');
                
                // Mostra section
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
        console.log('🎛️ Configurando menu colapsável...');
        
        document.querySelectorAll('.category-header').forEach(header => {
            header.addEventListener('click', (e) => {
                e.preventDefault();
                
                const category = header.parentElement;
                const isOpen = category.classList.contains('open');
                
                // Fecha todos
                document.querySelectorAll('.menu-category').forEach(cat => {
                    cat.classList.remove('open');
                });
                
                // Se não estava aberto, abre este
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
                console.log('🔄 Sidebar: ' + (sidebar.classList.contains('collapsed') ? 'colapsada' : 'expandida'));
            });
        }
    }

    // === WEBSOCKET ===
    connectWebSocket() {
        console.log('🔌 Tentando conectar WebSocket:', this.WS_URL);
        
        try {
            this.ws = new WebSocket(this.WS_URL);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket CONECTADO!');
                this.updateStatus('connected', 'WebSocket Conectado');
                this.fetchAllData();
            };
            
            this.ws.onmessage = (e) => {
                console.log('📡 WebSocket mensagem:', e.data);
                try {
                    const data = JSON.parse(e.data);
                    this.updateKPIs(data);
                } catch (error) {
                    console.error('Erro parsing WebSocket:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket ERROR:', error);
                this.updateStatus('disconnected', 'WebSocket Falhou - usando REST');
                this.startRESTFallback();
            };
            
            this.ws.onclose = () => {
                console.log('❌ WebSocket CLOSE');
                this.updateStatus('disconnected', 'WebSocket Desconectado - usando REST');
                this.startRESTFallback();
            };
        } catch (error) {
            console.error('❌ WebSocket EXCEÇÃO:', error);
            this.updateStatus('disconnected', 'Erro WebSocket - usando REST');
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
        
        console.log(`📊 Status: ${status} - ${text}`);
    }

    startRESTFallback() {
        console.log('⚡ Iniciando REST fallback (30s polling)...');
        
        if (this.restInterval) clearInterval(this.restInterval);
        this.restInterval = setInterval(() => this.fetchKPIs(), 30000);
        this.fetchKPIs();
    }

    // === FETCH ALL DATA ===
    async fetchAllData() {
        console.log('📥 Fetching all data via WebSocket...');
        await this.fetchData('workflow-list', '/workflow');
        await this.fetchData('pdca-board', '/pdca');
        await this.fetchData('kaizen-board', '/kaizen');
        await this.fetchData('crm-table', '/crm');
        await this.fetchData('projects-table', '/projects');
    }

    async fetchData(elementId, endpoint) {
        try {
            console.log(`📥 Fetching ${endpoint}...`);
            const res = await fetch(`${this.API_URL}${endpoint}`);
            
            if (!res.ok) {
                console.error(`❌ API error ${endpoint}: ${res.status}`);
                return;
            }
            
            const data = await res.json();
            console.log(`✅ ${endpoint}:`, data);
            this.renderData(elementId, data);
        } catch (error) {
            console.error(`❌ Erro ${endpoint}:`, error);
        }
    }

    // === KPIs REST ===
    async fetchKPIs() {
        console.log('📥 Fetching KPIs via REST...');
        
        try {
            const res = await fetch(`${this.API_URL}/kpis`);
            
            if (!res.ok) {
                console.error(`❌ API error: ${res.status}`);
                this.useMockData();
                return;
            }
            
            const data = await res.json();
            console.log('✅ KPIs REST:', data);
            this.updateKPIs(data);
        } catch (error) {
            console.error('❌ Erro fetching KPIs:', error);
            this.useMockData();
        }
    }

    updateKPIs(data) {
        console.log('🔄 Updating KPIs DOM...');
        this.kpis = data;
        const now = new Date().toLocaleTimeString();
        
        Object.keys(data).forEach(kpi => {
            const el = document.getElementById(`kpi-${kpi}`);
            const trend = document.getElementById(`trend-${kpi}`);
            const realtime = document.getElementById(`realtime-${kpi}`);
            
            // Correção: usa kpi (chave) não `kpi-${kpi}`
            if (el && data[kpi]) {
                const value = data[kpi];
                el.textContent = kpi === 'throughput' || kpi === 'nps' ? 
                               value.toFixed(0) : 
                               value.toFixed(1) + (kpi === 'cycleTime' ? 'h' : '%');
                
                const target = this.getTarget(kpi);
                const trendValue = this.calcTrend(value, target, kpi === 'rejection');
                trend.textContent = trendValue;
                trend.className = `trend ${trendValue.includes('+') ? 'up' : 'down'}`;
                
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
        console.log('📊 Usando MOCK DATA (API não disponível)');
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

    // === CHART ===
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
        
        console.log('📊 Chart.js initialized');
    }

    updateChart() {
        if (!this.chart || !this.kpis.cycleTime) return;
        
        const now = new Date().toLocaleTimeString();
        
        if (this.chart.data.labels.length > 20) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach(d => d.data.shift());
        }
        
        this.chart.data.labels.push(now);
        this.chart.data.datasets[0].data.push(this.kpis.cycleTime);
        this.chart.data.datasets[1].data.push(this.kpis.otif);
        this.chart.data.datasets[2].data.push(this.kpis.efficiency);
        this.chart.update();
    }

    // === RENDER DATA ===
    renderData(elementId, data) {
        const el = document.getElementById(elementId);
        if (!el || !data || !data.length) return;
        
        console.log(`🎨 Rendering ${elementId}:`, data);
        
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
        } else if (elementId.includes('table')) {
            const headers = Object.keys(data[0]);
            const rows = data.map(r => `<tr>${headers.map(h => `<td>${r[h]}</td>`).join('')}</tr>`).join('');
            el.innerHTML = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows}</tbody>`;
        }
    }

    // === DARK MODE ===
    setupDarkMode() {
        const themeBtn = document.getElementById('theme-toggle');
        if (!themeBtn) return;
        
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark');
            const isDark = document.body.classList.contains('dark');
            themeBtn.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
            console.log('🌙 Dark mode: ' + (isDark ? 'ATIVO' : 'DESCATIVADO'));
        });
    }
}

// === INIT ===
console.log('💡 Strategic Flow - DEBUG MODE ON');
const app = new StrategicFlowAPI();

// === DARK MODE (DOMContentLoaded) ===
document.addEventListener("DOMContentLoaded", () => {
    app.setupSidebarToggle();
    app.setupDarkMode();
});