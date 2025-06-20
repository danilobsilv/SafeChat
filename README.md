# Safe Chat Application

Bem-vindo ao **Safe Chat**, uma aplicação de chat em tempo real construída com um backend Python (FastAPI) e um frontend React (TypeScript). Este projeto demonstra uma arquitetura moderna para comunicação segura e persistência de dados, com foco em TLS (Transport Layer Security) para proteger as interações.

---

## 🚀 Visão Geral do Projeto

O Safe Chat oferece uma plataforma simples para usuários se conectarem e conversarem em uma sala de chat única. As principais características incluem:

* **Autenticação de Usuário:** Registro e login para gerenciar usuários.
* **Chat em Tempo Real:** Envio e recebimento instantâneo de mensagens via WebSockets.
* **Histórico de Mensagens:** Persistência de todas as conversas em um banco de dados SQLite.
* **Comunicação Segura (TLS):** Criptografia de ponta a ponta para proteger todas as requisições HTTPs e WebSockets (WSS).

---

## 🛠️ Tecnologias Principais

### Backend

* **Python 3.8+**: Linguagem de programação principal.
* **FastAPI**: Framework web de alta performance para construir APIs REST e WebSockets.
* **Uvicorn**: Servidor ASGI para executar o FastAPI.
* **SQLAlchemy**: ORM para interação com o banco de dados.
* **SQLite**: Banco de dados leve para persistência de dados.
* **OpenSSL**: Para geração e gerenciamento de certificados TLS.

### Frontend

* **React 19.x**: Biblioteca JavaScript para construção da interface do usuário.
* **TypeScript**: Adiciona tipagem estática para maior robustez do código.
* **Axios**: Cliente HTTP para requisições REST.
* **Reconnecting-WebSocket**: Para gerenciar a conexão WebSocket de forma resiliente.
* **Styled Components**: Para estilização dos componentes.

---

## 📂 Estrutura do Repositório

Este repositório é organizado em duas pastas principais, uma para o backend e outra para o frontend, cada uma com seu próprio `README.md` detalhado:

```
SafeChatApplication/
├── backend/                  # Contém todo o código-fonte do backend Python
│   └── README.md             # README detalhado do backend
├── frontend/                 # Contém todo o código-fonte do frontend React
│   └── README.md             # README detalhado do frontend
└── README.md                 # Este README global
```

---

## ⚙️ Como Começar

Para colocar a aplicação em funcionamento, siga os passos abaixo para configurar e executar tanto o backend quanto o frontend.

### Pré-requisitos

Certifique-se de ter instalado em sua máquina:

* **Python 3.8+** e **pip**
* **Node.js LTS** e **Yarn** (ou npm)
* **OpenSSL** (instalado e disponível no PATH do seu sistema, especialmente no Windows)

### 1. Configurar o Backend

Navegue até a pasta `backend/` e siga as instruções detalhadas no `README.md` específico do backend para:

* Instalar as dependências Python.
* **Gerar os certificados TLS (HTTPS/WSS) usando OpenSSL.**
* Executar o servidor FastAPI/Uvicorn com TLS configurado.

```bash
cd backend
# Siga as instruções do README.md para gerar certificados e iniciar
```

### 2. Configurar o Frontend

Em um **novo terminal**, navegue até a pasta `frontend/` e siga as instruções detalhadas no `README.md` específico do frontend para:

* Instalar as dependências Node.js/React.
* Configurar as variáveis de ambiente (`.env`) para apontar para o backend HTTPS/WSS.
* Executar o servidor de desenvolvimento React com HTTPS.

```bash
cd frontend
# Siga as instruções do README.md para configurar .env e iniciar
```

### 3. Aceitar Certificados no Navegador (Desenvolvimento Local)

Devido ao uso de certificados autoassinados para TLS em desenvolvimento, seu navegador exibirá avisos de segurança. Para que a aplicação funcione corretamente:

1.  **Acesse o frontend:** Navegue para `https://localhost:3000` (ou a porta que seu React estiver usando). Aceite o aviso de segurança do navegador para o certificado do servidor de desenvolvimento do React.
2.  **Acesse o backend:** Em uma **nova aba** do navegador, navegue diretamente para `https://localhost:8000` (ou a porta do seu backend). Aceite o aviso de segurança para o certificado do backend Python.

Após aceitar ambos os certificados manualmente uma vez, a comunicação completa entre frontend e backend estará segura e funcional em seu ambiente local.

---

## 🔒 Segurança

O projeto Safe Chat utiliza TLS para criptografar a comunicação entre cliente e servidor.

**Importante para Produção:**
* Em um ambiente de produção, **NUNCA utilize certificados autoassinados.** Obtenha certificados de uma Autoridade Certificadora (CA) confiável, como Let's Encrypt.
* Considere implementar **autenticação de usuário com JWT (JSON Web Tokens)** para proteger as rotas da API e o acesso ao WebSocket, garantindo que apenas usuários autenticados possam interagir com o chat. Esta é uma funcionalidade que pode ser adicionada como uma próxima etapa para fortalecer a segurança.

---

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

---

## Licença

Este projeto está licenciado sob a Licença MIT.

---