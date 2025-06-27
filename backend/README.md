# Backend do Safe Chat (Python, FastAPI, SQLite, TLS)

Este repositório contém o backend do Safe Chat, desenvolvido em Python usando **FastAPI** para as APIs REST e WebSockets, e **SQLAlchemy** para persistência de dados em um banco SQLite. A aplicação foi projetada para suportar um **chat individual e seguro**, com um fluxo de criptografia específico onde o servidor atua como um intermediário confiável. O backend está configurado para usar **TLS (Transport Layer Security)** para comunicação segura via HTTPS e WSS.

---

## 🚀 Visão Geral do Projeto

O backend do Safe Chat gerencia a autenticação de usuários, o armazenamento de chaves criptográficas, a persistência de mensagens e a retransmissão em tempo real.

* **Autenticação e Geração de Chaves**: No registro/login, o backend gera um par de chaves RSA (pública e privada) para cada usuário. A chave pública é fornecida ao frontend, e a chave privada é armazenada no banco de dados (em formato hexadecimal, **não criptografada por uma chave mestra do servidor neste exemplo**).
* **Armazenamento de Chaves em Hexadecimal**: Chaves públicas e privadas são serializadas para o formato DER (binário) e armazenadas como strings hexadecimais no banco de dados.
* **Chat Individual Protegido (Server-Side Decryption)**:
    * Recebe mensagens cifradas do frontend via WebSocket.
    * **Descriptografa a mensagem** usando a **chave privada do *remetente original*** (armazenada no servidor).
    * Verifica a integridade da mensagem usando um hash SHA256 (fornecido pelo remetente).
    * Salva a mensagem cifrada original no banco de dados.
    * Retransmite a mensagem **em texto claro** para o destinatário e para o próprio remetente (para que ambos vejam a conversa).
    * **Importante**: Neste fluxo, o servidor tem acesso ao conteúdo das mensagens em texto claro. **Isso NÃO é criptografia de ponta a ponta (E2EE)**, mas segue o modelo definido para permitir verificação e persistência centralizada.
* **Histórico de Mensagens**: Fornece um endpoint para carregar mensagens trocadas entre dois usuários específicos, já descriptografadas pelo servidor.
* **Atualização de Usuários em Tempo Real**: Notifica todos os clientes WebSocket conectados quando um novo usuário se registra, permitindo que as listas de contatos sejam atualizadas dinamicamente.
* **Comunicação Segura (TLS)**: Todas as comunicações REST e WebSocket são protegidas por TLS.

---

## 🛠️ Tecnologias Principais

* **Python 3.8+**: Linguagem de programação principal.
* **FastAPI**: Framework web moderno e de alta performance para construir APIs REST e WebSockets.
* **Uvicorn**: Servidor ASGI para executar a aplicação FastAPI de forma assíncrona e eficiente.
* **SQLAlchemy**: ORM (Object Relational Mapper) para interação com o banco de dados SQLite.
* **Pydantic**: Biblioteca de validação de dados, utilizada para modelar a entrada e saída das APIs.
* **`cryptography`**: Biblioteca poderosa para operações criptográficas (RSA, AES, hashing, serialização de chaves).
* **SQLite**: Banco de dados relacional leve e embutido, ideal para desenvolvimento local.
* **OpenSSL**: Ferramenta de linha de comando para gerar e gerenciar certificados SSL/TLS.

---

## 📂 Estrutura do Projeto

A estrutura do projeto é modular para facilitar a organização e manutenção do código:

