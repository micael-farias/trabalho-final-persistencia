from app.core.database import engine, Base
from app.models.escola import Escola
from app.models.infraestrutura import Infraestrutura  
from app.models.oferta_modalidade import OfertaModalidade
from app.models.curso_tecnico import CursoTecnico
from app.models.escola_curso import EscolaCurso
from sqlalchemy import text

def create_tables():
    print("🔨 Recriando banco de dados do zero...")
    print("=" * 60)
    
    try:
        # Testar conexão primeiro
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"🔗 Conectado ao banco: {db_name}")
        
        print("\n🗑️  ETAPA 1: Limpando banco de dados...")
        with engine.connect() as connection:
            # Desabilitar foreign key checks temporariamente
            connection.execute(text("SET session_replication_role = replica;"))
            
            # Verificar tabelas existentes
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """))
            existing_tables = [row[0] for row in result]
            
            if existing_tables:
                print(f"   📋 Tabelas existentes: {existing_tables}")
                
                # Dropar todas as tabelas
                for table in existing_tables:
                    try:
                        connection.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        print(f"   ✅ Tabela {table} removida")
                    except Exception as e:
                        print(f"   ⚠️  Erro ao remover {table}: {e}")
            else:
                print("   ✅ Nenhuma tabela existente encontrada")
            
            # Reabilitar foreign key checks
            connection.execute(text("SET session_replication_role = DEFAULT;"))
            connection.commit()
        
        print("\n🔨 ETAPA 2: Criando tabelas do zero...")
        
        # Importar todos os models para garantir que sejam registrados
        print("📋 Models importados:")
        print(f"   - Escola: {Escola.__tablename__}")
        print(f"   - Infraestrutura: {Infraestrutura.__tablename__}")
        print(f"   - OfertaModalidade: {OfertaModalidade.__tablename__}")
        print(f"   - CursoTecnico: {CursoTecnico.__tablename__}")
        print(f"   - EscolaCurso: {EscolaCurso.__tablename__}")
        
        # Mostrar tabelas registradas no metadata
        print(f"🗂️ Tabelas no metadata: {list(Base.metadata.tables.keys())}")
        
        # Tentar criar com SQLAlchemy primeiro
        try:
            print("🔨 Tentando criar com SQLAlchemy...")
            Base.metadata.create_all(bind=engine)
            print("   ✅ SQLAlchemy executado")
        except Exception as e:
            print(f"   ⚠️  SQLAlchemy falhou: {e}")
        
        # Criar tabelas manualmente com constraints
        print("🔨 Criando tabelas manualmente...")
        with engine.connect() as connection:
            create_sql = """
            -- Tabela principal: Escolas
            CREATE TABLE IF NOT EXISTS escolas (
                co_entidade INTEGER PRIMARY KEY,
                no_entidade VARCHAR(255) NOT NULL,
                sg_uf VARCHAR(2) NOT NULL,
                no_municipio VARCHAR(100) NOT NULL,
                tp_dependencia INTEGER NOT NULL,
                tp_localizacao INTEGER NOT NULL,
                tp_situacao_funcionamento INTEGER NOT NULL,
                qt_mat_bas INTEGER DEFAULT 0,
                qt_doc_bas INTEGER DEFAULT 0,
                nu_ano_censo INTEGER NOT NULL
            );

            -- Índices para performance
            CREATE INDEX IF NOT EXISTS ix_escolas_co_entidade ON escolas (co_entidade);
            CREATE INDEX IF NOT EXISTS ix_escolas_sg_uf ON escolas (sg_uf);
            CREATE INDEX IF NOT EXISTS ix_escolas_no_municipio ON escolas (no_municipio);

            -- Tabela de infraestrutura (1:1 com escola)
            CREATE TABLE IF NOT EXISTS infraestruturas (
                id SERIAL PRIMARY KEY,
                co_entidade INTEGER UNIQUE NOT NULL REFERENCES escolas(co_entidade) ON DELETE CASCADE,
                in_internet BOOLEAN DEFAULT FALSE,
                in_biblioteca BOOLEAN DEFAULT FALSE,
                in_laboratorio_informatica BOOLEAN DEFAULT FALSE,
                in_laboratorio_ciencias BOOLEAN DEFAULT FALSE,
                in_quadra_esportes BOOLEAN DEFAULT FALSE,
                in_acessibilidade_rampas BOOLEAN DEFAULT FALSE,
                qt_desktop_aluno INTEGER DEFAULT 0,
                qt_salas_utilizadas INTEGER DEFAULT 0
            );

            -- Tabela de ofertas de modalidade (1:N com escola)
            CREATE TABLE IF NOT EXISTS ofertas_modalidade (
                id SERIAL PRIMARY KEY,
                co_entidade INTEGER NOT NULL REFERENCES escolas(co_entidade) ON DELETE CASCADE,
                tipo_modalidade VARCHAR(50) NOT NULL,
                qt_matriculas INTEGER DEFAULT 0,
                qt_docentes INTEGER DEFAULT 0,
                qt_turmas INTEGER DEFAULT 0,
                in_diurno BOOLEAN DEFAULT FALSE,
                in_noturno BOOLEAN DEFAULT FALSE,
                nu_ano_censo INTEGER NOT NULL
            );

            -- Índice para performance nas consultas por modalidade
            CREATE INDEX IF NOT EXISTS ix_ofertas_modalidade_tipo ON ofertas_modalidade (tipo_modalidade);
            CREATE INDEX IF NOT EXISTS ix_ofertas_modalidade_escola ON ofertas_modalidade (co_entidade);

            -- Tabela de cursos técnicos
            CREATE TABLE IF NOT EXISTS cursos_tecnicos (
                co_curso_educ_profissional INTEGER PRIMARY KEY,
                no_curso_educ_profissional VARCHAR(255) NOT NULL,
                no_area_curso_profissional VARCHAR(255) NOT NULL,
                id_area_curso_profissional INTEGER NOT NULL,
                qt_mat_curso_tec INTEGER DEFAULT 0,
                qt_curso_tec_conc INTEGER DEFAULT 0,
                qt_curso_tec_subs INTEGER DEFAULT 0,
                qt_curso_tec_eja INTEGER DEFAULT 0,
                nu_ano_censo INTEGER NOT NULL
            );

            -- Índice para área profissional
            CREATE INDEX IF NOT EXISTS ix_cursos_area ON cursos_tecnicos (id_area_curso_profissional);

            -- Tabela associativa escola-curso (N:N)
            CREATE TABLE IF NOT EXISTS escola_cursos (
                id SERIAL PRIMARY KEY,
                co_entidade INTEGER NOT NULL REFERENCES escolas(co_entidade) ON DELETE CASCADE,
                co_curso_educ_profissional INTEGER NOT NULL REFERENCES cursos_tecnicos(co_curso_educ_profissional) ON DELETE CASCADE,
                qt_mat_curso_tec INTEGER DEFAULT 0,
                qt_mat_curso_tec_ct INTEGER DEFAULT 0,
                qt_mat_curso_tec_nm INTEGER DEFAULT 0,
                qt_mat_curso_tec_conc INTEGER DEFAULT 0,
                qt_mat_tec_subs INTEGER DEFAULT 0,
                qt_mat_tec_eja INTEGER DEFAULT 0,
                nu_ano_censo INTEGER NOT NULL,
                
                -- CONSTRAINT ÚNICA para evitar duplicatas
                CONSTRAINT uk_escola_curso UNIQUE (co_entidade, co_curso_educ_profissional)
            );

            -- Índices para performance
            CREATE INDEX IF NOT EXISTS ix_escola_cursos_escola ON escola_cursos (co_entidade);
            CREATE INDEX IF NOT EXISTS ix_escola_cursos_curso ON escola_cursos (co_curso_educ_profissional);
            """
            
            connection.execute(text(create_sql))
            connection.commit()
            print("   ✅ Tabelas criadas com SQL manual")
        
        print("\n📊 ETAPA 3: Verificando resultado...")
        # Verificar se foram criadas
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            print(f"✅ Tabelas criadas: {tables}")
            
            # Verificar constraints
            print("\n🔗 Verificando constraints:")
            result = connection.execute(text("""
                SELECT 
                    tc.table_name, 
                    tc.constraint_name,
                    tc.constraint_type
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'public' 
                AND tc.constraint_type IN ('UNIQUE', 'FOREIGN KEY', 'PRIMARY KEY')
                ORDER BY tc.table_name, tc.constraint_type
            """))
            
            constraints = result.fetchall()
            for table_name, constraint_name, constraint_type in constraints:
                print(f"   - {table_name}: {constraint_type} ({constraint_name})")
            
            # Verificar índices
            print("\n📊 Verificando índices:")
            result = connection.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            
            indexes = result.fetchall()
            for schema, table, index in indexes:
                print(f"   - {table}: {index}")
        
        print("\n" + "=" * 60)
        print("✅ BANCO DE DADOS CRIADO COM SUCESSO!")
        print("=" * 60)
        print("📋 Estrutura criada:")
        print("   🏫 5 tabelas principais")
        print("   🔗 Relacionamentos 1:1, 1:N e N:N")
        print("   🛡️  Constraints de integridade")
        print("   🚀 Índices para performance")
        print("   ✨ Pronto para importação!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_tables()