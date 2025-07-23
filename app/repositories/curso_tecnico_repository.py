
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.curso_tecnico import CursoTecnico
from .base_repository import BaseRepository
from sqlalchemy import text

class CursoTecnicoRepository(BaseRepository[CursoTecnico]):
    def __init__(self, db: Session):
        super().__init__(CursoTecnico, db)
    
    def bulk_insert_cursos_tecnicos(self, cursos_data: List[Dict]) -> int:
        """Insere cursos técnicos em lote"""
        if not cursos_data:
            return 0
        
        try:
            values_list = []
            for data in cursos_data:
                no_curso = data['no_curso_educ_profissional']
                no_area = data['no_area_curso_profissional']
                
                values = "({}, '{}', '{}', {}, {}, {}, {}, {}, {})".format(
                    data['co_curso_educ_profissional'],
                    no_curso,
                    no_area,
                    data['id_area_curso_profissional'],
                    data['qt_mat_curso_tec'],
                    data['qt_curso_tec_conc'],
                    data['qt_curso_tec_subs'],
                    data['qt_curso_tec_eja'],
                    data['nu_ano_censo']
                )
                values_list.append(values)
            
            values_str = ', '.join(values_list)
            sql = f"""
                INSERT INTO cursos_tecnicos (co_curso_educ_profissional, no_curso_educ_profissional, 
                                        no_area_curso_profissional, id_area_curso_profissional, 
                                        qt_mat_curso_tec, qt_curso_tec_conc, qt_curso_tec_subs, 
                                        qt_curso_tec_eja, nu_ano_censo)
                VALUES {values_str}
                ON CONFLICT (co_curso_educ_profissional) DO UPDATE SET
                    qt_mat_curso_tec = EXCLUDED.qt_mat_curso_tec,
                    qt_curso_tec_conc = EXCLUDED.qt_curso_tec_conc,
                    qt_curso_tec_subs = EXCLUDED.qt_curso_tec_subs,
                    qt_curso_tec_eja = EXCLUDED.qt_curso_tec_eja
            """
            
            self.db.execute(text(sql))
            return len(cursos_data)
        except Exception as e:
            print(f"⚠️  Erro no bulk insert de cursos técnicos: {e}")
            return 0