import asyncpg  # type: ignore
import asyncio
import logging
from typing import Optional, cast
from core.config import settings

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

_db_pool: Optional[asyncpg.Pool] = None


async def _create_system_tables(pool: asyncpg.Pool):
    """
    Cria todas as tabelas do sistema (originais + módulos) e faz o seed inicial.
    """
    query = """
    ------------------------------------------------------------
    --  TABELAS ORIGINAIS DO SISTEMA
    ------------------------------------------------------------

    CREATE TABLE IF NOT EXISTS kpis (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        name VARCHAR(50) NOT NULL,
        value NUMERIC(12, 4) NOT NULL,
        unit VARCHAR(10) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_kpis_tenant ON kpis(tenant_id);

    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        tenant_id VARCHAR(50) NOT NULL,
        role VARCHAR(30) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

    CREATE TABLE IF NOT EXISTS security_refresh_tokens (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        token VARCHAR(500) NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

   CREATE TABLE IF NOT EXISTS security_roles (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    permissions TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


    ------------------------------------------------------------
--  1. MÓDULO 5S
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS five_s_records (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL,
    seiri NUMERIC(5, 2) NOT NULL,
    seiton NUMERIC(5, 2) NOT NULL,
    seiso NUMERIC(5, 2) NOT NULL,
    seiketsu NUMERIC(5, 2) NOT NULL,
    shitsuke NUMERIC(5, 2) NOT NULL,
    auditor VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    score_total NUMERIC(5, 2) NOT NULL,
    audited_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_five_s_tenant ON five_s_records(tenant_id);

CREATE TABLE IF NOT EXISTS five_s_audits (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    department VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    auditor VARCHAR(100) NOT NULL,
    data_inicio TIMESTAMP WITH TIME ZONE NOT NULL,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


    ------------------------------------------------------------
--  2. MÓDULO KAIZEN
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS kaizen_records (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    departamento VARCHAR(100),
    processo_afetado VARCHAR(100),
    beneficio_esperado VARCHAR(200),
    ganho_financiero NUMERIC(12, 2),
    responsavel VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_kaizen_tenant ON kaizen_records(tenant_id);

    ------------------------------------------------------------
--  3. MÓDULO PDCA
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pdca_cycles (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    phase VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    departamento VARCHAR(100),
    processo_afetado VARCHAR(100),
    objetivo VARCHAR(200),
    meta VARCHAR(200),
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pdca_tenant ON pdca_cycles(tenant_id);

CREATE TABLE IF NOT EXISTS pdca_actions (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    pdca_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    fase VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    responsavel VARCHAR(100),
    data_planejada TIMESTAMP WITH TIME ZONE,
    data_realizada TIMESTAMP WITH TIME ZONE,
    prioridade VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
--  4. MÓDULO SIX SIGMA
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sixsigma_projects (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    phase VARCHAR(20) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    problem_statement TEXT NOT NULL,
    baseline_metric NUMERIC(12, 4) NOT NULL,
    target_metric NUMERIC(12, 4) NOT NULL,
    owner VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    departamento VARCHAR(100),
    processo_afetado VARCHAR(100),
    causa_root VARCHAR(200),
    solucao VARCHAR(200),
    beneficio_esperado NUMERIC(12, 2),
    beneficio_realizado NUMERIC(12, 2),
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sixsigma_tenant ON sixsigma_projects(tenant_id);

    ------------------------------------------------------------
--  5. MÓDULO VSM
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS vsm_records (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    process_name VARCHAR(200) NOT NULL,
    step_name VARCHAR(200) NOT NULL,
    step_type VARCHAR(20) NOT NULL,
    lane VARCHAR(100) NOT NULL,
    lead_time_hours NUMERIC(8, 2) NOT NULL,
    value_added BOOLEAN NOT NULL,
    waste_type VARCHAR(20),
    cicloTime NUMERIC(8, 2),
    takt_time NUMERIC(8, 2),
    setup_time NUMERIC(8, 2),
    uptime NUMERIC(5, 2),
    qualidade NUMERIC(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_vsm_tenant ON vsm_records(tenant_id);

CREATE TABLE IF NOT EXISTS vsm_maps (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    descricao TEXT,
    processo VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_by VARCHAR(100),
    data_criacao TIMESTAMP WITH TIME ZONE NOT NULL,
    data_atualizacao TIMESTAMP WITH TIME ZONE NOT NULL
);

   ------------------------------------------------------------
--  6. MÓDULO WORKFLOW
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS workflow_approvals (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    process_name VARCHAR(200) NOT NULL,
    requester VARCHAR(100) NOT NULL,
    approver VARCHAR(100) NOT NULL,
    level INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    sla_hours NUMERIC(8, 2),
    comment TEXT,
    data_aprovacao TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_workflow_tenant ON workflow_approvals(tenant_id);

CREATE TABLE IF NOT EXISTS workflow_processes (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    tipo VARCHAR(50) NOT NULL,
    status_atual VARCHAR(20) NOT NULL,
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

    ------------------------------------------------------------
--  7. MÓDULO BPMN
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bpmn_processes (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    version INT NOT NULL,
    xml_definition TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bpmn_tenant ON bpmn_processes(tenant_id);

CREATE TABLE IF NOT EXISTS bpmn_executions (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    process_id INT NOT NULL,
    process_version INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    case_id VARCHAR(100),
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


    ------------------------------------------------------------
--  8. MÓDULO AUDIT
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(20) NOT NULL,
    module VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    ip_address VARCHAR(50),
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_logs(tenant_id);

CREATE TABLE IF NOT EXISTS audit_findings (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    audit_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    risco_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    evidencia TEXT,
    responsavel VARCHAR(100),
    data_constatacao TIMESTAMP WITH TIME ZONE,
    data_correcao TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_ledger (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    finding_id INT NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    hash_data TEXT NOT NULL,
    criado_por VARCHAR(100),
    criado_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

    -----------------------------------------------------------
--  9. MÓDULO BI
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bi_reports (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    source_module VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'sql',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    cache_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    cache_ttl INT NOT NULL DEFAULT 300,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_executed TIMESTAMP WITH TIME ZONE,
    execution_count INT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bi_reports_tenant ON bi_reports(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bi_reports_source ON bi_reports(source_module);

CREATE TABLE IF NOT EXISTS bi_dashboards (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    widgets TEXT[],
    layout VARCHAR(20) NOT NULL DEFAULT 'grid',
    theme VARCHAR(20) NOT NULL DEFAULT 'light',
    public BOOLEAN NOT NULL DEFAULT FALSE,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bi_dashboards_tenant ON bi_dashboards(tenant_id);

CREATE TABLE IF NOT EXISTS bi_widgets (
    id SERIAL PRIMARY KEY,
    dashboard_id INT NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    query TEXT NOT NULL,
    query_params TEXT,
    cor VARCHAR(20),
    position_x INT NOT NULL DEFAULT 0,
    position_y INT NOT NULL DEFAULT 0,
    width INT NOT NULL DEFAULT 4,
    height INT NOT NULL DEFAULT 3,
    chart_type VARCHAR(20),
    cache_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    cache_ttl INT NOT NULL DEFAULT 300,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bi_widgets_dashboard ON bi_widgets(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_bi_widgets_tenant ON bi_widgets(tenant_id);

CREATE TABLE IF NOT EXISTS bi_powerbi_embeds (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    report_id INT NOT NULL,
    embed_token VARCHAR(500) NOT NULL,
    access_token VARCHAR(500) NOT NULL,
    report_url VARCHAR(500) NOT NULL,
    workspace_id VARCHAR(100) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    tenant_azure_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    refreshed_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_bi_powerbi_tenant ON bi_powerbi_embeds(tenant_id);

CREATE TABLE IF NOT EXISTS bi_etl_jobs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    report_id INT NOT NULL,
    job_name VARCHAR(200) NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    source_config TEXT NOT NULL,
    transformation TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    last_run TIMESTAMP WITH TIME ZONE,
    next_run TIMESTAMP WITH TIME ZONE,
    frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bi_etl_tenant ON bi_etl_jobs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bi_etl_report ON bi_etl_jobs(report_id);

CREATE TABLE IF NOT EXISTS bi_cache (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    key VARCHAR(200) NOT NULL,
    value TEXT NOT NULL,
    ttl INT NOT NULL DEFAULT 300,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bi_cache_tenant ON bi_cache(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bi_cache_key ON bi_cache(key);

CREATE TABLE IF NOT EXISTS bi_execution_logs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    report_id INT,
    widget_id INT,
    query TEXT NOT NULL,
    execution_time_ms FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    error TEXT,
    rows_returned INT NOT NULL DEFAULT 0,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_bi_logs_tenant ON bi_execution_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_bi_logs_report ON bi_execution_logs(report_id);
CREATE INDEX IF NOT EXISTS idx_bi_logs_executed ON bi_execution_logs(executed_at);

    ------------------------------------------------------------
--  10. MÓDULO CRM
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS crm_companies (
    id_empresa SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    razao_social VARCHAR(200) NOT NULL,
    nome_fantasia VARCHAR(200),
    cnpj VARCHAR(20),
    email VARCHAR(200),
    phone VARCHAR(50),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'ativo',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_crm_companies_tenant ON crm_companies(tenant_id);

CREATE TABLE IF NOT EXISTS crm_projects (
    id_projeto SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_empresa INT NOT NULL,
    nome_projeto VARCHAR(200) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'planejado',
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    owner VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_crm_projects_tenant ON crm_projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_crm_projects_empresa ON crm_projects(id_empresa);

   ------------------------------------------------------------
--  11. MÓDULO DIAGNOSTICS
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS project_diagnostics (
    id_diagnostico SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    pilar VARCHAR(50) NOT NULL,
    pontuacao NUMERIC(5,2) NOT NULL,
    observacoes TEXT,
    tipo VARCHAR(50),
    metodologia VARCHAR(100),
    tags TEXT[],
    status VARCHAR(50) NOT NULL DEFAULT 'pendente',
    data_inicio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP WITH TIME ZONE,
    criado_por VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_diagnostics_tenant ON project_diagnostics(tenant_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_projeto ON project_diagnostics(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_problemas (
    id_problema SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    id_diagnostico INT,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    etapa_processo VARCHAR(100),
    impacto_financeiro NUMERIC(10,2),
    impacto_tempo INT,
    status VARCHAR(50) NOT NULL DEFAULT 'pendente',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_problemas_tenant ON diagnostics_problemas(tenant_id);
CREATE INDEX IF NOT EXISTS idx_problemas_projeto ON diagnostics_problemas(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_matriz_gut (
    id_gut SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_problema INT NOT NULL,
    gravidade INT NOT NULL,
    urgencia INT NOT NULL,
    tendencia INT NOT NULL,
    pontuacao NUMERIC(5,2) NOT NULL,
    prioridade VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_gut_tenant ON diagnostics_matriz_gut(tenant_id);
CREATE INDEX IF NOT EXISTS idx_gut_problema ON diagnostics_matriz_gut(id_problema);

CREATE TABLE IF NOT EXISTS diagnostics_matriz_swot (
    id_swot SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    id_diagnostico INT,
    categoria VARCHAR(50) NOT NULL,
    elemento VARCHAR(200) NOT NULL,
    descricao TEXT,
    prioridade VARCHAR(50) NOT NULL DEFAULT 'media',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_swot_tenant ON diagnostics_matriz_swot(tenant_id);
CREATE INDEX IF NOT EXISTS idx_swot_projeto ON diagnostics_matriz_swot(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_ishikawa (
    id_ishikawa SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    id_diagnostico INT,
    problema TEXT NOT NULL,
    causa_1 TEXT NOT NULL,
    causa_2 TEXT NOT NULL,
    causa_3 TEXT NOT NULL,
    causa_4 TEXT NOT NULL,
    causa_5 TEXT,
    causa_raiz TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ishikawa_tenant ON diagnostics_ishikawa(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ishikawa_projeto ON diagnostics_ishikawa(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_mapeamento_asis (
    id_mapeamento SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    gatilho_inicial TEXT NOT NULL,
    entrega_final TEXT NOT NULL,
    fornecedores TEXT[],
    entradas TEXT[],
    passos TEXT[],
    saidas TEXT[],
    clientes TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_asis_tenant ON diagnostics_mapeamento_asis(tenant_id);
CREATE INDEX IF NOT EXISTS idx_asis_projeto ON diagnostics_mapeamento_asis(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_mapeamento_tobe (
    id_mapeamento SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    id_asis INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descricao TEXT,
    passos_ideal TEXT[],
    automatizacoes TEXT[],
    eliminacoes TEXT[],
    improvements TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_tobe_tenant ON diagnostics_mapeamento_tobe(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tobe_projeto ON diagnostics_mapeamento_tobe(id_projeto);

CREATE TABLE IF NOT EXISTS diagnostics_plano_acao (
    id_acao SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_projeto INT NOT NULL,
    id_problema INT NOT NULL,
    what TEXT NOT NULL,
    why TEXT NOT NULL,
    who TEXT NOT NULL,
    "when" TEXT NOT NULL,
    "where" TEXT NOT NULL,
    how TEXT NOT NULL,
    how_much NUMERIC(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pendente',
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_fim TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_acao_tenant ON diagnostics_plano_acao(tenant_id);
CREATE INDEX IF NOT EXISTS idx_acao_projeto ON diagnostics_plano_acao(id_projeto);

    ------------------------------------------------------------
--  12. MÓDULO WORKFORCE
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS workforce_consultants (
    id_consultor SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    nome VARCHAR(200) NOT NULL,
    cargo_senioridade VARCHAR(50) NOT NULL,
    hard_skills TEXT[],
    background_setorial TEXT[],
    custo_hora NUMERIC(10,2) NOT NULL,
    horas_uteis_mes INT NOT NULL DEFAULT 160,
    status_consultor VARCHAR(50) NOT NULL DEFAULT 'Ativo',
    email VARCHAR(200),
    phone VARCHAR(50),
    certifications TEXT[],
    foto_url VARCHAR(500),
    soft_skills TEXT[],
    grau_ingles VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(50),
    formacao VARCHAR(200),
    area_formacao VARCHAR(100),
    disponibilidade_viagem BOOLEAN NOT NULL DEFAULT FALSE,
    disponibilidade_home_office BOOLEAN NOT NULL DEFAULT TRUE,
    equipe VARCHAR(100),
    tags TEXT[],
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_workforce_consultants_tenant ON workforce_consultants(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workforce_consultants_status ON workforce_consultants(status_consultor);

CREATE TABLE IF NOT EXISTS workforce_allocations (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    id_consultor INT NOT NULL,
    id_projeto INT,
    status_disponibilidade VARCHAR(50) NOT NULL,
    porcentagem_dedicacao INT NOT NULL,
    horas_faturadas_mes INT NOT NULL,
    data_termino_prevista TIMESTAMP WITH TIME ZONE,
    data_inicio TIMESTAMP WITH TIME ZONE,
    notas TEXT,
    tipo_dedicacao VARCHAR(50),
    gestor_projeto VARCHAR(200),
    prioridade VARCHAR(50),
    turno VARCHAR(50),
    local_trabalho VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_workforce_allocations_tenant ON workforce_allocations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workforce_allocations_consultor ON workforce_allocations(id_consultor);

    ------------------------------------------------------------
--  13. MÓDULO REPORTS
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    content JSONB NOT NULL,
    formato VARCHAR(20) NOT NULL DEFAULT 'pdf',
    gerado_por VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'gerado',
    url_download VARCHAR(500),
    tamanho_bytes INT,
    views INT NOT NULL DEFAULT 0,
    last_viewed TIMESTAMP WITH TIME ZONE,
    projeto_id INT,
    cliente_id INT,
    parametros JSONB,
    intervalo_inicio TIMESTAMP WITH TIME ZONE,
    intervalo_fim TIMESTAMP WITH TIME ZONE,
    agendado BOOLEAN NOT NULL DEFAULT FALSE,
    agendamento_recorrencia VARCHAR(20),
    agendamento_horario VARCHAR(20),
    publico BOOLEAN NOT NULL DEFAULT FALSE,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_reports_tenant ON reports(tenant_id);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(type);
CREATE INDEX IF NOT EXISTS idx_reports_projeto ON reports(projeto_id);

   ------------------------------------------------------------
--  14. MÓDULO TEMPLATES
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS templates (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    tipo VARCHAR(20) NOT NULL DEFAULT 'texto',
    version INT NOT NULL DEFAULT 1,
    author VARCHAR(200),
    tags TEXT[],
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    variables TEXT[],
    exemplo TEXT,
    metadata JSONB,
    language VARCHAR(20) NOT NULL DEFAULT 'pt-BR',
    last_used TIMESTAMP WITH TIME ZONE,
    usages INT NOT NULL DEFAULT 0,
    template_relacionado INT,
    anexos TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_templates_tenant ON templates(tenant_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);

------------------------------------------------------------
--  15. MÓDULO INVENTORY
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    sku_name VARCHAR(200),
    quantity_available INT NOT NULL DEFAULT 0,
    quantity_reserved INT NOT NULL DEFAULT 0,
    location VARCHAR(100),
    class_ VARCHAR(5) NOT NULL DEFAULT 'B',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inventory_tenant ON inventory(tenant_id);
CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory(sku);

------------------------------------------------------------
--  SEED DE KPIs
------------------------------------------------------------

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'cycleTime', 19.5, 'h'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'cycleTime');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'otif', 96.2, '%'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'otif');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'efficiency', 92.4, '%'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'efficiency');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'rejection', 1.4, '%'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'rejection');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'roi', 245.0, '%'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'roi');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'success', 89.1, '%'
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'success');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'nps', 78.0, ''
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'nps');

INSERT INTO kpis (tenant_id, name, value, unit)
SELECT 'default-tenant', 'throughput', 1240.0, ''
WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'throughput');
    """
    logger.info("[DB] Todas as tabelas (originais + módulos) estruturadas.")

    # Use acquire context directly as a connection to satisfy type checkers
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query)


async def init_db(max_retries: int = 10, base_delay: float = 1.0) -> asyncpg.Pool:
    global _db_pool

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[DB] Tentando conectar ao PostgreSQL (tentativa {attempt}/{max_retries})...")
            # create_pool has a partially unknown return type in some type checkers;
            # cast explicitly to asyncpg.Pool to satisfy static type checkers
            _db_pool = cast(asyncpg.Pool, await asyncpg.create_pool(dsn=settings.DB_URL))

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


async def get_db() -> asyncpg.Pool:
    global _db_pool
    if _db_pool is None:
        await init_db()
    return _db_pool

async def close_db(pool: asyncpg.Pool):
    if pool:
        await pool.close()
        logger.info("[DB] Conexão fechada.")