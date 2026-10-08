# Nexus Jr. | ERP Gestão & Finanças 2.0 📊🚀

Sistema ERP de alta performance desenvolvido exclusivamente para **Empresas Juniores de Administração, Ciências Econômicas e Negócios (Gestão e Finanças)**, parametrizado com o portfólio oficial de serviços da **CJA - Consultoria Empresarial** e em estrita conformidade com a **Lei Federal nº 13.267/2016** (Lei das Empresas Juniores).

---

## 🌟 Principais Funcionalidades

1. **Painel Executivo (BI & Metas PE)**:
   - Indicadores de faturamento acumulado, margem estatutária e capacidade produtiva (HH).
   - Visual Analytics interativo em **Chart.js** (evolução de faturamento, distribuição do OBZ e comparação de HH orçado vs. executado).
   - Feed de atividades operacionais em tempo real com histórico de aprovações e alertas de Scope Creep.

2. **Pipeline Comercial & CPQ Paramétrico**:
   - Catálogo oficial dos **8 Serviços CJA** distribuídos nas 4 macro-áreas corporativas:
     - *Gestão de Processos* (Mapeamento de Processos)
     - *Finanças e Contabilidade* (Consultoria Financeira, Assessoria Contábil)
     - *Inteligência de Mercado & Experiência do Cliente* (Cliente Oculto, Pesquisa de Mercado, Pesquisa de Satisfação)
     - *Planejamento Estratégico & Marketing* (Plano de Negócios, Plano de Marketing)
   - Motor de cálculo de Homem-Hora (HH), senioridades (Trainee a Diretor) e **15% de margem estatutária obrigatória**.
   - Gestão completa do ciclo de vida das propostas (Gerada, Negociada, Convertida, Perdida).

3. **Gestão de Projetos & Cronogramas Gantt**:
   - Templates de cronograma calibrados automaticamente para cada serviço CJA.
   - **Travas Estatutárias de Mentor**: chancela formal e parecer acadêmico obrigatório para liberação de entregáveis críticos.

4. **Repositório de Ativos Intelectuais (Anti-Turnover)**:
   - Biblioteca de modelos padronizados (.xlsx, .docx, .pptx, .pdf) com controle semestral de versão e autoria.

5. **Timesheet Preditivo & Detecção de Scope Creep**:
   - Apontamento de horas por consultor e marco com alerta preditivo automático (consumo $\ge 75\%$ do orçamento).

6. **Tesouraria, Compliance & DRE por Centro de Custo**:
   - Centros de custo isolados por consultoria com **93,0% de margem de contribuição direta**.
   - Trava de **100% dos superávits destinados ao reinvestimento** e fundo de capacitação (vedada distribuição de dividendos a membros).
   - Exportação real de relatórios contábeis para **Excel (.xlsx)** e **PDF executivo**.

7. **Motor Econométrico de Forecasting & Simulação Macroeconômica**:
   - Projeções de séries temporais de fluxo de caixa (12 a 36 meses).
   - 3 cenários preditivos dinâmicos com controles deslizantes: **Otimista**, **Base** e **Pessimista**.

8. **Gente & Gestão (VPGG) & RBAC**:
   - Gestão de membros, papéis de acesso (Assessor, Gerente, Diretor, Presidente), centros de custo e ciclo semestral de gestão.

---

## 🚀 Como Rodar o Projeto

### Opção 1: Visualização Online Direta (GitHub Pages)
O projeto conta com um **Motor Standalone Inteligente** (`mock_backend.js`) que permite testar **todas as funcionalidades, gráficos, cálculos de CPQ e formulários diretamente no navegador pelo GitHub Pages**, sem a necessidade de instalar Python ou configurar servidores.

### Opção 2: Execução Local com Backend FastAPI (Python)
Para executar com o backend real em Python e banco de dados SQLite persistente:

1. **Instalar as dependências:**
   ```bash
   pip install fastapi uvicorn bcrypt openpyxl
   ```

2. **Iniciar o servidor:**
   ```bash
   python run_nexus.py
   ```

3. **Acessar no navegador:**
   - **Interface Web:** [http://127.0.0.1:8002](http://127.0.0.1:8002)
   - **Swagger Docs:** [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)

---

## 🏛️ Conformidade Legal
- **Lei nº 13.267/2016 (Art. 2º e Art. 4º)**: Fim estritamente educacional, gestão autônoma por estudantes universitários e proibição irrevogável de distribuição de qualquer superávit ou bonificação financeira a membros.
