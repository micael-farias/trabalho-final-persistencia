from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any, List
from ..models.escola import Escola
from ..models.infraestrutura import Infraestrutura
from ..models.oferta_modalidade import OfertaModalidade
from ..models.curso_tecnico import CursoTecnico
from ..models.escola_curso import EscolaCurso

class RelatorioRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def relatorio_geral(self) -> Dict[str, Any]:
        """Relatório geral com estatísticas gerais"""
        try:
            # Contadores gerais
            total_escolas = self.db.query(Escola).count()
            total_infraestruturas = self.db.query(Infraestrutura).count()
            total_ofertas = self.db.query(OfertaModalidade).count()
            total_cursos = self.db.query(CursoTecnico).count()
            total_escola_cursos = self.db.query(EscolaCurso).count()
            
            # Estatísticas por UF
            escolas_por_uf = self.db.query(
                Escola.sg_uf,
                func.count(Escola.co_entidade).label('total')
            ).group_by(Escola.sg_uf).order_by(func.count(Escola.co_entidade).desc()).all()
            
            # Matrículas por modalidade
            matriculas_por_modalidade = self.db.query(
                OfertaModalidade.tipo_modalidade,
                func.sum(OfertaModalidade.qt_matriculas).label('total_matriculas')
            ).group_by(OfertaModalidade.tipo_modalidade).order_by(func.sum(OfertaModalidade.qt_matriculas).desc()).all()
            
            # Infraestrutura - percentuais
            total_com_internet = self.db.query(Infraestrutura).filter(Infraestrutura.in_internet == True).count()
            total_com_biblioteca = self.db.query(Infraestrutura).filter(Infraestrutura.in_biblioteca == True).count()
            total_com_lab_info = self.db.query(Infraestrutura).filter(Infraestrutura.in_laboratorio_informatica == True).count()
            
            # Dependência administrativa
            escolas_por_dependencia = self.db.query(
                Escola.tp_dependencia,
                func.count(Escola.co_entidade).label('total')
            ).group_by(Escola.tp_dependencia).all()
            
            # Localização
            escolas_por_localizacao = self.db.query(
                Escola.tp_localizacao,
                func.count(Escola.co_entidade).label('total')
            ).group_by(Escola.tp_localizacao).all()
            
            return {
                'resumo_geral': {
                    'total_escolas': total_escolas,
                    'total_infraestruturas': total_infraestruturas,
                    'total_ofertas_modalidade': total_ofertas,
                    'total_cursos_tecnicos': total_cursos,
                    'total_relacoes_escola_curso': total_escola_cursos
                },
                'escolas_por_uf': [
                    {'uf': uf, 'total_escolas': total} 
                    for uf, total in escolas_por_uf
                ],
                'matriculas_por_modalidade': [
                    {
                        'modalidade': modalidade,
                        'total_matriculas': int(total or 0),
                        'modalidade_nome': self._get_modalidade_nome(modalidade)
                    }
                    for modalidade, total in matriculas_por_modalidade
                ],
                'infraestrutura_percentuais': {
                    'com_internet': round((total_com_internet / total_infraestruturas * 100), 2) if total_infraestruturas > 0 else 0,
                    'com_biblioteca': round((total_com_biblioteca / total_infraestruturas * 100), 2) if total_infraestruturas > 0 else 0,
                    'com_laboratorio_informatica': round((total_com_lab_info / total_infraestruturas * 100), 2) if total_infraestruturas > 0 else 0
                },
                'escolas_por_dependencia': [
                    {
                        'tipo_dependencia': dep,
                        'total_escolas': total,
                        'dependencia_nome': self._get_dependencia_nome(dep)
                    }
                    for dep, total in escolas_por_dependencia
                ],
                'escolas_por_localizacao': [
                    {
                        'tipo_localizacao': loc,
                        'total_escolas': total,
                        'localizacao_nome': self._get_localizacao_nome(loc)
                    }
                    for loc, total in escolas_por_localizacao
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def relatorio_por_uf(self, uf: str) -> Dict[str, Any]:
        """Relatório detalhado por UF"""
        try:
            uf = uf.upper()
            
            # Escolas na UF
            escolas = self.db.query(Escola).filter(Escola.sg_uf == uf).all()
            
            if not escolas:
                return {'error': f'Nenhuma escola encontrada para a UF: {uf}'}
            
            co_entidades = [e.co_entidade for e in escolas]
            
            # Estatísticas da UF
            total_escolas = len(escolas)
            total_matriculas = sum(e.qt_mat_bas for e in escolas)
            total_docentes = sum(e.qt_doc_bas for e in escolas)
            
            # Escolas por município
            escolas_por_municipio = self.db.query(
                Escola.no_municipio,
                func.count(Escola.co_entidade).label('total')
            ).filter(Escola.sg_uf == uf).group_by(Escola.no_municipio).order_by(func.count(Escola.co_entidade).desc()).all()
            
            # Infraestrutura na UF
            infra_stats = self.db.query(
                func.count(Infraestrutura.id).label('total'),
                func.sum(func.cast(Infraestrutura.in_internet, text('INTEGER'))).label('com_internet'),
                func.sum(func.cast(Infraestrutura.in_biblioteca, text('INTEGER'))).label('com_biblioteca'),
                func.sum(func.cast(Infraestrutura.in_laboratorio_informatica, text('INTEGER'))).label('com_lab_info'),
                func.sum(func.cast(Infraestrutura.in_quadra_esportes, text('INTEGER'))).label('com_quadra'),
                func.sum(Infraestrutura.qt_desktop_aluno).label('total_computadores')
            ).filter(Infraestrutura.co_entidade.in_(co_entidades)).first()
            
            # Modalidades oferecidas na UF
            modalidades_uf = self.db.query(
                OfertaModalidade.tipo_modalidade,
                func.count(OfertaModalidade.id).label('escolas_oferecem'),
                func.sum(OfertaModalidade.qt_matriculas).label('total_matriculas'),
                func.sum(OfertaModalidade.qt_docentes).label('total_docentes')
            ).filter(OfertaModalidade.co_entidade.in_(co_entidades)).group_by(OfertaModalidade.tipo_modalidade).all()
            
            return {
                'uf': uf,
                'resumo': {
                    'total_escolas': total_escolas,
                    'total_matriculas_basicas': total_matriculas,
                    'total_docentes_basicos': total_docentes,
                    'media_matriculas_por_escola': round(total_matriculas / total_escolas, 2) if total_escolas > 0 else 0,
                    'media_docentes_por_escola': round(total_docentes / total_escolas, 2) if total_escolas > 0 else 0
                },
                'escolas_por_municipio': [
                    {'municipio': municipio, 'total_escolas': total}
                    for municipio, total in escolas_por_municipio
                ],
                'infraestrutura': {
                    'total_escolas_com_dados': int(infra_stats.total or 0),
                    'com_internet': int(infra_stats.com_internet or 0),
                    'com_biblioteca': int(infra_stats.com_biblioteca or 0),
                    'com_laboratorio_informatica': int(infra_stats.com_lab_info or 0),
                    'com_quadra_esportes': int(infra_stats.com_quadra or 0),
                    'total_computadores_alunos': int(infra_stats.total_computadores or 0)
                },
                'modalidades_oferecidas': [
                    {
                        'modalidade': mod,
                        'modalidade_nome': self._get_modalidade_nome(mod),
                        'escolas_que_oferecem': int(escolas),
                        'total_matriculas': int(matriculas or 0),
                        'total_docentes': int(docentes or 0)
                    }
                    for mod, escolas, matriculas, docentes in modalidades_uf
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def relatorio_cursos_tecnicos(self) -> Dict[str, Any]:
        """Relatório sobre cursos técnicos"""
        try:
            # Cursos mais oferecidos
            cursos_mais_oferecidos = self.db.query(
                CursoTecnico.no_curso_educ_profissional,
                CursoTecnico.no_area_curso_profissional,
                func.count(EscolaCurso.id).label('escolas_oferecem'),
                func.sum(EscolaCurso.qt_mat_curso_tec).label('total_matriculas')
            ).join(EscolaCurso, CursoTecnico.co_curso_educ_profissional == EscolaCurso.co_curso_educ_profissional)\
            .group_by(CursoTecnico.co_curso_educ_profissional, CursoTecnico.no_curso_educ_profissional, CursoTecnico.no_area_curso_profissional)\
            .order_by(func.count(EscolaCurso.id).desc()).limit(20).all()
            
            # Áreas profissionais
            areas_profissionais = self.db.query(
                CursoTecnico.no_area_curso_profissional,
                func.count(CursoTecnico.co_curso_educ_profissional).label('total_cursos'),
                func.count(EscolaCurso.id).label('total_ofertas'),
                func.sum(EscolaCurso.qt_mat_curso_tec).label('total_matriculas')
            ).outerjoin(EscolaCurso, CursoTecnico.co_curso_educ_profissional == EscolaCurso.co_curso_educ_profissional)\
            .group_by(CursoTecnico.no_area_curso_profissional)\
            .order_by(func.sum(EscolaCurso.qt_mat_curso_tec).desc()).all()
            
            # Estatísticas gerais
            total_cursos = self.db.query(CursoTecnico).count()
            total_ofertas = self.db.query(EscolaCurso).count()
            total_matriculas_tec = self.db.query(func.sum(EscolaCurso.qt_mat_curso_tec)).scalar() or 0
            
            cursos_por_uf = self.db.query(
                Escola.sg_uf,
                func.count(EscolaCurso.id).label('total_ofertas'),
                func.sum(EscolaCurso.qt_mat_curso_tec).label('total_matriculas')
            ).join(Escola, EscolaCurso.co_entidade == Escola.co_entidade)\
            .group_by(Escola.sg_uf)\
            .order_by(func.sum(EscolaCurso.qt_mat_curso_tec).desc()).all()
            
            return {
                'resumo_geral': {
                    'total_cursos_cadastrados': total_cursos,
                    'total_ofertas_escolas': total_ofertas,
                    'total_matriculas_tecnicas': int(total_matriculas_tec)
                },
                'cursos_mais_oferecidos': [
                    {
                        'nome_curso': nome_curso,
                        'area_profissional': area,
                        'escolas_que_oferecem': int(escolas),
                        'total_matriculas': int(matriculas or 0)
                    }
                    for nome_curso, area, escolas, matriculas in cursos_mais_oferecidos
                ],
                'areas_profissionais': [
                    {
                        'area_profissional': area,
                        'total_cursos': int(cursos),
                        'total_ofertas': int(ofertas or 0),
                        'total_matriculas': int(matriculas or 0)
                    }
                    for area, cursos, ofertas, matriculas in areas_profissionais
                ],
                'cursos_por_uf': [
                    {
                        'uf': uf,
                        'total_ofertas': int(ofertas),
                        'total_matriculas': int(matriculas or 0)
                    }
                    for uf, ofertas, matriculas in cursos_por_uf
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def relatorio_infraestrutura(self) -> Dict[str, Any]:
        try:
            total_escolas = self.db.query(Infraestrutura).count()
            
            infra_stats = self.db.query(
                func.sum(func.cast(Infraestrutura.in_internet, text('INTEGER'))).label('com_internet'),
                func.sum(func.cast(Infraestrutura.in_biblioteca, text('INTEGER'))).label('com_biblioteca'),
                func.sum(func.cast(Infraestrutura.in_laboratorio_informatica, text('INTEGER'))).label('com_lab_info'),
                func.sum(func.cast(Infraestrutura.in_laboratorio_ciencias, text('INTEGER'))).label('com_lab_ciencias'),
                func.sum(func.cast(Infraestrutura.in_quadra_esportes, text('INTEGER'))).label('com_quadra'),
                func.sum(func.cast(Infraestrutura.in_acessibilidade_rampas, text('INTEGER'))).label('com_rampas'),
                func.sum(Infraestrutura.qt_desktop_aluno).label('total_computadores'),
                func.sum(Infraestrutura.qt_salas_utilizadas).label('total_salas')
            ).first()
            
            infra_por_uf = self.db.query(
                Escola.sg_uf,
                func.count(Infraestrutura.id).label('total_escolas'),
                func.sum(func.cast(Infraestrutura.in_internet, text('INTEGER'))).label('com_internet'),
                func.sum(func.cast(Infraestrutura.in_biblioteca, text('INTEGER'))).label('com_biblioteca'),
                func.sum(Infraestrutura.qt_desktop_aluno).label('total_computadores')
            ).join(Escola, Infraestrutura.co_entidade == Escola.co_entidade)\
            .group_by(Escola.sg_uf)\
            .order_by(func.count(Infraestrutura.id).desc()).all()
            
            return {
                'resumo_geral': {
                    'total_escolas_com_dados': total_escolas,
                    'percentual_com_internet': round((int(infra_stats.com_internet or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'percentual_com_biblioteca': round((int(infra_stats.com_biblioteca or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'percentual_com_lab_informatica': round((int(infra_stats.com_lab_info or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'percentual_com_lab_ciencias': round((int(infra_stats.com_lab_ciencias or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'percentual_com_quadra_esportes': round((int(infra_stats.com_quadra or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'percentual_com_acessibilidade': round((int(infra_stats.com_rampas or 0) / total_escolas * 100), 2) if total_escolas > 0 else 0,
                    'total_computadores_alunos': int(infra_stats.total_computadores or 0),
                    'total_salas_utilizadas': int(infra_stats.total_salas or 0),
                    'media_computadores_por_escola': round((int(infra_stats.total_computadores or 0) / total_escolas), 2) if total_escolas > 0 else 0
                },
                'infraestrutura_por_uf': [
                    {
                        'uf': uf,
                        'total_escolas': int(escolas),
                        'com_internet': int(internet or 0),
                        'com_biblioteca': int(biblioteca or 0),
                        'total_computadores': int(computadores or 0),
                        'percentual_internet': round((int(internet or 0) / int(escolas) * 100), 2) if int(escolas) > 0 else 0
                    }
                    for uf, escolas, internet, biblioteca, computadores in infra_por_uf
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_modalidade_nome(self, codigo: str) -> str:
        modalidades = {
            'INF': 'Educação Infantil',
            'FUND': 'Ensino Fundamental',
            'MED': 'Ensino Médio',
            'PROF': 'Educação Profissional',
            'EJA': 'Educação de Jovens e Adultos',
            'ESP': 'Educação Especial'
        }
        return modalidades.get(codigo, codigo)
    
    def _get_dependencia_nome(self, codigo: int) -> str:
        dependencias = {
            1: 'Federal',
            2: 'Estadual',
            3: 'Municipal',
            4: 'Privada'
        }
        return dependencias.get(codigo, f'Código {codigo}')
    
    def _get_localizacao_nome(self, codigo: int) -> str:
        localizacoes = {
            1: 'Urbana',
            2: 'Rural'
        }
        return localizacoes.get(codigo, f'Código {codigo}')