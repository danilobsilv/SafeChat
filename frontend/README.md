# Frontend do Safe Chat (React, TypeScript)

Este repositório contém o frontend do Safe Chat, desenvolvido com **React** e **TypeScript**. Ele se comunica com o backend Python (FastAPI) via APIs REST e WebSockets (WSS). O projeto foi projetado para um **chat individual e seguro**, com foco na criptografia de mensagens (RSA) e verificação de integridade (SHA256) onde o servidor atua como um intermediário confiável que descriptografa e retransmite as mensagens. A aplicação utiliza **TLS (Transport Layer Security)** para proteger todas as comunicações.

---

## 🚀 Visão Geral do Projeto

O Safe Chat oferece uma plataforma para usuários se comunicarem de forma individual e segura. As principais características incluem:

* **Autenticação de Usuário**: Registro e login para gerenciar usuários, onde o backend gera um par de chaves assimétricas (pública/privada) para cada usuário.
* **Chat Individual Protegido**: Usuários podem selecionar outro usuário na lista para iniciar uma conversa privada.
* **Criptografia Assimétrica de Mensagens**:
    * As mensagens são criptografadas no frontend utilizando a **chave pública do *próprio remetente***.
    * O backend recebe a mensagem cifrada, a **descriptografa com a chave privada do remetente** e a retransmite em texto claro para o destinatário.
    * Isso significa que o **servidor tem acesso ao conteúdo das mensagens** para fins de registro e moderação, mas a mensagem é protegida durante o trânsito do cliente para o servidor.
* **Verificação de Integridade (Hash SHA256)**: Cada mensagem é acompanhada de um hash SHA256 do seu conteúdo original (plaintext), gerado no frontend. O backend verifica este hash após a descriptografia para garantir que a mensagem não foi adulterada durante o envio.
* **Histórico de Mensagens**: Conversas anteriores são carregadas e exibidas ao selecionar um contato.
* **Atualização de Lista de Usuários em Tempo Real**: Novas contas registradas são automaticamente adicionadas à lista de usuários de todos os clientes conectados via WebSocket.
* **Comunicação Segura (TLS)**: Todas as requisições HTTPs e WebSockets (WSS) são criptografadas.

---

## 🛠️ Tecnologias Principais

* **React 19.x**: Biblioteca JavaScript para construção de interfaces de usuário.
* **TypeScript**: Superconjunto tipado de JavaScript que melhora a robustez e manutenibilidade do código.
* **Axios**: Cliente HTTP baseado em Promises para o navegador, usado para comunicação com a API REST.
* **Reconnecting-WebSocket**: Biblioteca que estende a API WebSocket nativa, adicionando funcionalidade de reconexão automática.
* **Styled Components**: Biblioteca para estilização de componentes React com CSS-in-JS.
* **Web Crypto API**: API nativa do navegador para operações criptográficas (RSA, SHA256, Base64, Hex).
* **uuid**: Biblioteca para geração de UUIDs (usado para IDs temporários de mensagens no frontend).
* **Create React App (CRA)**: Ferramenta oficial para configurar um ambiente de desenvolvimento React moderno.
* **cross-env**: Ferramenta para definir variáveis de ambiente de forma cross-platform em scripts npm/yarn.

---

## 📂 Estrutura do Projeto

A estrutura do projeto segue as convenções do Create React App:

```
frontend/
├── public/               \# Arquivos públicos (favicon.ico, index.html, etc.)
├── src/
│   ├── page/             \# Contém os componentes de página (telas principais da aplicação)
│   │   └── MainChat/     \# Componente da tela principal do chat
│   │       ├── index.tsx \# Lógica e JSX do componente MainChat (o coração da aplicação)
│   │       └── styles.ts \# Estilos específicos do componente MainChat (e.g., com Styled Components)
│   ├── services/         \# Módulos para integração com serviços externos (backend)
│   │   └── api.ts        \# Configuração do Axios para comunicação REST com o backend
│   │   \# O arquivo socket.ts foi removido, a instância de WebSocket é gerenciada internamente no MainChat.
│   ├── styles/           \# Arquivos de estilização global
│   │   └── global.ts     \# Estilos globais da aplicação (e.g., com Styled Components)
│   ├── App.tsx           \# Componente principal da aplicação (geralmente gerencia layout base)
│   ├── index.tsx         \# Ponto de entrada da aplicação React no DOM
│   ├── react-app-env.d.ts\# Arquivo de declaração de tipos para ambientes Create React App
│   └── web-vitals.ts     \# Para medir a performance da aplicação
├── .env                  \# Variáveis de ambiente (URLs do backend, etc.)
├── .gitignore            \# Arquivos e diretórios a serem ignorados pelo Git
├── package-lock.json     \# Registro das dependências instaladas (npm)
├── package.json          \# Metadados do projeto e scripts npm/yarn
├── README.md             \# Este arquivo
├── tsconfig.json         \# Configurações do TypeScript
└── yarn.lock             \# Registro das dependências instaladas (Yarn)
```


