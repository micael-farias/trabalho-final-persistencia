from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class EscolaCurso(Base):
    __tablename__ = "escola_cursos"
    
    id = Column(Integer, primary_key=True, index=True)
    co_entidade = Column(Integer, ForeignKey("escolas.co_entidade"))
    co_curso_educ_profissional = Column(Integer, ForeignKey("cursos_tecnicos.co_curso_educ_profissional"))
    qt_mat_curso_tec = Column(Integer, default=0)
    qt_mat_curso_tec_ct = Column(Integer, default=0)
    qt_mat_curso_tec_nm = Column(Integer, default=0)
    qt_mat_curso_tec_conc = Column(Integer, default=0)
    qt_mat_tec_subs = Column(Integer, default=0)
    qt_mat_tec_eja = Column(Integer, default=0)
    nu_ano_censo = Column(Integer, nullable=False)
    
    escola = relationship("Escola", back_populates="escola_cursos")
    curso_tecnico = relationship("CursoTecnico", back_populates="escola_cursos")