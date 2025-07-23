from pydantic import BaseModel
from typing import Optional, List

class EscolaBase(BaseModel):
    co_entidade: int
    no_entidade: str
    sg_uf: str
    no_municipio: str
    tp_dependencia: int
    tp_localizacao: int
    tp_situacao_funcionamento: int
    qt_mat_bas: Optional[int] = 0
    qt_doc_bas: Optional[int] = 0
    nu_ano_censo: int
    
class EscolaResponse(EscolaBase):
    class Config:
        from_attributes = True