from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.infraestrutura import Infraestrutura
from .base_repository import BaseRepository
from sqlalchemy import text

class InfraestruturaRepository(BaseRepository[Infraestrutura]):
    def __init__(self, db: Session):
        super().__init__(Infraestrutura, db)
    
    def bulk_insert_infraestruturas(self, infraestruturas_data: List[Dict]) -> int:
        if not infraestruturas_data:
            return 0
        
        try:
            values_list = []
            for data in infraestruturas_data:
                values = "({}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                    data['co_entidade'],
                    data['in_internet'],
                    data['in_biblioteca'],
                    data['in_laboratorio_informatica'],
                    data['in_laboratorio_ciencias'],
                    data['in_quadra_esportes'],
                    data['in_acessibilidade_rampas'],
                    data['qt_desktop_aluno'],
                    data['qt_salas_utilizadas']
                )
                values_list.append(values)
            
            values_str = ', '.join(values_list)
            sql = f"""
                INSERT INTO infraestruturas (co_entidade, in_internet, in_biblioteca, in_laboratorio_informatica,
                                           in_laboratorio_ciencias, in_quadra_esportes, in_acessibilidade_rampas,
                                           qt_desktop_aluno, qt_salas_utilizadas)
                VALUES {values_str}
                ON CONFLICT (co_entidade) DO NOTHING
            """
            
            self.db.execute(text(sql))
            return len(infraestruturas_data)
        except Exception as e:
            print(f"⚠️  Erro no bulk insert de infraestruturas: {e}")
            return 0
    