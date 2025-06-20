import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    # UUID como chave primária para flexibilidade e compatibilidade com indexação
    id = Column(BLOB(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Em um projeto real, armazene hashes de senha!

    messages = relationship("Message", back_populates="owner")

class Message(Base):
    __tablename__ = "messages"

    id = Column(BLOB(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now()) # Data e hora da criação
    
    # Chave estrangeira para o usuário que enviou a mensagem
    owner_id = Column(BLOB(16), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="messages")