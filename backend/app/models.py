import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BLOB(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False) # Lembre-se: HASHEAR SENHAS em produção!
    
    # Chave pública do usuário (em formato PEM) - Usada para criptografar para este usuário no frontend
    public_key = Column(Text, nullable=True) 
    # Chave privada do usuário (em formato PEM, criptografada com senha ou chave mestra do servidor)
    # ATENÇÃO: NUNCA SALVE A CHAVE PRIVADA SEM CRIPTOGRAFIA FORTE EM PROD!
    # Esta chave privada será usada pelo SERVIDOR para descriptografar mensagens.
    private_key_encrypted = Column(Text, nullable=True) 

    # Relação para mensagens enviadas por este usuário
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    # Relação para mensagens recebidas por este usuário
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BLOB(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    # Conteúdo da mensagem Cifrado (originalmente pelo remetente com a sua PRÓPRIA chave pública)
    encrypted_content = Column(Text, nullable=False)
    
    # Hash da mensagem original (plaintext) para verificação de integridade
    # Gerado pelo remetente, verificado pelo servidor.
    message_hash = Column(String, nullable=False) 
    
    created_at = Column(DateTime, default=func.now())
    
    # ID do remetente (para identificar quem enviou)
    sender_id = Column(BLOB(16), ForeignKey("users.id"), nullable=False)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")

    # ID do destinatário (para identificar quem deve receber a mensagem)
    recipient_id = Column(BLOB(16), ForeignKey("users.id"), nullable=False)
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")