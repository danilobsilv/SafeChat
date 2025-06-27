from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Union, Tuple
import json
from uuid import UUID # Importação do tipo UUID
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

import hashlib 
import base64 

from . import crud, models, schemas
from .database import engine, get_db, Base

# Cria as tabelas no banco de dados se elas não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Safe Chat Backend (Chat Individual com Descriptografia no Servidor)")

# Configuração CORS: Permite todas as origens para desenvolvimento.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciador de Conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"WebSocket conectado para o usuário {user_id}")

    def disconnect(self, user_id: UUID):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"WebSocket desconectado para o usuário {user_id}")

    async def send_personal_message(self, message: Union[str, dict], recipient_id: UUID):
        if recipient_id in self.active_connections:
            websocket = self.active_connections[recipient_id]
            if isinstance(message, dict):
                # NOVO: Chamar json.dumps() aqui para garantir serialização
                await websocket.send_text(json.dumps(message)) 
            else:
                await websocket.send_text(message)
        else:
            print(f"Destinatário {recipient_id} não está online. Mensagem não enviada via WS.")

    async def broadcast(self, message: dict):
        # NOVO: Chamar json.dumps() aqui para garantir serialização
        message_json_string = json.dumps(message) 
        for user_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_text(message_json_string)
            except RuntimeError as e:
                print(f"Erro ao transmitir para {user_id}: {e}")
                self.disconnect(user_id)


manager = ConnectionManager()

# --- Funções de Criptografia e Geração de Chaves (Backend-side) ---

def store_private_key_as_is(private_key_hex: str) -> str:
    """
    Simplesmente retorna a chave privada em HEX para armazenamento.
    NÃO HÁ CRIPTOGRAFIA DE PROTEÇÃO AQUI.
    """
    return private_key_hex

def retrieve_private_key_as_obj(private_key_hex: str) -> rsa.RSAPrivateKey:
    """
    Carrega a chave privada em HEX (que representa um DER) e retorna o objeto RSA PrivateKey.
    """
    # Converte de HEX para bytes (DER)
    private_der_bytes = bytes.fromhex(private_key_hex)

    return serialization.load_der_private_key( 
        private_der_bytes, 
        password=None, 
        backend=default_backend()
    )


def generate_rsa_key_pair() -> Tuple[str, str]:
    """Gera um par de chaves RSA e retorna em formato HEXADECIMAL (SPKI para pública, PKCS8 para privada)."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serializa para formato DER (binário) e depois para HEX
    private_der_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER, # DER é o formato binário
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_hex = private_der_bytes.hex()

    public_der_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER, # DER é o formato binário
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_hex = public_der_bytes.hex()

    return public_hex, private_hex


def rsa_decrypt_backend(encrypted_data_b64: str, private_key_obj: rsa.RSAPrivateKey) -> str:
    """
    Descriptografa dados com o OBJETO da chave privada RSA (no backend).
    O padding é OAEP para corresponder ao que o frontend (Web Crypto API) usa para criptografia.
    """
    decrypted_bytes = private_key_obj.decrypt( # Usa o objeto de chave, não o formato PEM ou HEX
        base64.b64decode(encrypted_data_b64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_bytes.decode('utf-8')


def sha256_hash_backend(data: str) -> str:
    """Gera o hash SHA256 de uma string (no backend)."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# --- Endpoints REST API ---

