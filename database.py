"""
Nexus Jr. | ERP Gestão & Finanças 2.0
Camada de Dados & Persistência SQLite (nexus_erp.db)
Controle de Acesso RBAC, Catálogo de Serviços, CPQ, Gantt com Mentores,
Gestão do Conhecimento com Versionamento, Timesheet Preditivo e DRE por Centro de Custo.
"""

import os
import sqlite3
import bcrypt
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "nexus_erp.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Usuários e RBAC
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        hashed_password TEXT NOT NULL,
        area TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('presidente', 'diretor', 'gerente', 'assessor')),
        cargo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Catálogo Oficial de Serviços Padronizados (16 Serviços nas 4 Macro-Frentes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS business_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        macro_area TEXT NOT NULL,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        lead_time_min_weeks INTEGER NOT NULL,
        lead_time_max_weeks INTEGER NOT NULL,
        default_hh INTEGER NOT NULL,
        recommended_seniority TEXT NOT NULL,
        hourly_rate REAL NOT NULL,
        description TEXT NOT NULL,
        deliverables TEXT NOT NULL,
        statutory_margin_pct REAL NOT NULL DEFAULT 0.15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Propostas Comerciais Geradas via CPQ
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cpq_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        service_name TEXT NOT NULL,
        macro_area TEXT NOT NULL,
        client_name TEXT NOT NULL,
        client_contact TEXT,
        seniority_level TEXT NOT NULL,
        horas_diagnostico INTEGER NOT NULL,
        horas_execucao INTEGER NOT NULL,
        total_hh INTEGER NOT NULL,
        hourly_rate REAL NOT NULL,
        risk_multiplier REAL NOT NULL DEFAULT 1.15,
        base_cost REAL NOT NULL,
        statutory_reinvestment REAL NOT NULL,
        total_price REAL NOT NULL,
        lead_time_weeks INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'proposta_gerada',
        notes TEXT,
        created_by TEXT NOT NULL DEFAULT 'Consultor Nexus Jr.',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES business_services(id)
    );
    """)

    # 4. Projetos Ativos e Cronogramas Gantt
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS business_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        client_name TEXT NOT NULL,
        service_name TEXT NOT NULL,
        macro_area TEXT NOT NULL,
        lead_time_weeks INTEGER NOT NULL,
        total_budgeted_hh INTEGER NOT NULL,
        consumed_hh REAL NOT NULL DEFAULT 0.0,
        progress_pct REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'em_andamento',
        start_date TEXT NOT NULL,
        expected_end_date TEXT NOT NULL,
        manager_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Marcos Técnicos e Travas de Segurança Estatutária (Orientadores/Mentores)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        phase_name TEXT NOT NULL,
        week_start INTEGER NOT NULL,
        week_end INTEGER NOT NULL,
        budgeted_hh INTEGER NOT NULL,
        consumed_hh REAL NOT NULL DEFAULT 0.0,
        progress_pct REAL NOT NULL DEFAULT 0.0,
        is_critical_path INTEGER NOT NULL DEFAULT 0,
        requires_mentor_approval INTEGER NOT NULL DEFAULT 0,
        mentor_approval_status TEXT NOT NULL DEFAULT 'nao_requerido',
        mentor_name TEXT,
        mentor_rubric TEXT,
        mentor_notes TEXT,
        approved_at TEXT,
        status TEXT NOT NULL DEFAULT 'pendente',
        FOREIGN KEY (project_id) REFERENCES business_projects(id)
    );
    """)

    # 6. Repositório de Ativos Intelectuais (com Controle de Versão e Ciclos de Turnover)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intellectual_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        macro_area TEXT NOT NULL,
        service_name TEXT NOT NULL,
        asset_code TEXT NOT NULL,
        title TEXT NOT NULL,
        file_format TEXT NOT NULL,
        version TEXT NOT NULL DEFAULT 'v1.0',
        version_notes TEXT,
        author_member TEXT NOT NULL,
        validator_mentor TEXT NOT NULL,
        turnover_cycle TEXT NOT NULL DEFAULT 'Ciclo 2026.1',
        download_url TEXT NOT NULL,
        file_size TEXT NOT NULL DEFAULT '1.2 MB',
        downloads_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Timesheet Diário com Alerta Preditivo de Scope Creep (Consumo >= 75%)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timesheet_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        milestone_id INTEGER,
        consultant_name TEXT NOT NULL,
        consultant_email TEXT NOT NULL,
        date TEXT NOT NULL,
        hours REAL NOT NULL,
        description TEXT NOT NULL,
        task_category TEXT NOT NULL DEFAULT 'Execução Técnica',
        scope_alert_triggered INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES business_projects(id)
    );
    """)

    # 8. DRE Gerencial Segmentada por Centro de Custo de Projetos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dre_project_cost_centers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        project_name TEXT NOT NULL,
        client_name TEXT NOT NULL,
        macro_area TEXT NOT NULL,
        periodo_fiscal TEXT NOT NULL DEFAULT '2026.1',
        receita_bruta REAL NOT NULL,
        impostos_deducoes REAL NOT NULL DEFAULT 0.0,
        receita_liquida REAL NOT NULL,
        custos_diretos_softwares REAL NOT NULL DEFAULT 0.0,
        custos_diretos_operacionais REAL NOT NULL DEFAULT 0.0,
        margem_contribuicao REAL NOT NULL,
        margem_contribuicao_pct REAL NOT NULL,
        despesas_operacionais_rateadas REAL NOT NULL DEFAULT 0.0,
        superavit_liquido REAL NOT NULL,
        reinvestimento_obrigatorio_pct REAL NOT NULL DEFAULT 1.0,
        fundo_reserva_capacitacao REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES business_projects(id)
    );
    """)

    # 9. Trilha Imutável de Auditoria (Audit Logs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT,
        details TEXT,
        ip_address TEXT DEFAULT '127.0.0.1',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 10. Feed de Atividades Operacionais em Tempo Real
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_name TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        action_type TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        project_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migrações seguras da tabela users (VPGG / Turnover / Centros de Custo)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN cost_center TEXT DEFAULT 'Presidência e Gestão Geral'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN turnover_cycle TEXT DEFAULT 'Ciclo 2026.1'")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'ativo'")
    except Exception:
        pass

    conn.commit()

    seed_users(conn)
    seed_services(conn)
    seed_projects(conn)
    seed_assets(conn)
    seed_timesheet_and_dre(conn)
    seed_activities(conn)
    migrate_cja_portfolio(conn)

    conn.close()
    print("[Nexus_ERP DB] Banco de dados nexus_erp.db inicializado com sucesso!")


