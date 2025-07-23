import pandas as pd
from ..utils.csv_utils import CSVUtils

class CSVValidators:
    @staticmethod
    def validate_escola_data(row) -> bool:
        """Valida se os dados básicos da escola estão presentes"""
        required_fields = ['CO_ENTIDADE', 'NO_ENTIDADE', 'SG_UF', 'NO_MUNICIPIO']
        
        for field in required_fields:
            value = row.get(field)
            if pd.isna(value) or value == '' or value is None:
                return False
        
        try:
            co_entidade = int(row['CO_ENTIDADE'])
            if co_entidade <= 0:
                return False
        except:
            return False
        
        return True
    
    @staticmethod
    def validate_curso_tecnico_data(row) -> bool:
        """Valida dados de curso técnico"""
        co_entidade = CSVUtils.safe_int(row.get('CO_ENTIDADE'))
        co_curso = CSVUtils.safe_int(row.get('CO_CURSO_EDUC_PROFISSIONAL'))
        
        return co_entidade > 0 and co_curso > 0