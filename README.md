# Safe Chat Application

Bem-vindo ao **Safe Chat**, uma aplicação de chat em tempo real desenvolvida para **conversas individuais e seguras**. Este projeto demonstra uma arquitetura de comunicação avançada utilizando um backend Python (FastAPI) e um frontend React (TypeScript), com foco em criptografia assimétrica de mensagens, verificação de integridade e comunicação segura via TLS.

---

## 🚀 Visão Geral do Projeto

O Safe Chat permite que usuários se conectem, gerenciem suas conversas privadas e troquem mensagens com garantia de confidencialidade (até o servidor) e integridade.

* **Autenticação de Usuário**: Registro e login com geração de um par de chaves RSA (pública/privada) para cada usuário no backend.
* **Chat Individual Protegido**: Usuários podem selecionar e conversar privativamente com outros usuários.
* **Criptografia de Mensagens Baseada no Remetente**:
    * Mensagens são criptografadas no frontend usando a **chave pública do *próprio remetente***.
    * O backend recebe a mensagem cifrada, a **descriptografa com a chave privada do *remetente*** (armazenada no servidor), verifica a integridade e retransmite a mensagem **em texto claro** para o destinatário.
    * **Importante**: Este fluxo significa que o **servidor tem acesso ao conteúdo das mensagens**. Não é um sistema de criptografia de ponta a ponta (E2EE) puro, mas garante que a mensagem é protegida em trânsito e que sua integridade é verificada.
* **Verificação de Integridade (Hash SHA256)**: Cada mensagem enviada inclui um hash SHA256 do seu conteúdo original (plaintext), verificado pelo backend para detectar adulterações.
* **Histórico de Conversas**: Mensagens trocadas entre usuários específicos são carregadas ao iniciar uma conversa.
* **Atualização em Tempo Real**: A lista de usuários é atualizada dinamicamente para todos os clientes quando novas contas são registradas.
* **Comunicação Segura (TLS)**: Todas as comunicações de rede (HTTPS para API REST, WSS para WebSockets) são criptografadas utilizando TLS.

---

## 🛠️ Tecnologias Principais

### Backend (Python)

* **Python 3.8+**
* **FastAPI**: Framework web de alta performance.
* **Uvicorn**: Servidor ASGI.
* **SQLAlchemy**: ORM para SQLite.
* **`cryptography`**: Para geração de chaves RSA, criptografia e hashing.
* **SQLite**: Banco de dados relacional leve.
* **OpenSSL**: Para certificados TLS.

### Frontend (React)

* **React 19.x**
* **TypeScript**
* **Axios**: Cliente HTTP para APIs REST.
* **Reconnecting-WebSocket**: Para gerenciar conexões WSS.
* **Web Crypto API**: API nativa do navegador para operações criptográficas.
* **Styled Components**: Para estilização.

---

## 📂 Estrutura do Repositório

Este repositório é dividido em duas pastas principais, cada uma contendo seu próprio `README.md` detalhado:

```

SafeChatApplication/
├── backend/                  \# Contém todo o código-fonte do backend Python.
│   └── README.md             \# README detalhado do backend (instalação, execução, endpoints, criptografia).
├── frontend/                 \# Contém todo o código-source do frontend React.
│   └── README.md             \# README detalhado do frontend (instalação, execução, uso, criptografia).
└── README.md                 \# Este README global do projeto.

```

---

## ⚙️ Como Começar

Para colocar a aplicação em funcionamento completo, você precisará configurar e executar tanto o backend quanto o frontend.

### Pré-requisitos Globais

Certifique-se de ter instalado em sua máquina:

* **Python 3.8+** e **pip**
* **Node.js LTS** e **Yarn** (ou npm)
* **OpenSSL** (instalado e disponível no PATH do seu sistema operacional)

### Passos para Iniciar o Projeto

