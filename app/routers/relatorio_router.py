from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Integer 
from typing import Dict, Any
from ..core.database import get_db
from ..repositories.relatorio_repository import RelatorioRepository
from ..logs import logging
from ..models import escola , infraestrutura

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
    logging.info("Solicitada geração de relatório geral do censo escolar")
    try:
        repo = RelatorioRepository(db)
        resultado = repo.relatorio_geral()
        if 'error' in resultado:
            logging.error(f"Erro ao gerar relatório geral: {resultado['error']}")
            raise HTTPException(status_code=500, detail=resultado['error'])
        logging.info("Relatório geral gerado com sucesso")
        return resultado
    except Exception as e:
        logging.exception(f"Exceção ao gerar relatório geral: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório geral: {str(e)}")

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
    logging.info(f"Solicitada geração de relatório por UF: {uf}")
    try:
        repo = RelatorioRepository(db)
        resultado = repo.relatorio_por_uf(uf)
        if 'error' in resultado:
            logging.error(f"Erro ao gerar relatório por UF {uf}: {resultado['error']}")
            raise HTTPException(status_code=404, detail=resultado['error'])
        logging.info(f"Relatório por UF {uf} gerado com sucesso")
        return resultado
    except Exception as e:
        logging.exception(f"Exceção ao gerar relatório por UF {uf}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório por UF: {str(e)}")

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
    logging.info("Solicitada geração de relatório de cursos técnicos")
    try:
        repo = RelatorioRepository(db)
        resultado = repo.relatorio_cursos_tecnicos()
        if 'error' in resultado:
            logging.error(f"Erro ao gerar relatório de cursos técnicos: {resultado['error']}")
            raise HTTPException(status_code=500, detail=resultado['error'])
        logging.info("Relatório de cursos técnicos gerado com sucesso")
        return resultado
    except Exception as e:
        logging.exception(f"Exceção ao gerar relatório de cursos técnicos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de cursos técnicos: {str(e)}")

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
    logging.info("Solicitada geração de relatório de infraestrutura escolar")
    try:
        repo = RelatorioRepository(db)
        resultado = repo.relatorio_infraestrutura()
        if 'error' in resultado:
            logging.error(f"Erro ao gerar relatório de infraestrutura: {resultado['error']}")
            raise HTTPException(status_code=500, detail=resultado['error'])
        logging.info("Relatório de infraestrutura gerado com sucesso")
        return resultado
    except Exception as e:
        logging.exception(f"Exceção ao gerar relatório de infraestrutura: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de infraestrutura: {str(e)}")

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
    
    
@router.get("/infraestrutura_das_escolas_por_municipio/")
def infraestrutura_das_escolas_filtro_por_municio(
    cidade: str, 
    paran : str ,  
    value,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_db)
):
    """
    Relatório da infraestrutura das escolas por município.

    Parâmetros aceitos para 'paran':
    - in_internet -> BOOL
    - in_biblioteca -> BOOL
    - in_laboratorio_informatica -> BOOL
    - in_laboratorio_ciencias -> BOOL
    - in_quadra_esportes -> BOOL
    - in_acessibilidade_rampas -> BOOL
    - qt_desktop_aluno -> inteiro
    - qt_salas_utilizadas -> inteiro
    """
    logging.info("Relatório da infraestrutura das escolas")
    
    try:
        if not hasattr(infraestrutura.Infraestrutura, paran):
            raise HTTPException(status_code=400, detail=f"Coluna '{paran}' não existe em Infraestrutura")

        filtro_col = getattr(infraestrutura.Infraestrutura, paran)
        # Total geral sem paginação

        total_escolas = session.query(escola.Escola).filter(escola.Escola.no_municipio == cidade).count()

        total_registros_geral = session.query(escola.Escola.no_entidade)
        total_registros_geral = total_registros_geral.join(
            infraestrutura.Infraestrutura,
            escola.Escola.co_entidade == infraestrutura.Infraestrutura.co_entidade
        ).filter(escola.Escola.no_municipio == cidade)
        total_registros_geral = total_registros_geral.filter(filtro_col == value).count()

        offset = (page - 1) * limit
        result = (
            session.query(escola.Escola.no_entidade, infraestrutura.Infraestrutura)
            .join(infraestrutura.Infraestrutura, escola.Escola.co_entidade == infraestrutura.Infraestrutura.co_entidade)
            .filter(escola.Escola.no_municipio == cidade)
            .filter(filtro_col == value)
            .order_by(escola.Escola.no_entidade.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        def serialize_infra(row):
            no_entidade = row[0]
            infra = row[1]
            return {
                "no_entidade": no_entidade,
                **{k: v for k, v in infra.__dict__.items() if not k.startswith('_')}
            }
        registros = [serialize_infra(r) for r in result]
        total_paginas = (total_registros_geral + limit - 1) // limit if limit > 0 else 1


        if total_escolas > 0:
            porcentagem = round(total_registros_geral/total_escolas,2)
        else:
            porcentagem = 0.0

        return {
            "pagina_atual": page,
            "total_paginas": total_paginas,
            "total_escolas" : total_escolas,
            "total_registros_geral": total_registros_geral,
            "porcentagem" : porcentagem,
            "dados": registros
        }
    except Exception as e:
        logging.error(f"Erro: {e} ")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@router.get("/infraestrutura_das_escolas_por_estado/")
def infraestrutura_das_escolas_filtro_por_estado(
    uf: str,
    paran: str,
    value,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_db)
):
    """
    Relatório da infraestrutura das escolas por estado, agrupando por município.

    Parâmetros aceitos para 'paran':
    - in_internet -> BOOL
    - in_biblioteca -> BOOL
    - in_laboratorio_informatica -> BOOL
    - in_laboratorio_ciencias -> BOOL
    - in_quadra_esportes -> BOOL
    - in_acessibilidade_rampas -> BOOL
    - qt_desktop_aluno -> inteiro
    - qt_salas_utilizadas -> inteiro
    """
    logging.info("Relatório da infraestrutura das escolas por estado")
    
    try:
        if not hasattr(infraestrutura.Infraestrutura, paran):
            raise HTTPException(status_code=400, detail=f"Coluna '{paran}' não existe em Infraestrutura")

        filtro_col = getattr(infraestrutura.Infraestrutura, paran)
        municipios_todos_query = session.query(escola.Escola.no_municipio).filter(escola.Escola.sg_uf == uf).distinct().order_by(escola.Escola.no_municipio.asc())
        municipios_lista = [m[0] for m in municipios_todos_query.all()]

        #Quantidade de munucipios do estado
        total_registros_geral = len(municipios_lista)

        #Quantidade de escolas no estado
        quantidade_escolas_total = session.query(escola.Escola).filter(escola.Escola.sg_uf == uf).count()

        #Quantide de escolas filtradas

        quantidade_escolas_filtradas = session.query(escola.Escola, infraestrutura.Infraestrutura).filter(escola.Escola.sg_uf == uf).filter(escola.Escola.co_entidade == infraestrutura.Infraestrutura.co_entidade).filter(filtro_col == value).count()


        if quantidade_escolas_total > 0:
            porcentagem = round(quantidade_escolas_filtradas/quantidade_escolas_total,2)
        else:
            porcentagem = 0.0

        total_paginas = (total_registros_geral + limit - 1) // limit if limit > 0 else 1
        offset = (page - 1) * limit
        municipios_paginados = municipios_lista[offset:offset+limit]

        municipios = []
        for municipio in municipios_paginados:
            count = session.query(escola.Escola.no_entidade)
            count = count.join(
                infraestrutura.Infraestrutura,
                escola.Escola.co_entidade == infraestrutura.Infraestrutura.co_entidade
            ).filter(escola.Escola.sg_uf == uf)
            count = count.filter(filtro_col == value)
            count = count.filter(escola.Escola.no_municipio == municipio).count()
            municipios.append({
                "municipio": municipio,
                "total_registros": count
            })

        return {
            "pagina_atual": page,
            "total_paginas": total_paginas,
            "total_municipios": len(municipios_lista),
            "porcentagem" : porcentagem,
            "municipios": municipios
        }
    except Exception as e:
        logging.error(f"Erro: {e} ")
        raise HTTPException(status_code=500, detail=str(e))