---

## 🔒 Comunicação Segura e Criptografia

O frontend do Safe Chat é projetado para interagir com um backend que implementa um fluxo de criptografia específico:

* **TLS (HTTPS/WSS)**: Todas as conexões de rede são criptografadas usando TLS. Em desenvolvimento, isso exige que você aceite manualmente os certificados autoassinados do servidor React (`https://localhost:3000`) e do backend Python (`https://localhost:8000`) em seu navegador na primeira vez.
* **Geração de Chaves Assíncronas (Backend)**: Cada usuário, ao ser criado no sistema (via registro/login inicial), recebe um par de chaves RSA assimétricas (uma chave pública e uma privada) geradas pelo backend.
    * A **chave pública** do usuário logado é retornada pelo backend no momento do login e armazenada no `localStorage` do navegador para ser usada na criptografia das mensagens.
    * A **chave privada** do usuário é armazenada (não criptografada, em HEX) no banco de dados do backend, acessível apenas pelo servidor.
* **Criptografia de Mensagem (Frontend)**: Quando você envia uma mensagem, o frontend executa os seguintes passos:
    1.  Gera um **hash SHA256** do conteúdo original (plaintext) da mensagem para verificação de integridade.
    2.  **Criptografa a mensagem** usando a **sua própria chave pública (do remetente)**, que foi obtida no login e está em `localStorage`.
    3.  Envia a mensagem cifrada, o hash e os IDs do remetente/destinatário para o backend via WebSocket.
* **Processamento de Mensagens (Backend)**: O backend recebe a mensagem cifrada, usa a **chave privada do *remetente original*** (armazenada em seu banco de dados) para descriptografá-la, verifica o hash para garantir a integridade, e então retransmite a mensagem **em texto claro** para o destinatário e para o próprio remetente.
* **Exibição de Mensagens (Frontend)**: As mensagens recebidas do backend já vêm descriptografadas. O frontend as exibe diretamente, com um indicador visual caso a verificação de integridade falhe (o que pode sugerir adulteração).

---

## ⚙️ Como Começar

Para colocar o frontend em funcionamento, você deve primeiro ter o backend Python configurado e rodando.

### Pré-requisitos

Certifique-se de ter instalado em sua máquina:

* **Node.js LTS** (recomendado)
* **Yarn** (ou npm)
* Seu **Backend Python** rodando (consulte o `README.md` da pasta `backend/` para instruções de instalação e execução, incluindo a geração de certificados TLS).

### 1. Clonar o Repositório (se aplicável)

Se este frontend estiver em um repositório separado:

```bash
git clone <url_do_seu_repositorio_frontend>
cd frontend
````

### 2\. Instalar Dependências

Na raiz do diretório `frontend/`, instale as dependências:

```bash
yarn install
# ou
npm install
```

### 3\. Configurar Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do seu projeto `frontend/` (na mesma pasta onde está o `package.json`) e adicione as URLs do seu backend Python (ajuste as portas se necessário):

```dotenv
# .env
REACT_APP_API_URL=https://localhost:8000
REACT_APP_WEBSOCKET_URL=wss://localhost:8000/ws
```

### 4\. Executar a Aplicação com TLS (HTTPS/WSS)

Certifique-se de que seu backend Python está rodando com HTTPS/WSS (conforme as instruções do `README.md` do backend).

Com o arquivo `.env` configurado e as dependências instaladas, inicie o servidor de desenvolvimento do React:

```bash
yarn start
# ou
npm start
```

O aplicativo será aberto no seu navegador (geralmente em `https://localhost:3000`). Se não abrir, acesse manualmente.

### 5\. Aceitar Certificados no Navegador (Desenvolvimento Local)

Devido ao uso de certificados autoassinados para TLS em desenvolvimento, seu navegador exibirá avisos de segurança. Para que a aplicação funcione corretamente:

1.  **Acesse o frontend:** Navegue para `https://localhost:3000` (ou a porta que seu React estiver usando). Aceite o aviso de segurança do navegador para o certificado do servidor de desenvolvimento do React.
2.  **Acesse o backend:** Em uma **nova aba** do navegador, navegue diretamente para `https://localhost:8000` (ou a porta do seu backend). Aceite o aviso de segurança para o certificado do backend Python.

Após aceitar ambos os certificados manualmente uma vez, a comunicação completa entre frontend e backend estará segura e funcional em seu ambiente local.

-----

## Contribuição

Contribuições são bem-vindas\! Sinta-se à vontade para abrir issues ou pull requests.

-----
