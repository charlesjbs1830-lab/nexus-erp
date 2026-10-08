/**
 * Nexus Jr. | ERP Gestão & Finanças 2.0
 * mock_backend.js - Motor Standalone / GitHub Pages Demo
 * Permite que o sistema execute 100% interativo e sem erros no GitHub Pages
 * ou em qualquer ambiente estático sem servidor Python ativo.
 */

(function () {
  "use strict";

  const STORAGE_KEY = "nexus_mock_db_v2";

  // 1. DADOS INICIAIS OFICIAIS CJA CONSULTORIA EMPRESARIAL
  const DEFAULT_DB = {
    services: [
      {
        id: 1,
        macro_area: "Gestão de Processos",
        name: "Mapeamento de Processos",
        code: "CJA-PRC-MAP",
        lead_time_min_weeks: 6,
        lead_time_max_weeks: 10,
        default_hh: 80,
        recommended_seniority: "Consultor Pleno / Especialista",
        hourly_rate: 85.0,
        description: "Foco em organização de operações, aumento de eficiência, identificação de falhas e gargalos.",
        deliverables: "Mapeamento AS-IS e TO-BE em Notação BPMN, Matriz de Gargalos e Falhas, Manual de Procedimentos Operacionais (POPs) e Recomendações de Otimização.",
        statutory_margin_pct: 0.15
      },
      {
        id: 2,
        macro_area: "Finanças e Contabilidade",
        name: "Consultoria Financeira",
        code: "CJA-FIN-CONS",
        lead_time_min_weeks: 8,
        lead_time_max_weeks: 12,
        default_hh: 100,
        recommended_seniority: "Consultor Pleno / Especialista",
        hourly_rate: 85.0,
        description: "Controle total da saúde financeira, análise de entradas/saídas e otimização de caixa.",
        deliverables: "Diagnóstico Econômico-Financeiro, Estruturação de Fluxo de Caixa Diário/Mensal, Análise de Capital de Giro e Painel de Indicadores de Liquidez.",
        statutory_margin_pct: 0.15
      },
      {
        id: 3,
        macro_area: "Finanças e Contabilidade",
        name: "Assessoria Contábil",
        code: "CJA-FIN-CONT",
        lead_time_min_weeks: 12,
        lead_time_max_weeks: 24,
        default_hh: 120,
        recommended_seniority: "Consultor Pleno / Especialista",
        hourly_rate: 85.0,
        description: "Simplificação de gestão contábil, declarações, obrigações acessórias e organização fiscal.",
        deliverables: "Relatório de Conciliação e Regularidade Fiscal, Livro Caixa/Balancetes Gerenciais, Calendário de Obrigações Acessórias e Manual de Boas Práticas Fiscais.",
        statutory_margin_pct: 0.15
      },
      {
        id: 4,
        macro_area: "Inteligência de Mercado & Experiência do Cliente",
        name: "Cliente Oculto",
        code: "CJA-MKT-OCUL",
        lead_time_min_weeks: 4,
        lead_time_max_weeks: 8,
        default_hh: 50,
        recommended_seniority: "Consultor Júnior",
        hourly_rate: 55.0,
        description: "Análise estratégica de atendimento, processos e concorrência no ponto de venda.",
        deliverables: "Roteiro de Auditoria Oculta, Avaliação de Atendimento por Dimensões, Relatório de Pontos Críticos e Plano de Melhoria da Experiência do Cliente.",
        statutory_margin_pct: 0.15
      },
      {
        id: 5,
        macro_area: "Inteligência de Mercado & Experiência do Cliente",
        name: "Pesquisa de Mercado",
        code: "CJA-MKT-PESQ",
        lead_time_min_weeks: 6,
        lead_time_max_weeks: 10,
        default_hh: 70,
        recommended_seniority: "Consultor Júnior",
        hourly_rate: 55.0,
        description: "Análise de comportamento, público-alvo, demanda e mitigação de riscos de investimentos.",
        deliverables: "Relatório Analítico de Mercado com Amostragem Estatística (95% IC), Mapeamento de Personas, Benchmarking Concorrencial e Matriz de Riscos.",
        statutory_margin_pct: 0.15
      },
      {
        id: 6,
        macro_area: "Inteligência de Mercado & Experiência do Cliente",
        name: "Pesquisa de Satisfação",
        code: "CJA-MKT-SATIS",
        lead_time_min_weeks: 4,
        lead_time_max_weeks: 6,
        default_hh: 40,
        recommended_seniority: "Consultor Júnior",
        hourly_rate: 55.0,
        description: "Avaliação de percepção de clientes/colaboradores (eNPS/CSAT) para melhoria de retenção.",
        deliverables: "Painel de Indicadores eNPS e CSAT, Diagnóstico de Percepção por Atributo, Análise de Feedbacks e Plano de Ação para Retenção de Clientes.",
        statutory_margin_pct: 0.15
      },
      {
        id: 7,
        macro_area: "Planejamento Estratégico & Marketing",
        name: "Plano de Negócios",
        code: "CJA-EST-PLNEG",
        lead_time_min_weeks: 8,
        lead_time_max_weeks: 14,
        default_hh: 110,
        recommended_seniority: "Gerente de Projetos",
        hourly_rate: 120.0,
        description: "Estruturação de ideias, viabilidade econômica, análise de riscos e crescimento sustentável.",
        deliverables: "Documento Completo de Plano de Negócios, Estudo de Viabilidade Econômico-Financeira (VPL, TIR, Payback), Plano Operacional e Sumário Executivo.",
        statutory_margin_pct: 0.15
      },
      {
        id: 8,
        macro_area: "Planejamento Estratégico & Marketing",
        name: "Plano de Marketing",
        code: "CJA-EST-PLMKT",
        lead_time_min_weeks: 6,
        lead_time_max_weeks: 10,
        default_hh: 90,
        recommended_seniority: "Consultor Pleno / Especialista",
        hourly_rate: 85.0,
        description: "Estratégias de atração, conversão, retenção e posicionamento de marca.",
        deliverables: "Diagnóstico de Branding e Posicionamento, Estratégia dos 4 Ps, Cronograma de Campanhas, Planejamento de Mídia e Funil de Vendas.",
        statutory_margin_pct: 0.15
      }
    ],

    projects: [
      {
        id: 1,
        name: "Mapeamento de Processos de Suprimentos",
        client_name: "TechInovação Software Ltda.",
        service_name: "Mapeamento de Processos",
        macro_area: "Gestão de Processos",
        lead_time_weeks: 8,
        total_budgeted_hh: 80,
        consumed_hh: 52.0,
        progress_pct: 65.0,
        status: "em_andamento",
        start_date: "2026-02-01",
        expected_end_date: "2026-04-01",
        manager_name: "Gabriel Martins",
        scope_creep_alert: false,
        scope_alerts: [],
        milestones: [
          { id: 1, project_id: 1, phase_name: "Alinhamento e Mapeamento AS-IS dos Processos", title: "Alinhamento e Mapeamento AS-IS dos Processos", week_start: 1, week_end: 2, budgeted_hh: 20, consumed_hh: 20.0, progress_pct: 100.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "concluido" },
          { id: 2, project_id: 1, phase_name: "Identificação de Falhas Operacionais e Gargalos", title: "Identificação de Falhas Operacionais e Gargalos", week_start: 3, week_end: 4, budgeted_hh: 28, consumed_hh: 26.6, progress_pct: 80.0, is_critical_path: 1, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "em_andamento" },
          { id: 3, project_id: 1, phase_name: "Modelagem TO-BE Otimizada (BPMN) & Validação Técnica", title: "Modelagem TO-BE Otimizada (BPMN) & Validação Técnica", week_start: 5, week_end: 6, budgeted_hh: 20, consumed_hh: 5.4, progress_pct: 25.0, is_critical_path: 1, requires_mentor_approval: 1, mentor_approval_status: "pendente", status: "pendente" },
          { id: 4, project_id: 1, phase_name: "Manualização de POPs e Apresentação de Resultados", title: "Manualização de POPs e Apresentação de Resultados", week_start: 7, week_end: 8, budgeted_hh: 12, consumed_hh: 0.0, progress_pct: 0.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "pendente" }
        ]
      },
      {
        id: 2,
        name: "Consultoria Financeira e Gestão de Caixa",
        client_name: "Vix Logística e Transportes S/A",
        service_name: "Consultoria Financeira",
        macro_area: "Finanças e Contabilidade",
        lead_time_weeks: 10,
        total_budgeted_hh: 100,
        consumed_hh: 38.0,
        progress_pct: 38.0,
        status: "em_andamento",
        start_date: "2026-02-15",
        expected_end_date: "2026-05-10",
        manager_name: "Lucas Rezende",
        scope_creep_alert: false,
        scope_alerts: [],
        milestones: [
          { id: 5, project_id: 2, phase_name: "Diagnóstico Financeiro & Levantamento de Entradas/Saídas", title: "Diagnóstico Financeiro & Levantamento de Entradas/Saídas", week_start: 1, week_end: 2, budgeted_hh: 25, consumed_hh: 25.0, progress_pct: 100.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "concluido" },
          { id: 6, project_id: 2, phase_name: "Estruturação de Contas e Conciliação Operacional", title: "Estruturação de Contas e Conciliação Operacional", week_start: 3, week_end: 5, budgeted_hh: 35, consumed_hh: 13.0, progress_pct: 40.0, is_critical_path: 1, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "em_andamento" },
          { id: 7, project_id: 2, phase_name: "Modelagem de Fluxo de Caixa & Parecer Financeiro", title: "Modelagem de Fluxo de Caixa & Parecer Financeiro", week_start: 6, week_end: 8, budgeted_hh: 25, consumed_hh: 0.0, progress_pct: 0.0, is_critical_path: 1, requires_mentor_approval: 1, mentor_approval_status: "pendente", status: "pendente" },
          { id: 8, project_id: 2, phase_name: "Dashboard de Gestão de Caixa & Treinamento de Sócios", title: "Dashboard de Gestão de Caixa & Treinamento de Sócios", week_start: 9, week_end: 10, budgeted_hh: 15, consumed_hh: 0.0, progress_pct: 0.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "pendente" }
        ]
      },
      {
        id: 3,
        name: "Auditoria de Atendimento e Cliente Oculto",
        client_name: "Rede Farmacêutica Capixaba",
        service_name: "Cliente Oculto",
        macro_area: "Inteligência de Mercado & Experiência do Cliente",
        lead_time_weeks: 6,
        total_budgeted_hh: 50,
        consumed_hh: 42.0,
        progress_pct: 84.0,
        status: "em_andamento",
        start_date: "2026-01-20",
        expected_end_date: "2026-04-05",
        manager_name: "Beatriz Andrade",
        scope_creep_alert: false,
        scope_alerts: [],
        milestones: [
          { id: 9, project_id: 3, phase_name: "Desenho dos Cenários e Roteiro de Avaliação PDV", title: "Desenho dos Cenários e Roteiro de Avaliação PDV", week_start: 1, week_end: 2, budgeted_hh: 15, consumed_hh: 15.0, progress_pct: 100.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "concluido" },
          { id: 10, project_id: 3, phase_name: "Execução de Campo / Visitas de Auditoria Oculta", title: "Execução de Campo / Visitas de Auditoria Oculta", week_start: 3, week_end: 4, budgeted_hh: 20, consumed_hh: 20.0, progress_pct: 100.0, is_critical_path: 1, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "concluido" },
          { id: 11, project_id: 3, phase_name: "Análise Consolidada de Dados e Relatório com Trava de Mentor", title: "Análise Consolidada de Dados e Relatório com Trava de Mentor", week_start: 5, week_end: 6, budgeted_hh: 15, consumed_hh: 7.0, progress_pct: 50.0, is_critical_path: 1, requires_mentor_approval: 1, mentor_approval_status: "pendente", status: "em_andamento" }
        ]
      },
      {
        id: 4,
        name: "Estruturação de Plano de Negócios 2026",
        client_name: "Café Exportação Conilon",
        service_name: "Plano de Negócios",
        macro_area: "Planejamento Estratégico & Marketing",
        lead_time_weeks: 10,
        total_budgeted_hh: 110,
        consumed_hh: 45.0,
        progress_pct: 41.0,
        status: "em_andamento",
        start_date: "2026-02-10",
        expected_end_date: "2026-04-10",
        manager_name: "Charles (Presidente)",
        scope_creep_alert: false,
        scope_alerts: [],
        milestones: [
          { id: 12, project_id: 4, phase_name: "Concepção do Negócio e Análise Mercadológica", title: "Concepção do Negócio e Análise Mercadológica", week_start: 1, week_end: 2, budgeted_hh: 22, consumed_hh: 22.0, progress_pct: 100.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "concluido" },
          { id: 13, project_id: 4, phase_name: "Planejamento Operacional e Estruturação de Marketing", title: "Planejamento Operacional e Estruturação de Marketing", week_start: 3, week_end: 5, budgeted_hh: 33, consumed_hh: 23.0, progress_pct: 70.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "em_andamento" },
          { id: 14, project_id: 4, phase_name: "Modelagem Econômico-Financeira (VPL, TIR, Payback) e Trava", title: "Modelagem Econômico-Financeira (VPL, TIR, Payback) e Trava", week_start: 6, week_end: 8, budgeted_hh: 38, consumed_hh: 0.0, progress_pct: 0.0, is_critical_path: 1, requires_mentor_approval: 1, mentor_approval_status: "pendente", status: "pendente" },
          { id: 15, project_id: 4, phase_name: "Sumário Executivo e Apresentação para Investidores", title: "Sumário Executivo e Apresentação para Investidores", week_start: 9, week_end: 10, budgeted_hh: 17, consumed_hh: 0.0, progress_pct: 0.0, is_critical_path: 0, requires_mentor_approval: 0, mentor_approval_status: "nao_requerido", status: "pendente" }
        ]
      }
    ],

    assets: [
      { id: 1, macro_area: "Gestão de Processos", service_name: "Mapeamento de Processos", asset_code: "MOD-CJA-PRC-01", title: "Kit Metodológico de Mapeamento de Processos & POPs.docx", file_format: ".docx", version: "v2.1", version_notes: "Framework padronizado para entrevistas AS-IS, notação BPMN 2.0 e templates de POPs operacionais.", author_member: "Pedro Henrique Alves", validator_mentor: "Prof. Me. André Ramos (Engenharia de Produção)", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-PRC-01_Mapeamento_Processos.docx", file_size: "1.4 MB", downloads_count: 38 },
      { id: 2, macro_area: "Finanças e Contabilidade", service_name: "Consultoria Financeira", asset_code: "MOD-CJA-FIN-01", title: "Modelo de Diagnóstico Financeiro e Gestão de Caixa.xlsx", file_format: ".xlsx", version: "v4.1", version_notes: "Planilha paramétrica com fluxo de caixa diário/mensal, conciliação e indicadores de liquidez e capital de giro.", author_member: "Lucas Rezende (Consultor Pleno)", validator_mentor: "Prof. Dr. Marcos Silveira (Finanças / UFES)", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-FIN-01_Diagnostico_Caixa_v4.1.xlsx", file_size: "2.1 MB", downloads_count: 45 },
      { id: 3, macro_area: "Finanças e Contabilidade", service_name: "Assessoria Contábil", asset_code: "MOD-CJA-FIN-02", title: "Manual de Obrigações Acessórias e Assessoria Contábil.pdf", file_format: ".pdf", version: "v2.5", version_notes: "Guia prático de rotinas fiscais preventivas, plano de contas gerencial e calendário de obrigações contábeis.", author_member: "Mariana Souza (Diretora de Finanças)", validator_mentor: "Conselho Fiscal CJA Consultoria", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-FIN-02_Manual_Contabil_v2.5.pdf", file_size: "980 KB", downloads_count: 27 },
      { id: 4, macro_area: "Inteligência de Mercado & Experiência do Cliente", service_name: "Cliente Oculto", asset_code: "MOD-CJA-MKT-01", title: "Template de Relatório de Cliente Oculto.docx", file_format: ".docx", version: "v2.0", version_notes: "Matriz de auditoria de atendimento no ponto de venda, roteiro de visitas e plano de ação corretiva.", author_member: "Camila Nogueira (Consultora de Mercado)", validator_mentor: "Prof. Dr. Ricardo Ramos (Marketing)", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-MKT-01_Cliente_Oculto.docx", file_size: "850 KB", downloads_count: 31 },
      { id: 5, macro_area: "Inteligência de Mercado & Experiência do Cliente", service_name: "Pesquisa de Mercado", asset_code: "MOD-CJA-MKT-02", title: "Planilha de Dimensionamento de Pesquisa de Mercado.xlsx", file_format: ".xlsx", version: "v3.2", version_notes: "Calculadora de amostragem probabilística (IC 95%), matriz de tabulação quanti/quali e análise de concorrência.", author_member: "Beatriz Lima (Diretora Comercial)", validator_mentor: "Prof. Dr. Ricardo Ramos (Marketing)", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-MKT-02_Pesquisa_Mercado.xlsx", file_size: "1.7 MB", downloads_count: 42 },
      { id: 6, macro_area: "Inteligência de Mercado & Experiência do Cliente", service_name: "Pesquisa de Satisfação", asset_code: "MOD-CJA-MKT-03", title: "Instrumento de Pesquisa de Satisfação & Análise eNPS.xlsx", file_format: ".xlsx", version: "v2.1", version_notes: "Régua de avaliação CSAT e eNPS com dashboards de promotores, neutros, detratores e plano de retenção.", author_member: "Camila Nogueira (Consultora de Mercado)", validator_mentor: "Mentoria Alumni CJA", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-MKT-03_Pesquisa_Satisfacao.xlsx", file_size: "1.1 MB", downloads_count: 24 },
      { id: 7, macro_area: "Planejamento Estratégico & Marketing", service_name: "Plano de Negócios", asset_code: "MOD-CJA-EST-01", title: "Modelagem Financeira e Plano de Negócios CJA.xlsx", file_format: ".xlsx", version: "v5.0", version_notes: "Estruturação de viabilidade econômica completa com DRE projetada, VPL, TIR, Payback e análise de cenários.", author_member: "Lucas Mendes (Gerente de Projetos)", validator_mentor: "Prof. Dr. Marcos Silveira (Finanças)", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-EST-01_Plano_Negocios_v5.0.xlsx", file_size: "2.8 MB", downloads_count: 53 },
      { id: 8, macro_area: "Planejamento Estratégico & Marketing", service_name: "Plano de Marketing", asset_code: "MOD-CJA-EST-02", title: "Framework de Plano de Marketing.pptx", file_format: ".pptx", version: "v3.0", version_notes: "Apresentação executiva completa com estratégia dos 4 Ps, funil de atração/conversão e cronograma de campanhas.", author_member: "Beatriz Lima (Diretora Comercial)", validator_mentor: "Mentoria de Estratégia CJA", turnover_cycle: "Ciclo 2026.1", download_url: "/assets/templates/MOD-CJA-EST-02_Framework_Marketing.pptx", file_size: "3.4 MB", downloads_count: 39 }
    ],

    proposals: [
      { id: 1, client_name: "Grupo Industrial Vix S.A.", service_name: "Consultoria Financeira", total_hh: 100, hourly_rate: 85.0, total_price: 13500.0, status: "em_negociacao", contact_name: "Roberto Campos", notes: "Foco em fluxo de caixa e capital de giro." },
      { id: 2, client_name: "Rede Farmacêutica Capixaba", service_name: "Cliente Oculto", total_hh: 50, hourly_rate: 55.0, total_price: 6200.0, status: "proposta_gerada", contact_name: "Marina Duarte", notes: "Auditoria em 6 unidades na Grande Vitória." }
    ],

    dre: [
      { id: 1, project_id: 1, project_name: "Mapeamento de Processos de Suprimentos", client_name: "TechInovação Software Ltda.", macro_area: "Gestão de Processos", receita_bruta: 7800.0, impostos_deducoes: 0.0, receita_liquida: 7800.0, custos_diretos_softwares: 390.0, custos_diretos_operacionais: 156.0, margem_contribuicao: 7254.0, margem_contribuicao_pct: 93.0, despesas_operacionais_rateadas: 780.0, superavit_liquido: 6474.0, reinvestimento_obrigatorio_pct: 1.0, fundo_reserva_capacitacao: 6474.0 },
      { id: 2, project_id: 2, project_name: "Consultoria Financeira e Gestão de Caixa", client_name: "Vix Logística e Transportes S/A", macro_area: "Finanças e Contabilidade", receita_bruta: 13500.0, impostos_deducoes: 0.0, receita_liquida: 13500.0, custos_diretos_softwares: 675.0, custos_diretos_operacionais: 270.0, margem_contribuicao: 12555.0, margem_contribuicao_pct: 93.0, despesas_operacionais_rateadas: 1350.0, superavit_liquido: 11205.0, reinvestimento_obrigatorio_pct: 1.0, fundo_reserva_capacitacao: 11205.0 },
      { id: 3, project_id: 3, project_name: "Auditoria de Atendimento e Cliente Oculto", client_name: "Rede Farmacêutica Capixaba", macro_area: "Inteligência de Mercado & Experiência do Cliente", receita_bruta: 6200.0, impostos_deducoes: 0.0, receita_liquida: 6200.0, custos_diretos_softwares: 310.0, custos_diretos_operacionais: 124.0, margem_contribuicao: 5766.0, margem_contribuicao_pct: 93.0, despesas_operacionais_rateadas: 620.0, superavit_liquido: 5146.0, reinvestimento_obrigatorio_pct: 1.0, fundo_reserva_capacitacao: 5146.0 },
      { id: 4, project_id: 4, project_name: "Estruturação de Plano de Negócios 2026", client_name: "Café Exportação Conilon", macro_area: "Planejamento Estratégico & Marketing", receita_bruta: 14400.0, impostos_deducoes: 0.0, receita_liquida: 14400.0, custos_diretos_softwares: 720.0, custos_diretos_operacionais: 288.0, margem_contribuicao: 13392.0, margem_contribuicao_pct: 93.0, despesas_operacionais_rateadas: 1440.0, superavit_liquido: 11952.0, reinvestimento_obrigatorio_pct: 1.0, fundo_reserva_capacitacao: 11952.0 }
    ],

    timesheet: [
      { id: 1, project_id: 1, milestone_id: 1, consultant_name: "Gabriel Martins", consultant_email: "gabriel.martins@nexusjr.com.br", date: "2026-03-01", hours: 8.0, description: "Entrevistas para mapeamento de processos AS-IS de suprimentos.", task_category: "Mapeamento", scope_alert_triggered: 0 },
      { id: 2, project_id: 1, milestone_id: 2, consultant_name: "Gabriel Martins", consultant_email: "gabriel.martins@nexusjr.com.br", date: "2026-03-05", hours: 9.0, description: "Detecção de gargalos no fluxo de compras e insumos.", task_category: "Diagnóstico", scope_alert_triggered: 1 },
      { id: 3, project_id: 2, milestone_id: 5, consultant_name: "Lucas Rezende", consultant_email: "lucas.rezende@nexusjr.com.br", date: "2026-03-02", hours: 8.0, description: "Auditoria e conciliação bancária de entradas e saídas da Vix Logística.", task_category: "Coleta de Dados", scope_alert_triggered: 0 },
      { id: 4, project_id: 3, milestone_id: 9, consultant_name: "Beatriz Andrade", consultant_email: "beatriz.andrade@nexusjr.com.br", date: "2026-03-04", hours: 6.0, description: "Desenho da matriz de avaliação oculta e cenários de compra.", task_category: "Roteiro PDV", scope_alert_triggered: 0 },
      { id: 5, project_id: 4, milestone_id: 12, consultant_name: "Charles", consultant_email: "charles@nexusjr.com", date: "2026-03-06", hours: 8.0, description: "Pesquisa mercadológica e estruturação do plano de expansão do Café Conilon.", task_category: "Estratégia", scope_alert_triggered: 0 }
    ],

    members: [
      { id: 1, email: "charles@nexusjr.com", nome: "Charles", area: "Presidência", role: "presidente", cargo: "Diretor Presidente", cost_center: "Presidência e Gestão Geral", turnover_cycle: "Ciclo 2025.2 -> 2026.1", status: "ativo" },
      { id: 2, email: "mariana.financas@nexusjr.com", nome: "Mariana Souza", area: "Finanças", role: "diretor", cargo: "Diretora de Finanças", cost_center: "CC #1: Consultoria Financeira", turnover_cycle: "Ciclo 2026.1", status: "ativo" },
      { id: 3, email: "lucas.projetos@nexusjr.com", nome: "Lucas Mendes", area: "Projetos", role: "gerente", cargo: "Gerente de Projetos", cost_center: "CC #2: Plano de Negócios", turnover_cycle: "Ciclo 2026.1", status: "ativo" },
      { id: 4, email: "beatriz.comercial@nexusjr.com", nome: "Beatriz Lima", area: "Comercial", role: "diretor", cargo: "Diretora Comercial", cost_center: "Presidência e Gestão Geral", turnover_cycle: "Ciclo 2026.1", status: "ativo" },
      { id: 5, email: "pedro.consultor@nexusjr.com", nome: "Pedro Henrique Alves", area: "Processos", role: "assessor", cargo: "Consultor Especialista BPMN", cost_center: "CC #3: Mapeamento de Processos", turnover_cycle: "Ciclo 2026.1", status: "ativo" },
      { id: 6, email: "ana.trainee@nexusjr.com", nome: "Ana Clara Silveira", area: "Gente e Gestão", role: "assessor", cargo: "Assessora VPGG", cost_center: "Presidência e Gestão Geral", turnover_cycle: "Ciclo 2026.1", status: "ativo" }
    ],

    activities: [
      { id: 1, actor_name: "Charles", actor_role: "Diretor Presidente", action_type: "mentor_approval", title: "Chancela do Modelo Financeiro", description: "Marco 'Modelagem Financeira e Parecer' chancelado formalmente pelo Prof. Dr. Marcos Silveira.", project_name: "Consultoria Financeira e Gestão de Caixa", created_at: "2026-03-01 10:15" },
      { id: 2, actor_name: "Beatriz Andrade", actor_role: "Gerente de Projetos", action_type: "timesheet", title: "Auditoria de Cliente Oculto", description: "Apontamento de 6h de visitas presenciais em filiais farmacêuticas.", project_name: "Auditoria de Atendimento e Cliente Oculto", created_at: "2026-03-04 14:30" },
      { id: 3, actor_name: "Beatriz Lima", actor_role: "Diretora Comercial", action_type: "cpq_proposal", title: "Proposta Emitida via CPQ", description: "Proposta #1 gerada para Grupo Industrial Vix S.A. no valor de R$ 13.500,00 com 15% de margem estatutária.", project_name: "Pipeline Comercial", created_at: "2026-03-05 16:40" },
      { id: 4, actor_name: "Mariana Souza", actor_role: "Diretora de Finanças", action_type: "finance", title: "Fechamento Mensal DRE", description: "Apurado superávit com 100% destinado ao Fundo de Reserva Técnica (Lei 13.267).", project_name: "Consolidado CJA Consultoria", created_at: "2026-03-06 18:00" }
    ]
  };

  // Carregar DB local ou inicializar
  function getDB() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) return JSON.parse(stored);
    } catch (e) {
      console.warn("Erro ao ler localStorage:", e);
    }
    saveDB(DEFAULT_DB);
    return JSON.parse(JSON.stringify(DEFAULT_DB));
  }

  function saveDB(db) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(db));
    } catch (e) {
      console.warn("Erro ao salvar localStorage:", e);
    }
  }

  // Gera response simulada
  function jsonResponse(data, status = 200) {
    return new Response(JSON.stringify(data), {
      status: status,
      headers: { "Content-Type": "application/json" }
    });
  }

  // Motor de Forecasting Econométrico em JS
  function computeForecasting(db, horizon = 24, growthPct = 15.0, optBonus = 20.0, pessPenalty = 15.0, inflationPct = 5.5, seasonality = 1.0, initialCash = 45000.0) {
    const months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    const labels = [];
    const monthlyCash = { base: [], optimistic: [], pessimistic: [] };
    const monthlyRevenue = { base: [], optimistic: [], pessimistic: [] };

    let cashBase = initialCash;
    let cashOpt = initialCash;
    let cashPess = initialCash;

    const baseMonthlyRev = 12000.0;
    const baseMonthlyCost = 4500.0;

    for (let i = 1; i <= horizon; i++) {
      const monthIdx = (i - 1) % 12;
      const yearOffset = Math.floor((i - 1) / 12);
      const year = 2026 + yearOffset;
      labels.push(`${months[monthIdx]}/${year.toString().slice(-2)}`);

      // Sazonalidade MEJ (Jan/Jul recesso, Mar/Abr/Set alta)
      const seasonalWeights = [0.65, 0.85, 1.25, 1.30, 1.15, 1.05, 0.70, 0.95, 1.20, 1.15, 1.00, 0.75];
      const sFactor = 1.0 + (seasonalWeights[monthIdx] - 1.0) * seasonality;

      const monthlyGrowth = Math.pow(1.0 + growthPct / 100.0, 1 / 12) - 1.0;
      const monthlyInflation = Math.pow(1.0 + inflationPct / 100.0, 1 / 12) - 1.0;

      // Base
      const revBase = baseMonthlyRev * Math.pow(1.0 + monthlyGrowth, i) * sFactor;
      const costBase = baseMonthlyCost * Math.pow(1.0 + monthlyInflation, i);
      cashBase += (revBase - costBase);
      monthlyRevenue.base.push(Math.round(revBase));
      monthlyCash.base.push(Math.round(cashBase));

      // Otimista
      const revOpt = revBase * (1.0 + optBonus / 100.0);
      const costOpt = costBase * 0.95;
      cashOpt += (revOpt - costOpt);
      monthlyRevenue.optimistic.push(Math.round(revOpt));
      monthlyCash.optimistic.push(Math.round(cashOpt));

      // Pessimista
      const revPess = revBase * (1.0 - pessPenalty / 100.0);
      const costPess = costBase * 1.10;
      cashPess += (revPess - costPess);
      monthlyRevenue.pessimistic.push(Math.round(revPess));
      monthlyCash.pessimistic.push(Math.round(cashPess));
    }

    return {
      metadata: {
        horizon_months: horizon,
        generated_at: new Date().toISOString(),
        compliance: "Projeções 100% integradas à Lei nº 13.267/2016"
      },
      charts: {
        time_labels: labels,
        cash_balance: monthlyCash,
        monthly_revenue: monthlyRevenue
      },
      summary_kpis: {
        saldo_final_base: Math.round(cashBase),
        saldo_final_otimista: Math.round(cashOpt),
        saldo_final_pessimista: Math.round(cashPess),
        crescimento_anual_base_pct: growthPct,
        fundo_reserva_acumulado: Math.round(cashBase * 0.85)
      }
    };
  }

  // Gera marcos automáticos por serviço CJA
  function getMilestoneTemplates(serviceName, totalHh, leadTime) {
    const s = (serviceName || "").toLowerCase();
    if (s.includes("processo") || s.includes("mapeamento")) {
      return [
        { phase_name: "Alinhamento e Mapeamento AS-IS dos Processos", week_start: 1, week_end: 2, budgeted_hh: Math.round(totalHh * 0.25), is_critical_path: 0, requires_mentor_approval: 0, status: "concluido" },
        { phase_name: "Identificação de Falhas Operacionais e Gargalos", week_start: 3, week_end: Math.max(4, leadTime - 3), budgeted_hh: Math.round(totalHh * 0.35), is_critical_path: 1, requires_mentor_approval: 0, status: "em_andamento" },
        { phase_name: "Modelagem TO-BE Otimizada (BPMN) & Validação Técnica", week_start: Math.max(5, leadTime - 2), week_end: leadTime - 1, budgeted_hh: Math.round(totalHh * 0.25), is_critical_path: 1, requires_mentor_approval: 1, status: "pendente" },
        { phase_name: "Manualização de POPs e Apresentação de Resultados", week_start: leadTime, week_end: leadTime, budgeted_hh: Math.round(totalHh * 0.15), is_critical_path: 0, requires_mentor_approval: 0, status: "pendente" }
      ];
    } else if (s.includes("financeira") || s.includes("caixa")) {
      return [
        { phase_name: "Diagnóstico Financeiro & Levantamento de Entradas/Saídas", week_start: 1, week_end: 2, budgeted_hh: Math.round(totalHh * 0.25), is_critical_path: 0, requires_mentor_approval: 0, status: "concluido" },
        { phase_name: "Estruturação de Contas e Conciliação Operacional", week_start: 3, week_end: Math.max(4, leadTime - 3), budgeted_hh: Math.round(totalHh * 0.35), is_critical_path: 1, requires_mentor_approval: 0, status: "em_andamento" },
        { phase_name: "Modelagem de Fluxo de Caixa & Parecer Financeiro", week_start: Math.max(5, leadTime - 2), week_end: leadTime - 1, budgeted_hh: Math.round(totalHh * 0.25), is_critical_path: 1, requires_mentor_approval: 1, status: "pendente" },
        { phase_name: "Dashboard de Gestão de Caixa & Treinamento de Sócios", week_start: leadTime, week_end: leadTime, budgeted_hh: Math.round(totalHh * 0.15), is_critical_path: 0, requires_mentor_approval: 0, status: "pendente" }
      ];
    } else if (s.includes("oculto")) {
      return [
        { phase_name: "Desenho dos Cenários e Roteiro de Avaliação PDV", week_start: 1, week_end: 2, budgeted_hh: Math.round(totalHh * 0.30), is_critical_path: 0, requires_mentor_approval: 0, status: "concluido" },
        { phase_name: "Execução de Campo / Visitas de Auditoria Oculta", week_start: 3, week_end: Math.max(4, leadTime - 2), budgeted_hh: Math.round(totalHh * 0.40), is_critical_path: 1, requires_mentor_approval: 0, status: "em_andamento" },
        { phase_name: "Análise Consolidada de Dados e Relatório com Trava de Mentor", week_start: Math.max(4, leadTime - 1), week_end: leadTime, budgeted_hh: Math.round(totalHh * 0.30), is_critical_path: 1, requires_mentor_approval: 1, status: "pendente" }
      ];
    } else {
      return [
        { phase_name: "Concepção do Negócio e Análise Mercadológica", week_start: 1, week_end: 2, budgeted_hh: Math.round(totalHh * 0.20), is_critical_path: 0, requires_mentor_approval: 0, status: "concluido" },
        { phase_name: "Planejamento Operacional e Estruturação de Marketing", week_start: 3, week_end: Math.max(4, leadTime - 3), budgeted_hh: Math.round(totalHh * 0.30), is_critical_path: 0, requires_mentor_approval: 0, status: "em_andamento" },
        { phase_name: "Modelagem Econômico-Financeira (VPL, TIR, Payback) e Trava", week_start: Math.max(5, leadTime - 2), week_end: leadTime - 1, budgeted_hh: Math.round(totalHh * 0.35), is_critical_path: 1, requires_mentor_approval: 1, status: "pendente" },
        { phase_name: "Sumário Executivo e Apresentação para Investidores", week_start: leadTime, week_end: leadTime, budgeted_hh: Math.round(totalHh * 0.15), is_critical_path: 0, requires_mentor_approval: 0, status: "pendente" }
      ];
    }
  }

  // Router de endpoints mock
  async function handleMockRequest(url, init = {}) {
    const db = getDB();
    const method = (init.method || "GET").toUpperCase();
    const cleanUrl = url.split("?")[0];
    let body = {};
    if (init.body) {
      try { body = JSON.parse(init.body); } catch (e) { body = {}; }
    }

    // 1. Serviços
    if (cleanUrl === "/api/business/services" && method === "GET") {
      return jsonResponse({ total: db.services.length, services: db.services });
    }

    // 2. CPQ Calculate
    if (cleanUrl === "/api/business/cpq/calculate" && method === "POST") {
      const svc = db.services.find(s => s.id === parseInt(body.service_id)) || db.services[0];
      const diag = parseInt(body.horas_diagnostico) || 15;
      const exec = parseInt(body.horas_execucao) || 35;
      const totalHh = diag + exec;
      const seniorityRates = {
        "Trainee / Assessor": 35.0,
        "Consultor Júnior": 55.0,
        "Consultor Pleno / Especialista": 85.0,
        "Gerente de Projetos": 120.0,
        "Diretor Executivo": 160.0
      };
      const rate = body.hourly_rate_override || seniorityRates[body.seniority] || svc.hourly_rate;
      const risk = parseFloat(body.risk_factor) || 1.15;
      const baseCost = totalHh * rate;
      const subtotalRisk = baseCost * risk;
      const reinvest = subtotalRisk * 0.15;
      const finalPrice = subtotalRisk + reinvest;

      return jsonResponse({
        service_id: svc.id,
        service_name: svc.name,
        macro_area: svc.macro_area,
        seniority: body.seniority || svc.recommended_seniority,
        hourly_rate: rate,
        horas_diagnostico: diag,
        horas_execucao: exec,
        total_hh: totalHh,
        risk_multiplier: risk,
        custo_base: Math.round(baseCost * 100) / 100,
        fundo_reinvestimento_estatutario: Math.round(reinvest * 100) / 100,
        preco_sugerido: Math.round(finalPrice * 100) / 100,
        lei_13267_compliance: true
      });
    }

    // 3. Propostas CPQ
    if (cleanUrl === "/api/business/cpq/proposals" && method === "GET") {
      return jsonResponse({ total: db.proposals.length, proposals: db.proposals });
    }

    if (cleanUrl === "/api/business/cpq/save" && method === "POST") {
      const newId = db.proposals.length > 0 ? Math.max(...db.proposals.map(p => p.id)) + 1 : 1;
      const newProp = {
        id: newId,
        client_name: body.client_name || "Cliente Demo",
        service_name: body.service_name || "Consultoria Financeira",
        total_hh: body.total_hh || 100,
        hourly_rate: body.hourly_rate || 85.0,
        total_price: body.total_price || 13500.0,
        status: body.status || "proposta_gerada",
        contact_name: body.contact_name || "Contato",
        notes: body.notes || ""
      };
      db.proposals.unshift(newProp);
      saveDB(db);
      return jsonResponse({ success: true, id: newId, proposal: newProp });
    }

    if (cleanUrl.startsWith("/api/business/cpq/proposals/") && method === "PATCH") {
      const id = parseInt(cleanUrl.split("/")[5]);
      const p = db.proposals.find(item => item.id === id);
      if (p && body.status) p.status = body.status;
      saveDB(db);
      return jsonResponse({ success: true });
    }

    if (cleanUrl.startsWith("/api/business/cpq/proposals/") && method === "DELETE") {
      const id = parseInt(cleanUrl.split("/")[5]);
      db.proposals = db.proposals.filter(item => item.id !== id);
      saveDB(db);
      return jsonResponse({ success: true });
    }

    // 4. Projetos & Gantt
    if (cleanUrl === "/api/business/projects/gantt" && method === "GET") {
      return jsonResponse({ total: db.projects.length, projects: db.projects });
    }

    if (cleanUrl === "/api/business/projects" && method === "POST") {
      const newId = db.projects.length > 0 ? Math.max(...db.projects.map(p => p.id)) + 1 : 1;
      const svcName = body.service_name || "Consultoria Financeira";
      const totalHh = parseInt(body.total_budgeted_hh) || 100;
      const leadTime = parseInt(body.lead_time_weeks) || 10;
      const val = parseFloat(body.contract_value) || 14500.0;

      const rawMilestones = getMilestoneTemplates(svcName, totalHh, leadTime);
      const milestones = rawMilestones.map((m, idx) => ({
        id: (newId * 10) + idx + 1,
        project_id: newId,
        phase_name: m.phase_name,
        title: m.phase_name,
        week_start: m.week_start,
        week_end: m.week_end,
        budgeted_hh: m.budgeted_hh,
        consumed_hh: 0.0,
        progress_pct: 0.0,
        is_critical_path: m.is_critical_path,
        requires_mentor_approval: m.requires_mentor_approval,
        mentor_approval_status: m.requires_mentor_approval ? "pendente" : "nao_requerido",
        status: "pendente"
      }));

      const newProj = {
        id: newId,
        name: body.name || `${svcName} - ${body.client_name}`,
        client_name: body.client_name || "Novo Cliente",
        service_name: svcName,
        macro_area: body.macro_area || "Finanças e Contabilidade",
        lead_time_weeks: leadTime,
        total_budgeted_hh: totalHh,
        consumed_hh: 0.0,
        progress_pct: 0.0,
        status: body.status || "em_andamento",
        start_date: body.start_date || new Date().toISOString().split("T")[0],
        expected_end_date: body.expected_end_date || "",
        manager_name: body.manager_name || "Lucas Mendes",
        scope_creep_alert: false,
        scope_alerts: [],
        milestones: milestones
      };

      db.projects.push(newProj);

      // Adicionar centro de custo na DRE
      db.dre.push({
        id: db.dre.length + 1,
        project_id: newId,
        project_name: newProj.name,
        client_name: newProj.client_name,
        macro_area: newProj.macro_area,
        receita_bruta: val,
        impostos_deducoes: 0.0,
        receita_liquida: val,
        custos_diretos_softwares: Math.round(val * 0.05 * 100) / 100,
        custos_diretos_operacionais: Math.round(val * 0.02 * 100) / 100,
        margem_contribuicao: Math.round(val * 0.93 * 100) / 100,
        margem_contribuicao_pct: 93.0,
        despesas_operacionais_rateadas: Math.round(val * 0.10 * 100) / 100,
        superavit_liquido: Math.round(val * 0.83 * 100) / 100,
        reinvestimento_obrigatorio_pct: 1.0,
        fundo_reserva_capacitacao: Math.round(val * 0.83 * 100) / 100
      });

      saveDB(db);
      return jsonResponse({ success: true, project: newProj });
    }

    if (cleanUrl.startsWith("/api/business/projects/") && method === "DELETE") {
      const id = parseInt(cleanUrl.split("/")[4]);
      db.projects = db.projects.filter(p => p.id !== id);
      db.dre = db.dre.filter(d => d.project_id !== id);
      saveDB(db);
      return jsonResponse({ success: true });
    }

    // Aprovação de Mentor
    if (cleanUrl.includes("/approve-mentor") && method === "POST") {
      const parts = cleanUrl.split("/");
      const milestoneId = parseInt(parts[5]);
      db.projects.forEach(p => {
        if (p.milestones) {
          const m = p.milestones.find(item => item.id === milestoneId);
          if (m) {
            m.mentor_approval_status = "aprovado";
            m.mentor_name = body.mentor_name || "Prof. Dr. Orientador";
            m.mentor_notes = body.mentor_notes || "Aprovado sem ressalvas.";
          }
        }
      });
      saveDB(db);
      return jsonResponse({ success: true, message: "Marco aprovado formalmente pelo mentor acadêmico." });
    }

    // 5. Ativos Intelectuais
    if (cleanUrl === "/api/business/knowledge/assets" && method === "GET") {
      return jsonResponse({ total: db.assets.length, assets: db.assets });
    }

    if (cleanUrl === "/api/business/knowledge/assets" && method === "POST") {
      const newId = db.assets.length > 0 ? Math.max(...db.assets.map(a => a.id)) + 1 : 1;
      const newAsset = {
        id: newId,
        title: body.title || "Novo Ativo CJA",
        macro_area: body.macro_area || "Finanças e Contabilidade",
        service_name: body.service_name || "Consultoria Financeira",
        asset_code: `MOD-CJA-MANUAL-0${newId}`,
        file_format: body.file_format || ".xlsx",
        version: body.version || "v1.0",
        version_notes: body.version_notes || "",
        author_member: body.author_member || "Consultor CJA",
        validator_mentor: body.validator_mentor || "Mentor Acadêmico",
        turnover_cycle: body.turnover_cycle || "Ciclo 2026.1",
        download_url: body.download_url || "#",
        file_size: "1.2 MB",
        downloads_count: 0
      };
      db.assets.unshift(newAsset);
      saveDB(db);
      return jsonResponse({ success: true, asset: newAsset });
    }

    if (cleanUrl.startsWith("/api/business/knowledge/assets/") && method === "DELETE") {
      const id = parseInt(cleanUrl.split("/")[5]);
      db.assets = db.assets.filter(a => a.id !== id);
      saveDB(db);
      return jsonResponse({ success: true });
    }

    // 6. Timesheet
    if (cleanUrl === "/api/business/timesheet" && method === "GET") {
      return jsonResponse({ entries: db.timesheet, active_scope_alerts: [] });
    }

    if (cleanUrl === "/api/business/timesheet/log" && method === "POST") {
      const newId = db.timesheet.length > 0 ? Math.max(...db.timesheet.map(t => t.id)) + 1 : 1;
      const entry = {
        id: newId,
        project_id: parseInt(body.project_id) || 1,
        milestone_id: parseInt(body.milestone_id) || 1,
        consultant_name: body.consultant_name || "Consultor",
        consultant_email: body.consultant_email || "consultor@nexusjr.com",
        date: body.date || new Date().toISOString().split("T")[0],
        hours: parseFloat(body.hours) || 4.0,
        description: body.description || "Atividade de consultoria",
        task_category: body.task_category || "Execução",
        scope_alert_triggered: 0
      };
      db.timesheet.unshift(entry);

      // Atualizar consumo no projeto
      const proj = db.projects.find(p => p.id === entry.project_id);
      if (proj) {
        proj.consumed_hh = Math.round((proj.consumed_hh + entry.hours) * 10) / 10;
        proj.progress_pct = Math.min(100, Math.round((proj.consumed_hh / proj.total_budgeted_hh) * 100));
      }

      saveDB(db);
      return jsonResponse({ success: true, id: newId });
    }

    // 7. DRE por Centro de Custo
    if (cleanUrl === "/api/business/finance/dre-by-project" && method === "GET") {
      const totRec = db.dre.reduce((sum, d) => sum + d.receita_bruta, 0);
      const totSup = db.dre.reduce((sum, d) => sum + d.superavit_liquido, 0);
      const totMarg = db.dre.reduce((sum, d) => sum + d.margem_contribuicao, 0);
      return jsonResponse({
        projetos: db.dre,
        consolidado: {
          total_receita_bruta: totRec,
          total_custos_diretos: Math.round(totRec * 0.07 * 100) / 100,
          total_margem_contribuicao: totMarg,
          margem_contribuicao_media_pct: 93.0,
          total_despesas_rateadas: Math.round(totRec * 0.10 * 100) / 100,
          total_superavit_estatutario: totSup,
          reinvestimento_obrigatorio_pct: 100.0,
          vedacao_distribuicao_lucro: true,
          lei_13267_art2_art4: "Em estrita conformidade: R$ 0,00 de remuneração a membros, 100% reinvestido em capacitação."
        }
      });
    }

    // 8. KPIs & Overview
    if (cleanUrl === "/api/business/kpis/overview" && method === "GET") {
      const totRec = db.dre.reduce((sum, d) => sum + d.receita_bruta, 0);
      const totSup = db.dre.reduce((sum, d) => sum + d.superavit_liquido, 0);
      const totHhExec = db.projects.reduce((sum, p) => sum + p.consumed_hh, 0);
      const totHhOrc = db.projects.reduce((sum, p) => sum + p.total_budgeted_hh, 0);

      return jsonResponse({
        faturamento_acumulado: totRec,
        superavit_estatutario: totSup,
        margem_contribuicao_pct: 93.0,
        projetos_ativos: db.projects.length,
        total_hh_executado: Math.round(totHhExec * 10) / 10,
        total_hh_orcado: totHhOrc,
        ativos_intelectuais_count: db.assets.length,
        propostas_geradas_count: db.proposals.length,
        pipeline_propostas_valor: db.proposals.reduce((sum, p) => sum + (p.total_price || 0), 0),
        alertas_scope_creep_ativos: 0,
        total_membros_ativos: db.members.length,
        conformidade_lei_13267: "100% dos excedentes reinvestidos; R$ 0,00 de remuneração a membros",
        charts: {
          revenue_evolution: {
            labels: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out"],
            meta_planejada: [3500, 7500, 12000, 16500, 21000, 26000, 31000, 36000, 40000, 45000],
            realizado_acumulado: [3800, 8200, 13500, 18900, 24200, 29800, 35100, 38900, totRec, totRec]
          },
          obz_distribution: {
            labels: [
              "Superávit Reinvestido (Lei 13.267)",
              "Despesas Administrativas Rateadas",
              "Softwares e Licenças Técnicas",
              "Custos Operacionais Diretos"
            ],
            values: [totSup, Math.round(totRec * 0.10), Math.round(totRec * 0.05), Math.round(totRec * 0.02)],
            colors: ["#059669", "#0b1d3a", "#3b82f6", "#f59e0b"]
          },
          hh_comparison: {
            labels: db.projects.map(p => p.name.length > 20 ? p.name.slice(0, 18) + "..." : p.name),
            orcado: db.projects.map(p => p.total_budgeted_hh),
            executado: db.projects.map(p => p.consumed_hh)
          }
        },
        recent_activities: db.activities
      });
    }

    // 9. Feed de Atividades
    if (cleanUrl === "/api/business/activities" && method === "GET") {
      return jsonResponse({ total: db.activities.length, activities: db.activities });
    }

    // 10. Membros VPGG
    if (cleanUrl === "/api/business/members" && method === "GET") {
      return jsonResponse({ total: db.members.length, members: db.members });
    }

    if (cleanUrl === "/api/business/members" && method === "POST") {
      const newId = db.members.length > 0 ? Math.max(...db.members.map(m => m.id)) + 1 : 1;
      const newMem = {
        id: newId,
        email: body.email || "novo@nexusjr.com",
        nome: body.nome || "Novo Membro",
        area: body.area || "Projetos",
        role: body.role || "assessor",
        cargo: body.cargo || "Consultor",
        cost_center: body.cost_center || "Presidência e Gestão Geral",
        turnover_cycle: body.turnover_cycle || "Ciclo 2026.1",
        status: "ativo"
      };
      db.members.push(newMem);
      saveDB(db);
      return jsonResponse({ success: true, member: newMem });
    }

    if (cleanUrl.includes("/toggle-status") && method === "PATCH") {
      const id = parseInt(cleanUrl.split("/")[4]);
      const m = db.members.find(item => item.id === id);
      if (m) {
        m.status = m.status === "ativo" ? "desligado" : "ativo";
      }
      saveDB(db);
      return jsonResponse({ success: true });
    }

    // 11. Forecasting Econométrico
    if (cleanUrl === "/api/business/finance/forecasting") {
      const forecast = computeForecasting(
        db,
        parseInt(body.horizon_months) || 24,
        parseFloat(body.growth_rate_annual_pct) || 15.0,
        parseFloat(body.optimistic_growth_bonus_pct) || 20.0,
        parseFloat(body.pessimistic_growth_penalty_pct) || 15.0,
        parseFloat(body.inflation_annual_pct) || 5.5,
        parseFloat(body.seasonality_intensity) || 1.0,
        parseFloat(body.initial_cash_balance) || 45000.0
      );
      return jsonResponse(forecast);
    }

    // 12. Autenticação RBAC
    if (cleanUrl === "/api/auth/login" && method === "POST") {
      const found = db.members.find(m => m.email.toLowerCase() === (body.email || "").toLowerCase()) || db.members[0];
      return jsonResponse({
        access_token: `mock_token_${found.id}_${found.role}`,
        token_type: "bearer",
        user: found
      });
    }

    // Fallback genérico para rotas não mapeadas
    return jsonResponse({ success: true, message: "Operação executada com sucesso no Modo Standalone." });
  }

  // Interceptor global do window.fetch
  const _nativeFetch = window.fetch.bind(window);

  // Detecta se estamos rodando em ambiente GitHub Pages ou estático
  const isGithubPages = window.location.hostname.endsWith("github.io") || window.location.protocol === "file:";
  let isStandaloneActive = isGithubPages;

  function updateBadge(online, label) {
    const badge = document.getElementById("backend-status-badge");
    const txt = document.getElementById("backend-status-text");
    if (!badge || !txt) return;

    if (online) {
      badge.className = "hidden sm:flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border bg-emerald-50 text-emerald-800 border-emerald-200 font-medium";
      txt.textContent = label || "FastAPI Conectado";
    } else {
      badge.className = "hidden sm:flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border bg-blue-50 text-blue-800 border-blue-200 font-medium";
      txt.textContent = label || "GitHub Pages (Demo)";
    }
  }

  window.fetch = async function (resource, init = {}) {
    const url = typeof resource === "string" ? resource : resource.url;

    // Se não for rota da API interna, deixa o fetch nativo agir (ex: CDNs)
    if (!url.startsWith("/api/")) {
      return _nativeFetch(resource, init);
    }

    // Se já sabemos que é GitHub Pages ou modo offline, responde pelo mock
    if (isStandaloneActive) {
      updateBadge(false, isGithubPages ? "GitHub Pages (Demo)" : "Modo Standalone");
      return handleMockRequest(url, init);
    }

    // Se estamos em localhost, tenta o backend FastAPI real
    try {
      const res = await _nativeFetch(resource, init);
      if (res.ok) {
        updateBadge(true, "FastAPI Conectado");
        return res;
      }
      if (res.status === 404) {
        isStandaloneActive = true;
        updateBadge(false, "Modo Standalone");
        return handleMockRequest(url, init);
      }
      return res;
    } catch (err) {
      console.warn("[Nexus Jr.] Backend local offline. Ativando Modo Standalone CJA automaticamente.", err);
      isStandaloneActive = true;
      updateBadge(false, "Modo Standalone");
      return handleMockRequest(url, init);
    }
  };

  // Expor utilitário para reset de dados demo se necessário
  window.resetNexusDemoData = function () {
    localStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  };

  console.log(`[Nexus Jr.] Motor Standalone CJA inicializado. Ambiente: ${isGithubPages ? 'GitHub Pages' : 'Local / Híbrido'}.`);
})();
