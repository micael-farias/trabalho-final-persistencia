from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Infraestrutura(Base):
    __tablename__ = "infraestruturas"
    
    id = Column(Integer, primary_key=True, index=True)
    co_entidade = Column(Integer, ForeignKey("escolas.co_entidade"), unique=True)
    in_internet = Column(Boolean, default=False)
    in_biblioteca = Column(Boolean, default=False)
    in_laboratorio_informatica = Column(Boolean, default=False)
    in_laboratorio_ciencias = Column(Boolean, default=False)
    in_quadra_esportes = Column(Boolean, default=False)
    in_acessibilidade_rampas = Column(Boolean, default=False)
    qt_desktop_aluno = Column(Integer, default=0)
    qt_salas_utilizadas = Column(Integer, default=0)
    
    escola = relationship("Escola", back_populates="infraestrutura")