```

python-backend/
├── app/
│   ├── **init**.py
│   ├── main.py           \# Ponto de entrada da aplicação FastAPI, definições de rotas e lógica criptográfica central.
│   ├── database.py       \# Configuração da conexão com o banco de dados SQLite.
│   ├── models.py         \# Definição dos modelos de dados (SQLAlchemy ORM) para Usuários e Mensagens, incluindo chaves.
│   ├── schemas.py        \# Modelos de dados para validação (Pydantic) de entrada/saída da API.
│   └── crud.py           \# Funções de operações CRUD (Create, Read, Update, Delete) com o banco de dados.
├── certs/                \# Diretório para armazenar os certificados TLS (chave e certificado do servidor).
│   ├── server.key
│   └── server.crt
├── requirements.txt      \# Lista de dependências Python.
└── README.md             \# Este arquivo.

````

---

## 🔒 Comunicação Segura e Criptografia

O backend é o ponto central para a segurança da comunicação das mensagens:

* **TLS (Transport Layer Security)**: Todas as conexões HTTPs e WebSockets (WSS) são criptografadas. Em ambiente de desenvolvimento, são utilizados **certificados autoassinados** gerados com OpenSSL. Isso exige que o navegador confie explicitamente nesses certificados na primeira vez (visitando `https://localhost:8000/` e aceitando o aviso de segurança).
* **Geração de Chaves RSA (2048-bit)**: Para cada novo usuário, um par de chaves RSA é gerado.
    * A chave pública (formato SPKI DER) é convertida para hexadecimal (`public_key`) e armazenada no banco de dados. É retornada ao frontend no login.
    * A chave privada (formato PKCS#8 DER) é convertida para hexadecimal (`private_key_encrypted`) e **armazenada diretamente no banco de dados**.
        * **AVISO DE SEGURANÇA (APENAS PARA DESENVOLVIMENTO):** A chave privada é armazenada em texto claro (hexadecimal) no banco de dados. Em um ambiente de produção, a chave privada **NUNCA** deve ser armazenada sem criptografia forte (ex: usando um KMS, HSM ou criptografia com chave mestra do servidor). Este design simplificado é apenas para fins didáticos e de desenvolvimento.
* **Descriptografia e Verificação de Integridade (no Servidor)**:
    * Ao receber uma mensagem cifrada via WebSocket (cifrada com a chave pública do remetente), o backend recupera a chave privada do *remetente* do banco de dados.
    * A mensagem é descriptografada usando essa chave privada (RSA-OAEP).
    * O hash SHA256 da mensagem original é verificado para garantir que a mensagem não foi adulterada.
    * A mensagem (agora em texto claro) é preparada e retransmitida para o destinatário e o remetente.

---

## Como Instalar e Executar

Siga os passos abaixo para configurar e executar o backend:

### 1. Pré-requisitos

Certifique-se de ter instalado:

* **Python 3.8+**
* **pip** (gerenciador de pacotes Python)
* **OpenSSL** (instalado e no PATH do seu sistema, especialmente no Windows)

### 2. Clonar o Repositório (se aplicável)

Se este backend estiver em um repositório separado:

```bash
git clone <url_do_seu_repositorio_backend>
cd python-backend
````

### 3\. Instalar Dependências Python

Na raiz do diretório `python-backend/`, instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4\. Gerar Certificados TLS com OpenSSL

Navegue até o diretório `python-backend/` no seu terminal e crie uma pasta `certs` se ela não existir.

```powershell
mkdir certs
```

Em seguida, gere a chave privada e o certificado autoassinado para o seu servidor. **É crucial que o `Common Name (CN)` seja `localhost` e que as `Subject Alternative Names (SANs)` incluam `localhost` e `127.0.0.1`**.

```powershell
# Gerar a chave privada
openssl genrsa -out certs/server.key 2048

# Gerar o certificado autoassinado (para localhost)
openssl req -new -x509 -key certs/server.key -out certs/server.crt -days 365 -subj "/CN=localhost" -sha256 -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"
```

Você terá os arquivos `certs/server.key` e `certs/server.crt` dentro da pasta `certs`.

### 5\. Executar a Aplicação com TLS (HTTPS/WSS)

Com os certificados gerados, inicie o servidor Uvicorn a partir da raiz do diretório `python-backend/`:

```powershell
uvicorn app.main:app --reload --ssl-keyfile=certs/server.key --ssl-certfile=certs/server.crt --host 0.0.0.0 --port 8000
```

  * `--reload`: Recarrega o servidor automaticamente ao detectar mudanças no código (ótimo para desenvolvimento).
  * `--ssl-keyfile` e `--ssl-certfile`: Apontam para os arquivos de chave privada e certificado que você acabou de gerar.
  * `--host 0.0.0.0`: Permite que o servidor seja acessível de todas as interfaces de rede (incluindo `localhost`).
  * `--port 8000`: Define a porta em que o servidor escutará.

Seu backend agora estará acessível via `https://localhost:8000` para APIs REST e `wss://localhost:8000/ws` para WebSockets.

-----

## Endpoints da API REST

Acesse `https://localhost:8000/docs` no seu navegador para ver a documentação interativa da API (Swagger UI).

### Autenticação/Registro de Usuário

  * **`POST /register-or-login`**
      * **Descrição**: Permite que um usuário se registre ou faça login. Se o `username` já existir, verifica a senha. Caso contrário, cria um novo usuário e um par de chaves RSA para ele. Retorna o UUID do usuário, username e sua **chave pública (em hexadecimal)**.
      * **Corpo da Requisição (JSON)**:
        ```json
        {
          "username": "seu_nome_de_usuario",
          "password": "sua_senha_secreta"
        }
        ```
      * **Resposta (JSON)**:
        ```json
        {
          "id": "uuid-do-usuario-gerado",
          "username": "seu_nome_de_usuario",
          "public_key": "hexadecimal_da_chave_publica_do_usuario"
        }
        ```

### Listar Usuários

  * **`GET /users`**
      * **Descrição**: Retorna uma lista de todos os usuários registrados no sistema, incluindo seus IDs, nomes de usuário e chaves públicas (em hexadecimal). Essencial para o frontend construir a lista de contatos.
      * **Resposta (JSON - Exemplo)**:
        ```json
        [
          {
            "id": "uuid-do-usuario-1",
            "username": "Json",
            "public_key": "hex_da_chave_publica_Json"
          },
          {
            "id": "uuid-do-usuario-2",
            "username": "Bob",
            "public_key": "hex_da_chave_publica_bob"
          }
        ]
        ```

### Listar Mensagens de Conversa

  * **`GET /messages/{user1_id}/{user2_id}`**
      * **Descrição**: Retorna todas as mensagens trocadas entre `user1_id` e `user2_id`. O backend descriptografa cada mensagem com a chave privada do remetente original e verifica sua integridade antes de retorná-la.
      * **Resposta (JSON - Exemplo)**:
        ```json
        [
          {
            "id": "uuid-da-mensagem-1",
            "content": "Olá, Bob!",                 # Conteúdo já descriptografado
            "created_at": "2024-07-20T10:30:00.123456",
            "sender_id": "uuid-Json",
            "sender_username": "Json",
            "recipient_id": "uuid-bob",
            "recipient_username": "Bob",
            "is_integrity_valid": true              # Resultado da verificação de hash
          }
        ]
        ```

-----

## Funcionalidade WebSocket

  * **Endpoint**: `wss://localhost:8000/ws/{user_id}`
      * O `user_id` na URL identifica a conexão WebSocket para roteamento de mensagens privadas.
  * **Tipos de Mensagem WebSocket**: O backend processa diferentes tipos de mensagens WebSocket baseadas no campo `type` do JSON recebido.
      * **`CHAT_MESSAGE`**:
          * **Envio do Frontend**: Espera um `payload` com `encrypted_content` (cifrado com a **chave pública do REMETENTE**), `message_hash`, `sender_id` e `recipient_id`.
          * **Processamento do Backend**: Descriptografa `encrypted_content` usando a chave privada do remetente, verifica o `message_hash`, salva a mensagem original cifrada no DB.
          * **Retransmissão**: Envia a mensagem **descriptografada e verificada** (`type: CHAT_MESSAGE`, `payload: MessageDecryptedOut`) para o remetente e o destinatário via suas conexões WebSocket ativas.
      * **`NEW_USER_REGISTERED`**:
          * **Origem**: Gerada pelo backend quando um novo usuário se registra.
          * **Broadcast**: Transmitida para *todos* os clientes WebSocket conectados.
          * **Payload**: Contém os dados do novo usuário (ID, username, public\_key) para que o frontend possa atualizar suas listas de contatos em tempo real.

-----