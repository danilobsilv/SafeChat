from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List

# Esquema para criação de usuário (entrada na API)
class UserCreate(BaseModel):
    username: str
    password: str

# Esquema para dados de usuário (saída da API)
# A chave pública agora será em formato hexadecimal
class UserResponse(BaseModel):
    id: UUID
    username: str
    public_key: Optional[str] = None # Chave pública do usuário (formato HEXADECIMAL)

    class Config:
        from_attributes = True

# Esquema para uma mensagem cifrada enviada do frontend para o backend
# O encrypted_content será cifrado com a chave pública do REMETENTE
class MessageEncryptedIn(BaseModel):
    encrypted_content: str  # Conteúdo cifrado com a chave pública do REMETENTE
    message_hash: str       # Hash SHA256 do conteúdo original (plaintext)
    sender_id: UUID
    recipient_id: UUID

# Esquema para uma mensagem (descriptografada) retornada do backend para o frontend
class MessageDecryptedOut(BaseModel):
    id: UUID
    content: str            # Conteúdo da mensagem já descriptografado pelo backend
    created_at: datetime
    sender_id: UUID
    sender_username: str    # Nome do remetente
    recipient_id: UUID
    recipient_username: str # Nome do destinatário
    is_integrity_valid: bool # Indica se o hash conferiu (integridade)

    class Config:
        from_attributes = True

# Esquema para listar todos os usuários (para a lista de contatos no frontend)
class UserInList(BaseModel):
    id: UUID
    username: str
    public_key: str # Chave pública do usuário (formato HEXADECIMAL)

    class Config:
        from_attributes = True