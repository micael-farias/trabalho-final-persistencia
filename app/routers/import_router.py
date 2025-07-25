from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..repositories.csv_import_repository import CSVImportRepository
from ..logs import logging
import tempfile
import os

router = APIRouter(prefix="/import", tags=["Import"])

@router.post("/microdados-escola")
async def import_microdados_escola(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logging.info(f"Iniciando importação de microdados escola: {file.filename}")
    if not file.filename.endswith('.csv'):
        logging.warning(f"Arquivo inválido enviado: {file.filename}")
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        import_repo = CSVImportRepository(db)
        result = import_repo.import_microdados_escola(temp_file_path)

        if result['success']:
            logging.info(f"Importação de microdados escola realizada com sucesso: {file.filename}")
            return {
                "message": "Importação realizada com sucesso",
                "details": result
            }
        else:
            logging.error(f"Erro na importação de microdados escola: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Erro na importação: {result['error']}")

    finally:
        os.unlink(temp_file_path)

@router.post("/cursos-tecnicos")
async def import_cursos_tecnicos(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logging.info(f"Iniciando importação de cursos técnicos: {file.filename}")
    if not file.filename.endswith('.csv'):
        logging.warning(f"Arquivo inválido enviado: {file.filename}")
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        import_repo = CSVImportRepository(db)
        result = import_repo.import_cursos_tecnicos(temp_file_path)

        if result['success']:
            logging.info(f"Importação de cursos técnicos realizada com sucesso: {file.filename}")
            return {
                "message": "Importação realizada com sucesso",
                "details": result
            }
        else:
            logging.error(f"Erro na importação de cursos técnicos: {result['error']}")
            raise HTTPException(status_code=500, detail=f"Erro na importação: {result['error']}")

    finally:
        os.unlink(temp_file_path)