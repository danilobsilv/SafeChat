from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Nome do arquivo do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

# Cria o motor do SQLAlchemy. check_same_thread é necessário para SQLite com múltiplos threads
# como pode acontecer em um servidor web.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma instância de SessionLocal. Cada instância de SessionLocal será uma sessão de banco de dados.
# A sessão em si é a "conversa" com o banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos do SQLAlchemy.
# Esta classe será herdada pelos modelos de dados.
Base = declarative_base()

# Função para obter uma sessão de banco de dados.
# Usaremos isso com o FastAPI para gerenciar as sessões por requisição.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()