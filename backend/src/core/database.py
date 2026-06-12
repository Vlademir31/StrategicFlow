import asyncpg
import asyncio
import logging
from core.config import settings

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

_db_pool = None

async def _create_system_tables(pool):
    """Cria de forma ordenada e automática todas as tabelas mapeadas do sistema."""
    query = """
    -- 1. TABELA DE KPIS (DASHBOARD)
    CREATE TABLE IF NOT EXISTS kpis (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL,
        value NUMERIC(12, 4) NOT NULL,
        unit VARCHAR(10) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_kpis_tenant ON kpis(tenant_id);

    -- Carga inicial para o Dashboard se estiver vazio
    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'Cycle Time', 19.5, 'h' 
    WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'Cycle Time');
    
    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'OTIF', 96.2, '%' 
    WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'OTIF');

    -- 2. CRM: EMPRESAS (ACCOUNTS)
    CREATE TABLE IF NOT EXISTS crm_companies (
        id_empresa SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        razao_social VARCHAR(150) NOT NULL,
        cnpj VARCHAR(20),
        segmento VARCHAR(100),
        porte_empresa VARCHAR(50),
        numero_funcionarios INT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_crm_comp_tenant ON crm_companies(tenant_id);

    -- Carga de Teste para Empresas do CRM se estiver vazio
    INSERT INTO crm_companies (tenant_id, razao_social, cnpj, segmento, porte_empresa, numero_funcionarios)
    SELECT 'default-tenant', 'Indústrias Alfa S.A.', '00.000.000/0001-00', 'Manufatura', 'Grande', 250
    WHERE NOT EXISTS (SELECT 1 FROM crm_companies);

    -- 3. CRM: CONTATOS (CONTACTS)
    CREATE TABLE IF NOT EXISTS crm_contacts (
        id_contato SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_empresa INT NOT NULL REFERENCES crm_companies(id_empresa) ON DELETE CASCADE,
        nome VARCHAR(100) NOT NULL,
        cargo VARCHAR(100),
        email VARCHAR(150),
        telefone_whatsapp VARCHAR(20),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_crm_cont_tenant ON crm_contacts(tenant_id);

    -- 4. CRM: OPORTUNIDADES / PROPOSTAS (OPPORTUNITIES / DEALS)
    CREATE TABLE IF NOT EXISTS crm_opportunities (
        id_oportunidade SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_empresa INT NOT NULL REFERENCES crm_companies(id_empresa) ON DELETE CASCADE,
        titulo_proposta VARCHAR(150) NOT NULL,
        valor_projeto NUMERIC(12, 2) DEFAULT 0.00,
        fase_pipeline VARCHAR(50) DEFAULT 'Diagnóstico',
        motivo_perda TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_crm_opp_tenant ON crm_opportunities(tenant_id);

    -- 5. CRM: PROJETOS (PROJECTS)
    CREATE TABLE IF NOT EXISTS crm_projects (
        id_projeto SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_empresa INT NOT NULL REFERENCES crm_companies(id_empresa) ON DELETE CASCADE,
        escopo_servico TEXT NOT NULL,
        status_projeto VARCHAR(50) DEFAULT 'Ativo',
        data_inicio DATE,
        data_fim DATE,
        valor_contratado NUMERIC(12, 2) DEFAULT 0.00,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_crm_proj_tenant ON crm_projects(tenant_id);

    -- 6. CRM: ENTREGÁVEIS / HORAS (DELIVERABLES / TIMESHEET)
    CREATE TABLE IF NOT EXISTS crm_deliverables (
        id_entregavel SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_projeto INT NOT NULL REFERENCES crm_projects(id_projeto) ON DELETE CASCADE,
        descricao_entrega TEXT NOT NULL,
        horas_estimadas NUMERIC(6, 2) DEFAULT 0.00,
        horas_realizadas NUMERIC(6, 2) DEFAULT 0.00,
        status_entrega VARCHAR(50) DEFAULT 'Pendente',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_crm_deliv_tenant ON crm_deliverables(tenant_id);

    -- 7. CRM: ATIVIDADES E INTERAÇÕES (ACTIVITIES)
    CREATE TABLE IF NOT EXISTS crm_activities (
        id_atividade SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_contato INT NOT NULL REFERENCES crm_contacts(id_contato) ON DELETE CASCADE,
        data_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        tipo_atividade VARCHAR(50) NOT NULL,
        descricao_resumo TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_crm_act_tenant ON crm_activities(tenant_id);

    -- 8. AUTENTICAÇÃO: USUÁRIOS GLOBAIS COM VÍNCULO DO PORTAL
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'consultant',
        id_empresa INT REFERENCES crm_companies(id_empresa) ON DELETE SET NULL,
        id_projeto INT REFERENCES crm_projects(id_projeto) ON DELETE SET NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_users_tenant_str ON users(tenant_id);

    -- 9. CLIENT PORTAL: PROCESSOS MAPEADOS (BPMN COZINHA)
    CREATE TABLE IF NOT EXISTS portal_mapped_processes (
        id_processo SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        nome_processo VARCHAR(150) NOT NULL,
        id_empresa INT NOT NULL REFERENCES crm_companies(id_empresa) ON DELETE CASCADE,
        id_projeto INT NOT NULL REFERENCES crm_projects(id_projeto) ON DELETE CASCADE,
        visivel_portal BOOLEAN DEFAULT FALSE,
        xml_bpmn TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_portal_proc_tenant ON portal_mapped_processes(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_portal_proc_security ON portal_mapped_processes(id_empresa, id_projeto, visivel_portal);

    -- 10. CLIENT PORTAL: COMENTÁRIOS COLABORATIVOS DO CHAT
    CREATE TABLE IF NOT EXISTS portal_comments (
        id_comentario SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_processo INT NOT NULL REFERENCES portal_mapped_processes(id_processo) ON DELETE CASCADE,
        usuario_email VARCHAR(150) NOT NULL,
        usuario_nome VARCHAR(100) NOT NULL,
        mensagem TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_portal_comments_proc ON portal_comments(id_processo);
    CREATE INDEX IF NOT EXISTS idx_portal_comments_tenant ON portal_comments(tenant_id);
   
        -- [Queries anteriores de KPIs, CRM, Usuários e Portal permanecem acima...]

    -- 11. WORKFORCE: CADASTRO DE TALENTOS & SKILLS (QUEM SÃO E O QUE SABEM)
    CREATE TABLE IF NOT EXISTS workforce_consultants (
        id_consultor SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        nome VARCHAR(100) NOT NULL,
        cargo_senioridade VARCHAR(50) NOT NULL, -- Trainee, Consultor, Senior, Diretor
        hard_skills TEXT[],                     -- Array do Postgres: {'Lean', 'PMP', 'Python'}
        background_setorial TEXT[],             -- Array do Postgres: {'Varejo', 'Logística'}
        custo_hora NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
        horas_uteis_mes INT DEFAULT 160,        -- Capacidade padrão total de horas
        status_consultor VARCHAR(30) DEFAULT 'Ativo'
    );
    CREATE INDEX IF NOT EXISTS idx_wf_cons_tenant ON workforce_consultants(tenant_id);

    -- 12. WORKFORCE: MATRIZ DE ALOCAÇÃO (ONDE ELES ESTÃO ATUALMENTE)
    CREATE TABLE IF NOT EXISTS workforce_allocations (
        id_alocacao SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_consultor INT NOT NULL REFERENCES workforce_consultants(id_consultor) ON DELETE CASCADE,
        id_projeto INT REFERENCES crm_projects(id_projeto) ON DELETE SET NULL,
        status_disponibilidade VARCHAR(30) DEFAULT 'Disponível', -- Disponível, Alocado, Férias
        porcentagem_dedicacao INT DEFAULT 100,                  -- Ex: 50 (para 50%)
        horas_faturadas_mes INT DEFAULT 0,                       -- Horas vendidas pro cliente
        data_termino_prevista DATE
    );
    CREATE INDEX IF NOT EXISTS idx_wf_alloc_cons ON workforce_allocations(id_consultor);

    -- 13. WORKFORCE: HISTÓRICO DE ENTREGAS E AVALIAÇÃO (O QUE JÁ ENTREGARAM)
    CREATE TABLE IF NOT EXISTS workforce_history (
        id_historico SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        id_consultor INT NOT NULL REFERENCES workforce_consultants(id_consultor) ON DELETE CASCADE,
        id_projeto INT NOT NULL REFERENCES crm_projects(id_projeto) ON DELETE CASCADE,
        nota_desempenho NUMERIC(3, 1), -- Nota de 1 a 5
        nps_interno INT,               -- NPS de 0 a 100 dado pelo cliente
        data_conclusao DATE DEFAULT CURRENT_DATE
    );
    CREATE INDEX IF NOT EXISTS idx_wf_hist_cons ON workforce_history(id_consultor);

    -- Carga de Teste para o novo modelo de Consultores
    INSERT INTO workforce_consultants (tenant_id, nome, cargo_senioridade, hard_skills, background_setorial, custo_hora)
    SELECT 'default-tenant', 'Juliana Sênior Lean', 'Senior', '{"Lean Six Sigma", "Mapeamento VSM"}', '{"Manufatura", "Logística"}', 120.00
    WHERE NOT EXISTS (SELECT 1 FROM workforce_consultants);
 """
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query)
            logger.info("[DB] Todas as tabelas (Dashboard, CRM, Users, Portal e Comentários) estruturadas.")

async def init_db(max_retries: int = 10, base_delay: float = 1.0):
    global _db_pool

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[DB] Tentando conectar ao PostgreSQL (tentativa {attempt}/{max_retries})...")
            _db_pool = await asyncpg.create_pool(dsn=settings.DB_URL)
            
            # ---> Executa a verificação e criação automatizada de todas as tabelas
            await _create_system_tables(_db_pool)
            
            logger.info("[DB] Conexão estabelecida com sucesso!")
            return _db_pool

        except Exception as e:
            wait_time = base_delay * (2 ** (attempt - 1))
            logger.error(f"[DB] Falha ao conectar: {e}")
            logger.info(f"[DB] Aguardando {wait_time:.1f}s antes de tentar novamente...")
            await asyncio.sleep(wait_time)

    logger.critical("[DB] Não foi possível conectar ao PostgreSQL após várias tentativas.")
    raise RuntimeError("Falha ao conectar ao banco de dados.")

async def get_db():
    global _db_pool
    if _db_pool is None:
        await init_db()
    return _db_pool
