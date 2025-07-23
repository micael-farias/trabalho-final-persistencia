import pandas as pd
import chardet

class CSVUtils:
    @staticmethod
    def safe_int(value, default=0):
        """Converte valor para int de forma segura"""
        if pd.isna(value) or value == '' or value is None:
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_bool(value, default=False):
        """Converte valor para bool de forma segura"""
        if pd.isna(value) or value == '' or value is None:
            return default
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_str(value, default='', max_length=None):
        """Converte valor para string de forma segura"""
        if pd.isna(value) or value is None:
            return default
        
        try:
            result = str(value).strip()
            # Escapar aspas simples para SQL
            result = result.replace("'", "''")
            if max_length and len(result) > max_length:
                result = result[:max_length]
            return result
        except:
            return default
    
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detecta a codificação do arquivo"""
        encodings_to_try = ['iso-8859-1', 'windows-1252', 'cp1252', 'latin1', 'utf-8']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as test_file:
                    test_file.read(1000)
                print(f"✅ Usando codificação: {encoding}")
                return encoding
            except:
                continue
        
        return 'iso-8859-1'
    
    @staticmethod
    def read_csv_safe(file_path: str, **kwargs) -> pd.DataFrame:
        """Lê CSV com detecção automática de codificação"""
        encoding = CSVUtils.detect_encoding(file_path)
        
        try:
            df = pd.read_csv(
                file_path, 
                sep=';', 
                encoding=encoding, 
                low_memory=False,
                na_values=['', ' ', 'NULL', 'null', 'NaN', 'nan'],
                keep_default_na=True,
                **kwargs
            )
            print(f"✅ CSV lido com sucesso usando {encoding}")
            return df
        except Exception as e:
            print(f"❌ Erro ao ler CSV: {e}")
            raise