@app.post("/register-or-login", response_model=schemas.UserResponse)
async def register_or_login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar ou logar um usuário.
    Se o usuário não existir, ele é criado com um novo par de chaves RSA.
    Retorna o UUID, username e chave pública do usuário (em HEX).
    """
    db_user = crud.get_user_by_username(db, username=user_data.username)
    if db_user:
        if db_user.password != user_data.password: 
            raise HTTPException(status_code=400, detail="Senha incorreta")
        return schemas.UserResponse(
            id=UUID(bytes=db_user.id),
            username=db_user.username,
            public_key=db_user.public_key # Retorna a chave pública existente (HEX)
        )
    
    # Usuário não existe, criar novo e gerar chaves RSA
    public_hex, private_hex = generate_rsa_key_pair()
    
    # Salva a chave privada diretamente (em HEX) no DB sem criptografia adicional
    private_key_to_save = store_private_key_as_is(private_hex)

    new_user = crud.create_user(
        db=db,
        user_data=user_data,
        public_key_pem=public_hex, # Salvando o HEX na coluna public_key
        private_key_pem_encrypted=private_key_to_save # Agora armazena o HEX não criptografado
    )
    
    # Notifica todos os clientes WebSocket sobre o novo usuário
    # NOVO: Converte os campos UUID para string explicitamente aqui
    new_user_data_serializable = {
        "id": str(new_user.id), # Converte UUID para string
        "username": new_user.username,
        "public_key": new_user.public_key
    }
    
    # Inclui um tipo de mensagem para o frontend saber o que fazer
    broadcast_message = {
        "type": "NEW_USER_REGISTERED",
        "user": new_user_data_serializable # Passa o dicionário com UUIDs convertidos
    }
    # manager.broadcast espera um dicionário, que json.dumps() irá serializar
    await manager.broadcast(broadcast_message) 
    
    return schemas.UserResponse(
        id=UUID(bytes=new_user.id),
        username=new_user.username,
        public_key=new_user.public_key # Retorna a chave pública do novo usuário (HEX)
    )

@app.get("/users", response_model=List[schemas.UserInList])
async def list_users(db: Session = Depends(get_db)):
    """
    Endpoint para listar todos os usuários com seus IDs, usernames e chaves públicas (em HEX).
    """
    return crud.get_all_users_for_list(db)


@app.get("/messages/{user1_id}/{user2_id}", response_model=List[schemas.MessageDecryptedOut])
async def get_conversation(user1_id: UUID, user2_id: UUID, db: Session = Depends(get_db)):
    """
    Endpoint para listar todas as mensagens trocadas entre dois usuários.
    As mensagens são DESCRIPTOGRAFADAS pelo servidor usando a CHAVE PRIVADA DO REMETENTE original.
    A integridade é VERIFICADA.
    """
    messages = crud.get_messages_between_users(db, user1_id, user2_id)
    
    decrypted_messages_out = []
    for msg in messages:
        # Pega a chave privada do REMETENTE original para descriptografar a mensagem
        sender_user = crud.get_user_by_id(db, UUID(bytes=msg.sender_id))
        
        if not sender_user or not sender_user.private_key_encrypted:
            print(f"ATENÇÃO: Remetente {msg.sender_id} ou sua chave privada não encontrada no servidor.")
            decrypted_messages_out.append(schemas.MessageDecryptedOut(
                id=UUID(bytes=msg.id),
                content="[Mensagem cifrada - Não foi possível descriptografar no servidor]",
                created_at=msg.created_at,
                sender_id=UUID(bytes=msg.sender_id),
                sender_username=(crud.get_user_by_id(db, UUID(bytes=msg.sender_id)) or {}).username or "Desconhecido",
                recipient_id=UUID(bytes=msg.recipient_id),
                recipient_username=(crud.get_user_by_id(db, UUID(bytes=msg.recipient_id)) or {}).username or "Desconhecido",
                is_integrity_valid=False
            ))
            continue

        try:
            # Carrega a chave privada como objeto, diretamente do HEX salvo no DB
            sender_private_key_obj = retrieve_private_key_as_obj(sender_user.private_key_encrypted)

            # Descriptografa o conteúdo da mensagem com a CHAVE PRIVADA DO REMETENTE
            decrypted_content = rsa_decrypt_backend(msg.encrypted_content, sender_private_key_obj)

            # Verifica a integridade (hash)
            calculated_hash = sha256_hash_backend(decrypted_content)
            is_integrity_valid = (calculated_hash == msg.message_hash)
            
            sender_username_val = sender_user.username
            recipient_user_obj = crud.get_user_by_id(db, UUID(bytes=msg.recipient_id))
            recipient_username_val = (recipient_user_obj or {}).username or "Desconhecido"

            decrypted_messages_out.append(schemas.MessageDecryptedOut(
                id=UUID(bytes=msg.id),
                content=decrypted_content,
                created_at=msg.created_at,
                sender_id=UUID(bytes=msg.sender_id),
                sender_username=sender_username_val,
                recipient_id=UUID(bytes=msg.recipient_id),
                recipient_username=recipient_username_val,
                is_integrity_valid=is_integrity_valid
            ))

        except Exception as e:
            print(f"Erro ao descriptografar/verificar mensagem {msg.id}: {e}")
            decrypted_messages_out.append(schemas.MessageDecryptedOut(
                id=UUID(bytes=msg.id),
                content=f"[Erro de Descriptografia/Verificação no servidor: {e}]",
                created_at=msg.created_at,
                sender_id=UUID(bytes=msg.sender_id),
                sender_username=(crud.get_user_by_id(db, UUID(bytes=msg.sender_id)) or {}).username or "Desconhecido",
                recipient_id=UUID(bytes=msg.recipient_id),
                recipient_username=(crud.get_user_by_id(db, UUID(bytes=msg.recipient_id)) or {}).username or "Desconhecido",
                is_integrity_valid=False
            ))

    return decrypted_messages_out


# --- Endpoint WebSocket ---

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID, db: Session = Depends(get_db)):
    """
    Endpoint WebSocket para comunicação em tempo real de mensagens privadas.
    O servidor DESCRIPTOGRAFA a mensagem usando a CHAVE PRIVADA DO REMETENTE
    e verifica a integridade antes de retransmitir a mensagem em CLARO para o destinatário e remetente.
    """
    
    # Verifica se o usuário que está se conectando existe
    connecting_user = crud.get_user_by_id(db, user_id)
    if not connecting_user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            message_data: Dict = json.loads(data)
            
            # Verifica o tipo de mensagem recebida pelo WebSocket
            message_type = message_data.get("type")
            
            if message_type == "CHAT_MESSAGE":
                try:
                    # Valida a mensagem cifrada recebida do cliente
                    parsed_message = schemas.MessageEncryptedIn(**message_data.get("payload", {}))
                except Exception as e:
                    await manager.send_personal_message(f"Erro de validação da mensagem de chat: {e}", user_id)
                    continue
                
                # Pega o usuário REMETENTE para acessar sua chave privada e descriptografar
                sender_user = crud.get_user_by_id(db, parsed_message.sender_id)
                if not sender_user or not sender_user.private_key_encrypted:
                    await manager.send_personal_message("Erro: Remetente ou sua chave privada não encontrada no servidor para descriptografia.", user_id)
                    continue

                
                # Carrega a chave privada como objeto, diretamente do HEX salvo no DB
                sender_private_key_obj = retrieve_private_key_as_obj(sender_user.private_key_encrypted)
                
                # Descriptografa o conteúdo da mensagem com a CHAVE PRIVADA DO REMETENTE
                decrypted_content = rsa_decrypt_backend(parsed_message.encrypted_content, sender_private_key_obj)

                # Verifica a integridade (hash)
                calculated_hash = sha256_hash_backend(decrypted_content)
                is_integrity_valid = (calculated_hash == parsed_message.message_hash)

                # Salva a mensagem cifrada original no banco de dados (o backend não guarda plaintext)
                db_message = crud.create_message(db, parsed_message)
                
                # Prepara a mensagem DESCRIPTOGRAFADA para envio ao destinatário E remetente
                sender_username_val = sender_user.username
                recipient_user_obj = crud.get_user_by_id(db, parsed_message.recipient_id)
                recipient_username_val = (recipient_user_obj or {}).username or "Desconhecido"

                # NOVO: Converte os campos UUID para string explicitamente aqui antes de model_dump()
                message_to_send_decrypted_dict = {
                    "id": str(UUID(bytes=db_message.id)), # Converte UUID para string
                    "content": decrypted_content,
                    "created_at": db_message.created_at.isoformat(), # Converte datetime para ISO format string
                    "sender_id": str(UUID(bytes=db_message.sender_id)), # Converte UUID para string
                    "sender_username": sender_username_val,
                    "recipient_id": str(UUID(bytes=db_message.recipient_id)), # Converte UUID para string
                    "recipient_username": recipient_username_val,
                    "is_integrity_valid": is_integrity_valid
                }
                
                # Encapsula a mensagem de chat para broadcast
                chat_broadcast_message = {
                    "type": "CHAT_MESSAGE",
                    "payload": message_to_send_decrypted_dict # Passa o dicionário já serializável
                }

                # Envia a mensagem DESCRIPTOGRAFADA para o remetente (para ele ver sua própria mensagem enviada)
                await manager.send_personal_message(chat_broadcast_message, user_id)
                
                # Envia a mensagem DESCRIPTOGRAFADA para o destinatário
                if parsed_message.sender_id != parsed_message.recipient_id: 
                    await manager.send_personal_message(chat_broadcast_message, parsed_message.recipient_id)
            
            else:
                print(f"Tipo de mensagem WebSocket desconhecido: {message_type}")
                await manager.send_personal_message({"error": f"Tipo de mensagem desconhecido: {message_type}"}, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)
        await manager.send_personal_message({"error": f"Um erro inesperado ocorreu: {e}"}, user_id)