def seed_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    default_pw = "edv2026!"
    hashed_pw = bcrypt.hashpw(default_pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    nexus_pw = bcrypt.hashpw("nexus2026!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    users_to_seed = [
        ("charles@nexusjr.com", "Charles", hashed_pw, "Presidência", "presidente", "Diretor Presidente", "Presidência e Gestão Geral", "Ciclo 2025.2 -> 2026.1", "ativo"),
        ("mariana.financas@nexusjr.com", "Mariana Souza", nexus_pw, "Finanças", "diretor", "Diretora de Finanças", "CC #1: Valuation Alpha", "Ciclo 2026.1", "ativo"),
        ("lucas.projetos@nexusjr.com", "Lucas Mendes", nexus_pw, "Projetos", "gerente", "Gerente de Projetos", "CC #2: Estruturação OBZ", "Ciclo 2026.1", "ativo"),
        ("beatriz.comercial@nexusjr.com", "Beatriz Lima", nexus_pw, "Comercial", "diretor", "Diretora Comercial", "Presidência e Gestão Geral", "Ciclo 2026.1", "ativo"),
        ("pedro.consultor@nexusjr.com", "Pedro Henrique Alves", nexus_pw, "Processos", "assessor", "Consultor Especialista BPMN", "CC #3: Otimização BPMN", "Ciclo 2026.1", "ativo"),
        ("ana.trainee@nexusjr.com", "Ana Clara Silveira", nexus_pw, "Gente e Gestão", "assessor", "Assessora VPGG", "Presidência e Gestão Geral", "Ciclo 2026.1", "ativo")
    ]

    for u in users_to_seed:
        cursor.execute("SELECT id FROM users WHERE email = ?", (u[0],))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("""
            INSERT INTO users (email, nome, hashed_password, area, role, cargo, cost_center, turnover_cycle, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, u)
    conn.commit()


def seed_activities(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM activity_logs")
    if cursor.fetchone()[0] > 0:
        return

    sample_activities = [
        ("Charles", "Diretor Presidente", "mentor_approval", "Chancela do Modelo FCD", "Marco 'Modelo Financeiro Preliminar' chancelado formalmente pelo Prof. Dr. Marcos Silveira (Finanças).", "Valuation e Modelagem Financeira (FCD)"),
        ("Sistema Nexus Engine", "Inteligência Operacional", "scope_alert", "Alerta Preditivo de Scope Creep", "Consumo de 38h de 45h (84,4%) atingido no marco 'Matrizes de Gastos e Pacotes' com apenas 50% de avanço.", "Estruturação de Orçamento Base Zero (OBZ)"),
        ("Lucas Mendes", "Gerente de Projetos", "timesheet", "Lançamento de Timesheet", "Apontamento de 5.0h dedicadas à consolidação dos pacotes orçamentários de compras.", "Estruturação de Orçamento Base Zero (OBZ)"),
        ("Beatriz Lima", "Diretora Comercial", "cpq_proposal", "Proposta Comercial Emitida via CPQ", "Proposta #1 gerada para Grupo Industrial Vix no valor de R$ 15.870,00 com 15% de margem estatutária.", "Valuation e Modelagem Financeira (FCD)"),
        ("Mariana Souza", "Diretora de Finanças", "finance", "Fechamento Mensal DRE por Centro de Custo", "Apurado superávit de R$ 33.950,00 com 100% destinado ao Fundo de Reserva Técnica (Lei 13.267).", "Consolidado Nexus Jr."),
        ("Ana Clara Silveira", "Assessora VPGG", "member_management", "Atualização Cadastral e Alocação", "Pedro Henrique Alves associado como consultor técnico líder no Centro de Custo #3 (Otimização BPMN).", "Gestão de Pessoas (VPGG)")
    ]

    for a in sample_activities:
        cursor.execute("""
        INSERT INTO activity_logs (actor_name, actor_role, action_type, title, description, project_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """, a)
    conn.commit()



def get_service_milestone_templates(service_name: str, total_hh: int = 100, lead_time_weeks: int = 10) -> List[Dict[str, Any]]:
    s_norm = (service_name or "").lower()

    if "processo" in s_norm or "mapeamento" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.3))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.6))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.85))
        return [
            {"phase_name": "Alinhamento e Mapeamento AS-IS dos Processos", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Identificação de Falhas Operacionais e Gargalos", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.35), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Modelagem TO-BE Otimizada (BPMN) & Validação Técnica", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Manualização de POPs e Apresentação de Resultados", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    elif "financeira" in s_norm or "finan" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.55))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.8))
        return [
            {"phase_name": "Diagnóstico Financeiro & Levantamento de Entradas/Saídas", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Estruturação de Contas e Conciliação Operacional", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.35), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Modelagem de Fluxo de Caixa & Parecer Financeiro", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Dashboard de Gestão de Caixa & Treinamento de Sócios", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    elif "contábil" in s_norm or "contabil" in s_norm:
        w_end1 = max(3, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.55))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.8))
        return [
            {"phase_name": "Auditoria Contábil Preliminar & Regularidade Fiscal", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Organização de Plano de Contas e Balancetes", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.35), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Revisão de Obrigações Acessórias com Trava Contábil", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Manual de Rotinas Fiscais & Calendário Tributário", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    elif "oculto" in s_norm or "cliente" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.3))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.7))
        return [
            {"phase_name": "Desenho dos Cenários e Roteiro de Avaliação PDV", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.30), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Execução de Campo / Visitas de Auditoria Oculta", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.40), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Análise Consolidada de Dados e Relatório com Trava de Mentor", "week_start": w_end2 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.30), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"}
        ]
    elif "satisfação" in s_norm or "satisfacao" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.35))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.7))
        return [
            {"phase_name": "Definição de Métricas (eNPS/CSAT) e Formulário de Pesquisa", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Disparo da Pesquisa e Engajamento da Base de Respondentes", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.35), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Relatório de Percepção, Retenção e Validação do Mentor", "week_start": w_end2 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.40), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"}
        ]
    elif "pesquisa de mercado" in s_norm or "mercado" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.6))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.85))
        return [
            {"phase_name": "Definição do Problema, Amostragem e Questionário", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.20), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Coleta de Campo Quali/Quanti e Tabulação", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.45), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Análise Estatística e Validação Metodológica de Amostra", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.20), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Relatório de Personas, Benchmarking e Apresentação", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    elif "negócios" in s_norm or "negocios" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.55))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.8))
        return [
            {"phase_name": "Concepção do Negócio e Análise Mercadológica", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.20), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Planejamento Operacional e Estruturação de Marketing", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.30), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Modelagem Econômico-Financeira (VPL, TIR, Payback) e Trava", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.35), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Sumário Executivo e Apresentação para Investidores", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    elif "marketing" in s_norm:
        w_end1 = max(2, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.6))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.85))
        return [
            {"phase_name": "Diagnóstico de Marca, Posicionamento e Benchmarking", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.20), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Estruturação dos 4 Ps e Estratégia de Atração/Conversão", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.40), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Planejamento de Mídia e Validação Estratégica com Mentor", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Cronograma Tático de Ações e Playbook de Comunicação", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.15), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]
    else:
        w_end1 = max(2, int(lead_time_weeks * 0.25))
        w_end2 = max(w_end1 + 1, int(lead_time_weeks * 0.6))
        w_end3 = max(w_end2 + 1, int(lead_time_weeks * 0.85))
        return [
            {"phase_name": "Diagnóstico Inicial e Alinhamento de Escopo", "week_start": 1, "week_end": w_end1, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "concluido"},
            {"phase_name": "Execução Técnica e Levantamento de Dados", "week_start": w_end1 + 1, "week_end": w_end2, "budgeted_hh": int(total_hh * 0.40), "is_critical_path": 1, "requires_mentor_approval": 0, "status": "em_andamento"},
            {"phase_name": "Elaboração de Entregáveis e Trava de Validação Técnica", "week_start": w_end2 + 1, "week_end": w_end3, "budgeted_hh": int(total_hh * 0.25), "is_critical_path": 1, "requires_mentor_approval": 1, "status": "pendente"},
            {"phase_name": "Apresentação Executiva e Entrega Final ao Cliente", "week_start": w_end3 + 1, "week_end": lead_time_weeks, "budgeted_hh": int(total_hh * 0.10), "is_critical_path": 0, "requires_mentor_approval": 0, "status": "pendente"}
        ]

def seed_services(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM business_services WHERE code LIKE 'CJA-%'")
    if cursor.fetchone()[0] == 8:
        return

    cursor.execute("DELETE FROM business_services")

    services = [
        # a) Gestão de Processos
        ("Gestão de Processos", "Mapeamento de Processos", "CJA-PRC-MAP", 6, 10, 80, "Consultor Pleno / Especialista", 85.00,
         "Foco em organização de operações, aumento de eficiência, identificação de falhas e gargalos.",
         "Mapeamento AS-IS e TO-BE em Notação BPMN, Matriz de Gargalos e Falhas, Manual de Procedimentos Operacionais (POPs) e Recomendações de Otimização."),

        # b) Finanças e Contabilidade
        ("Finanças e Contabilidade", "Consultoria Financeira", "CJA-FIN-CONS", 8, 12, 100, "Consultor Pleno / Especialista", 85.00,
         "Controle total da saúde financeira, análise de entradas/saídas e otimização de caixa.",
         "Diagnóstico Econômico-Financeiro, Estruturação de Fluxo de Caixa Diário/Mensal, Análise de Capital de Giro e Painel de Indicadores de Liquidez."),
        ("Finanças e Contabilidade", "Assessoria Contábil", "CJA-FIN-CONT", 12, 24, 120, "Consultor Pleno / Especialista", 85.00,
         "Simplificação de gestão contábil, declarações, obrigações acessórias e organização fiscal.",
         "Relatório de Conciliação e Regularidade Fiscal, Livro Caixa/Balancetes Gerenciais, Calendário de Obrigações Acessórias e Manual de Boas Práticas Fiscais."),

        # c) Inteligência de Mercado & Experiência do Cliente
        ("Inteligência de Mercado & Experiência do Cliente", "Cliente Oculto", "CJA-MKT-OCUL", 4, 8, 50, "Consultor Júnior", 55.00,
         "Análise estratégica de atendimento, processos e concorrência no ponto de venda.",
         "Roteiro de Auditoria Oculta, Avaliação de Atendimento por Dimensões, Relatório de Pontos Críticos e Plano de Melhoria da Experiência do Cliente."),
        ("Inteligência de Mercado & Experiência do Cliente", "Pesquisa de Mercado", "CJA-MKT-PESQ", 6, 10, 70, "Consultor Júnior", 55.00,
         "Análise de comportamento, público-alvo, demanda e mitigação de riscos de investimentos.",
         "Relatório Analítico de Mercado com Amostragem Estatística (95% IC), Mapeamento de Personas, Benchmarking Concorrencial e Matriz de Riscos."),
        ("Inteligência de Mercado & Experiência do Cliente", "Pesquisa de Satisfação", "CJA-MKT-SATIS", 4, 6, 40, "Consultor Júnior", 55.00,
         "Avaliação de percepção de clientes/colaboradores (eNPS/CSAT) para melhoria de retenção.",
         "Painel de Indicadores eNPS e CSAT, Diagnóstico de Percepção por Atributo, Análise de Feedbacks e Plano de Ação para Retenção de Clientes."),

        # d) Planejamento Estratégico & Marketing
        ("Planejamento Estratégico & Marketing", "Plano de Negócios", "CJA-EST-PLNEG", 8, 14, 110, "Gerente de Projetos", 120.00,
         "Estruturação de ideias, viabilidade econômica, análise de riscos e crescimento sustentável.",
         "Documento Completo de Plano de Negócios, Estudo de Viabilidade Econômico-Financeira (VPL, TIR, Payback), Plano Operacional e Sumário Executivo."),
        ("Planejamento Estratégico & Marketing", "Plano de Marketing", "CJA-EST-PLMKT", 6, 10, 90, "Consultor Pleno / Especialista", 85.00,
         "Estratégias de atração, conversão, retenção e posicionamento de marca.",
         "Diagnóstico de Branding e Posicionamento, Estratégia dos 4 Ps, Cronograma de Campanhas, Planejamento de Mídia e Funil de Vendas.")
    ]

    for s in services:
        cursor.execute("""
        INSERT INTO business_services (
            macro_area, name, code, lead_time_min_weeks, lead_time_max_weeks,
            default_hh, recommended_seniority, hourly_rate, description, deliverables, statutory_margin_pct
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0.15)
        """, s)
    conn.commit()


def seed_projects(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM business_projects")
    if cursor.fetchone()[0] > 0:
        return

    projects = [
        ("Mapeamento de Processos de Suprimentos", "TechInovação Software Ltda.", "Mapeamento de Processos", "Gestão de Processos",
         8, 80, 52.0, 65.0, "em_andamento", "2026-02-01", "2026-04-01", "Gabriel Martins"),
        ("Consultoria Financeira e Gestão de Caixa", "Vix Logística e Transportes S/A", "Consultoria Financeira", "Finanças e Contabilidade",
         10, 100, 38.0, 38.0, "em_andamento", "2026-02-15", "2026-05-10", "Lucas Rezende"),
        ("Auditoria de Atendimento e Cliente Oculto", "Rede Farmacêutica Capixaba", "Cliente Oculto", "Inteligência de Mercado & Experiência do Cliente",
         6, 50, 42.0, 84.0, "em_andamento", "2026-01-20", "2026-04-05", "Beatriz Andrade"),
        ("Estruturação de Plano de Negócios 2026", "Café Exportação Conilon", "Plano de Negócios", "Planejamento Estratégico & Marketing",
         10, 110, 45.0, 41.0, "em_andamento", "2026-02-10", "2026-04-10", "Charles (Presidente)")
    ]

    for p in projects:
        cursor.execute("""
        INSERT INTO business_projects (
            name, client_name, service_name, macro_area, lead_time_weeks,
            total_budgeted_hh, consumed_hh, progress_pct, status,
            start_date, expected_end_date, manager_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)
        proj_id = cursor.lastrowid
        service_name = p[2]
        lead_time = p[4]
        budgeted_hh = p[5]

        # Inserir marcos usando o template específico de cada serviço CJA
        m_list = get_service_milestone_templates(service_name, budgeted_hh, lead_time)
        for idx, m in enumerate(m_list):
            m_status = "pendente"
            m_approval = "nao_requerido"
            mentor_name = None
            mentor_rubric = None
            mentor_notes = None
            approved_at = None

            if m["requires_mentor_approval"]:
                m_approval = "pendente"
                mentor_notes = "Etapa crítica: Trava estatutária de mentor acadêmico requerida antes da entrega final."
            if idx == 0:
                m_status = "concluido"
            elif idx == 1:
                m_status = "em_andamento"

            # Caso especial para demonstração do TechInovação com Scope Creep
            consumed = m["budgeted_hh"] * 0.95 if (proj_id == 1 and idx == 1) else (m["budgeted_hh"] if idx == 0 else 0.0)

            cursor.execute("""
            INSERT INTO project_milestones (
                project_id, phase_name, week_start, week_end, budgeted_hh,
                consumed_hh, progress_pct, is_critical_path, requires_mentor_approval,
                mentor_approval_status, mentor_name, mentor_rubric, mentor_notes, approved_at, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                proj_id, m["phase_name"], m["week_start"], m["week_end"], m["budgeted_hh"],
                consumed, (100.0 if idx == 0 else (60.0 if idx == 1 else 0.0)),
                m["is_critical_path"], m["requires_mentor_approval"], m_approval,
                mentor_name, mentor_rubric, mentor_notes, approved_at, m_status
            ))
    conn.commit()


def seed_assets(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM intellectual_assets WHERE asset_code LIKE 'MOD-CJA-%'")
    if cursor.fetchone()[0] == 8:
        return

    cursor.execute("DELETE FROM intellectual_assets")

    assets = [
        ("Gestão de Processos", "Mapeamento de Processos", "MOD-CJA-PRC-01",
         "Manual de Mapeamento de Processos e Notação BPMN 2.0.pdf", ".pdf", "v3.0",
         "Padrão oficial CJA para mapeamento e modelagem AS-IS/TO-BE com piscinas, raias e eventos de tempo.",
         "Gabriel Martins (Consultor de Processos)", "Prof. Dra. Beatriz (Processos / Fucape)", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-PRC-01_BPMN_v3.0.pdf", "1.2 MB", 38),

        ("Finanças e Contabilidade", "Consultoria Financeira", "MOD-CJA-FIN-01",
         "Modelo de Diagnóstico Financeiro e Gestão de Caixa.xlsx", ".xlsx", "v4.1",
         "Planilha paramétrica com fluxo de caixa diário/mensal, conciliação e indicadores de liquidez e capital de giro.",
         "Lucas Rezende (Consultor Pleno)", "Prof. Dr. Marcos Silveira (Finanças / UFES)", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-FIN-01_Diagnostico_Caixa_v4.1.xlsx", "2.1 MB", 45),

        ("Finanças e Contabilidade", "Assessoria Contábil", "MOD-CJA-FIN-02",
         "Manual de Obrigações Acessórias e Assessoria Contábil.pdf", ".pdf", "v2.5",
         "Guia prático de rotinas fiscais preventivas, plano de contas gerencial e calendário de obrigações contábeis.",
         "Mariana Souza (Diretora de Finanças)", "Conselho Fiscal CJA Consultoria", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-FIN-02_Manual_Contabil_v2.5.pdf", "980 KB", 27),

        ("Inteligência de Mercado & Experiência do Cliente", "Cliente Oculto", "MOD-CJA-MKT-01",
         "Template de Relatório de Cliente Oculto.docx", ".docx", "v2.0",
         "Matriz de auditoria de atendimento no ponto de venda, roteiro de visitas e plano de ação corretiva.",
         "Camila Nogueira (Consultora de Mercado)", "Prof. Dr. Ricardo Ramos (Marketing)", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-MKT-01_Cliente_Oculto.docx", "850 KB", 31),

        ("Inteligência de Mercado & Experiência do Cliente", "Pesquisa de Mercado", "MOD-CJA-MKT-02",
         "Planilha de Dimensionamento de Pesquisa de Mercado.xlsx", ".xlsx", "v3.2",
         "Calculadora de amostragem probabilística (IC 95%), matriz de tabulação quanti/quali e análise de concorrência.",
         "Beatriz Lima (Diretora Comercial)", "Prof. Dr. Ricardo Ramos (Marketing)", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-MKT-02_Pesquisa_Mercado.xlsx", "1.7 MB", 42),

        ("Inteligência de Mercado & Experiência do Cliente", "Pesquisa de Satisfação", "MOD-CJA-MKT-03",
         "Instrumento de Pesquisa de Satisfação & Análise eNPS.xlsx", ".xlsx", "v2.1",
         "Régua de avaliação CSAT e eNPS com dashboards de promotores, neutros, detratores e plano de retenção.",
         "Camila Nogueira (Consultora de Mercado)", "Mentoria Alumni CJA", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-MKT-03_Pesquisa_Satisfacao.xlsx", "1.1 MB", 24),

        ("Planejamento Estratégico & Marketing", "Plano de Negócios", "MOD-CJA-EST-01",
         "Modelagem Financeira e Plano de Negócios CJA.xlsx", ".xlsx", "v5.0",
         "Estruturação de viabilidade econômica completa com DRE projetada, VPL, TIR, Payback e análise de cenários.",
         "Lucas Mendes (Gerente de Projetos)", "Prof. Dr. Marcos Silveira (Finanças)", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-EST-01_Plano_Negocios_v5.0.xlsx", "2.8 MB", 53),

        ("Planejamento Estratégico & Marketing", "Plano de Marketing", "MOD-CJA-EST-02",
         "Framework de Plano de Marketing.pptx", ".pptx", "v3.0",
         "Apresentação executiva completa com estratégia dos 4 Ps, funil de atração/conversão e cronograma de campanhas.",
         "Beatriz Lima (Diretora Comercial)", "Mentoria de Estratégia CJA", "Ciclo 2026.1",
         "/assets/templates/MOD-CJA-EST-02_Framework_Marketing.pptx", "3.4 MB", 39)
    ]

    for a in assets:
        cursor.execute("""
        INSERT INTO intellectual_assets (
            macro_area, service_name, asset_code, title, file_format,
            version, version_notes, author_member, validator_mentor,
            turnover_cycle, download_url, file_size, downloads_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, a)
    conn.commit()


def seed_timesheet_and_dre(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM timesheet_entries")
    if cursor.fetchone()[0] > 0:
        return

    timesheets = [
        (1, 1, "Gabriel Martins", "gabriel.martins@nexusjr.com.br", "2026-03-01", 8.0, "Entrevistas para mapeamento de processos AS-IS de suprimentos.", "Mapeamento", 0),
        (1, 2, "Gabriel Martins", "gabriel.martins@nexusjr.com.br", "2026-03-05", 9.0, "Detecção de gargalos no fluxo de compras e insumos.", "Diagnóstico", 1),
        (1, 2, "Camila Nogueira", "camila.nogueira@nexusjr.com.br", "2026-03-08", 7.5, "Reunião de alinhamento com diretores da TechInovação.", "Alinhamento", 1),
        (2, 5, "Lucas Rezende", "lucas.rezende@nexusjr.com.br", "2026-03-02", 8.0, "Auditoria e conciliação bancária de entradas e saídas da Vix Logística.", "Coleta de Dados", 0),
        (2, 6, "Lucas Rezende", "lucas.rezende@nexusjr.com.br", "2026-03-10", 7.0, "Estruturação das contas e análise do capital de giro operacional.", "Modelagem", 0),
        (3, 9, "Beatriz Andrade", "beatriz.andrade@nexusjr.com.br", "2026-03-04", 6.0, "Desenho da matriz de avaliação oculta e cenários de compra.", "Roteiro PDV", 0),
        (3, 10, "Beatriz Andrade", "beatriz.andrade@nexusjr.com.br", "2026-03-12", 8.5, "Visitas presenciais de cliente oculto em 4 filiais farmacêuticas.", "Campo", 0),
        (4, 13, "Charles", "charles@nexusjr.com", "2026-03-06", 8.0, "Pesquisa mercadológica e estruturação do plano de expansão do Café Conilon.", "Estratégia", 0)
    ]

    for t in timesheets:
        cursor.execute("""
        INSERT INTO timesheet_entries (
            project_id, milestone_id, consultant_name, consultant_email,
            date, hours, description, task_category, scope_alert_triggered
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, t)

    dre_entries = [
        (1, "Mapeamento de Processos de Suprimentos", "TechInovação Software Ltda.", "Gestão de Processos",
         7800.00, 0.0, 7800.00, 390.00, 156.00, 7254.00, 93.0, 780.00, 6474.00, 1.0, 6474.00),
        (2, "Consultoria Financeira e Gestão de Caixa", "Vix Logística e Transportes S/A", "Finanças e Contabilidade",
         13500.00, 0.0, 13500.00, 675.00, 270.00, 12555.00, 93.0, 1350.00, 11205.00, 1.0, 11205.00),
        (3, "Auditoria de Atendimento e Cliente Oculto", "Rede Farmacêutica Capixaba", "Inteligência de Mercado & Experiência do Cliente",
         6200.00, 0.0, 6200.00, 310.00, 124.00, 5766.00, 93.0, 620.00, 5146.00, 1.0, 5146.00),
        (4, "Estruturação de Plano de Negócios 2026", "Café Exportação Conilon", "Planejamento Estratégico & Marketing",
         14400.00, 0.0, 14400.00, 720.00, 288.00, 13392.00, 93.0, 1440.00, 11952.00, 1.0, 11952.00)
    ]

    for d in dre_entries:
        cursor.execute("""
        INSERT INTO dre_project_cost_centers (
            project_id, project_name, client_name, macro_area,
            receita_bruta, impostos_deducoes, receita_liquida,
            custos_diretos_softwares, custos_diretos_operacionais,
            margem_contribuicao, margem_contribuicao_pct,
            despesas_operacionais_rateadas, superavit_liquido,
            reinvestimento_obrigatorio_pct, fundo_reserva_capacitacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, d)
    conn.commit()


def migrate_cja_portfolio(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM business_services WHERE code LIKE 'CJA-%'")
    count = cursor.fetchone()[0]
    if count == 8:
        return

    print("[Nexus_ERP DB] Migrando portfólio oficial para os 8 serviços da CJA - Consultoria Empresarial...")

    # 1. Atualizar serviços
    cursor.execute("DELETE FROM business_services")
    seed_services(conn)

    # 2. Atualizar ativos intelectuais
    cursor.execute("DELETE FROM intellectual_assets")
    seed_assets(conn)

    # 3. Atualizar projetos, marcos, timesheet e DRE para CJA
    cursor.execute("DELETE FROM project_milestones")
    cursor.execute("DELETE FROM timesheet_entries")
    cursor.execute("DELETE FROM dre_project_cost_centers")
    cursor.execute("DELETE FROM business_projects")
    seed_projects(conn)
    seed_timesheet_and_dre(conn)

    conn.commit()
    print("[Nexus_ERP DB] Migração CJA concluída com sucesso! 8 serviços, marcos e ativos parametrizados.")


# ==============================================================================
# QUERIES E SERVIÇOS
# ==============================================================================

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user["hashed_password"].encode("utf-8")):
        return dict(user)
    return None

def get_services_list(macro_area: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if macro_area and macro_area != "ALL":
        cursor.execute("SELECT * FROM business_services WHERE macro_area = ? ORDER BY name", (macro_area,))
    else:
        cursor.execute("SELECT * FROM business_services ORDER BY macro_area, name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def calculate_cpq_service(service_id: int, seniority: str = "Gerente de Projetos", horas_diag: int = 20, horas_exec: int = 80, risk_multiplier: float = 1.15, hourly_rate_override: Optional[float] = None, **kwargs):
    horas_diag = kwargs.get("horas_diagnostico", horas_diag)
    horas_exec = kwargs.get("horas_execucao", horas_exec)
    risk_multiplier = kwargs.get("risk_factor", risk_multiplier)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM business_services WHERE id = ?", (service_id,))
    service = cursor.fetchone()
    conn.close()

    taxas = {
        "Trainee / Assessor": 35.0,
        "Consultor Júnior": 55.0,
        "Consultor Pleno / Especialista": 85.0,
        "Gerente de Projetos": 120.0,
        "Diretor Executivo": 160.0
    }
    hourly_rate = hourly_rate_override or taxas.get(seniority, 85.0 if not service else service["hourly_rate"])
    service_name = service["name"] if service else "Consultoria em Gestão"
    macro_area = service["macro_area"] if service else "Finanças Corporativas"

    total_hh = horas_diag + horas_exec
    custo_base = total_hh * hourly_rate
    subtotal_risco = custo_base * risk_multiplier
    fundo_reinvestimento = subtotal_risco * 0.15 # 15% obrigatório Lei 13.267
    preco_final = subtotal_risco + fundo_reinvestimento

    return {
        "service_id": service_id,
        "service_name": service_name,
        "macro_area": macro_area,
        "seniority": seniority,
        "hourly_rate": hourly_rate,
        "horas_diagnostico": horas_diag,
        "horas_execucao": horas_exec,
        "total_hh": total_hh,
        "risk_multiplier": risk_multiplier,
        "custo_base": round(custo_base, 2),
        "fundo_reinvestimento_estatutario": round(fundo_reinvestimento, 2),
        "preco_sugerido": round(preco_final, 2),
        "lei_13267_compliance": True
    }

calculate_cpq = calculate_cpq_service


def get_projects_gantt_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM business_projects ORDER BY id ASC")
    projects = [dict(r) for r in cursor.fetchall()]

    for p in projects:
        cursor.execute("SELECT * FROM project_milestones WHERE project_id = ? ORDER BY week_start ASC", (p["id"],))
        milestones_list = []
        for m_row in cursor.fetchall():
            m_dict = dict(m_row)
            m_dict["title"] = m_dict["phase_name"]
            milestones_list.append(m_dict)
        p["milestones"] = milestones_list

        scope_creep = False
        scope_alerts = []
        for m in p["milestones"]:
            if m["budgeted_hh"] > 0:
                pct = (m["consumed_hh"] / m["budgeted_hh"]) * 100
                if pct >= 75.0 and m["progress_pct"] < 90.0:
                    scope_creep = True
                    scope_alerts.append({
                        "phase_name": m["phase_name"],
                        "budgeted_hh": m["budgeted_hh"],
                        "consumed_hh": m["consumed_hh"],
                        "consumption_pct": round(pct, 1),
                        "progress_pct": m["progress_pct"]
                    })
        p["scope_creep_alert"] = scope_creep
        p["scope_alerts"] = scope_alerts

    conn.close()
    return projects

get_projects_gantt = get_projects_gantt_data

def log_activity(actor_name: str, actor_role: str, action_type: str, title: str, description: str, project_name: Optional[str] = None):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO activity_logs (actor_name, actor_role, action_type, title, description, project_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (actor_name, actor_role, action_type, title, description, project_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[ActivityLog Error]:", e)
        return False

def get_activity_logs(limit: int = 30, action_type: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if action_type and action_type != "ALL":
        cursor.execute("SELECT * FROM activity_logs WHERE action_type = ? ORDER BY id DESC LIMIT ?", (action_type, limit))
    else:
        cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def approve_mentor_milestone(milestone_id: int, mentor_name: str, mentor_notes: str, rubric: str = "APROVADO-MEJ-2026"):
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    SELECT m.phase_name, p.name as project_name
    FROM project_milestones m
    JOIN business_projects p ON m.project_id = p.id
    WHERE m.id = ?
    """, (milestone_id,))
    m_info = cursor.fetchone()
    phase_name = m_info["phase_name"] if m_info else f"Marco #{milestone_id}"
    project_name = m_info["project_name"] if m_info else "Projeto Corporativo"

    cursor.execute("""
    UPDATE project_milestones
    SET mentor_approval_status = 'aprovado',
        mentor_name = ?,
        mentor_rubric = ?,
        mentor_notes = ?,
        approved_at = ?,
        status = 'concluido'
    WHERE id = ?
    """, (mentor_name, rubric, mentor_notes, now_str, milestone_id))
    conn.commit()
    conn.close()

    log_activity(
        actor_name=mentor_name,
        actor_role="Professor / Mentor Orientador",
        action_type="mentor_approval",
        title="Chancela Acadêmica de Marco Crítico",
        description=f"Entregável '{phase_name}' validado formalmente sob rubrica '{rubric}'.",
        project_name=project_name
    )

    return True

def get_assets_list(macro_area: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if macro_area and macro_area != "ALL":
        cursor.execute("SELECT * FROM intellectual_assets WHERE macro_area = ? ORDER BY id DESC", (macro_area,))
    else:
        cursor.execute("SELECT * FROM intellectual_assets ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def create_asset(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    macro_area = data.get("macro_area", "Finanças Corporativas")
    service_name = data.get("service_name", "Consultoria Geral")
    asset_code = data.get("asset_code") or f"MOD-{datetime.now().strftime('%y%m%d%H%M')}"
    title = data.get("title", "Novo Ativo")
    file_format = data.get("file_format", ".xlsx")
    version = data.get("version", "v1.0")
    version_notes = data.get("version_notes", "Versão inicial cadastrada no repositório.")
    author_member = data.get("author_member", "Consultor Nexus Jr.")
    validator_mentor = data.get("validator_mentor", "Prof. Orientador")
    turnover_cycle = data.get("turnover_cycle", "Ciclo 2026.1")
    download_url = data.get("download_url") or "/assets/templates/novo_ativo.xlsx"
    file_size = data.get("file_size", "1.5 MB")

    cursor.execute("""
    INSERT INTO intellectual_assets (
        macro_area, service_name, asset_code, title, file_format,
        version, version_notes, author_member, validator_mentor,
        turnover_cycle, download_url, file_size
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        macro_area, service_name, asset_code, title, file_format,
        version, version_notes, author_member, validator_mentor,
        turnover_cycle, download_url, file_size
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_activity(
        actor_name=author_member,
        actor_role="Gestão do Conhecimento",
        action_type="member_management",
        title="Novo Ativo Intelectual Cadastrado",
        description=f"Ativo '{title}' ({version}) cadastrado na área {macro_area}.",
        project_name=macro_area
    )
    return {"id": new_id, "title": title, "version": version, "macro_area": macro_area}

def update_asset(asset_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []
    for k in ["title", "macro_area", "service_name", "version", "version_notes", "turnover_cycle", "file_format", "download_url", "validator_mentor", "author_member"]:
        if k in data and data[k] is not None:
            fields.append(f"{k} = ?")
            values.append(data[k])

    if not fields:
        conn.close()
        return True

    values.append(asset_id)
    cursor.execute(f"UPDATE intellectual_assets SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("updated_by", "Diretoria de Conhecimento"),
        actor_role="Gestão do Conhecimento",
        action_type="member_management",
        title="Ativo Intelectual Atualizado",
        description=f"Ativo #{asset_id} atualizado com novas notas de versão/parâmetros.",
        project_name=data.get("macro_area")
    )
    return True

def delete_asset(asset_id: int, deleted_by: str = "Diretoria de Conhecimento"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title, macro_area FROM intellectual_assets WHERE id = ?", (asset_id,))
    row = cursor.fetchone()
    title = row["title"] if row else f"Ativo #{asset_id}"

    cursor.execute("DELETE FROM intellectual_assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Gestão do Conhecimento",
        action_type="member_management",
        title="Ativo Intelectual Removido",
        description=f"Ativo '{title}' removido da biblioteca.",
        project_name="Base de Conhecimento"
    )
    return True


def log_timesheet(project_id: int, milestone_id: int, consultant_name: str, consultant_email: str, date: str, hours: float, description: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM business_projects WHERE id = ?", (project_id,))
    p_row = cursor.fetchone()
    project_name = p_row["name"] if p_row else f"Projeto #{project_id}"

    phase_name = "Marco Geral"
    if milestone_id:
        cursor.execute("SELECT phase_name FROM project_milestones WHERE id = ?", (milestone_id,))
        m_row = cursor.fetchone()
        if m_row:
            phase_name = m_row["phase_name"]

    cursor.execute("""
    INSERT INTO timesheet_entries (
        project_id, milestone_id, consultant_name, consultant_email, date, hours, description
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (project_id, milestone_id, consultant_name, consultant_email, date, hours, description))
    new_id = cursor.lastrowid

    cursor.execute("UPDATE business_projects SET consumed_hh = consumed_hh + ? WHERE id = ?", (hours, project_id))
    if milestone_id:
        cursor.execute("UPDATE project_milestones SET consumed_hh = consumed_hh + ? WHERE id = ?", (hours, milestone_id))

    scope_alert = False
    if milestone_id:
        cursor.execute("SELECT budgeted_hh, consumed_hh, progress_pct FROM project_milestones WHERE id = ?", (milestone_id,))
        m = cursor.fetchone()
        if m and m["budgeted_hh"] > 0:
            if (m["consumed_hh"] / m["budgeted_hh"]) >= 0.75 and m["progress_pct"] < 90.0:
                scope_alert = True
                cursor.execute("UPDATE timesheet_entries SET scope_alert_triggered = 1 WHERE id = ?", (new_id,))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=consultant_name,
        actor_role="Consultor de Projetos",
        action_type="timesheet",
        title="Lançamento de Horas no Timesheet",
        description=f"{hours:.1f}h apontadas no marco '{phase_name}'.",
        project_name=project_name
    )

    if scope_alert:
        log_activity(
            actor_name="Sistema Nexus Engine",
            actor_role="Inteligência Preditiva",
            action_type="scope_alert",
            title="Alerta Preditivo de Scope Creep",
            description=f"Consumo de horas atingiu patamar de risco (≥75%) no marco '{phase_name}'.",
            project_name=project_name
        )

    return {"success": True, "id": new_id, "scope_alert_triggered": scope_alert}

def get_dre_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dre_project_cost_centers ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]

    total_receita = sum(r["receita_bruta"] for r in rows)
    total_custos_diretos = sum(r["custos_diretos_softwares"] + r["custos_diretos_operacionais"] for r in rows)
    total_margem = sum(r["margem_contribuicao"] for r in rows)
    total_despesas_rateadas = sum(r["despesas_operacionais_rateadas"] for r in rows)
    total_superavit = sum(r["superavit_liquido"] for r in rows)

    conn.close()
    return {
        "projetos": rows,
        "consolidado": {
            "total_receita_bruta": round(total_receita, 2),
            "total_custos_diretos": round(total_custos_diretos, 2),
            "total_margem_contribuicao": round(total_margem, 2),
            "margem_contribuicao_media_pct": round((total_margem / total_receita * 100), 1) if total_receita else 0,
            "total_despesas_rateadas": round(total_despesas_rateadas, 2),
            "total_superavit_estatutario": round(total_superavit, 2),
            "reinvestimento_obrigatorio_pct": 100.0,
            "vedacao_distribuicao_lucro": True,
            "lei_13267_art2_art4": "Em estrita conformidade: R$ 0,00 de remuneração a membros, 100% reinvestido em capacitação."
        }
    }

def calculate_econometric_forecasting(params: Optional[dict] = None) -> dict:
    if params is None:
        params = {}

    horizon = int(params.get("horizon_months", 24))
    horizon = max(6, min(36, horizon))

    # Parâmetros de calibração macroeconômica
    growth_base_annual = float(params.get("growth_rate_annual_pct", 15.0)) / 100.0
    optimistic_bonus = float(params.get("optimistic_growth_bonus_pct", 20.0)) / 100.0
    pessimistic_penalty = float(params.get("pessimistic_growth_penalty_pct", 15.0)) / 100.0

    inflation_annual = float(params.get("inflation_annual_pct", 5.5)) / 100.0
    cost_containment = float(params.get("cost_containment_bonus_pct", 5.0)) / 100.0
    cost_pressure = float(params.get("pessimistic_inflation_penalty_pct", 6.0)) / 100.0

    seasonality_alpha = float(params.get("seasonality_intensity", 0.25))
    initial_cash = float(params.get("initial_cash_balance", 45000.0))

    # Obter baseline da DRE atual e projetos
    dre = get_dre_data()
    consolidado = dre["consolidado"]
    total_rec = consolidado["total_receita_bruta"]
    total_custos = consolidado["total_custos_diretos"] + consolidado["total_despesas_rateadas"]

    # Taxa mensal base (considerando ciclo de 4 meses operacionais)
    base_monthly_revenue = max(8000.0, total_rec / 4.0)
    base_monthly_cost = max(2000.0, total_custos / 4.0)

    # Pesos sazonais históricos do Movimento Empresa Júnior (MEJ) no Brasil
    raw_seasonality = {
        1: 0.70,   # Jan: Férias acadêmicas / recesso
        2: 0.85,   # Fev: Retorno de aulas / prospecção inicial
        3: 1.15,   # Mar: Pico de prospecção e fechamento 1º sem
        4: 1.25,   # Abr: Execução em alta velocidade
        5: 1.20,   # Mai: Entregas e aditivos
        6: 1.05,   # Jun: Fechamento de ciclo 1
        7: 0.75,   # Jul: Recesso de meio de ano / transição de diretoria
        8: 1.15,   # Ago: Reinício forte 2º sem
        9: 1.25,   # Set: Pico de vendas 2º sem
        10: 1.20,  # Out: Faturamento e entregas
        11: 1.15,  # Nov: Batimento de metas anuais / PE
        12: 0.80   # Dez: Fechamento contábil e recesso
    }

    def get_seasonality_factor(month_num: int) -> float:
        raw_val = raw_seasonality.get(month_num, 1.0)
        return 1.0 + (raw_val - 1.0) * (seasonality_alpha / 0.25)

    # Taxas mensais compostas
    g_base_mo = (1.0 + growth_base_annual) ** (1.0 / 12.0) - 1.0
    inf_base_mo = (1.0 + inflation_annual) ** (1.0 / 12.0) - 1.0

    g_opt_mo = (1.0 + (growth_base_annual + optimistic_bonus)) ** (1.0 / 12.0) - 1.0
    inf_opt_mo = max(0.0, (1.0 + (inflation_annual - cost_containment)) ** (1.0 / 12.0) - 1.0)

    g_pess_mo = (1.0 + (growth_base_annual - pessimistic_penalty)) ** (1.0 / 12.0) - 1.0
    inf_pess_mo = (1.0 + (inflation_annual + cost_pressure)) ** (1.0 / 12.0) - 1.0

    start_year = 2026
    start_month = 11

    month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    labels = []
    series_base = {"receita": [], "custos": [], "fluxo_liquido": [], "saldo_acumulado": [], "reinvestimento": []}
    series_opt = {"receita": [], "custos": [], "fluxo_liquido": [], "saldo_acumulado": [], "reinvestimento": []}
    series_pess = {"receita": [], "custos": [], "fluxo_liquido": [], "saldo_acumulado": [], "reinvestimento": []}

    cash_base = initial_cash
    cash_opt = initial_cash
    cash_pess = initial_cash

    for i in range(horizon):
        curr_m_idx = (start_month - 1 + i) % 12
        curr_year = start_year + ((start_month - 1 + i) // 12)
        month_label = f"{month_names[curr_m_idx]}/{str(curr_year)[2:]}"
        labels.append(month_label)

        s_factor = get_seasonality_factor(curr_m_idx + 1)

        # 1. BASE
        rec_b = base_monthly_revenue * ((1.0 + g_base_mo) ** (i + 1)) * s_factor
        custo_b = base_monthly_cost * ((1.0 + inf_base_mo) ** (i + 1)) * (1.0 + 0.25 * (s_factor - 1.0))
        fluxo_b = rec_b - custo_b
        reinvest_b = max(0.0, fluxo_b)
        cash_base += fluxo_b

        series_base["receita"].append(round(rec_b, 2))
        series_base["custos"].append(round(custo_b, 2))
        series_base["fluxo_liquido"].append(round(fluxo_b, 2))
        series_base["reinvestimento"].append(round(reinvest_b, 2))
        series_base["saldo_acumulado"].append(round(cash_base, 2))

        # 2. OTIMISTA (+5% prêmio valuation/ticket médio)
        rec_o = (base_monthly_revenue * 1.05) * ((1.0 + g_opt_mo) ** (i + 1)) * s_factor
        custo_o = base_monthly_cost * ((1.0 + inf_opt_mo) ** (i + 1)) * (1.0 + 0.20 * (s_factor - 1.0))
        fluxo_o = rec_o - custo_o
        reinvest_o = max(0.0, fluxo_o)
        cash_opt += fluxo_o

        series_opt["receita"].append(round(rec_o, 2))
        series_opt["custos"].append(round(custo_o, 2))
        series_opt["fluxo_liquido"].append(round(fluxo_o, 2))
        series_opt["reinvestimento"].append(round(reinvest_o, 2))
        series_opt["saldo_acumulado"].append(round(cash_opt, 2))

        # 3. PESSIMISTA (-5% desconto por pressão de mercado)
        rec_p = (base_monthly_revenue * 0.95) * ((1.0 + g_pess_mo) ** (i + 1)) * s_factor
        custo_p = base_monthly_cost * ((1.0 + inf_pess_mo) ** (i + 1)) * (1.0 + 0.30 * (s_factor - 1.0))
        fluxo_p = rec_p - custo_p
        reinvest_p = max(0.0, fluxo_p)
        cash_pess += fluxo_p

        series_pess["receita"].append(round(rec_p, 2))
        series_pess["custos"].append(round(custo_p, 2))
        series_pess["fluxo_liquido"].append(round(fluxo_p, 2))
        series_pess["reinvestimento"].append(round(reinvest_p, 2))
        series_pess["saldo_acumulado"].append(round(cash_pess, 2))

    def build_summary(series, final_cash):
        tot_rec = sum(series["receita"])
        tot_custo = sum(series["custos"])
        tot_superavit = sum(series["fluxo_liquido"])
        min_cash = min(series["saldo_acumulado"])
        deficit_months = sum(1 for c in series["saldo_acumulado"] if c < initial_cash * 0.5)
        avg_monthly_breakeven = tot_custo / horizon
        avg_contracts_breakeven = round(avg_monthly_breakeven / 10500.0, 2)

        return {
            "receita_total_projetada": round(tot_rec, 2),
            "custos_totais_projetados": round(tot_custo, 2),
            "superavit_estatutario_total": round(tot_superavit, 2),
            "margem_media_pct": round((tot_superavit / tot_rec * 100), 1) if tot_rec else 0,
            "saldo_final_tesouraria": round(final_cash, 2),
            "saldo_minimo_tesouraria": round(min_cash, 2),
            "meses_risco_caixa": deficit_months,
            "ponto_equilibrio_mensal": round(avg_monthly_breakeven, 2),
            "contratos_breakeven_mes": avg_contracts_breakeven,
            "probabilidade_superavit_positivo": 100.0 if min_cash > 0 else round(max(0, (1 - abs(min_cash)/initial_cash)*100), 1)
        }

    summary_base = build_summary(series_base, cash_base)
    summary_opt = build_summary(series_opt, cash_opt)
    summary_pess = build_summary(series_pess, cash_pess)

    current_runway_months = round(initial_cash / base_monthly_cost, 1)

    return {
        "premissas": {
            "horizon_months": horizon,
            "growth_rate_annual_pct": round(growth_base_annual * 100, 1),
            "optimistic_growth_bonus_pct": round(optimistic_bonus * 100, 1),
            "pessimistic_growth_penalty_pct": round(pessimistic_penalty * 100, 1),
            "inflation_annual_pct": round(inflation_annual * 100, 1),
            "cost_containment_bonus_pct": round(cost_containment * 100, 1),
            "pessimistic_inflation_penalty_pct": round(cost_pressure * 100, 1),
            "seasonality_intensity": seasonality_alpha,
            "initial_cash_balance": initial_cash,
            "base_monthly_revenue": round(base_monthly_revenue, 2),
            "base_monthly_cost": round(base_monthly_cost, 2),
            "runway_meses_sem_vendas": current_runway_months
        },
        "labels": labels,
        "cenarios": {
            "otimista": {
                "nome": "Cenário Otimista (Alta de Demanda & Eficiência)",
                "descricao": "Crescimento acelerado (+35% a.a.), prêmio em valuation e controle de despesas operacionais.",
                "cor_hex": "#059669",
                "dados": series_opt,
                "resumo": summary_opt
            },
            "base": {
                "nome": "Cenário Base (Tendência Linear Histórica)",
                "descricao": "Projeção consistente com a evolução orgânica da EJ (+15% a.a.) e inflação padrão.",
                "cor_hex": "#0b1d3a",
                "dados": series_base,
                "resumo": summary_base
            },
            "pessimista": {
                "nome": "Cenário Pessimista (Estagnação & Pressão de Custos)",
                "descricao": "Estagnação contratual, descontos comerciais e pressão inflacionária de insumos/softwares.",
                "cor_hex": "#dc2626",
                "dados": series_pess,
                "resumo": summary_pess
            }
        },
        "compliance_estatutario": {
            "lei_13267_artigo": "Lei Federal nº 13.267/2016",
            "vedacao_distribuicao_lucro": True,
            "reinvestimento_capacitacao_pct": 100.0,
            "superavit_projetado_reinvestido_base": summary_base["superavit_estatutario_total"],
            "parecer": "100% dos superávits financeiros gerados nos 3 cenários são direcionados por lei para reinvestimento em educação e infraestrutura dos membros."
        }
    }

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, nome, area, role, cargo, cost_center, turnover_cycle, status, created_at FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_proposal(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    service_id = data.get("service_id")
    seniority = data.get("seniority", "Gerente de Projetos")
    horas_diag = data.get("horas_diagnostico", 20)
    horas_exec = data.get("horas_execucao", 80)
    risk_factor = data.get("risk_factor", 1.15)

    cursor.execute("SELECT * FROM business_services WHERE id = ?", (service_id,))
    service = cursor.fetchone()

    service_name = service["name"] if service else "Consultoria Personalizada"
    macro_area = service["macro_area"] if service else "Finanças Corporativas"
    lead_time = service["lead_time_max_weeks"] if service else 10

    taxas = {
        "Trainee / Assessor": 35.0,
        "Consultor Júnior": 55.0,
        "Consultor Pleno / Especialista": 85.0,
        "Gerente de Projetos": 120.0,
        "Diretor Executivo": 160.0
    }
    hourly_rate = data.get("hourly_rate_override") or taxas.get(seniority, 85.0)
    total_hh = horas_diag + horas_exec
    base_cost = total_hh * hourly_rate
    subtotal_risco = base_cost * risk_factor
    statutory_reinvestment = subtotal_risco * 0.15
    total_price = subtotal_risco + statutory_reinvestment

    client_name = data.get("client_name", "Cliente")
    created_by = data.get("created_by", "Consultor Nexus Jr.")

    cursor.execute("""
    INSERT INTO cpq_proposals (
        service_id, service_name, macro_area, client_name, client_contact,
        seniority_level, horas_diagnostico, horas_execucao, total_hh,
        hourly_rate, risk_multiplier, base_cost, statutory_reinvestment,
        total_price, lead_time_weeks, status, notes, created_by
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'proposta_gerada', ?, ?)
    """, (
        service_id, service_name, macro_area, client_name, data.get("client_contact", ""),
        seniority, horas_diag, horas_exec, total_hh, hourly_rate, risk_factor,
        round(base_cost, 2), round(statutory_reinvestment, 2), round(total_price, 2),
        lead_time, data.get("notes", ""), created_by
    ))
    proposal_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_activity(
        actor_name=created_by,
        actor_role="Área Comercial",
        action_type="cpq_proposal",
        title="Nova Proposta Comercial Gerada",
        description=f"Cotação #{proposal_id} emitida para '{client_name}' no valor de R$ {total_price:,.2f} ({total_hh}h / {service_name}).",
        project_name=service_name
    )

    return {
        "id": proposal_id,
        "service_name": service_name,
        "client_name": client_name,
        "total_price": round(total_price, 2),
        "statutory_reinvestment": round(statutory_reinvestment, 2),
        "total_hh": total_hh,
        "lead_time_weeks": lead_time,
        "status": "proposta_gerada"
    }

def get_proposals_list():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cpq_proposals ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

# ==============================================================================
# GESTÃO DE MEMBROS E EQUIPA (PAINEL VPGG / RBAC)
# ==============================================================================

def get_members_list(area: Optional[str] = None, role: Optional[str] = None, status: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, email, nome, area, role, cargo, cost_center, turnover_cycle, status, created_at FROM users WHERE 1=1"
    params = []
    if area and area != "ALL":
        query += " AND area = ?"
        params.append(area)
    if role and role != "ALL":
        query += " AND role = ?"
        params.append(role)
    if status and status != "ALL":
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY CASE role WHEN 'presidente' THEN 1 WHEN 'diretor' THEN 2 WHEN 'gerente' THEN 3 ELSE 4 END, nome ASC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def create_member(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    email = data.get("email", "").strip().lower()
    nome = data.get("nome", "").strip()
    area = data.get("area", "Projetos")
    role = data.get("role", "assessor").lower()
    cargo = data.get("cargo", "Consultor Júnior")
    cost_center = data.get("cost_center", "Presidência e Gestão Geral")
    turnover_cycle = data.get("turnover_cycle", "Ciclo 2026.1")
    member_status = data.get("status", "ativo")

    password = data.get("password") or "nexus2026!"
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute("""
    INSERT INTO users (email, nome, hashed_password, area, role, cargo, cost_center, turnover_cycle, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, nome, hashed_pw, area, role, cargo, cost_center, turnover_cycle, member_status))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("created_by_name", "Diretoria VPGG"),
        actor_role="Gente e Gestão",
        action_type="member_management",
        title="Novo Membro Integrado",
        description=f"{nome} cadastrado como {cargo} ({area}) alocado no {cost_center}.",
        project_name=cost_center
    )

    return get_user_by_id(new_id)

def update_member(member_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []

    for key in ["nome", "area", "role", "cargo", "cost_center", "turnover_cycle", "status"]:
        if key in data and data[key] is not None:
            fields.append(f"{key} = ?")
            values.append(data[key])

    if "password" in data and data["password"]:
        hashed_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        fields.append("hashed_password = ?")
        values.append(hashed_pw)

    if not fields:
        conn.close()
        return get_user_by_id(member_id)

    values.append(member_id)
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("updated_by_name", "Diretoria VPGG"),
        actor_role="Gente e Gestão",
        action_type="member_management",
        title="Cadastro de Membro Atualizado",
        description=f"Atribuições e cargo do membro #{member_id} ({data.get('nome', '')}) foram atualizados.",
        project_name=data.get("cost_center")
    )

    return get_user_by_id(member_id)

def delete_member(member_id: int, deleted_by: str = "Diretoria VPGG"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cargo FROM users WHERE id = ?", (member_id,))
    u = cursor.fetchone()
    nome = u["nome"] if u else f"Membro #{member_id}"

    cursor.execute("UPDATE users SET status = 'desligado' WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Gente e Gestão",
        action_type="member_management",
        title="Membro Desligado / Registro de Turnover",
        description=f"Turnover registrado para {nome}. Histórico preservado para conformidade estatutária.",
        project_name="Gente e Gestão (VPGG)"
    )
    return True

def toggle_member_status(member_id: int, updated_by: str = "Diretoria VPGG"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, status FROM users WHERE id = ?", (member_id,))
    u = cursor.fetchone()
    if not u:
        conn.close()
        return None

    current = u["status"]
    new_status = "desligado" if current == "ativo" else "ativo"

    cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, member_id))
    conn.commit()
    conn.close()

    log_activity(
        actor_name=updated_by,
        actor_role="Gente e Gestão",
        action_type="member_management",
        title=f"Status de Membro: {new_status.capitalize()}",
        description=f"Status de {u['nome']} alterado para '{new_status}' (Ciclo VPGG).",
        project_name="Gente e Gestão (VPGG)"
    )
    return {"id": member_id, "status": new_status, "nome": u["nome"]}

# ==============================================================================
# 1. TRANSAÇÕES DE PROPOSTAS COMERCIAIS (CPQ)
# ==============================================================================
def update_proposal(proposal_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []
    for k in ["client_name", "client_contact", "status", "seniority_level", "horas_diagnostico", "horas_execucao", "total_hh", "hourly_rate", "risk_multiplier", "base_cost", "statutory_reinvestment", "total_price", "notes"]:
        if k in data and data[k] is not None:
            fields.append(f"{k} = ?")
            values.append(data[k])

    if not fields:
        conn.close()
        return True

    values.append(proposal_id)
    cursor.execute(f"UPDATE cpq_proposals SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("updated_by", "Consultor Comercial"),
        actor_role="Área Comercial",
        action_type="cpq_proposal",
        title="Proposta Comercial Atualizada",
        description=f"Proposta #{proposal_id} ({data.get('client_name', '')}) teve parâmetros revisados.",
        project_name="Pipeline CPQ"
    )
    return True

def update_proposal_status(proposal_id: int, status_str: str, updated_by: str = "Consultor Comercial"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT client_name, service_name, total_price FROM cpq_proposals WHERE id = ?", (proposal_id,))
    p = cursor.fetchone()
    client_name = p["client_name"] if p else f"Proposta #{proposal_id}"

    cursor.execute("UPDATE cpq_proposals SET status = ? WHERE id = ?", (status_str, proposal_id))
    conn.commit()
    conn.close()

    status_labels = {
        "proposta_gerada": "Gerada",
        "em_negociacao": "Em Negociação",
        "convertida": "Convertida em Contrato",
        "perdida": "Perdida"
    }
    label = status_labels.get(status_str, status_str)

    log_activity(
        actor_name=updated_by,
        actor_role="Área Comercial",
        action_type="cpq_proposal",
        title=f"Status da Proposta: {label}",
        description=f"Proposta comercial #{proposal_id} ({client_name}) marcada como '{label}'.",
        project_name="Pipeline CPQ"
    )
    return True

def delete_proposal(proposal_id: int, deleted_by: str = "Consultor Comercial"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT client_name FROM cpq_proposals WHERE id = ?", (proposal_id,))
    p = cursor.fetchone()
    client_name = p["client_name"] if p else f"Proposta #{proposal_id}"

    cursor.execute("DELETE FROM cpq_proposals WHERE id = ?", (proposal_id,))
    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Área Comercial",
        action_type="cpq_proposal",
        title="Proposta Comercial Excluída",
        description=f"Registro da proposta #{proposal_id} ({client_name}) foi excluído do histórico.",
        project_name="Pipeline CPQ"
    )
    return True

# ==============================================================================
# 2. TRANSAÇÕES DE PROJETOS E MARCOS GANTT
# ==============================================================================
def create_project(data: dict):
    conn = get_db()
    cursor = conn.cursor()

    name = data.get("name")
    client_name = data.get("client_name")
    service_name = data.get("service_name", "Consultoria em Gestão")
    macro_area = data.get("macro_area", "Finanças Corporativas")
    lead_time_weeks = int(data.get("lead_time_weeks", 10))
    total_budgeted_hh = int(data.get("total_budgeted_hh", 100))
    manager_name = data.get("manager_name", "Lucas Mendes")
    start_date = data.get("start_date") or datetime.now().strftime("%Y-%m-%d")
    expected_end_date = data.get("expected_end_date") or datetime.now().strftime("%Y-%m-%d")
    proj_status = data.get("status", "em_andamento")
    contract_value = float(data.get("contract_value", 12500.00))

    cursor.execute("""
    INSERT INTO business_projects (
        name, client_name, service_name, macro_area, lead_time_weeks,
        total_budgeted_hh, consumed_hh, progress_pct, status,
        start_date, expected_end_date, manager_name
    ) VALUES (?, ?, ?, ?, ?, ?, 0.0, 0.0, ?, ?, ?, ?)
    """, (
        name, client_name, service_name, macro_area, lead_time_weeks,
        total_budgeted_hh, proj_status, start_date, expected_end_date, manager_name
    ))
    new_project_id = cursor.lastrowid

    # Criar marcos parametrizados para o cronograma Gantt com base no template do serviço CJA
    milestone_templates = get_service_milestone_templates(service_name, total_budgeted_hh, lead_time_weeks)
    for m in milestone_templates:
        req_approval = m.get("requires_mentor_approval", 0)
        app_status = "pendente" if req_approval else "nao_requerido"
        cursor.execute("""
        INSERT INTO project_milestones (
            project_id, phase_name, week_start, week_end, budgeted_hh,
            consumed_hh, progress_pct, is_critical_path, requires_mentor_approval,
            mentor_approval_status, status
        ) VALUES (?, ?, ?, ?, ?, 0.0, 0.0, ?, ?, ?, ?)
        """, (
            new_project_id,
            m["phase_name"],
            m["week_start"],
            m["week_end"],
            m["budgeted_hh"],
            m.get("is_critical_path", 0),
            req_approval,
            app_status,
            m.get("status", "pendente")
        ))

    # Inserir também no Centro de Custo da DRE
    cursor.execute("""
    INSERT INTO dre_project_cost_centers (
        project_id, project_name, client_name, macro_area,
        receita_bruta, impostos_deducoes, receita_liquida,
        custos_diretos_softwares, custos_diretos_operacionais,
        margem_contribuicao, margem_contribuicao_pct,
        despesas_operacionais_rateadas, superavit_liquido,
        reinvestimento_obrigatorio_pct, fundo_reserva_capacitacao
    ) VALUES (?, ?, ?, ?, ?, 0.0, ?, ?, ?, ?, ?, ?, ?, 1.0, ?)
    """, (
        new_project_id, name, client_name, macro_area,
        contract_value, contract_value,
        round(contract_value * 0.05, 2), round(contract_value * 0.02, 2),
        round(contract_value * 0.93, 2), 93.0,
        round(contract_value * 0.10, 2), round(contract_value * 0.83, 2),
        round(contract_value * 0.83, 2)
    ))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=manager_name,
        actor_role="Gerência de Projetos",
        action_type="mentor_approval",
        title="Novo Projeto & Contrato Iniciado",
        description=f"Consultoria '{name}' iniciada para {client_name} ({lead_time_weeks} sem, {total_budgeted_hh}h orçadas).",
        project_name=name
    )
    return {"id": new_project_id, "name": name, "client_name": client_name}

def update_project(project_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []
    for k in ["name", "client_name", "manager_name", "status", "lead_time_weeks", "total_budgeted_hh", "start_date", "expected_end_date", "progress_pct"]:
        if k in data and data[k] is not None:
            fields.append(f"{k} = ?")
            values.append(data[k])

    if not fields:
        conn.close()
        return True

    values.append(project_id)
    cursor.execute(f"UPDATE business_projects SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("updated_by", "Gerência de Projetos"),
        actor_role="Gerência de Projetos",
        action_type="timesheet",
        title="Parâmetros do Projeto Atualizados",
        description=f"Projeto #{project_id} teve dados de cronograma atualizados.",
        project_name=data.get("name")
    )
    return True

def delete_project(project_id: int, deleted_by: str = "Gerência de Projetos"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM business_projects WHERE id = ?", (project_id,))
    p = cursor.fetchone()
    name = p["name"] if p else f"Projeto #{project_id}"

    cursor.execute("DELETE FROM project_milestones WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM timesheet_entries WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM dre_project_cost_centers WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM business_projects WHERE id = ?", (project_id,))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Gerência de Projetos",
        action_type="scope_alert",
        title="Projeto e Cronograma Excluídos",
        description=f"Projeto '{name}' e seus registros foram removidos.",
        project_name=name
    )
    return True

def create_milestone(project_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    phase_name = data.get("phase_name", "Nova Fase Técnica")
    week_start = int(data.get("week_start", 1))
    week_end = int(data.get("week_end", 2))
    budgeted_hh = int(data.get("budgeted_hh", 20))
    is_critical_path = 1 if data.get("is_critical_path") else 0
    requires_mentor_approval = 1 if data.get("requires_mentor_approval") else 0
    approval_status = "pendente" if requires_mentor_approval else "nao_requerido"

    cursor.execute("""
    INSERT INTO project_milestones (
        project_id, phase_name, week_start, week_end, budgeted_hh,
        consumed_hh, progress_pct, is_critical_path, requires_mentor_approval,
        mentor_approval_status, status
    ) VALUES (?, ?, ?, ?, ?, 0.0, 0.0, ?, ?, ?, 'pendente')
    """, (
        project_id, phase_name, week_start, week_end, budgeted_hh,
        is_critical_path, requires_mentor_approval, approval_status
    ))
    new_m_id = cursor.lastrowid

    # Recalcular total orçado do projeto
    cursor.execute("UPDATE business_projects SET total_budgeted_hh = (SELECT COALESCE(SUM(budgeted_hh), 0) FROM project_milestones WHERE project_id = ?) WHERE id = ?", (project_id, project_id))

    cursor.execute("SELECT name FROM business_projects WHERE id = ?", (project_id,))
    p_name = cursor.fetchone()["name"]

    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("created_by", "Gerência de Projetos"),
        actor_role="Gerência de Projetos",
        action_type="timesheet",
        title="Novo Marco Técnico Criado",
        description=f"Marco '{phase_name}' adicionado ao projeto '{p_name}' (Semanas {week_start}-{week_end}, {budgeted_hh}h).",
        project_name=p_name
    )
    return {"id": new_m_id, "phase_name": phase_name, "project_id": project_id}

def update_milestone(milestone_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []
    for k in ["phase_name", "week_start", "week_end", "budgeted_hh", "progress_pct", "is_critical_path", "requires_mentor_approval", "status"]:
        if k in data and data[k] is not None:
            fields.append(f"{k} = ?")
            values.append(data[k])

    if not fields:
        conn.close()
        return True

    values.append(milestone_id)
    cursor.execute(f"UPDATE project_milestones SET {', '.join(fields)} WHERE id = ?", values)

    cursor.execute("SELECT project_id, phase_name, budgeted_hh, consumed_hh, progress_pct FROM project_milestones WHERE id = ?", (milestone_id,))
    m = cursor.fetchone()
    project_id = m["project_id"]

    # Recalcular total_budgeted_hh e progress_pct médio
    cursor.execute("UPDATE business_projects SET total_budgeted_hh = (SELECT COALESCE(SUM(budgeted_hh), 0) FROM project_milestones WHERE project_id = ?), progress_pct = (SELECT COALESCE(AVG(progress_pct), 0) FROM project_milestones WHERE project_id = ?) WHERE id = ?", (project_id, project_id, project_id))

    conn.commit()
    conn.close()
    return True

def delete_milestone(milestone_id: int, deleted_by: str = "Gerência de Projetos"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT project_id, phase_name FROM project_milestones WHERE id = ?", (milestone_id,))
    m = cursor.fetchone()
    project_id = m["project_id"] if m else None
    phase_name = m["phase_name"] if m else f"Marco #{milestone_id}"

    cursor.execute("DELETE FROM project_milestones WHERE id = ?", (milestone_id,))

    if project_id:
        cursor.execute("UPDATE business_projects SET total_budgeted_hh = (SELECT COALESCE(SUM(budgeted_hh), 0) FROM project_milestones WHERE project_id = ?), progress_pct = (SELECT COALESCE(AVG(progress_pct), 0) FROM project_milestones WHERE project_id = ?) WHERE id = ?", (project_id, project_id, project_id))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Gerência de Projetos",
        action_type="timesheet",
        title="Marco Técnico Removido",
        description=f"Marco '{phase_name}' removido do cronograma Gantt.",
        project_name="Gantt & Projetos"
    )
    return True

# ==============================================================================
# 3. TRANSAÇÕES DE TIMESHEET COM RECÁLCULO AUTOMÁTICO DE HH
# ==============================================================================
def update_timesheet_entry(entry_id: int, data: dict):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT project_id, milestone_id, hours, consultant_name FROM timesheet_entries WHERE id = ?", (entry_id,))
    old = cursor.fetchone()
    if not old:
        conn.close()
        raise ValueError("Apontamento de timesheet não encontrado")

    old_hours = old["hours"]
    project_id = old["project_id"]
    milestone_id = old["milestone_id"]
    new_hours = float(data.get("hours", old_hours))
    hour_diff = new_hours - old_hours

    date_val = data.get("date")
    desc_val = data.get("description")

    fields = ["hours = ?"]
    values = [new_hours]
    if date_val:
        fields.append("date = ?")
        values.append(date_val)
    if desc_val:
        fields.append("description = ?")
        values.append(desc_val)

    values.append(entry_id)
    cursor.execute(f"UPDATE timesheet_entries SET {', '.join(fields)} WHERE id = ?", values)

    # Ajustar consumo acumulado no projeto
    cursor.execute("UPDATE business_projects SET consumed_hh = MAX(0, consumed_hh + ?) WHERE id = ?", (hour_diff, project_id))
    if milestone_id:
        cursor.execute("UPDATE project_milestones SET consumed_hh = MAX(0, consumed_hh + ?) WHERE id = ?", (hour_diff, milestone_id))

        # Reavaliar scope creep
        cursor.execute("SELECT budgeted_hh, consumed_hh, progress_pct FROM project_milestones WHERE id = ?", (milestone_id,))
        m = cursor.fetchone()
        if m and m["budgeted_hh"] > 0:
            scope_triggered = 1 if ((m["consumed_hh"] / m["budgeted_hh"]) >= 0.75 and m["progress_pct"] < 90.0) else 0
            cursor.execute("UPDATE timesheet_entries SET scope_alert_triggered = ? WHERE id = ?", (scope_triggered, entry_id))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=data.get("updated_by", old["consultant_name"]),
        actor_role="Consultoria",
        action_type="timesheet",
        title="Apontamento de Horas Editado",
        description=f"Lançamento #{entry_id} alterado de {old_hours}h para {new_hours}h. Consumo do projeto recalculado com sucesso.",
        project_name=f"Projeto #{project_id}"
    )
    return {"success": True, "hour_diff": hour_diff, "new_hours": new_hours}

def delete_timesheet_entry(entry_id: int, deleted_by: str = "Consultoria"):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT project_id, milestone_id, hours, consultant_name, description FROM timesheet_entries WHERE id = ?", (entry_id,))
    entry = cursor.fetchone()
    if not entry:
        conn.close()
        return False

    hours = entry["hours"]
    project_id = entry["project_id"]
    milestone_id = entry["milestone_id"]
    consultant = entry["consultant_name"]

    cursor.execute("DELETE FROM timesheet_entries WHERE id = ?", (entry_id,))

    # Subtrair horas consumidas do projeto e marco
    cursor.execute("UPDATE business_projects SET consumed_hh = MAX(0, consumed_hh - ?) WHERE id = ?", (hours, project_id))
    if milestone_id:
        cursor.execute("UPDATE project_milestones SET consumed_hh = MAX(0, consumed_hh - ?) WHERE id = ?", (hours, milestone_id))

    conn.commit()
    conn.close()

    log_activity(
        actor_name=deleted_by,
        actor_role="Consultoria",
        action_type="timesheet",
        title="Apontamento de Timesheet Removido",
        description=f"Lançamento de {hours}h de {consultant} removido. Consumo acumulado recalculado.",
        project_name=f"Projeto #{project_id}"
    )
    return True

# Aliases para compatibilidade da API
get_services_catalog = get_services_list
get_projects_gantt = get_projects_gantt_data


