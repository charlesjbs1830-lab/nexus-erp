import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8002"

def request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode("utf-8")
        status = response.status
        try:
            return status, json.loads(res_body)
        except Exception:
            return status, res_body

def test_crud_suite():
    print("--- INICIANDO TESTES AUTOMATIZADOS DO KERNEL CRUD (URLLIB) ---")
    
    # 1. TESTE CPQ PROPOSALS
    print("\n[1/5] Testando Ciclo de Vida de Propostas CPQ...")
    # Criar proposta
    cpq_payload = {
        "service_id": 1,
        "client_name": "Empresa Teste Alpha Ltda",
        "client_contact": "teste@alpha.com",
        "horas_diagnostico": 15,
        "horas_execucao": 45,
        "seniority": "Gerente de Projetos",
        "risk_factor": 1.15,
        "notes": "Proposta automatizada de teste",
        "created_by": "Charles Teste"
    }
    status, prop_data = request("POST", "/api/business/cpq/save", cpq_payload)
    assert status == 200, f"Falha ao criar proposta: {prop_data}"
    prop_id = prop_data["id"]
    print(f"  -> Proposta #{prop_id} criada com sucesso. Total: R$ {prop_data['total_price']}")

    # Atualizar proposta (PUT)
    update_prop = {
        "client_name": "Empresa Teste Alpha Renovada S.A.",
        "status": "em_negociacao",
        "total_price": 9500.0,
        "notes": "Renegociação comercial iniciada",
        "updated_by": "Charles Teste"
    }
    status, res = request("PUT", f"/api/business/cpq/proposals/{prop_id}", update_prop)
    assert status == 200, f"Falha ao atualizar proposta: {res}"
    print(f"  -> Proposta #{prop_id} atualizada com sucesso via PUT.")

    # Alterar status (PATCH)
    status, res = request("PATCH", f"/api/business/cpq/proposals/{prop_id}/status", {"status": "convertida", "updated_by": "Charles Teste"})
    assert status == 200, f"Falha ao alterar status da proposta: {res}"
    print(f"  -> Status da proposta #{prop_id} alterado para 'convertida' via PATCH.")

    # Excluir proposta (DELETE)
    status, res = request("DELETE", f"/api/business/cpq/proposals/{prop_id}?deleted_by=Charles%20Teste")
    assert status == 200, f"Falha ao excluir proposta: {res}"
    print(f"  -> Proposta #{prop_id} excluída com sucesso via DELETE.")

    # 2. TESTE PROJETOS E MARCOS GANTT
    print("\n[2/5] Testando Projetos e Marcos (Gantt)...")
    proj_payload = {
        "name": "Consultoria de Estruturação FCD Gama",
        "client_name": "Gama Participações S.A.",
        "service_name": "Valuation (FCD + Múltiplos)",
        "macro_area": "Finanças Corporativas",
        "lead_time_weeks": 8,
        "total_budgeted_hh": 90,
        "manager_name": "Lucas Mendes",
        "start_date": "2026-04-01",
        "expected_end_date": "2026-05-30",
        "status": "em_andamento",
        "contract_value": 15000.0
    }
    status, proj_json = request("POST", "/api/business/projects", proj_payload)
    assert status == 200, f"Falha ao criar projeto: {proj_json}"
    proj_res = proj_json["project"]
    proj_id = proj_res["id"]
    print(f"  -> Projeto #{proj_id} '{proj_res['name']}' criado com sucesso.")

    # Atualizar projeto (PUT)
    status, res = request("PUT", f"/api/business/projects/{proj_id}", {"lead_time_weeks": 9, "progress_pct": 25.0})
    assert status == 200, f"Falha ao atualizar projeto: {res}"
    print(f"  -> Projeto #{proj_id} atualizado (lead time = 9 sem, avanço = 25%).")

    # Criar marco (POST)
    m_payload = {
        "phase_name": "Fase Extra: Teste de Sensibilidade Monte Carlo",
        "week_start": 4,
        "week_end": 6,
        "budgeted_hh": 25,
        "is_critical_path": True,
        "requires_mentor_approval": True,
        "created_by": "Lucas Mendes"
    }
    status, m_json = request("POST", f"/api/business/projects/{proj_id}/milestones", m_payload)
    assert status == 200, f"Falha ao criar marco: {m_json}"
    m_res = m_json["milestone"]
    m_id = m_res["id"]
    print(f"  -> Marco #{m_id} '{m_res['phase_name']}' inserido no cronograma.")

    # Atualizar marco (PUT)
    status, res = request("PUT", f"/api/business/projects/milestones/{m_id}", {"progress_pct": 50.0, "budgeted_hh": 30})
    assert status == 200, f"Falha ao atualizar marco: {res}"
    print(f"  -> Marco #{m_id} atualizado com sucesso via PUT.")

    # Excluir marco (DELETE)
    status, res = request("DELETE", f"/api/business/projects/milestones/{m_id}")
    assert status == 200, f"Falha ao excluir marco: {res}"
    print(f"  -> Marco #{m_id} excluído com sucesso via DELETE.")

    # Excluir projeto (DELETE)
    status, res = request("DELETE", f"/api/business/projects/{proj_id}")
    assert status == 200, f"Falha ao excluir projeto: {res}"
    print(f"  -> Projeto #{proj_id} excluído com sucesso via DELETE.")

    # 3. TESTE ATIVOS INTELECTUAIS
    print("\n[3/5] Testando Repositório de Ativos Intelectuais...")
    asset_payload = {
        "title": "Planilha Paramétrica de WACC e Custo de Capital 2026",
        "macro_area": "Finanças Corporativas",
        "service_name": "Valuation",
        "file_format": ".xlsx",
        "version": "v1.2",
        "version_notes": "Ajuste do risco-país e inflação implícita NTN-B.",
        "author_member": "Mariana Souza",
        "validator_mentor": "Prof. Dr. Marcos Silveira",
        "turnover_cycle": "Ciclo 2026.1",
        "download_url": "https://drive.nexusjr.com/assets/wacc_v12.xlsx"
    }
    status, asset_json = request("POST", "/api/business/knowledge/assets", asset_payload)
    assert status == 200, f"Falha ao cadastrar ativo: {asset_json}"
    asset_res = asset_json["asset"]
    asset_id = asset_res["id"]
    print(f"  -> Ativo #{asset_id} '{asset_res['title']}' cadastrado com sucesso.")

    # Atualizar ativo (PUT)
    status, res = request("PUT", f"/api/business/knowledge/assets/{asset_id}", {"version": "v1.3", "version_notes": "Revisão semestral"})
    assert status == 200, f"Falha ao atualizar ativo: {res}"
    print(f"  -> Ativo #{asset_id} atualizado para v1.3 com sucesso.")

    # Excluir ativo (DELETE)
    status, res = request("DELETE", f"/api/business/knowledge/assets/{asset_id}")
    assert status == 200, f"Falha ao excluir ativo: {res}"
    print(f"  -> Ativo #{asset_id} excluído do repositório.")

    # 4. TESTE TIMESHEET COM RECÁLCULO AUTOMÁTICO DE HH
    print("\n[4/5] Testando Apontamento de Timesheet e Recálculo Automático...")
    status, gantt_json = request("GET", "/api/business/projects/gantt")
    projects = gantt_json["projects"]
    assert len(projects) > 0, "Nenhum projeto encontrado"
    test_p = projects[0]
    p_id = test_p["id"]
    m_id = test_p["milestones"][0]["id"] if test_p["milestones"] else None
    hh_inicial = test_p["consumed_hh"]
    print(f"  -> Projeto #{p_id} ({test_p['name']}): Consumo inicial = {hh_inicial} h")

    # Lançar horas (+6.0 h)
    ts_payload = {
        "project_id": p_id,
        "milestone_id": m_id,
        "consultant_name": "Charles Auditor",
        "consultant_email": "charles@nexusjr.com",
        "date": "2026-04-15",
        "hours": 6.0,
        "description": "Elaboração de testes e validação de cálculo DRE"
    }
    status, ts_entry = request("POST", "/api/business/timesheet/log", ts_payload)
    assert status == 200, f"Falha ao lançar timesheet: {ts_entry}"
    ts_id = ts_entry["id"]
    print(f"  -> Apontamento #{ts_id} criado (+6.0 h). Alerta Scope Creep: {ts_entry['scope_alert_triggered']}")

    # Verificar consumo no projeto (+6.0h)
    status, gantt_after = request("GET", "/api/business/projects/gantt")
    proj_updated = next(p for p in gantt_after["projects"] if p["id"] == p_id)
    print(f"  -> Consumo após lançamento: {proj_updated['consumed_hh']} h (esperado: {hh_inicial + 6.0} h)")
    assert proj_updated["consumed_hh"] == hh_inicial + 6.0, "Recálculo de HH incorreto após lançamento"

    # Editar apontamento (de 6.0 para 10.0 h -> +4.0 h diff)
    status, res = request("PUT", f"/api/business/timesheet/{ts_id}", {"hours": 10.0, "description": "Lançamento expandido para 10h", "date": "2026-04-15"})
    assert status == 200, f"Falha ao editar timesheet: {res}"
    status, gantt_after2 = request("GET", "/api/business/projects/gantt")
    proj_updated2 = next(p for p in gantt_after2["projects"] if p["id"] == p_id)
    print(f"  -> Consumo após edição para 10h: {proj_updated2['consumed_hh']} h (esperado: {hh_inicial + 10.0} h)")
    assert proj_updated2["consumed_hh"] == hh_inicial + 10.0, "Recálculo de HH incorreto após edição"

    # Excluir apontamento (deve subtrair 10.0 h e retornar a hh_inicial)
    status, res = request("DELETE", f"/api/business/timesheet/{ts_id}")
    assert status == 200, f"Falha ao excluir timesheet: {res}"
    status, gantt_after3 = request("GET", "/api/business/projects/gantt")
    proj_updated3 = next(p for p in gantt_after3["projects"] if p["id"] == p_id)
    print(f"  -> Consumo após exclusão: {proj_updated3['consumed_hh']} h (esperado: {hh_inicial} h)")
    assert proj_updated3["consumed_hh"] == hh_inicial, "Recálculo de HH incorreto após exclusão"

    # 5. TESTE TOGGLE MEMBRO VPGG
    print("\n[5/5] Testando Toggle de Status de Membro VPGG...")
    status, mem_json = request("GET", "/api/business/members")
    members = mem_json["members"]
    assert len(members) > 0, "Nenhum membro encontrado"
    member = members[0]
    mem_id = member["id"]
    status_antigo = member["status"]

    status, toggle_json = request("PATCH", f"/api/business/members/{mem_id}/toggle-status")
    assert status == 200, f"Falha ao alternar status do membro: {toggle_json}"
    mem_res = toggle_json["member"]
    print(f"  -> Membro #{mem_id} ({member['nome']}): status alternado de '{status_antigo}' para '{mem_res['status']}'.")
    assert mem_res["status"] != status_antigo, "Status do membro não mudou"

    # Reverter toggle
    status, res = request("PATCH", f"/api/business/members/{mem_id}/toggle-status")
    assert status == 200
    print(f"  -> Membro #{mem_id} restaurado para status original '{status_antigo}'.")

    # 6. VERIFICAÇÃO DE FEED DE ATIVIDADES
    print("\n[Verificação Final] Feed de Atividades...")
    status, act_json = request("GET", "/api/business/activities")
    activities = act_json["activities"]
    print(f"  -> Total de atividades registradas no log: {len(activities)}")
    print(f"  -> Última ação: [{activities[0]['action_type']}] {activities[0]['title']} ({activities[0]['description']})")

    print("\n" + "=" * 60)
    print("TODOS OS TESTES DE CRUD E RECÁLCULO PASSARAM COM 100% DE SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    test_crud_suite()
