"""
Nexus Jr. | ERP Gestão & Finanças 2.0
Backend Server - FastAPI Standalone
Rotas Transacionais Completas (CRUD em Todos os Módulos):
Autenticação RBAC, Catálogo, CPQ e Ciclo de Vida de Propostas,
Gestão de Projetos e Marcos Gantt com Travas de Mentores,
Repositório de Ativos com Cadastro/Edição, Timesheet com Recálculo de HH,
DRE Gerencial por Centro de Custo, Feed de Auditoria e Painel VPGG.
"""

import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field

from database import (
    init_db,
    authenticate_user,
    get_user_by_id,
    get_services_catalog,
    calculate_cpq,
    save_proposal,
    update_proposal,
    update_proposal_status,
    delete_proposal,
    get_proposals_list,
    get_projects_gantt,
    create_project,
    update_project,
    delete_project,
    create_milestone,
    update_milestone,
    delete_milestone,
    approve_mentor_milestone,
    get_assets_list,
    create_asset,
    update_asset,
    delete_asset,
    log_timesheet,
    update_timesheet_entry,
    delete_timesheet_entry,
    get_dre_data,
    get_db,
    log_activity,
    get_activity_logs,
    get_members_list,
    create_member,
    update_member,
    delete_member,
    toggle_member_status,
    calculate_econometric_forecasting
)

