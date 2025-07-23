import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..utils.csv_utils import CSVUtils
from ..validators.csv_validators import CSVValidators
from ..repositories.curso_tecnico_repository import CursoTecnicoRepository
from ..repositories.escola_cursos_repository import EscolaCursosRepository

class CursoProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.curso_repo = CursoTecnicoRepository(db)
        self.escola_curso_repo = EscolaCursosRepository(db)
        self.utils = CSVUtils()
        self.validators = CSVValidators()
    
    def import_cursos_tecnicos(self, csv_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            print("🚀 IMPORTAÇÃO DE CURSOS TÉCNICOS - OTIMIZADA")
            print("=" * 50)
            
            print("📊 Carregando CSV de cursos técnicos...")
            df = self.utils.read_csv_safe(csv_path)
            print(f"📈 {len(df):,} registros encontrados")
            
            required_columns = ['CO_ENTIDADE', 'CO_CURSO_EDUC_PROFISSIONAL']
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                return {
                    'success': False, 
                    'error': f'Colunas obrigatórias ausentes: {missing_cols}'
                }
            
            print("🔍 Filtrando registros válidos...")
            valid_indices = []
            for idx, row in df.iterrows():
                if self.validators.validate_curso_tecnico_data(row):
                    valid_indices.append(idx)
            
            valid_df = df.loc[valid_indices]
            print(f"✅ {len(valid_df):,} registros válidos")
            
            if len(valid_df) == 0:
                return {'success': False, 'error': 'Nenhum curso técnico válido encontrado'}
            
            return self._process_curso_batches(valid_df, start_time)
            
        except Exception as e:
            self.db.rollback()
            return {
                'success': False, 
                'error': f'Erro geral na importação de cursos técnicos: {str(e)}',
                'processing_time_seconds': time.time() - start_time
            }
    
    def _process_curso_batches(self, valid_df, start_time):
        """Processa cursos em lotes"""
        BATCH_SIZE = 500
        total_batches = (len(valid_df) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"📦 Processando em {total_batches} lotes de até {BATCH_SIZE} registros")
        print("=" * 50)
        
        total_cursos = 0
        total_escola_cursos = 0
        total_errors = 0
        
        for batch_num in range(total_batches):
            batch_start_time = time.time()
            start_idx = batch_num * BATCH_SIZE
            end_idx = min((batch_num + 1) * BATCH_SIZE, len(valid_df))
            batch_df = valid_df.iloc[start_idx:end_idx]
            
            print(f"🔄 Lote {batch_num + 1}/{total_batches}: registros {start_idx+1}-{end_idx} ({len(batch_df)} registros)")
            
            # Processar lote
            batch_results = self._process_single_curso_batch(batch_df)
            
            try:
                # Usar os novos repositórios específicos
                batch_cursos = self.curso_repo.bulk_insert_cursos_tecnicos(batch_results['cursos'])
                batch_escola_cursos = self.escola_curso_repo.bulk_insert_escola_cursos(batch_results['escola_cursos'])
                
                self.db.commit()
                
                total_cursos += batch_cursos
                total_escola_cursos += batch_escola_cursos
                total_errors += batch_results['errors']
                
                batch_time = time.time() - batch_start_time
                print(f"   ✅ Concluído em {batch_time:.1f}s: {batch_cursos} cursos únicos, {batch_escola_cursos} relações escola-curso")
                
                # ETA - Cálculo do tempo estimado restante
                if batch_num > 0:
                    avg_time_per_batch = (time.time() - start_time) / (batch_num + 1)
                    remaining_batches = total_batches - (batch_num + 1)
                    eta_seconds = remaining_batches * avg_time_per_batch
                    eta_minutes = int(eta_seconds / 60)
                    print(f"   ⏱️  ETA: ~{eta_minutes}min {int(eta_seconds % 60)}s restantes")
            
            except Exception as e:
                self.db.rollback()
                print(f"   ❌ Erro no lote: {e}")
                total_errors += len(batch_df)
                continue
            
            print()
        
        # Estatísticas finais
        return self._generate_curso_final_stats(valid_df, total_cursos, total_escola_cursos, total_errors, total_batches, start_time)
    
    def _process_single_curso_batch(self, batch_df):
        """Processa um único lote de cursos"""
        cursos_batch = []
        escola_cursos_batch = []
        batch_errors = 0
        cursos_vistos = set()
        
        for _, row in batch_df.iterrows():
            try:
                co_curso = self.utils.safe_int(row['CO_CURSO_EDUC_PROFISSIONAL'])
                co_entidade = self.utils.safe_int(row['CO_ENTIDADE'])
                
                # Dados do curso técnico (apenas uma vez por curso)
                if co_curso not in cursos_vistos:
                    curso_data = {
                        'co_curso_educ_profissional': co_curso,
                        'no_curso_educ_profissional': self.utils.safe_str(row.get('NO_CURSO_EDUC_PROFISSIONAL'), max_length=255),
                        'no_area_curso_profissional': self.utils.safe_str(row.get('NO_AREA_CURSO_PROFISSIONAL'), max_length=255),
                        'id_area_curso_profissional': self.utils.safe_int(row.get('ID_AREA_CURSO_PROFISSIONAL')),
                        'qt_mat_curso_tec': self.utils.safe_int(row.get('QT_MAT_CURSO_TEC')),
                        'qt_curso_tec_conc': self.utils.safe_int(row.get('QT_CURSO_TEC_CONC')),
                        'qt_curso_tec_subs': self.utils.safe_int(row.get('QT_CURSO_TEC_SUBS')),
                        'qt_curso_tec_eja': self.utils.safe_int(row.get('QT_CURSO_TEC_EJA')),
                        'nu_ano_censo': self.utils.safe_int(row.get('NU_ANO_CENSO'), 2024)
                    }
                    cursos_batch.append(curso_data)
                    cursos_vistos.add(co_curso)
                
                # Dados da relação escola-curso
                escola_curso_data = {
                    'co_entidade': co_entidade,
                    'co_curso_educ_profissional': co_curso,
                    'qt_mat_curso_tec': self.utils.safe_int(row.get('QT_MAT_CURSO_TEC')),
                    'qt_mat_curso_tec_ct': self.utils.safe_int(row.get('QT_MAT_CURSO_TEC_CT')),
                    'qt_mat_curso_tec_nm': self.utils.safe_int(row.get('QT_MAT_CURSO_TEC_NM')),
                    'qt_mat_curso_tec_conc': self.utils.safe_int(row.get('QT_MAT_CURSO_TEC_CONC')),
                    'qt_mat_tec_subs': self.utils.safe_int(row.get('QT_MAT_TEC_SUBS')),
                    'qt_mat_tec_eja': self.utils.safe_int(row.get('QT_MAT_TEC_EJA')),
                    'nu_ano_censo': self.utils.safe_int(row.get('NU_ANO_CENSO'), 2024)
                }
                escola_cursos_batch.append(escola_curso_data)
                
            except Exception as e:
                batch_errors += 1
                continue
        
        return {
            'cursos': cursos_batch,
            'escola_cursos': escola_cursos_batch,
            'errors': batch_errors
        }
    
    def _generate_curso_final_stats(self, valid_df, total_cursos, total_escola_cursos, total_errors, total_batches, start_time):
        """Gera estatísticas finais para cursos"""
        total_time = time.time() - start_time
        minutes = int(total_time / 60)
        seconds = int(total_time % 60)
        
        print("=" * 50)
        print("📊 IMPORTAÇÃO DE CURSOS TÉCNICOS CONCLUÍDA!")
        print("=" * 50)
        print(f"⏱️  Tempo total: {minutes}min {seconds}s")
        print(f"📈 Registros processados: {len(valid_df):,}")
        print(f"🎓 Cursos técnicos únicos: {total_cursos:,}")
        print(f"🏫 Relações escola-curso: {total_escola_cursos:,}")
        print(f"⚠️  Erros: {total_errors:,}")
        print(f"📊 Taxa de sucesso: {((total_escola_cursos)/(len(valid_df))*100):.1f}%")
        print(f"🚀 Velocidade: {len(valid_df)/total_time:.0f} registros/segundo")
        
        return {
            'success': True,
            'cursos_imported': total_cursos,
            'escola_cursos_imported': total_escola_cursos,
            'total_processed': len(valid_df),
            'errors_count': total_errors,
            'processing_time_seconds': total_time,
            'processing_time_formatted': f"{minutes}min {seconds}s",
            'records_per_second': round(len(valid_df)/total_time, 2) if total_time > 0 else 0,
            'batches_processed': total_batches,
            'success_rate': f"{((total_escola_cursos)/(len(valid_df))*100):.1f}%"
        }