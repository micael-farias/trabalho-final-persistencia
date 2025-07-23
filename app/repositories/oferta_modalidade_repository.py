
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.oferta_modalidade import OfertaModalidade
from .base_repository import BaseRepository
from sqlalchemy import text

class OfertaModalidadeRepository(BaseRepository[OfertaModalidade]):
    def __init__(self, db: Session):
        super().__init__(OfertaModalidade, db)
    
    def bulk_insert_ofertas_modalidade(self, ofertas_data: List[Dict]) -> int:
        if not ofertas_data:
            return 0
        
        try:
            values_list = []
            for data in ofertas_data:
                values = "({}, '{}', {}, {}, {}, {}, {}, {})".format(
                    data['co_entidade'],
                    data['tipo_modalidade'],
                    data['qt_matriculas'],
                    data['qt_docentes'],
                    data['qt_turmas'],
                    data['in_diurno'],
                    data['in_noturno'],
                    data['nu_ano_censo']
                )
                values_list.append(values)
            
            values_str = ', '.join(values_list)
            sql = f"""
                INSERT INTO ofertas_modalidade (co_entidade, tipo_modalidade, qt_matriculas, qt_docentes,
                                              qt_turmas, in_diurno, in_noturno, nu_ano_censo)
                VALUES {values_str}
            """
            
            self.db.execute(text(sql))
            return len(ofertas_data)
        except Exception as e:
            print(f"⚠️  Erro no bulk insert de ofertas: {e}")
            return 0
    