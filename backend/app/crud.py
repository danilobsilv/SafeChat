from uuid import UUID
from sqlalchemy.orm import Session
from . import models, schemas

# --- Operações de Usuário ---

def get_user_by_username(db: Session, username: str):
    """Busca um usuário pelo nome de usuário."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Cria um novo usuário."""
    # Em um projeto real, você hash a senha aqui antes de salvar!
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Operações de Mensagem ---

def create_message(db: Session, message: schemas.MessageCreate):
    """Cria e salva uma nova mensagem no banco de dados."""
    db_message = models.Message(content=message.content, owner_id=message.user_id.bytes)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_all_messages(db: Session):
    """Lista todas as mensagens com as informações do usuário."""
    # Junta as tabelas Message e User para obter o username
    messages = db.query(models.Message, models.User.username)\
                 .join(models.User, models.Message.owner_id == models.User.id)\
                 .order_by(models.Message.created_at)\
                 .all()
    
    # Formata os resultados para o schema MessageResponse
    formatted_messages = []
    for msg, username in messages:
        formatted_messages.append(schemas.MessageResponse(
            id=UUID(bytes=msg.id),
            content=msg.content,
            created_at=msg.created_at,
            username=username
        ))
    return formatted_messages