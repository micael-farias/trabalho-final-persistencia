from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..core.database import get_db
from ..repositories.relatorio_repository import RelatorioRepository

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.get("/geral")
async def relatorio_geral(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Relatório geral com estatísticas do censo escolar
    
    Retorna:
    - Totais gerais (escolas, infraestrutura, ofertas, cursos)
    - Distribuição por UF
    - Matrículas por modalidade de ensino
    - Percentuais de infraestrutura
    - Distribuição por dependência administrativa
    """
    repo = RelatorioRepository(db)
    resultado = repo.relatorio_geral()
    
    if 'error' in resultado:
        raise HTTPException(status_code=500, detail=resultado['error'])
    
    return resultado

@router.get("/uf/{uf}")
async def relatorio_por_uf(uf: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Relatório detalhado por Unidade Federativa
    
    Args:
        uf: Sigla da UF (ex: SP, RJ, MG)
    
    Retorna:
    - Estatísticas da UF
    - Distribuição por município
    - Infraestrutura disponível
    - Modalidades de ensino oferecidas
    """
    repo = RelatorioRepository(db)
    resultado = repo.relatorio_por_uf(uf)
    
    if 'error' in resultado:
        raise HTTPException(status_code=404, detail=resultado['error'])
    
    return resultado

@router.get("/cursos-tecnicos")
async def relatorio_cursos_tecnicos(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Relatório sobre cursos técnicos oferecidos
    
    Retorna:
    - Cursos mais oferecidos
    - Áreas profissionais
    - Distribuição por UF
    - Estatísticas de matrículas
    """
    repo = RelatorioRepository(db)
    resultado = repo.relatorio_cursos_tecnicos()
    
    if 'error' in resultado:
        raise HTTPException(status_code=500, detail=resultado['error'])
    
    return resultado

@router.get("/infraestrutura")
async def relatorio_infraestrutura(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Relatório detalhado sobre infraestrutura escolar
    
    Retorna:
    - Percentuais de infraestrutura disponível
    - Distribuição de equipamentos
    - Comparativo por UF
    - Indicadores de acessibilidade
    """
    repo = RelatorioRepository(db)
    resultado = repo.relatorio_infraestrutura()
    
    if 'error' in resultado:
        raise HTTPException(status_code=500, detail=resultado['error'])
    
    return resultado

@router.get("/dashboard")
async def dashboard_resumo(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Dashboard com dados resumidos para visualização
    
    Retorna dados otimizados para dashboards e gráficos
    """
    repo = RelatorioRepository(db)
    
    try:
        # Dados do relatório geral
        geral = repo.relatorio_geral()
        
        if 'error' in geral:
            raise HTTPException(status_code=500, detail=geral['error'])
        
        # Dados de cursos técnicos
        cursos = repo.relatorio_cursos_tecnicos()
        
        # Dados de infraestrutura
        infra = repo.relatorio_infraestrutura()
        
        # Compilar dashboard
        dashboard = {
            'cards_principais': {
                'total_escolas': geral['resumo_geral']['total_escolas'],
                'total_matriculas': sum([m['total_matriculas'] for m in geral['matriculas_por_modalidade']]),
                'total_cursos_tecnicos': cursos['resumo_geral']['total_cursos_cadastrados'],
                'percentual_com_internet': infra['resumo_geral']['percentual_com_internet']
            },
            'top_5_ufs_escolas': geral['escolas_por_uf'][:5],
            'modalidades_mais_populares': geral['matriculas_por_modalidade'][:5],
            'infraestrutura_percentuais': geral['infraestrutura_percentuais'],
            'areas_profissionais_top': cursos['areas_profissionais'][:5] if 'error' not in cursos else [],
            'distribuicao_dependencia': geral['escolas_por_dependencia'],
            'distribuicao_localizacao': geral['escolas_por_localizacao']
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard: {str(e)}")

@router.get("/estatisticas-rapidas")
async def estatisticas_rapidas(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Estatísticas rápidas do banco de dados
    
    Retorna contadores básicos para verificação dos dados
    """
    try:
        from ..models.escola import Escola
        from ..models.infraestrutura import Infraestrutura
        from ..models.oferta_modalidade import OfertaModalidade
        from ..models.curso_tecnico import CursoTecnico
        from ..models.escola_curso import EscolaCurso
        
        return {
            'contadores': {
                'escolas': db.query(Escola).count(),
                'infraestruturas': db.query(Infraestrutura).count(),
                'ofertas_modalidade': db.query(OfertaModalidade).count(),
                'cursos_tecnicos': db.query(CursoTecnico).count(),
                'relacoes_escola_curso': db.query(EscolaCurso).count()
            },
            'ufs_com_dados': db.query(Escola.sg_uf).distinct().count(),
            'municipios_com_dados': db.query(Escola.no_municipio).distinct().count(),
            'status': 'OK'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")