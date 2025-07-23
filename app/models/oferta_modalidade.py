from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class OfertaModalidade(Base):
    __tablename__ = "ofertas_modalidade"
    
    id = Column(Integer, primary_key=True, index=True)
    co_entidade = Column(Integer, ForeignKey("escolas.co_entidade"))
    tipo_modalidade = Column(String(50), nullable=False)  # INF, FUND, MED, PROF, EJA, ESP
    qt_matriculas = Column(Integer, default=0)
    qt_docentes = Column(Integer, default=0)
    qt_turmas = Column(Integer, default=0)
    in_diurno = Column(Boolean, default=False)
    in_noturno = Column(Boolean, default=False)
    nu_ano_censo = Column(Integer, nullable=False)
    
    escola = relationship("Escola", back_populates="ofertas_modalidade")