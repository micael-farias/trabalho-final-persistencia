import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..utils.csv_utils import CSVUtils
from ..validators.csv_validators import CSVValidators
from ..repositories.escola_repository import EscolaRepository
from ..repositories.infra_repository import InfraestruturaRepository
from ..repositories.oferta_modalidade_repository import OfertaModalidadeRepository

class EscolaProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.escola_repo = EscolaRepository(db)
        self.infra_repo = InfraestruturaRepository(db)
        self.oferta_repo = OfertaModalidadeRepository(db)
        self.utils = CSVUtils()
        self.validators = CSVValidators()
    
    def import_microdados_escola(self, csv_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            print("🚀 IMPORTAÇÃO OTIMIZADA - PROCESSANDO TODOS OS REGISTROS")
            print("=" * 60)
            
            print("📊 Carregando CSV...")
            df = self.utils.read_csv_safe(csv_path)
            print(f"📈 {len(df):,} registros encontrados")
            print(f"📋 {len(df.columns)} colunas encontradas")
            
            required_columns = ['CO_ENTIDADE', 'NO_ENTIDADE', 'SG_UF', 'NO_MUNICIPIO']
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                return {
                    'success': False, 
                    'error': f'Colunas obrigatórias ausentes: {missing_cols}'
                }
            
            print("🔍 Filtrando registros válidos...")
            valid_indices = []
            for idx, row in df.iterrows():
                if self.validators.validate_escola_data(row):
                    valid_indices.append(idx)
            
            valid_df = df.loc[valid_indices]
            print(f"✅ {len(valid_df):,} registros válidos de {len(df):,} totais ({len(valid_df)/len(df)*100:.1f}%)")
            
            return self._process_escola_batches(valid_df, start_time)
            
        except Exception as e:
            self.db.rollback()
            return {
                'success': False, 
                'error': f'Erro geral na importação: {str(e)}',
                'processing_time_seconds': time.time() - start_time
            }
    
    def _process_escola_batches(self, valid_df, start_time):
        """Processa escolas em lotes"""
        BATCH_SIZE = 1000
        total_batches = (len(valid_df) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"📦 Processando em {total_batches} lotes de até {BATCH_SIZE} registros")
        print("=" * 60)
        
        total_escolas = 0
        total_infra = 0
        total_ofertas = 0
        total_errors = 0
        
        for batch_num in range(total_batches):
            batch_start_time = time.time()
            start_idx = batch_num * BATCH_SIZE
            end_idx = min((batch_num + 1) * BATCH_SIZE, len(valid_df))
            batch_df = valid_df.iloc[start_idx:end_idx]
            
            print(f"🔄 Lote {batch_num + 1}/{total_batches}: registros {start_idx+1}-{end_idx} ({len(batch_df)} registros)")
            
            # Processar lote
            batch_results = self._process_single_batch(batch_df)
            
            try:
                # Usar os novos repositórios específicos
                batch_escolas = self.escola_repo.bulk_insert_escolas(batch_results['escolas'])
                batch_infra = self.infra_repo.bulk_insert_infraestruturas(batch_results['infraestruturas'])
                batch_ofertas = self.oferta_repo.bulk_insert_ofertas_modalidade(batch_results['ofertas'])
                
                self.db.commit()
                
                total_escolas += batch_escolas
                total_infra += batch_infra
                total_ofertas += batch_ofertas
                total_errors += batch_results['errors']
                
                batch_time = time.time() - batch_start_time
                print(f"   ✅ Concluído em {batch_time:.1f}s: {batch_escolas} escolas, {batch_infra} infraestruturas, {batch_ofertas} ofertas")
                
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
        return self._generate_final_stats(valid_df, total_escolas, total_infra, total_ofertas, total_errors, total_batches, start_time)
    
    def _process_single_batch(self, batch_df):
        """Processa um único lote"""
        escolas_batch = []
        infraestruturas_batch = []
        ofertas_batch = []
        batch_errors = 0
        
        for _, row in batch_df.iterrows():
            try:
                co_entidade = self.utils.safe_int(row['CO_ENTIDADE'])
                
                # Dados da escola
                escola_data = {
                    'co_entidade': co_entidade,
                    'no_entidade': self.utils.safe_str(row['NO_ENTIDADE'], max_length=255),
                    'sg_uf': self.utils.safe_str(row['SG_UF'], max_length=2),
                    'no_municipio': self.utils.safe_str(row['NO_MUNICIPIO'], max_length=100),
                    'tp_dependencia': self.utils.safe_int(row.get('TP_DEPENDENCIA'), 1),
                    'tp_localizacao': self.utils.safe_int(row.get('TP_LOCALIZACAO'), 1),
                    'tp_situacao_funcionamento': self.utils.safe_int(row.get('TP_SITUACAO_FUNCIONAMENTO'), 1),
                    'qt_mat_bas': self.utils.safe_int(row.get('QT_MAT_BAS'), 0),
                    'qt_doc_bas': self.utils.safe_int(row.get('QT_DOC_BAS'), 0),
                    'nu_ano_censo': self.utils.safe_int(row.get('NU_ANO_CENSO'), 2024)
                }
                escolas_batch.append(escola_data)
                
                # Dados de infraestrutura
                infra_data = {
                    'co_entidade': co_entidade,
                    'in_internet': self.utils.safe_bool(row.get('IN_INTERNET')),
                    'in_biblioteca': self.utils.safe_bool(row.get('IN_BIBLIOTECA')),
                    'in_laboratorio_informatica': self.utils.safe_bool(row.get('IN_LABORATORIO_INFORMATICA')),
                    'in_laboratorio_ciencias': self.utils.safe_bool(row.get('IN_LABORATORIO_CIENCIAS')),
                    'in_quadra_esportes': self.utils.safe_bool(row.get('IN_QUADRA_ESPORTES')),
                    'in_acessibilidade_rampas': self.utils.safe_bool(row.get('IN_ACESSIBILIDADE_RAMPAS')),
                    'qt_desktop_aluno': self.utils.safe_int(row.get('QT_DESKTOP_ALUNO')),
                    'qt_salas_utilizadas': self.utils.safe_int(row.get('QT_SALAS_UTILIZADAS'))
                }
                infraestruturas_batch.append(infra_data)
                
                # Dados de modalidades
                modalidades = {
                    'INF': 'Educação Infantil',
                    'FUND': 'Ensino Fundamental',
                    'MED': 'Ensino Médio',
                    'PROF': 'Educação Profissional',
                    'EJA': 'Educação de Jovens e Adultos',
                    'ESP': 'Educação Especial'
                }
                
                for cod_modalidade, nome_modalidade in modalidades.items():
                    oferece_modalidade = self.utils.safe_bool(row.get(f'IN_{cod_modalidade}'))
                    qt_matriculas = self.utils.safe_int(row.get(f'QT_MAT_{cod_modalidade}'))
                    
                    if oferece_modalidade or qt_matriculas > 0:
                        oferta_data = {
                            'co_entidade': co_entidade,
                            'tipo_modalidade': cod_modalidade,
                            'qt_matriculas': qt_matriculas,
                            'qt_docentes': self.utils.safe_int(row.get(f'QT_DOC_{cod_modalidade}')),
                            'qt_turmas': self.utils.safe_int(row.get(f'QT_TUR_{cod_modalidade}')),
                            'in_diurno': self.utils.safe_bool(row.get('IN_DIURNO')),
                            'in_noturno': self.utils.safe_bool(row.get('IN_NOTURNO')),
                            'nu_ano_censo': 2024
                        }
                        ofertas_batch.append(oferta_data)
                
            except Exception as e:
                batch_errors += 1
                continue
        
        return {
            'escolas': escolas_batch,
            'infraestruturas': infraestruturas_batch,
            'ofertas': ofertas_batch,
            'errors': batch_errors
        }
    
    def _generate_final_stats(self, valid_df, total_escolas, total_infra, total_ofertas, total_errors, total_batches, start_time):
        """Gera estatísticas finais"""
        total_time = time.time() - start_time
        minutes = int(total_time / 60)
        seconds = int(total_time % 60)
        
        print("=" * 60)
        print("📊 IMPORTAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print(f"⏱️  Tempo total: {minutes}min {seconds}s")
        print(f"📈 Registros processados: {len(valid_df):,}")
        print(f"🏫 Escolas importadas: {total_escolas:,}")
        print(f"🏗️  Infraestruturas importadas: {total_infra:,}")
        print(f"📚 Ofertas de modalidade importadas: {total_ofertas:,}")
        print(f"⚠️  Erros: {total_errors:,}")
        print(f"📊 Taxa de sucesso: {((total_escolas)/(len(valid_df))*100):.1f}%")
        print(f"🚀 Velocidade: {len(valid_df)/total_time:.0f} registros/segundo")
        
        return {
            'success': True,
            'escolas_imported': total_escolas,
            'infraestruturas_imported': total_infra,
            'ofertas_imported': total_ofertas,
            'total_processed': len(valid_df),
            'errors_count': total_errors,
            'processing_time_seconds': total_time,
            'processing_time_formatted': f"{minutes}min {seconds}s",
            'records_per_second': round(len(valid_df)/total_time, 2) if total_time > 0 else 0,
            'batches_processed': total_batches,
            'success_rate': f"{((total_escolas)/(len(valid_df))*100):.1f}%"
        }