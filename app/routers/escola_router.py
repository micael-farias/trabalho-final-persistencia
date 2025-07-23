from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..repositories.escola_repository import EscolaRepository
from ..schemas.escola_schema import EscolaResponse

router = APIRouter(prefix="/escolas", tags=["Escolas"])

@router.get("/", response_model=List[EscolaResponse])
def get_escolas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    escola_repo = EscolaRepository(db)
    return escola_repo.get_all(skip=skip, limit=limit)

@router.get("/{co_entidade}", response_model=EscolaResponse)
def get_escola(co_entidade: int, db: Session = Depends(get_db)):
    escola_repo = EscolaRepository(db)
    escola = escola_repo.get_by_codigo(co_entidade)
    if not escola:
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    return escola

@router.get("/uf/{uf}", response_model=List[EscolaResponse])
def get_escolas_by_uf(uf: str, db: Session = Depends(get_db)):
    """Buscar escolas por UF"""
    escola_repo = EscolaRepository(db)
    return escola_repo.get_by_uf(uf.upper())

@router.get("/municipio/{municipio}", response_model=List[EscolaResponse])
def get_escolas_by_municipio(municipio: str, db: Session = Depends(get_db)):
    """Buscar escolas por município"""
    escola_repo = EscolaRepository(db)
    return escola_repo.get_by_municipio(municipio)