from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    escola_router,
    import_router,
    relatorio_router  # ← ADICIONAR ESTA LINHA
)

app = FastAPI(
    title="API do Censo Escolar",
    description="API para análise dos microdados do Censo Escolar da Educação Básica 2024",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(import_router.router)
app.include_router(escola_router.router)
app.include_router(relatorio_router.router)  # ← ADICIONAR ESTA LINHA

@app.get("/")
def read_root():
    return {
        "message": "API do Censo Escolar 2024",
        "version": "1.0.0",
        "status": "✅ Funcionando",
        "endpoints": [
            "/docs - Documentação da API",
            "/import/microdados-escola - Importar CSV de escolas",
            "/import/cursos-tecnicos - Importar CSV de cursos técnicos", 
            "/escolas - Listar escolas",
            "/escolas/{co_entidade} - Buscar escola por código",
            "/escolas/uf/{uf} - Buscar escolas por UF",
            "/escolas/municipio/{municipio} - Buscar escolas por município",
            "/relatorios/geral - Relatório geral do censo",  # ← NOVO
            "/relatorios/uf/{uf} - Relatório por UF",         # ← NOVO
            "/relatorios/cursos-tecnicos - Relatório de cursos", # ← NOVO
            "/relatorios/infraestrutura - Relatório de infraestrutura", # ← NOVO
            "/relatorios/dashboard - Dashboard resumido"       # ← NOVO
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando corretamente"}