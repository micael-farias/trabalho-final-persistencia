from app.core.database import engine
from sqlalchemy import text

def clear_database():
    try:
        print("🗑️  Limpando banco de dados...")
        
        with engine.connect() as connection:
            connection.execute(text("SET session_replication_role = replica;"))
            
            tables = [
                'escola_cursos',
                'ofertas_modalidade', 
                'infraestruturas',
                'cursos_tecnicos',
                'escolas'
            ]
            
            for table in tables:
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count_before = result.fetchone()[0]
                    
                    connection.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                    print(f"   ✅ {table}: {count_before:,} registros removidos")
                except Exception as e:
                    print(f"   ⚠️  {table}: {e}")
            
            connection.execute(text("SET session_replication_role = DEFAULT;"))
            
            print("\n📊 Verificação:")
            for table in tables:
                try:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"   - {table}: {count:,} registros")
                except Exception as e:
                    print(f"   - {table}: erro - {e}")
            
            connection.commit()
            print("\n✅ Banco de dados limpo com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")

if __name__ == "__main__":
    clear_database()