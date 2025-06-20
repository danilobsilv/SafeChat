---

Sim, com certeza! Aqui está o `README.md` completo no formato Markdown, pronto para você copiar e colar no seu projeto.

---

# Backend do Safe Chat (Python, FastAPI, SQLite, TLS)

Este repositório contém o backend do Safe Chat, desenvolvido em Python usando **FastAPI** para as APIs REST e WebSockets, e **SQLAlchemy** para persistência de dados em um banco SQLite. A aplicação inclui funcionalidades de autenticação básica (registro/login), envio e recebimento de mensagens em tempo real, e está configurada para usar **TLS (Transport Layer Security)** para comunicação segura via HTTPS e WSS.

---

## Estrutura do Projeto

A estrutura do projeto é modular para facilitar a organização e manutenção do código:

```
python-backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Ponto de entrada da aplicação FastAPI e definições de rotas
│   ├── database.py       # Configuração da conexão com o banco de dados SQLite
│   ├── models.py         # Definição dos modelos de dados (SQLAlchemy ORM) para Usuários e Mensagens
│   ├── schemas.py        # Modelos de dados para validação (Pydantic) de entrada/saída da API
│   └── crud.py           # Funções de operações CRUD (Create, Read, Update, Delete) com o banco de dados
├── certs/                # Diretório para armazenar os certificados TLS (chave e certificado)
│   ├── server.key
│   └── server.crt
├── requirements.txt      # Lista de dependências Python
└── README.md             # Este arquivo
```

---

## Tecnologias Utilizadas

* **FastAPI**: Framework web moderno e de alta performance para construir APIs com Python, baseado em tipos (type hints).
* **Uvicorn**: Servidor ASGI para executar a aplicação FastAPI de forma assíncrona e eficiente.
* **SQLAlchemy**: Toolkit SQL e ORM (Object Relational Mapper) para interagir com o banco de dados SQLite.
* **Pydantic**: Biblioteca de validação de dados usada pelo FastAPI para garantir a integridade dos dados.
* **OpenSSL**: Ferramenta de linha de comando para gerar e gerenciar certificados SSL/TLS.
* **SQLite**: Banco de dados relacional leve e embutido, ideal para desenvolvimento local e aplicações menores.

---

## TLS (Transport Layer Security) na Aplicação

A aplicação está configurada para usar **TLS (Transport Layer Security)**, o que garante que toda a comunicação entre o frontend (React) e o backend (FastAPI) seja **criptografada**. Isso protege os dados em trânsito de serem interceptados e lidos por terceiros.

No ambiente de desenvolvimento, utilizamos **certificados autoassinados** gerados com **OpenSSL**. Isso significa que você mesmo é a "Autoridade Certificadora" que emitiu o certificado do seu servidor. Por padrão, navegadores não confiam em certificados autoassinados, o que resultará no erro `net::ERR_CERT_AUTHORITY_INVALID` ao tentar acessar o backend via HTTPS/WSS pela primeira vez.

**Para contornar isso em desenvolvimento**, você precisará aceitar manualmente o certificado do backend no seu navegador. Basta navegar diretamente para a URL do seu backend (`https://localhost:8000/`) e aceitar o aviso de segurança (clicando em "Avançado" e depois em "Prosseguir para localhost" ou similar). Feito isso uma vez, o navegador confiará temporariamente na conexão para futuras requisições do seu frontend.

**Em um ambiente de produção**, você **DEVERÁ** usar certificados emitidos por uma Autoridade Certificadora (CA) reconhecida globalmente (como Let's Encrypt), e geralmente um proxy reverso (como Nginx ou Caddy) seria configurado para gerenciar o TLS.

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
```

### 3. Instalar Dependências Python

Na raiz do diretório `python-backend/`, instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Gerar Certificados TLS com OpenSSL

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

### 5. Executar a Aplicação com TLS (HTTPS/WSS)

Com os certificados gerados, inicie o servidor Uvicorn a partir da raiz do diretório `python-backend/`:

```powershell
uvicorn app.main:app --reload --ssl-keyfile=certs/server.key --ssl-certfile=certs/server.crt
```

* `--reload`: Recarrega o servidor automaticamente ao detectar mudanças no código (ótimo para desenvolvimento).
* `--ssl-keyfile` e `--ssl-certfile`: Apontam para os arquivos de chave privada e certificado que você acabou de gerar.

Seu backend agora estará acessível via `https://localhost:8000` para APIs REST e `wss://localhost:8000/ws` para WebSockets.

---

## Endpoints da API REST

Acesse `https://localhost:8000/docs` no seu navegador para ver a documentação interativa da API (Swagger UI).

### Autenticação/Registro de Usuário

* **`POST /register-or-login`**
    * **Descrição**: Permite que um usuário se registre ou faça login. Se o `username` já existir, verifica a senha. Caso contrário, cria um novo usuário.
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
          "username": "seu_nome_de_usuario"
        }
        ```
        **Importante**: O `id` retornado é o UUID do usuário, necessário para enviar mensagens via WebSocket.

### Listar Mensagens

* **`GET /messages`**
    * **Descrição**: Retorna uma lista de todas as mensagens públicas já enviadas no sistema.
    * **Resposta (JSON - Exemplo)**:
        ```json
        [
          {
            "id": "uuid-da-mensagem-1",
            "content": "Olá a todos!",
            "created_at": "2024-07-20T10:30:00.123456",
            "username": "Json"
          },
          {
            "id": "uuid-da-mensagem-2",
            "content": "Bem-vindos ao chat seguro!",
            "created_at": "2024-07-20T10:31:15.789012",
            "username": "Bob"
          }
        ]
        ```

---

## Funcionalidade WebSocket (Chat em Tempo Real)

* **Endpoint**: `wss://localhost:8000/ws`
* **Conexão**: Todos os clientes se conectam a uma **sala de chat única**. Não há salas separadas.
* **Envio de Mensagens**:
    * Clientes enviam mensagens no formato JSON através da conexão WebSocket.
    * **Formato da Mensagem (JSON)**:
        ```json
        {
          "content": "Minha mensagem para o chat",
          "user_id": "uuid-do-usuario-logado"
        }
        ```
        (O `user_id` é o UUID obtido no endpoint `/register-or-login`).
* **Recebimento de Mensagens**:
    * Toda mensagem enviada por qualquer cliente é salva no banco de dados.
    * Após ser salva, a mensagem é **transmitida (broadcast)** para todos os clientes WebSocket conectados.
    * **Formato da Mensagem Recebida (JSON)**:
        ```json
        {
          "id": "uuid-da-mensagem-salva",
          "content": "Minha mensagem para o chat",
          "created_at": "2024-07-20T10:35:00.000000",
          "username": "NomeDoUsuario"
        }
        ```
---