from reports import (
    generate_dre_excel,
    generate_timesheet_excel,
    generate_dre_pdf_html
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Nexus Jr. | ERP Gestão & Finanças 2.0",
    description="Sistema ERP Corporativo Especializado para Empresas Juniores de Administração, Economia e Negócios",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# --- Modelos Pydantic Transacionais ---
class LoginPayload(BaseModel):
    email: str
    password: str

class CPQCalcPayload(BaseModel):
    service_id: int
    horas_diagnostico: int = Field(default=20, ge=1)
    horas_execucao: int = Field(default=80, ge=1)
    seniority: str = Field(default="Gerente de Projetos")
    risk_factor: float = Field(default=1.15, ge=1.0, le=2.0)
    hourly_rate_override: Optional[float] = None

class CPQSavePayload(BaseModel):
    service_id: int
    client_name: str
    client_contact: Optional[str] = ""
    horas_diagnostico: int
    horas_execucao: int
    seniority: str
    risk_factor: float = 1.15
    hourly_rate_override: Optional[float] = None
    created_by: str = "Consultor Nexus Jr."
    notes: Optional[str] = ""

class ProposalUpdatePayload(BaseModel):
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    status: Optional[str] = None
    seniority_level: Optional[str] = None
    horas_diagnostico: Optional[int] = None
    horas_execucao: Optional[int] = None
    total_hh: Optional[int] = None
    hourly_rate: Optional[float] = None
    risk_multiplier: Optional[float] = None
    total_price: Optional[float] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = "Consultor Comercial"

class ProposalStatusPayload(BaseModel):
    status: str
    updated_by: Optional[str] = "Consultor Comercial"

class ProjectCreatePayload(BaseModel):
    name: str
    client_name: str
    service_name: Optional[str] = "Consultoria Financeira"
    macro_area: Optional[str] = "Finanças e Contabilidade"
    lead_time_weeks: int = Field(default=10, ge=1)
    total_budgeted_hh: int = Field(default=100, ge=1)
    manager_name: str = "Lucas Mendes"
    start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    status: str = "em_andamento"
    contract_value: float = Field(default=12500.0, ge=0)

class ProjectUpdatePayload(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = None
    lead_time_weeks: Optional[int] = None
    total_budgeted_hh: Optional[int] = None
    start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    progress_pct: Optional[float] = None
    updated_by: Optional[str] = "Gerência de Projetos"

class MilestoneCreatePayload(BaseModel):
    phase_name: str
    week_start: int = Field(default=1, ge=1)
    week_end: int = Field(default=2, ge=1)
    budgeted_hh: int = Field(default=20, ge=1)
    is_critical_path: bool = False
    requires_mentor_approval: bool = False
    created_by: Optional[str] = "Gerente de Projetos"

class MilestoneUpdatePayload(BaseModel):
    phase_name: Optional[str] = None
    week_start: Optional[int] = None
    week_end: Optional[int] = None
    budgeted_hh: Optional[int] = None
    progress_pct: Optional[float] = None
    is_critical_path: Optional[bool] = None
    requires_mentor_approval: Optional[bool] = None
    status: Optional[str] = None
    updated_by: Optional[str] = "Gerente de Projetos"

class MentorApprovalPayload(BaseModel):
    mentor_name: str
    mentor_notes: str
    mentor_rubric: str = "APROVADO-MEJ-2026"

class AssetCreatePayload(BaseModel):
    title: str
    macro_area: str
    service_name: Optional[str] = "Consultoria Financeira"
    asset_code: Optional[str] = None
    file_format: str = ".xlsx"
    version: str = "v1.0"
    version_notes: Optional[str] = "Versão inicial cadastrada."
    author_member: Optional[str] = "Consultor Nexus Jr."
    validator_mentor: Optional[str] = "Prof. Orientador"
    turnover_cycle: Optional[str] = "Ciclo 2026.1"
    download_url: Optional[str] = None
    file_size: Optional[str] = "1.5 MB"

class AssetUpdatePayload(BaseModel):
    title: Optional[str] = None
    macro_area: Optional[str] = None
    service_name: Optional[str] = None
    version: Optional[str] = None
    version_notes: Optional[str] = None
    turnover_cycle: Optional[str] = None
    file_format: Optional[str] = None
    download_url: Optional[str] = None
    validator_mentor: Optional[str] = None
    author_member: Optional[str] = None
    updated_by: Optional[str] = "Diretoria de Conhecimento"

class TimesheetPayload(BaseModel):
    project_id: int
    milestone_id: Optional[int] = None
    consultant_name: str
    consultant_email: str
    date: str
    hours: float = Field(..., gt=0)
    description: str

class TimesheetUpdatePayload(BaseModel):
    date: Optional[str] = None
    hours: float = Field(..., gt=0)
    description: Optional[str] = None
    updated_by: Optional[str] = "Consultoria"

class MemberCreatePayload(BaseModel):
    email: str
    nome: str
    area: str = "Projetos"
    role: str = "assessor"
    cargo: str = "Consultor Júnior"
    cost_center: str = "Presidência e Gestão Geral"
    turnover_cycle: str = "Ciclo 2026.1"
    status: str = "ativo"
    password: Optional[str] = "nexus2026!"
    created_by_name: Optional[str] = "Diretoria VPGG"

class MemberUpdatePayload(BaseModel):
    nome: Optional[str] = None
    area: Optional[str] = None
    role: Optional[str] = None
    cargo: Optional[str] = None
    cost_center: Optional[str] = None
    turnover_cycle: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None
    updated_by_name: Optional[str] = "Diretoria VPGG"

class ForecastingPayload(BaseModel):
    horizon_months: int = Field(default=24, ge=6, le=36)
    growth_rate_annual_pct: float = Field(default=15.0, ge=-50.0, le=100.0)
    optimistic_growth_bonus_pct: float = Field(default=20.0, ge=0.0, le=100.0)
    pessimistic_growth_penalty_pct: float = Field(default=15.0, ge=0.0, le=100.0)
    inflation_annual_pct: float = Field(default=5.5, ge=0.0, le=30.0)
    cost_containment_bonus_pct: float = Field(default=5.0, ge=0.0, le=20.0)
    pessimistic_inflation_penalty_pct: float = Field(default=6.0, ge=0.0, le=30.0)
    seasonality_intensity: float = Field(default=0.25, ge=0.0, le=1.0)
    initial_cash_balance: float = Field(default=45000.0, ge=0.0)


# ==============================================================================
# ROTAS DE AUTENTICAÇÃO RBAC
# ==============================================================================
@app.post("/api/auth/login")
def login(payload: LoginPayload):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais corporativas inválidas")
    return {
        "access_token": f"nexus_jwt_token_{user['id']}_{user['role']}",
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me")
def get_current_user_profile(user_id: int = 1):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


# ==============================================================================
# ROTAS DE CATÁLOGO & CPQ PARAMÉTRICO (CRUD PROPOSTAS)
# ==============================================================================
@app.get("/api/business/services")
def list_services(macro_area: Optional[str] = None):
    services = get_services_catalog(macro_area)
    return {"total": len(services), "services": services}

@app.post("/api/business/cpq/calculate")
def simulate_cpq(payload: CPQCalcPayload):
    try:
        quote = calculate_cpq(
            service_id=payload.service_id,
            horas_diagnostico=payload.horas_diagnostico,
            horas_execucao=payload.horas_execucao,
            seniority=payload.seniority,
            risk_factor=payload.risk_factor,
            hourly_rate_override=payload.hourly_rate_override
        )
        return quote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/business/cpq/save")
def create_proposal(payload: CPQSavePayload):
    try:
        result = save_proposal(payload.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/business/cpq/proposals")
def list_proposals():
    proposals = get_proposals_list()
    return {"total": len(proposals), "proposals": proposals}

@app.put("/api/business/cpq/proposals/{proposal_id}")
def edit_proposal(proposal_id: int, payload: ProposalUpdatePayload):
    success = update_proposal(proposal_id, payload.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return {"success": True, "message": f"Proposta #{proposal_id} atualizada com sucesso."}

@app.patch("/api/business/cpq/proposals/{proposal_id}/status")
def change_proposal_status(proposal_id: int, payload: ProposalStatusPayload):
    success = update_proposal_status(proposal_id, payload.status, payload.updated_by)
    if not success:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return {"success": True, "message": f"Status da proposta #{proposal_id} alterado para {payload.status}."}

@app.delete("/api/business/cpq/proposals/{proposal_id}")
def remove_proposal(proposal_id: int, deleted_by: str = "Consultor Comercial"):
    success = delete_proposal(proposal_id, deleted_by)
    if not success:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")
    return {"success": True, "message": "Proposta excluída com sucesso."}


# ==============================================================================
# ROTAS DE PROJETOS, GANTT & MARCOS (CRUD COMPLETO)
# ==============================================================================
@app.get("/api/business/projects/gantt")
def get_projects():
    projects = get_projects_gantt()
    return {"total": len(projects), "projects": projects}

@app.post("/api/business/projects")
def add_project(payload: ProjectCreatePayload):
    res = create_project(payload.dict())
    return {"success": True, "project": res}

@app.put("/api/business/projects/{project_id}")
def edit_project(project_id: int, payload: ProjectUpdatePayload):
    success = update_project(project_id, payload.dict())
    return {"success": success, "message": f"Projeto #{project_id} atualizado."}

@app.delete("/api/business/projects/{project_id}")
def remove_project(project_id: int, deleted_by: str = "Gerência de Projetos"):
    success = delete_project(project_id, deleted_by)
    return {"success": success, "message": "Projeto e cronograma excluídos com sucesso."}

@app.post("/api/business/projects/{project_id}/milestones")
def add_milestone(project_id: int, payload: MilestoneCreatePayload):
    res = create_milestone(project_id, payload.dict())
    return {"success": True, "milestone": res}

@app.put("/api/business/projects/milestones/{milestone_id}")
def edit_milestone(milestone_id: int, payload: MilestoneUpdatePayload):
    success = update_milestone(milestone_id, payload.dict())
    return {"success": success, "message": f"Marco #{milestone_id} atualizado."}

@app.delete("/api/business/projects/milestones/{milestone_id}")
def remove_milestone(milestone_id: int, deleted_by: str = "Gerência de Projetos"):
    success = delete_milestone(milestone_id, deleted_by)
    return {"success": success, "message": "Marco removido com sucesso."}

@app.post("/api/business/projects/milestones/{milestone_id}/approve-mentor")
def approve_milestone(milestone_id: int, payload: MentorApprovalPayload):
    if not payload.mentor_name.strip():
        raise HTTPException(status_code=400, detail="O nome do professor/mentor orientador é obrigatório")
    success = approve_mentor_milestone(
        milestone_id=milestone_id,
        mentor_name=payload.mentor_name,
        mentor_notes=payload.mentor_notes,
        rubric=payload.mentor_rubric
    )
    return {
        "success": success,
        "message": f"Marco #{milestone_id} validado e liberado com chancela acadêmica de {payload.mentor_name}."
    }


# ==============================================================================
# ROTAS DE ATIVOS INTELECTUAIS (CRUD COMPLETO)
# ==============================================================================
@app.get("/api/business/knowledge/assets")
def list_assets(macro_area: Optional[str] = None):
    assets = get_assets_list(macro_area)
    return {"total": len(assets), "assets": assets}

@app.post("/api/business/knowledge/assets")
def add_asset(payload: AssetCreatePayload):
    res = create_asset(payload.dict())
    return {"success": True, "asset": res}

@app.put("/api/business/knowledge/assets/{asset_id}")
def edit_asset(asset_id: int, payload: AssetUpdatePayload):
    success = update_asset(asset_id, payload.dict())
    return {"success": success, "message": f"Ativo #{asset_id} atualizado com sucesso."}

@app.delete("/api/business/knowledge/assets/{asset_id}")
def remove_asset(asset_id: int, deleted_by: str = "Diretoria de Conhecimento"):
    success = delete_asset(asset_id, deleted_by)
    return {"success": success, "message": "Ativo excluído com sucesso."}


# ==============================================================================
# ROTAS DE TIMESHEET (CRUD COMPLETO COM RECÁLCULO DE HH)
# ==============================================================================
@app.get("/api/business/timesheet")
def list_timesheet():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, p.name as project_name, m.phase_name as milestone_title, m.phase_name as title
    FROM timesheet_entries t
    LEFT JOIN business_projects p ON t.project_id = p.id
    LEFT JOIN project_milestones m ON t.milestone_id = m.id
    ORDER BY t.date DESC, t.id DESC
    LIMIT 50
    """)
    entries = [dict(r) for r in cursor.fetchall()]

    # Alertas globais de Scope Creep
    cursor.execute("""
    SELECT m.*, p.name as project_name
    FROM project_milestones m
    JOIN business_projects p ON m.project_id = p.id
    WHERE m.budgeted_hh > 0
      AND (CAST(m.consumed_hh AS REAL) / m.budgeted_hh) >= 0.75
      AND m.progress_pct < 90.0
    """)
    alerts = []
    for r in cursor.fetchall():
        row_dict = dict(r)
        row_dict["title"] = row_dict["phase_name"]
        alerts.append(row_dict)
    conn.close()

    return {
        "entries": entries,
        "active_scope_alerts": alerts,
        "total_alerts": len(alerts)
    }

@app.post("/api/business/timesheet/log")
def create_timesheet_entry(payload: TimesheetPayload):
    res = log_timesheet(
        project_id=payload.project_id,
        milestone_id=payload.milestone_id,
        consultant_name=payload.consultant_name,
        consultant_email=payload.consultant_email,
        date=payload.date,
        hours=payload.hours,
        description=payload.description
    )
    return res

@app.put("/api/business/timesheet/{entry_id}")
def edit_timesheet_entry(entry_id: int, payload: TimesheetUpdatePayload):
    try:
        res = update_timesheet_entry(entry_id, payload.dict())
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/business/timesheet/{entry_id}")
def remove_timesheet_entry(entry_id: int, deleted_by: str = "Consultoria"):
    success = delete_timesheet_entry(entry_id, deleted_by)
    if not success:
        raise HTTPException(status_code=404, detail="Apontamento não encontrado")
    return {"success": True, "message": "Apontamento removido e consumo recalculado."}


# ==============================================================================
# ROTAS DE TESOURARIA & DRE POR CENTRO DE CUSTO
# ==============================================================================
@app.get("/api/business/finance/dre-by-project")
def get_finance_dre():
    dre = get_dre_data()
    return dre

@app.get("/api/business/finance/forecasting")
def get_forecasting(
    horizon_months: int = 24,
    growth_rate_annual_pct: float = 15.0,
    optimistic_growth_bonus_pct: float = 20.0,
    pessimistic_growth_penalty_pct: float = 15.0,
    inflation_annual_pct: float = 5.5,
    cost_containment_bonus_pct: float = 5.0,
    pessimistic_inflation_penalty_pct: float = 6.0,
    seasonality_intensity: float = 0.25,
    initial_cash_balance: float = 45000.0
):
    params = {
        "horizon_months": horizon_months,
        "growth_rate_annual_pct": growth_rate_annual_pct,
        "optimistic_growth_bonus_pct": optimistic_growth_bonus_pct,
        "pessimistic_growth_penalty_pct": pessimistic_growth_penalty_pct,
        "inflation_annual_pct": inflation_annual_pct,
        "cost_containment_bonus_pct": cost_containment_bonus_pct,
        "pessimistic_inflation_penalty_pct": pessimistic_inflation_penalty_pct,
        "seasonality_intensity": seasonality_intensity,
        "initial_cash_balance": initial_cash_balance
    }
    return calculate_econometric_forecasting(params)

@app.post("/api/business/finance/forecasting")
def post_forecasting(payload: ForecastingPayload):
    return calculate_econometric_forecasting(payload.dict())


# ==============================================================================
# FEED DE ATIVIDADES EM TEMPO REAL
# ==============================================================================
@app.get("/api/business/activities")
def list_activities(limit: int = 30, action_type: Optional[str] = None):
    logs = get_activity_logs(limit, action_type)
    return {"total": len(logs), "activities": logs}


# ==============================================================================
# GESTÃO DE MEMBROS E EQUIPA (PAINEL VPGG / RBAC)
# ==============================================================================
@app.get("/api/business/members")
def list_members(area: Optional[str] = None, role: Optional[str] = None, status: Optional[str] = None):
    members = get_members_list(area, role, status)
    return {"total": len(members), "members": members}

@app.post("/api/business/members")
def add_member(payload: MemberCreatePayload):
    member = create_member(payload.dict())
    return {"success": True, "member": member}

@app.put("/api/business/members/{member_id}")
def edit_member(member_id: int, payload: MemberUpdatePayload):
    updated = update_member(member_id, payload.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"success": True, "member": updated}

@app.patch("/api/business/members/{member_id}/toggle-status")
def toggle_status(member_id: int, updated_by: str = "Diretoria VPGG"):
    res = toggle_member_status(member_id, updated_by)
    if not res:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"success": True, "member": res}

@app.delete("/api/business/members/{member_id}")
def remove_member(member_id: int, deleted_by: str = "Diretoria VPGG"):
    success = delete_member(member_id, deleted_by)
    return {"success": success, "message": "Turnover registrado. Membro desativado mantendo conformidade estatutária."}


# ==============================================================================
# EXPORTAÇÃO REAL DE RELATÓRIOS (EXCEL .XLSX E PDF/HTML)
# ==============================================================================
@app.get("/api/business/reports/dre/excel")
def download_dre_excel():
    dre = get_dre_data()
    buf = generate_dre_excel(dre)
    filename = f"DRE_Gerencial_NexusJr_{datetime.now().strftime('%Y%m%d')}.xlsx"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.get("/api/business/reports/timesheet/excel")
def download_timesheet_excel():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, p.name as project_name, m.phase_name as milestone_title
    FROM timesheet_entries t
    LEFT JOIN business_projects p ON t.project_id = p.id
    LEFT JOIN project_milestones m ON t.milestone_id = m.id
    ORDER BY t.date DESC
    """)
    entries = [dict(r) for r in cursor.fetchall()]
    conn.close()
    projects = get_projects_gantt()
    buf = generate_timesheet_excel(entries, projects)
    filename = f"Timesheet_HH_NexusJr_{datetime.now().strftime('%Y%m%d')}.xlsx"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.get("/api/business/reports/dre/pdf-view")
def view_dre_pdf():
    dre = get_dre_data()
    html = generate_dre_pdf_html(dre)
    return HTMLResponse(content=html)


# ==============================================================================
# KPIS GERAIS & ANALYTICS VISUAL (CHART.JS)
# ==============================================================================
@app.get("/api/business/kpis/overview")
def get_overview_kpis():
    dre = get_dre_data()
    projects = get_projects_gantt()
    assets = get_assets_list()
    proposals = get_proposals_list()
    activities = get_activity_logs(limit=10)
    members = get_members_list()

    total_propostas_valor = sum(p["total_price"] for p in proposals)
    total_hh_executado = sum(p["consumed_hh"] for p in projects)
    total_hh_orcado = sum(p["total_budgeted_hh"] for p in projects)

    active_alerts = 0
    for p in projects:
        if p.get("scope_creep_alert"):
            active_alerts += len(p.get("scope_alerts", []))

    chart_revenue_evolution = {
        "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out"],
        "meta_planejada": [3500, 7500, 12000, 16500, 21000, 26000, 31000, 36000, 40000, 45000],
        "realizado_acumulado": [3800, 8200, 13500, 18900, 24200, 29800, 35100, 38900, 41900, 41900]
    }

    chart_obz_distribution = {
        "labels": [
            "Superávit Reinvestido (Lei 13.267)",
            "Despesas Administrativas Rateadas",
            "Softwares e Licenças Técnicas",
            "Custos Operacionais Diretos"
        ],
        "values": [33950.00, 4500.00, 2400.00, 1050.00],
        "colors": ["#059669", "#0b1d3a", "#3b82f6", "#f59e0b"]
    }

    chart_hh_comparison = {
        "labels": [p["name"][:20] + "..." if len(p["name"]) > 20 else p["name"] for p in projects],
        "orcado": [p["total_budgeted_hh"] for p in projects],
        "executado": [p["consumed_hh"] for p in projects]
    }

    return {
        "faturamento_acumulado": dre["consolidado"]["total_receita_bruta"],
        "superavit_estatutario": dre["consolidado"]["total_superavit_estatutario"],
        "margem_contribuicao_pct": dre["consolidado"]["margem_contribuicao_media_pct"],
        "projetos_ativos": len(projects),
        "total_hh_executado": round(total_hh_executado, 1),
        "total_hh_orcado": total_hh_orcado,
        "ativos_intelectuais_count": len(assets),
        "propostas_geradas_count": len(proposals),
        "pipeline_propostas_valor": round(total_propostas_valor, 2),
        "alertas_scope_creep_ativos": active_alerts,
        "total_membros_ativos": len([m for m in members if m.get("status") == "ativo"]),
        "conformidade_lei_13267": "100% dos excedentes reinvestidos; R$ 0,00 de remuneração a membros",
        "charts": {
            "revenue_evolution": chart_revenue_evolution,
            "obz_distribution": chart_obz_distribution,
            "hh_comparison": chart_hh_comparison
        },
        "recent_activities": activities
    }


# ==============================================================================
# SERVIÇO DE ARQUIVOS ESTÁTICOS & SINGLE-PAGE APP
# ==============================================================================
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "Nexus Jr. API running. Please ensure index.html exists."})

@app.get("/{full_path:path}")
def serve_static(full_path: str):
    file_path = os.path.join(BASE_DIR, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_file = os.path.join(BASE_DIR, "index.html")
    return FileResponse(index_file)
