
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.escola_curso import EscolaCurso
from .base_repository import BaseRepository
from sqlalchemy import text

class EscolaCursosRepository(BaseRepository[EscolaCurso]):
    def __init__(self, db: Session):
        super().__init__(EscolaCurso, db)
    
    def bulk_insert_escola_cursos(self, escola_cursos_data: List[Dict]) -> int:
        """Insere relações escola-curso em lote"""
        if not escola_cursos_data:
            return 0
        
        try:
            values_list = []
            for data in escola_cursos_data:
                values = "({}, {}, {}, {}, {}, {}, {}, {}, {})".format(
                    data['co_entidade'],
                    data['co_curso_educ_profissional'],
                    data['qt_mat_curso_tec'],
                    data['qt_mat_curso_tec_ct'],
                    data['qt_mat_curso_tec_nm'],
                    data['qt_mat_curso_tec_conc'],
                    data['qt_mat_tec_subs'],
                    data['qt_mat_tec_eja'],
                    data['nu_ano_censo']
                )
                values_list.append(values)
            
            values_str = ', '.join(values_list)
            sql = f"""
                INSERT INTO escola_cursos (co_entidade, co_curso_educ_profissional, qt_mat_curso_tec,
                                        qt_mat_curso_tec_ct, qt_mat_curso_tec_nm, qt_mat_curso_tec_conc,
                                        qt_mat_tec_subs, qt_mat_tec_eja, nu_ano_censo)
                VALUES {values_str}
                ON CONFLICT (co_entidade, co_curso_educ_profissional) DO UPDATE SET
                    qt_mat_curso_tec = EXCLUDED.qt_mat_curso_tec,
                    qt_mat_curso_tec_ct = EXCLUDED.qt_mat_curso_tec_ct,
                    qt_mat_curso_tec_nm = EXCLUDED.qt_mat_curso_tec_nm,
                    qt_mat_curso_tec_conc = EXCLUDED.qt_mat_curso_tec_conc,
                    qt_mat_tec_subs = EXCLUDED.qt_mat_tec_subs,
                    qt_mat_tec_eja = EXCLUDED.qt_mat_tec_eja
            """
            
            self.db.execute(text(sql))
            return len(escola_cursos_data)
        except Exception as e:
            print(f"⚠️  Erro no bulk insert de escola-cursos: {e}")
            return 0