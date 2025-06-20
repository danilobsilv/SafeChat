from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from uuid import UUID

from . import crud, models, schemas
from .database import engine, get_db, Base

# Cria as tabelas no banco de dados se elas não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Safe Chat Backend")

# Configuração CORS: Permite todas as origens para desenvolvimento.
# Lembre-se de restringir isso em produção!
origins = ["*"] # Para desenvolvimento, permita tudo.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos HTTP
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# Gerenciador de Conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected: {websocket.client.host}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected: {websocket.client.host}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Endpoints REST API ---

@app.post("/register-or-login", response_model=schemas.UserResponse)
async def register_or_login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar ou logar um usuário.
    Se o usuário não existir, ele é criado. Caso contrário, retorna os dados do usuário existente.
    Retorna o UUID do usuário.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        # Usuário existe, verificar senha (simplificado para este exemplo)
        if db_user.password != user.password:
            raise HTTPException(status_code=400, detail="Senha incorreta")
        # Retorna o UUID do usuário existente
        return schemas.UserResponse(id=UUID(bytes=db_user.id), username=db_user.username)
    
    # Usuário não existe, criar novo
    new_user = crud.create_user(db=db, user=user)
    # Retorna o UUID do novo usuário
    return schemas.UserResponse(id=UUID(bytes=new_user.id), username=new_user.username)

@app.get("/messages", response_model=List[schemas.MessageResponse])
async def list_messages(db: Session = Depends(get_db)):
    """
    Endpoint para listar todas as mensagens do sistema.
    Retorna o conteúdo da mensagem, data, UUID da mensagem e nome do usuário.
    """
    messages = crud.get_all_messages(db)
    return messages

# --- Endpoint WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    Endpoint WebSocket para comunicação em tempo real.
    Todos os usuários se conectam a uma única sala.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Espera por uma mensagem do cliente WebSocket
            data = await websocket.receive_text()
            
            # As mensagens via WebSocket devem ser JSON, contendo 'content' e 'user_id'
            message_data: Dict = json.loads(data)
            content = message_data.get("content")
            user_id_str = message_data.get("user_id")

            if not content or not user_id_str:
                await manager.send_personal_message("Erro: 'content' e 'user_id' são obrigatórios.", websocket)
                continue
            
            try:
                user_id = UUID(user_id_str)
            except ValueError:
                await manager.send_personal_message("Erro: user_id inválido (não é um UUID válido).", websocket)
                continue

            # Verifica se o usuário existe no banco de dados
            db_user = db.query(models.User).filter(models.User.id == user_id.bytes).first()
            if not db_user:
                await manager.send_personal_message("Erro: Usuário não encontrado.", websocket)
                continue

            # Cria e salva a mensagem no banco de dados
            message_to_save = schemas.MessageCreate(content=content, user_id=user_id)
            db_message = crud.create_message(db, message_to_save)
            
            # Formata a mensagem para broadcast
            full_message = schemas.MessageResponse(
                id=UUID(bytes=db_message.id),
                content=db_message.content,
                created_at=db_message.created_at,
                username=db_user.username # Usa o nome de usuário do DB
            ).model_dump_json() # Converte o Pydantic model para JSON string

            # Transmite a mensagem para todos os clientes conectados
            await manager.broadcast(full_message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        await manager.send_personal_message(f"Um erro inesperado ocorreu: {e}", websocket)