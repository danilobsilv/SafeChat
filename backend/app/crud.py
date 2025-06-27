from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_ # Para consultas com OR
from . import models, schemas
from typing import List, Tuple

# --- Operações de Usuário ---

def get_user_by_username(db: Session, username: str):
    """Busca um usuário pelo nome de usuário."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: UUID):
    """Busca um usuário pelo ID."""
    return db.query(models.User).filter(models.User.id == user_id.bytes).first()

def get_all_users_for_list(db: Session) -> List[schemas.UserInList]:
    """Retorna todos os usuários com seus IDs, usernames e chaves públicas."""
    users = db.query(models.User).all()
    return [schemas.UserInList(id=UUID(bytes=u.id), username=u.username, public_key=u.public_key) for u in users if u.public_key]

def create_user(db: Session, user_data: schemas.UserCreate, public_key_pem: str, private_key_pem_encrypted: str):
    """Cria um novo usuário, salvando suas chaves."""
    db_user = models.User(
        username=user_data.username,
        password=user_data.password, # Lembre-se de HASHEAR em prod!
        public_key=public_key_pem,
        private_key_encrypted=private_key_pem_encrypted # EM PROD: CRIPTOGRAFE ISSO DE VERDADE!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Operações de Mensagem ---

def create_message(db: Session, message: schemas.MessageEncryptedIn):
    """Cria e salva uma nova mensagem cifrada no banco de dados."""
    db_message = models.Message(
        encrypted_content=message.encrypted_content,
        message_hash=message.message_hash,
        sender_id=message.sender_id.bytes,
        recipient_id=message.recipient_id.bytes
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages_between_users(db: Session, user1_id: UUID, user2_id: UUID) -> List[models.Message]:
    """
    Busca mensagens trocadas entre dois usuários específicos.
    Assume que as mensagens são armazenadas independentemente da direção.
    """
    # Consulta mensagens onde user1 é remetente E user2 é destinatário
    # OU user2 é remetente E user1 é destinatário
    messages = db.query(models.Message)\
                 .filter(
                     or_(
                         (models.Message.sender_id == user1_id.bytes) & (models.Message.recipient_id == user2_id.bytes),
                         (models.Message.sender_id == user2_id.bytes) & (models.Message.recipient_id == user1_id.bytes)
                     )
                 )\
                 .order_by(models.Message.created_at)\
                 .all()
    return messages