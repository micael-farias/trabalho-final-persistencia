from fastapi import APIRouter, Depends, HTTPException
from ..models import escola, escola_curso, curso_tecnico
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..repositories.escola_repository import EscolaRepository
from ..schemas.escola_schema import EscolaResponse
from ..logs import logging


router = APIRouter(prefix="/escolas", tags=["Escolas"])


@router.get("/", response_model=List[EscolaResponse])
def get_escolas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logging.info("EndPoint GET /escolas chamado")
    try:
        escola_repo = EscolaRepository(db)
        escolas = escola_repo.get_all(skip=skip, limit=limit)
        logging.info(f"Retornando {len(escolas)} escolas (skip={skip}, limit={limit})")
        return escolas
    except Exception as e:
        logging.error(f"Erro ao processar escolas: {e}")
        raise HTTPException(status_code=404, detail=f"Erro ao processar escolas: {e}")


@router.get(
    "/filter/{filter}/{data}/{page}/{limit}")
def get_filted_data(
    filter: str,
    data: str,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_db),
):
    logging.info(
        f"EndPoint GET /escolas/filter/{{filter}}/{{data}}/{{page}}/{{limit}} chamado (filter={filter}, data={data}, page={page}, limit={limit})"
    )
    try:
        if not hasattr(escola.Escola, filter):
            logging.warning(f"Filtro '{filter}' inválido")
            raise HTTPException(status_code=400, detail=f"Filtro '{filter}' inválido")

        offset = (page - 1) * limit
        coluna = getattr(escola.Escola, filter)
        result = (
            session.query(escola.Escola)
            .filter(coluna == data)
            .offset(offset)
            .limit(limit)
            .all()
        )
        logging.info(
            f"Retornando {len(result)} escolas filtradas por {filter}={data} (page={page}, limit={limit})"
        )
        total_filtradas = session.query(escola.Escola).filter(coluna == data).count()
        total_pages = (total_filtradas) // limit
        return {"page": page, "total_pages": total_pages, "data": result}
    except Exception as e:
        logging.error(f"Erro ao filtrar escolas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao filtrar escolas: {e}")
    
@router.get("/curso/{nome_curso}/{page}/{limit}")
def get_escolas_por_curso(
    nome_curso:str,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_db),
    ):
    try:
        
        offset = (page - 1) * limit
        result = (
            session.query(escola.Escola)
            .join(escola_curso.EscolaCurso, escola.Escola.co_entidade == escola_curso.EscolaCurso.co_entidade)
            .join(curso_tecnico.CursoTecnico, curso_tecnico.CursoTecnico.co_curso_educ_profissional == escola_curso.EscolaCurso.co_curso_educ_profissional)
            .filter(curso_tecnico.CursoTecnico.no_curso_educ_profissional == nome_curso)
            .distinct()
            .limit(limit)
            .offset(offset)
        )

        total_filtradas = (
            session.query(escola.Escola)
            .join(escola_curso.EscolaCurso, escola.Escola.co_entidade == escola_curso.EscolaCurso.co_entidade)
            .join(curso_tecnico.CursoTecnico, curso_tecnico.CursoTecnico.co_curso_educ_profissional == escola_curso.EscolaCurso.co_curso_educ_profissional)
            .filter(curso_tecnico.CursoTecnico.no_curso_educ_profissional == nome_curso)
            .distinct()
            .count()
            )
        
        total_pages = (total_filtradas) // limit
        return {"page": page, "total_pages": total_pages, "data": result.all()}
    except Exception as e:
        logging.error(f"Erro ao filtrar escolas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao filtrar escolas: {e}")


@router.get("/{co_entidade}", response_model=EscolaResponse)
def get_escola(co_entidade: int, db: Session = Depends(get_db)):
    logging.info(
        f"EndPoint GET /escolas/{{co_entidade}} chamado (co_entidade={co_entidade})"
    )
    try: 
        escola_repo = EscolaRepository(db)
        escola = escola_repo.get_by_codigo(co_entidade)
        if not escola:
            logging.warning(f"Escola não encontrada: co_entidade={co_entidade}")
            raise HTTPException(status_code=404, detail="Escola não encontrada")
        logging.info(f"Escola encontrada: co_entidade={co_entidade}")
        return escola
    except Exception as e:
        logging.error(f"Erro ao buscar escola: {e}")
        raise HTTPException(status_code=404, detail=f"Erro ao buscar escola: {e}")


@router.get("/uf/{uf}", response_model=List[EscolaResponse])
def get_escolas_by_uf(uf: str, db: Session = Depends(get_db)):
    logging.info(f"EndPoint GET /escolas/uf/{{uf}} chamado (uf={uf})")
    try:
        escola_repo = EscolaRepository(db)
        escolas = escola_repo.get_by_uf(uf.upper())
        logging.info(f"Retornando {len(escolas)} escolas para UF={uf.upper()}")
        return escolas
    except Exception as e:
        logging.error(f"Erro ao buscar escolas por UF: {e}")
        raise HTTPException(
            status_code=404, detail=f"Erro ao buscar escolas por UF: {e}"
        )


@router.get("/municipio/{municipio}", response_model=List[EscolaResponse])
def get_escolas_by_municipio(municipio: str, db: Session = Depends(get_db)):
    logging.info(
        f"EndPoint GET /escolas/municipio/{{municipio}} chamado (municipio={municipio})"
    )
    try:
        escola_repo = EscolaRepository(db)
        escolas = escola_repo.get_by_municipio(municipio)
        logging.info(f"Retornando {len(escolas)} escolas para municipio={municipio}")
        return escolas
    except Exception as e:
        logging.error(f"Erro ao buscar escolas por município: {e}")
        raise HTTPException(
            status_code=404, detail=f"Erro ao buscar escolas por município: {e}"
        )
