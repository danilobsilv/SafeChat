---

Sem problemas! Aqui está o `README.md` completo para o seu frontend React, no formato Markdown, pronto para ser copiado e colado.

---

# Frontend do Safe Chat (React, TypeScript)

Este repositório contém o frontend do Safe Chat, desenvolvido com **React** e **TypeScript**. Ele se comunica com o backend Python (FastAPI) via APIs REST para autenticação e listagem de histórico de mensagens, e via WebSockets (WSS) para comunicação em tempo real no chat. A aplicação é configurada para operar com **TLS (Transport Layer Security)**, garantindo uma conexão segura do navegador ao backend.

---

## Estrutura do Projeto

A estrutura do projeto segue as convenções do Create React App, com algumas adições para organização:

```
frontend/
├── public/               # Arquivos públicos (favicon.ico, index.html, etc.)
├── src/
│   ├── page/             # Contém os componentes de página (telas principais da aplicação)
│   │   └── MainChat/     # Componente da tela principal do chat
│   │       ├── index.tsx # Lógica e JSX do componente MainChat
│   │       └── styles.ts # Estilos específicos do componente MainChat (ex: Styled Components)
│   ├── services/         # Módulos para integração com serviços externos (backend)
│   │   ├── api.ts        # Configuração do Axios para comunicação REST com o backend
│   │   └── socket.ts     # Configuração do ReconnectingWebSocket para comunicação em tempo real
│   ├── styles/           # Arquivos de estilização global
│   │   └── global.ts     # Estilos globais da aplicação (ex: Styled Components)
│   ├── App.tsx           # Componente principal da aplicação (geralmente gerencia rotas ou layout base)
│   ├── index.tsx         # Ponto de entrada da aplicação React no DOM
│   ├── react-app-env.d.ts# Arquivo de declaração de tipos para ambientes Create React App
│   └── web-vitals.ts     # Para medir a performance da aplicação
├── .env                  # Variáveis de ambiente (URLs do backend, etc.)
├── .gitignore            # Arquivos e diretórios a serem ignorados pelo Git
├── package-lock.json     # Registro das dependências instaladas (npm)
├── package.json          # Metadados do projeto e scripts npm/yarn
├── README.md             # Este arquivo
├── tsconfig.json         # Configurações do TypeScript
└── yarn.lock             # Registro das dependências instaladas (Yarn)
```

---

## Tecnologias Utilizadas

* **React 19.x**: Biblioteca JavaScript para construção de interfaces de usuário.
* **TypeScript**: Superconjunto tipado de JavaScript que melhora a robustez e manutenibilidade do código.
* **Axios**: Cliente HTTP baseado em Promises para o navegador e Node.js, usado para comunicação com a API REST.
* **Reconnecting-WebSocket**: Biblioteca que estende a API WebSocket nativa, adicionando funcionalidade de reconexão automática.
* **Styled Components**: Biblioteca para estilização de componentes React com CSS-in-JS.
* **Create React App (CRA)**: Ferramenta oficial para configurar um ambiente de desenvolvimento React moderno.
* **cross-env**: Ferramenta para definir variáveis de ambiente de forma cross-platform em scripts npm/yarn.

---

## TLS (Transport Layer Security) na Aplicação

O frontend está configurado para se conectar ao backend usando **HTTPS** para requisições REST e **WSS** para WebSockets, garantindo que a comunicação seja criptografada com **TLS**.

Em ambiente de desenvolvimento, tanto o servidor de desenvolvimento do React (via `create-react-app`) quanto o backend Python estão configurados para usar **certificados autoassinados**. Isso significa que seus navegadores podem exibir avisos de segurança (`net::ERR_CERT_AUTHORITY_INVALID`) na primeira vez que você acessar ou interagir com o aplicativo.

**Para contornar esses avisos em desenvolvimento:**

1.  **Para o Frontend (servidor de desenvolvimento do React):** Na primeira vez que você executar `yarn start` e o navegador abrir `https://localhost:3000`, você verá um aviso. Aceite-o (geralmente clicando em "Avançado" e depois em "Prosseguir para localhost").
2.  **Para o Backend (Python FastAPI):** Antes de interagir com o chat, abra uma nova aba no seu navegador e navegue diretamente para a URL do seu backend: `https://localhost:8000/`. Você verá outro aviso de segurança. Aceite-o da mesma forma.

Após aceitar os certificados autoassinados em ambas as URLs no seu navegador, a comunicação entre o frontend e o backend ocorrerá de forma segura e sem interrupções.

---

## Como Instalar e Executar

Siga os passos abaixo para configurar e executar o frontend:

### 1. Pré-requisitos

Certifique-se de ter instalado:

* **Node.js** (versão LTS recomendada)
* **npm** ou **Yarn** (Yarn é o que usamos nos exemplos de scripts)

### 2. Clonar o Repositório (se aplicável)

Se este frontend estiver em um repositório separado:

```bash
git clone <url_do_seu_repositorio_frontend>
cd frontend
```

### 3. Instalar Dependências

Na raiz do diretório `frontend/`, instale as dependências:

```bash
yarn install
# ou
npm install
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do seu projeto `frontend/` (na mesma pasta onde está o `package.json`) e adicione as URLs do seu backend Python (ajuste as portas se necessário):

```dotenv
# .env
REACT_APP_API_URL=https://localhost:8000
REACT_APP_WEBSOCKET_URL=wss://localhost:8000/ws
```

### 5. Executar a Aplicação com TLS (HTTPS/WSS)

Certifique-se de que seu backend Python está rodando com HTTPS/WSS (conforme as instruções do `README.md` do backend).

Com o arquivo `.env` configurado e as dependências instaladas, inicie o servidor de desenvolvimento do React:

```bash
yarn start
# ou
npm start
```

O aplicativo será aberto no seu navegador (geralmente em `https://localhost:3000`). Se não abrir, acesse manualmente.

---

## Funcionalidades

* **Registro/Login de Usuário**: Os usuários podem se registrar ou fazer login usando um nome de usuário e senha. Se o usuário já existe, ele é logado; caso contrário, uma nova conta é criada.
* **Chat em Tempo Real**: Após o login, os usuários podem enviar e receber mensagens em uma sala de chat única via WebSockets.
* **Histórico de Mensagens**: As mensagens enviadas são persistidas no backend e são carregadas automaticamente ao fazer login.
* **Interface Simples**: Uma interface de usuário limpa e funcional para a interação do chat.

---