1.  **Configurar e Iniciar o Backend**:
    * Navegue até a pasta `backend/`.
    * Siga as instruções detalhadas no `backend/README.md` para instalar as dependências Python, **gerar os certificados TLS (HTTPS/WSS) com OpenSSL** e executar o servidor FastAPI/Uvicorn.
    * **Importante**: O backend gerará os pares de chaves RSA para os usuários e os armazenará no banco de dados.

2.  **Configurar e Iniciar o Frontend**:
    * Em um **novo terminal**, navegue até a pasta `frontend/`.
    * Siga as instruções detalhadas no `frontend/README.md` para instalar as dependências Node.js/React, configurar as variáveis de ambiente (`.env`) e executar o servidor de desenvolvimento React com HTTPS.

3.  **Aceitar Certificados no Navegador (Desenvolvimento Local)**:
    * Devido ao uso de certificados autoassinados para TLS em ambiente de desenvolvimento, seu navegador exibirá avisos de segurança. Para que a aplicação funcione corretamente:
        * **Acesse o frontend:** Navegue para `https://localhost:3000` (ou a porta que seu React estiver usando). Aceite o aviso de segurança para o certificado do servidor de desenvolvimento do React.
        * **Acesse o backend:** Em uma **nova aba** do navegador, navegue diretamente para `https://localhost:8000` (ou a porta do seu backend). Aceite o aviso de segurança para o certificado do backend Python.
    * Após aceitar ambos os certificados manualmente uma vez, a comunicação completa entre frontend e backend estará segura e funcional em seu ambiente local.

---

## 🔒 Comunicação Segura e Fluxo Criptográfico Detalhado

O Safe Chat implementa um modelo de segurança que garante a confidencialidade e integridade das mensagens durante o trânsito e no servidor, conforme seu diagrama:

1.  **Geração de Chaves (Backend)**:
    * Ao registrar, cada usuário (`UserA`) tem um par de chaves RSA (pública `Kp_A` e privada `K_P_A_privada`) gerado no backend.
    * `Kp_A` é enviada ao frontend. `K_P_A_privada` é armazenada (em HEX) no DB.

2.  **Envio de Mensagem (Frontend - `UserA`)**:
    * `UserA` escreve a mensagem `M`.
    * Gera um `hash(M)` (SHA256) no frontend.
    * Criptografa `M` usando sua própria chave pública `Kp_A`: `C(M, Kp_A)`.
    * Envia `{ C(M, Kp_A), hash(M), UserA_ID, UserB_ID }` via WebSocket (WSS) para o backend.

3.  **Processamento no Servidor (Backend)**:
    * Recebe `{ C(M, Kp_A), hash(M), UserA_ID, UserB_ID }`.
    * Recupera `K_P_A_privada` do banco de dados (que corresponde a `UserA_ID`).
    * **Descriptografa `C(M, Kp_A)` com `K_P_A_privada` para obter `M` (plaintext).**
    * Calcula `novo_hash(M)` e compara com `hash(M)`. Se forem iguais, `is_integrity_valid = true`.
    * Armazena `C(M, Kp_A)`, `hash(M)`, `UserA_ID`, `UserB_ID` no DB.
    * Prepara a mensagem para retransmissão: `{ id_msg, M, data, UserA_Username, UserB_Username, is_integrity_valid }`.

4.  **Recebimento de Mensagem (Frontend - `UserB`)**:
    * `UserB` recebe a mensagem **em texto claro** (`M`) via WebSocket (WSS) do backend.
    * A integridade já foi verificada pelo servidor, e o status (`is_integrity_valid`) é fornecido.

**Observação de Segurança**: Este fluxo permite que o servidor atue como um ponto central de controle e persistência de mensagens em texto claro. Para cenários que exigem que o servidor **NUNCA** veja o conteúdo da mensagem (True End-to-End Encryption), um fluxo diferente (como criptografia com chave pública do *destinatário* e descriptografia no *cliente do destinatário*) seria necessário.

---

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## Licença

Este projeto está licenciado sob a Licença MIT. 

---
