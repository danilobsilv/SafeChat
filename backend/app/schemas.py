from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

# Esquema para criação de usuário (entrada na API)
class UserCreate(BaseModel):
    username: str
    password: str

# Esquema para dados de usuário (saída da API)
class UserResponse(BaseModel):
    id: UUID
    username: str

    class Config:
        from_attributes = True # Permite que Pydantic crie um modelo a partir de um objeto SQLAlchemy

# Esquema para criar uma mensagem (entrada na API/WebSocket)
class MessageCreate(BaseModel):
    content: str
    user_id: UUID # O UUID do usuário que está enviando a mensagem

# Esquema para uma mensagem completa (saída da API/WebSocket)
class MessageResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    username: str # Adicionamos o nome do usuário para exibição no frontend

    class Config:
        from_attributes = True