from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..models.escola import Escola
from .base_repository import BaseRepository
from sqlalchemy import text

class EscolaRepository(BaseRepository[Escola]):
    def __init__(self, db: Session):
        super().__init__(Escola, db)
    
    def get_by_codigo(self, co_entidade: int) -> Optional[Escola]:
        return self.db.query(self.model).filter(self.model.co_entidade == co_entidade).first()
    
    def get_by_uf(self, uf: str) -> List[Escola]:
        return self.db.query(self.model).filter(self.model.sg_uf == uf).all()
    
    def get_by_municipio(self, municipio: str) -> List[Escola]:
        return self.db.query(self.model).filter(self.model.no_municipio.ilike(f"%{municipio}%")).all()

    def bulk_insert_escolas(self, escolas_data: List[Dict]) -> int:
        if not escolas_data:
            return 0
        
        try:
            values_list = []
            for data in escolas_data:
                no_entidade = data['no_entidade']
                no_municipio = data['no_municipio']
                
                values = "({}, '{}', '{}', '{}', {}, {}, {}, {}, {}, {})".format(
                    data['co_entidade'],
                    no_entidade,
                    data['sg_uf'],
                    no_municipio,
                    data['tp_dependencia'],
                    data['tp_localizacao'],
                    data['tp_situacao_funcionamento'],
                    data['qt_mat_bas'],
                    data['qt_doc_bas'],
                    data['nu_ano_censo']
                )
                values_list.append(values)
            
            values_str = ', '.join(values_list)
            sql = f"""
                INSERT INTO escolas (co_entidade, no_entidade, sg_uf, no_municipio, tp_dependencia, 
                                   tp_localizacao, tp_situacao_funcionamento, qt_mat_bas, qt_doc_bas, nu_ano_censo)
                VALUES {values_str}
                ON CONFLICT (co_entidade) DO NOTHING
            """
            
            self.db.execute(text(sql))
            return len(escolas_data)
        except Exception as e:
            print(f"⚠️  Erro no bulk insert de escolas: {e}")
            return 0
    