from sqlalchemy.orm import Session
from typing import Dict, Any
from ..processors.escola_processor import EscolaProcessor
from ..processors.curso_processor import CursoProcessor

class CSVImportRepository:
    def __init__(self, db: Session):
        self.db = db
        self.escola_processor = EscolaProcessor(db)
        self.curso_processor = CursoProcessor(db)
    
    def import_microdados_escola(self, csv_path: str) -> Dict[str, Any]:
        """Importa microdados de escolas"""
        return self.escola_processor.import_microdados_escola(csv_path)
    
    def import_cursos_tecnicos(self, csv_path: str) -> Dict[str, Any]:
        """Importa cursos técnicos"""
        return self.curso_processor.import_cursos_tecnicos(csv_path)