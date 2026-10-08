"""
Nexus Jr. | ERP Gestão & Finanças 2.0
Script de Inicialização do Servidor FastAPI
Porta: 8002 (totalmente isolado do sistema jurídico EDV na porta 8000)
"""

import sys
import os

# Adiciona o diretório backend ao PATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8002))
    print("=" * 70)
    print("  NEXUS JR. | ERP GESTÃO & FINANÇAS 2.0")
    print("  Sistema ERP Especializado para EJs de Negócios (FEA / FGV / FACE)")
    print("=" * 70)
    print(f"  URL Local:          http://127.0.0.1:{port}")
    print(f"  Documentação API:   http://127.0.0.1:{port}/docs")
    print(f"  Credenciais Padrão: charles@nexusjr.com | Senha: edv2026!")
    print("=" * 70)
    print("Iniciando servidor Uvicorn...\n")
    
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False, app_dir=BACKEND_DIR)
