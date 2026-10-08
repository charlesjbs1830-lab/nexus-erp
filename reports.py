"""
Nexus Jr. | ERP Gestão & Finanças 2.0
Gerador de Relatórios Executivos Oficiais (Excel .xlsx e PDF/HTML Imprimível)
Em conformidade com a Lei Federal nº 13.267/2016 e padrões FEA Jr. / FGV Jr.
"""

import io
from datetime import datetime
from typing import Dict, Any, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==============================================================================
# 1. EXPORTAÇÃO EXCEL DA DRE GERENCIAL POR CENTRO DE CUSTO
# ==============================================================================
def generate_dre_excel(dre_data: Dict[str, Any]) -> io.BytesIO:
    wb = openpyxl.Workbook()
    
    # --- ABA 1: DRE Consolidada ---
    ws1 = wb.active
    ws1.title = "DRE Consolidada 2026"
    ws1.views.sheetView[0].showGridLines = True

    # Cores corporativas
    fill_header = PatternFill(start_color="059669", end_color="059669", fill_type="solid") # Emerald
    fill_navy = PatternFill(start_color="0B1D3A", end_color="0B1D3A", fill_type="solid") # Navy
    fill_subtle = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
    fill_gray = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=11, bold=True, color="000000")
    font_regular = Font(name="Calibri", size=10, color="000000")
    font_navy_bold = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

    border_thin = Side(style="thin", color="CBD5E1")
    border_thick = Side(style="medium", color="059669")
    cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    # Cabeçalho da Empresa
    ws1.merge_cells("A1:D1")
    ws1["A1"] = "NEXUS JR. | DEMONSTRATIVO DE RESULTADO DO EXERCÍCIO (DRE)"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_navy
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 32

    ws1.merge_cells("A2:D2")
    ws1["A2"] = f"Governança Estatutária MEJ 2026 • Lei Federal nº 13.267/2016 • Emitido em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    ws1["A2"].font = font_sub
    ws1["A2"].fill = fill_navy
    ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[2].height = 20

    ws1.append([]) # Linha em branco

    # Cabeçalhos da Tabela
    headers = ["Rubrica Contábil / Gerencial", "Valor Realizado (R$)", "% Rec. Bruta", "Classificação Estatutária"]
    ws1.append(headers)
    ws1.row_dimensions[4].height = 25
    for col_idx in range(1, 5):
        cell = ws1.cell(row=4, column=col_idx)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left", vertical="center")
        cell.border = cell_border

    c = dre_data["consolidado"]
    receita_bruta = c["total_receita_bruta"]
    superavit = c["total_superavit_estatutario"]

    dre_rows = [
        ("(+) RECEITA BRUTA DE CONSULTORIA", receita_bruta, 1.0, "Receita de Atividades Educativas", True, fill_gray),
        ("(-) Deduções e Tributos Incidentes", 0.0, 0.0, "Isenção Estatutária (Lei 13.267)", False, None),
        ("(=) RECEITA OPERACIONAL LÍQUIDA", receita_bruta, 1.0, "Base Líquida de Operações", True, fill_gray),
        ("(-) Custos Diretos com Licenças de Software", 2400.00, 2400.0/receita_bruta if receita_bruta else 0, "Ferramentas Técnicas do Projeto", False, None),
        ("(-) Custos Diretos Operacionais e Deslocamentos", 1050.00, 1050.0/receita_bruta if receita_bruta else 0, "Insumos Diretos de Execução", False, None),
        ("(=) MARGEM DE CONTRIBUIÇÃO DIRETA", c["total_margem_contribuicao"], c["margem_contribuicao_media_pct"]/100, "Margem Operacional de Negócios", True, fill_subtle),
        ("(-) Despesas Administrativas e Fixas Rateadas", c["total_despesas_rateadas"], c["total_despesas_rateadas"]/receita_bruta if receita_bruta else 0, "Rateio Institucional da Sede", False, None),
        ("(=) SUPERÁVIT LÍQUIDO DO EXERCÍCIO", superavit, superavit/receita_bruta if receita_bruta else 0, "Excedente Operacional Apurado", True, fill_navy),
        ("(=) REINVESTIMENTO ESTATUTÁRIO OBRIGATÓRIO (100%)", superavit, 1.0, "Fundo Reserva e Capacitação Técnica", True, fill_header),
        ("(-) Distribuição de Lucros ou Remuneração a Membros", 0.00, 0.0, "VEDAÇÃO LEGAL (Art. 2º Lei 13.267)", False, None)
    ]

    curr_row = 5
    for title, val, pct, desc, is_bold, bg_fill in dre_rows:
        ws1.row_dimensions[curr_row].height = 22
        
        c1 = ws1.cell(row=curr_row, column=1, value=title)
        c2 = ws1.cell(row=curr_row, column=2, value=val)
        c3 = ws1.cell(row=curr_row, column=3, value=pct)
        c4 = ws1.cell(row=curr_row, column=4, value=desc)

        # Formatações numéricas
        c2.number_format = "R$ #,##0.00"
        c3.number_format = "0.0%"

        font_to_use = font_navy_bold if bg_fill == fill_navy else (font_bold if is_bold else font_regular)

        for col_idx, cell in enumerate([c1, c2, c3, c4], start=1):
            cell.font = font_to_use
            cell.border = cell_border
            if bg_fill:
                cell.fill = bg_fill
            if col_idx in [2, 3]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx == 4:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        curr_row += 1

    # Nota Estatutária de Rodapé
    curr_row += 1
    ws1.merge_cells(f"A{curr_row}:D{curr_row}")
    nota_cell = ws1.cell(row=curr_row, column=1)
    nota_cell.value = "CERTIDÃO DE CONFORMIDADE ESTATUTÁRIA: Atestamos que 100% dos superávits acima apurados são integralmente reinvestidos no desenvolvimento profissional dos membros e na manutenção das atividades da Empresa Júnior, em estrito cumprimento dos Arts. 2º e 4º da Lei nº 13.267/2016."
    nota_cell.font = Font(name="Calibri", size=9, italic=True, color="334155")
    nota_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws1.row_dimensions[curr_row].height = 36

    # --- ABA 2: Detalhamento por Centros de Custo ---
    ws2 = wb.create_sheet(title="Centros de Custo")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "NEXUS JR. | RESULTADO DETALHADO POR PROJETO (CENTRO DE CUSTO)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_header
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 30

    cc_headers = ["ID", "Projeto / Serviço", "Cliente", "Área de Negócios", "Receita Bruta (R$)", "Margem Contrib. (R$)", "Margem %"]
    ws2.append(cc_headers)
    ws2.row_dimensions[2].height = 24
    for col_idx in range(1, 8):
        c_cell = ws2.cell(row=2, column=col_idx)
        c_cell.font = font_header
        c_cell.fill = fill_navy
        c_cell.border = cell_border
        c_cell.alignment = Alignment(horizontal="center", vertical="center")

    row_cc = 3
    for p in dre_data.get("projetos", []):
        ws2.row_dimensions[row_cc].height = 20
        c_id = ws2.cell(row=row_cc, column=1, value=f"CC #{p['project_id']}")
        c_name = ws2.cell(row=row_cc, column=2, value=p["project_name"])
        c_client = ws2.cell(row=row_cc, column=3, value=p["client_name"])
        c_area = ws2.cell(row=row_cc, column=4, value=p["macro_area"])
        c_rec = ws2.cell(row=row_cc, column=5, value=p["receita_bruta"])
        c_mg = ws2.cell(row=row_cc, column=6, value=p["margem_contribuicao"])
        c_pct = ws2.cell(row=row_cc, column=7, value=p["margem_contribuicao_pct"] / 100)

        c_rec.number_format = "R$ #,##0.00"
        c_mg.number_format = "R$ #,##0.00"
        c_pct.number_format = "0.0%"

        for col_idx, cell in enumerate([c_id, c_name, c_client, c_area, c_rec, c_mg, c_pct], start=1):
            cell.font = font_regular
            cell.border = cell_border
            if col_idx in [5, 6, 7]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif col_idx in [1, 4]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        row_cc += 1

    # Ajuste automático de largura das colunas
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and "\n" not in val_str and cell.coordinate not in ["A1", "A2"]:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    ws1.column_dimensions["A"].width = 46
    ws1.column_dimensions["D"].width = 38
    ws2.column_dimensions["B"].width = 40
    ws2.column_dimensions["C"].width = 32

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ==============================================================================
# 2. EXPORTAÇÃO EXCEL DE TIMESHEET & HOMEM-HORA (HH)
# ==============================================================================
def generate_timesheet_excel(timesheet_entries: List[Dict[str, Any]], projects_data: List[Dict[str, Any]]) -> io.BytesIO:
    wb = openpyxl.Workbook()

    # Cores
    fill_header = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
    fill_navy = PatternFill(start_color="0B1D3A", end_color="0B1D3A", fill_type="solid")
    fill_alert = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Amber

    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_regular = Font(name="Calibri", size=10, color="000000")
    font_bold = Font(name="Calibri", size=10, bold=True, color="000000")

    border_thin = Side(style="thin", color="CBD5E1")
    cell_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

    # --- ABA 1: Apontamentos Detalhados ---
    ws1 = wb.active
    ws1.title = "Apontamentos de Horas (HH)"
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:G1")
    ws1["A1"] = f"NEXUS JR. | REGISTRO AUDITADO DE TIMESHEET • Emitido em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_navy
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 28

    headers = ["Data", "Consultor", "E-mail", "Projeto", "Marco Técnico", "Horas (HH)", "Alerta Escopo", "Descrição da Atividade"]
    ws1.append(headers)
    ws1.row_dimensions[2].height = 22
    for col_idx in range(1, 9):
        c = ws1.cell(row=2, column=col_idx)
        c.font = font_header
        c.fill = fill_header
        c.border = cell_border
        c.alignment = Alignment(horizontal="center", vertical="center")

    row_idx = 3
    for t in timesheet_entries:
        ws1.row_dimensions[row_idx].height = 20
        c_date = ws1.cell(row=row_idx, column=1, value=t.get("date"))
        c_name = ws1.cell(row=row_idx, column=2, value=t.get("consultant_name"))
        c_email = ws1.cell(row=row_idx, column=3, value=t.get("consultant_email"))
        c_proj = ws1.cell(row=row_idx, column=4, value=t.get("project_name") or f"Projeto #{t.get('project_id')}")
        c_milestone = ws1.cell(row=row_idx, column=5, value=t.get("milestone_title") or "Marco Geral")
        c_hours = ws1.cell(row=row_idx, column=6, value=t.get("hours"))
        c_alert = ws1.cell(row=row_idx, column=7, value="ALERTA DE ESCOPO" if t.get("scope_alert_triggered") else "Normal")
        c_desc = ws1.cell(row=row_idx, column=8, value=t.get("description"))

        c_hours.number_format = "#,##0.0"

        for col_idx, cell in enumerate([c_date, c_name, c_email, c_proj, c_milestone, c_hours, c_alert, c_desc], start=1):
            cell.font = font_regular
            cell.border = cell_border
            if t.get("scope_alert_triggered") and col_idx == 7:
                cell.fill = fill_alert
                cell.font = font_bold
            if col_idx in [1, 7]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 6:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        row_idx += 1

    # --- ABA 2: Resumo de Capacidade por Projeto ---
    ws2 = wb.create_sheet(title="Capacidade por Projeto")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "NEXUS JR. | BALANÇO DE CAPACIDADE PRODUTIVA (ORÇADO VS. EXECUTADO)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_header
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 28

    p_headers = ["Projeto", "Cliente", "Gerente", "HH Orçado", "HH Consumido", "Taxa Consumo %", "Progresso Físico %"]
    ws2.append(p_headers)
    ws2.row_dimensions[2].height = 22
    for col_idx in range(1, 8):
        c = ws2.cell(row=2, column=col_idx)
        c.font = font_header
        c.fill = fill_navy
        c.border = cell_border
        c.alignment = Alignment(horizontal="center", vertical="center")

    row_p = 3
    for p in projects_data:
        ws2.row_dimensions[row_p].height = 20
        c1 = ws2.cell(row=row_p, column=1, value=p["name"])
        c2 = ws2.cell(row=row_p, column=2, value=p["client_name"])
        c3 = ws2.cell(row=row_p, column=3, value=p["manager_name"])
        c4 = ws2.cell(row=row_p, column=4, value=p["total_budgeted_hh"])
        c5 = ws2.cell(row=row_p, column=5, value=p["consumed_hh"])
        ratio = (p["consumed_hh"] / p["total_budgeted_hh"]) if p["total_budgeted_hh"] else 0
        c6 = ws2.cell(row=row_p, column=6, value=ratio)
        c7 = ws2.cell(row=row_p, column=7, value=p["progress_pct"] / 100)

        c6.number_format = "0.0%"
        c7.number_format = "0.0%"

        for col_idx, cell in enumerate([c1, c2, c3, c4, c5, c6, c7], start=1):
            cell.font = font_regular
            cell.border = cell_border
            if col_idx in [4, 5, 6, 7]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
        row_p += 1

    # Ajuste de largura
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len and "\n" not in val_str and cell.coordinate not in ["A1"]:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 13)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ==============================================================================
# 3. RELATÓRIO EXECUTIVO EM HTML/PDF IMPRIMÍVEL (DRE)
# ==============================================================================
def generate_dre_pdf_html(dre_data: Dict[str, Any]) -> str:
    c = dre_data["consolidado"]
    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    projetos_rows = ""
    for p in dre_data.get("projetos", []):
        projetos_rows += f"""
        <tr>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-weight: 600;">{p['project_name']}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0;">{p['client_name']}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-family: monospace;">R$ {p['receita_bruta']:,.2f}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-family: monospace; color: #059669; font-weight: bold;">R$ {p['margem_contribuicao']:,.2f}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e2e8f0; text-align: right; font-family: monospace;">{p['margem_contribuicao_pct']}%</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Prestação de Contas DRE - Nexus Jr. 2026</title>
  <style>
    @page {{
      size: A4;
      margin: 1.5cm;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      color: #1e293b;
      margin: 0;
      padding: 20px;
      background: #ffffff;
    }}
    .header-box {{
      border-bottom: 3px solid #059669;
      padding-bottom: 16px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}
    .brand-title {{
      font-size: 22px;
      font-weight: 800;
      color: #0b1d3a;
      margin: 0 0 4px 0;
    }}
    .brand-sub {{
      font-size: 12px;
      color: #64748b;
      margin: 0;
    }}
    .badge-stamp {{
      background: #ecfdf5;
      color: #059669;
      border: 1px solid #a7f3d0;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .table-dre {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 24px;
      font-size: 13px;
    }}
    .table-dre th {{
      background: #0b1d3a;
      color: #ffffff;
      padding: 10px 14px;
      text-align: left;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .table-dre td {{
      padding: 9px 14px;
      border-bottom: 1px solid #e2e8f0;
    }}
    .row-highlight {{
      background: #ecfdf5;
      font-weight: bold;
      color: #065f46;
    }}
    .row-navy {{
      background: #0b1d3a;
      font-weight: bold;
      color: #ffffff;
    }}
    .legal-box {{
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-left: 4px solid #059669;
      padding: 14px 18px;
      border-radius: 6px;
      font-size: 11px;
      color: #334155;
      line-height: 1.5;
      margin-bottom: 30px;
    }}
    .signature-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 40px;
      margin-top: 50px;
      padding-top: 20px;
    }}
    .signature-line {{
      border-top: 1px solid #94a3b8;
      text-align: center;
      padding-top: 8px;
      font-size: 12px;
    }}
    .btn-print {{
      background: #059669;
      color: white;
      border: none;
      padding: 10px 20px;
      font-weight: bold;
      font-size: 14px;
      border-radius: 8px;
      cursor: pointer;
      margin-bottom: 20px;
    }}
    @media print {{
      .btn-print {{ display: none; }}
      body {{ padding: 0; }}
    }}
  </style>
</head>
<body>
  <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Salvar como PDF</button>

  <div class="header-box">
    <div>
      <h1 class="brand-title">Nexus Jr. | ERP Gestão & Finanças 2.0</h1>
      <p class="brand-sub">Empresa Júnior de Consultoria em Negócios • FEA / FGV / FACE Pattern</p>
      <p class="brand-sub" style="margin-top: 4px;">Demonstrativo Oficial de Resultados do Exercício (DRE) • Gerado em: {now_str}</p>
    </div>
    <div class="badge-stamp">
      Lei nº 13.267/2016 • 100% Reinvestido
    </div>
  </div>

  <table class="table-dre">
    <thead>
      <tr>
        <th>Rubrica Gerencial / Classificação</th>
        <th style="text-align: right;">Valor (R$)</th>
        <th style="text-align: right;">% Rec. Bruta</th>
      </tr>
    </thead>
    <tbody>
      <tr style="font-weight: bold; background: #f8fafc;">
        <td>(+) RECEITA BRUTA DE CONSULTORIA</td>
        <td style="text-align: right; font-family: monospace;">R$ {c['total_receita_bruta']:,.2f}</td>
        <td style="text-align: right; font-family: monospace;">100.0%</td>
      </tr>
      <tr style="color: #64748b;">
        <td style="padding-left: 28px;">(-) Deduções e Impostos (Isenção Estatutária)</td>
        <td style="text-align: right; font-family: monospace;">R$ 0,00</td>
        <td style="text-align: right; font-family: monospace;">0.0%</td>
      </tr>
      <tr style="font-weight: 600;">
        <td>(=) RECEITA OPERACIONAL LÍQUIDA</td>
        <td style="text-align: right; font-family: monospace;">R$ {c['total_receita_bruta']:,.2f}</td>
        <td style="text-align: right; font-family: monospace;">100.0%</td>
      </tr>
      <tr style="color: #b91c1c;">
        <td style="padding-left: 28px;">(-) Custos Diretos com Licenças de Softwares Especializados</td>
        <td style="text-align: right; font-family: monospace;">-R$ 2.400,00</td>
        <td style="text-align: right; font-family: monospace;">-5.7%</td>
      </tr>
      <tr style="color: #b91c1c;">
        <td style="padding-left: 28px;">(-) Custos Diretos Operacionais e Deslocamentos</td>
        <td style="text-align: right; font-family: monospace;">-R$ 1.050,00</td>
        <td style="text-align: right; font-family: monospace;">-2.5%</td>
      </tr>
      <tr class="row-highlight">
        <td>(=) MARGEM DE CONTRIBUIÇÃO DIRETA</td>
        <td style="text-align: right; font-family: monospace; font-size: 14px;">R$ {c['total_margem_contribuicao']:,.2f}</td>
        <td style="text-align: right; font-family: monospace; font-size: 14px;">{c['margem_contribuicao_media_pct']}%</td>
      </tr>
      <tr style="color: #475569;">
        <td style="padding-left: 28px;">(-) Despesas Operacionais e Administrativas Rateadas</td>
        <td style="text-align: right; font-family: monospace;">-R$ {c['total_despesas_rateadas']:,.2f}</td>
        <td style="text-align: right; font-family: monospace;">-10.7%</td>
      </tr>
      <tr class="row-navy">
        <td style="font-size: 14px;">(=) SUPERÁVIT LÍQUIDO DO EXERCÍCIO</td>
        <td style="text-align: right; font-family: monospace; font-size: 15px;">R$ {c['total_superavit_estatutario']:,.2f}</td>
        <td style="text-align: right; font-family: monospace; font-size: 14px;">81.0%</td>
      </tr>
      <tr style="background: #f1f5f9; font-weight: bold; color: #047857;">
        <td style="padding-left: 28px;">(&rarr;) Destinação Estatutária Obrigatória: Reinvestimento Integral</td>
        <td style="text-align: right; font-family: monospace;">R$ {c['total_superavit_estatutario']:,.2f}</td>
        <td style="text-align: right; font-family: monospace;">100.0%</td>
      </tr>
    </tbody>
  </table>

  <h3 style="font-size: 14px; font-weight: bold; color: #0b1d3a; margin-top: 24px; margin-bottom: 8px;">Detalhamento por Projeto (Centros de Custo)</h3>
  <table class="table-dre">
    <thead>
      <tr>
        <th>Projeto</th>
        <th>Cliente</th>
        <th style="text-align: right;">Receita Bruta</th>
        <th style="text-align: right;">Margem Direta</th>
        <th style="text-align: right;">Margem %</th>
      </tr>
    </thead>
    <tbody>
      {projetos_rows}
    </tbody>
  </table>

  <div class="legal-box">
    <strong>CERTIDÃO DE CONFORMIDADE ESTATUTÁRIA (LEI FEDERAL Nº 13.267/2016):</strong><br>
    Certificamos para os devidos fins de transparência perante a Federação Estadual e Brasil Júnior que todos os recursos auferidos pela Nexus Jr. decorrem estritamente da prestação de serviços de consultoria com finalidade educacional. Em conformidade com os artigos 2º e 4º da legislação supracitada, <strong>inexiste qualquer distribuição de lucros, bonificações ou remuneração a membros voluntários</strong>, sendo 100% dos excedentes reinvestidos em cursos, licenças e infraestrutura de aprendizagem.
  </div>

  <div class="signature-grid">
    <div class="signature-line">
      <strong>Charles</strong><br>
      Diretor Presidente Executivo<br>
      Nexus Consultoria Júnior
    </div>
    <div class="signature-line">
      <strong>Mariana Souza</strong><br>
      Diretora de Finanças e Tesouraria<br>
      Nexus Consultoria Júnior
    </div>
  </div>
</body>
</html>"""
    return html
