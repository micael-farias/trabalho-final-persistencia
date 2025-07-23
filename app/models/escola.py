from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Escola(Base):
    __tablename__ = "escolas"
    
    co_entidade = Column(Integer, primary_key=True, index=True)
    no_entidade = Column(String(255), nullable=False)
    sg_uf = Column(String(2), nullable=False, index=True)
    no_municipio = Column(String(100), nullable=False, index=True)
    tp_dependencia = Column(Integer, nullable=False)
    tp_localizacao = Column(Integer, nullable=False)
    tp_situacao_funcionamento = Column(Integer, nullable=False)
    qt_mat_bas = Column(Integer, default=0)
    qt_doc_bas = Column(Integer, default=0)
    nu_ano_censo = Column(Integer, nullable=False)
    
    infraestrutura = relationship("Infraestrutura", back_populates="escola", uselist=False)
    ofertas_modalidade = relationship("OfertaModalidade", back_populates="escola")
    escola_cursos = relationship("EscolaCurso", back_populates="escola")