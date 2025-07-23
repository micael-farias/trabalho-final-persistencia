from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class CursoTecnico(Base):
    __tablename__ = "cursos_tecnicos"
    
    co_curso_educ_profissional = Column(Integer, primary_key=True, index=True)
    no_curso_educ_profissional = Column(String(255), nullable=False)
    no_area_curso_profissional = Column(String(255), nullable=False)
    id_area_curso_profissional = Column(Integer, nullable=False)
    qt_mat_curso_tec = Column(Integer, default=0)
    qt_curso_tec_conc = Column(Integer, default=0)
    qt_curso_tec_subs = Column(Integer, default=0)
    qt_curso_tec_eja = Column(Integer, default=0)
    nu_ano_censo = Column(Integer, nullable=False)
    
    escola_cursos = relationship("EscolaCurso", back_populates="curso_tecnico")