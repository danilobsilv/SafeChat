import React, { useCallback, useState, useEffect, useRef } from 'react';
import {v4 as uuidv4} from 'uuid'
import ReconnectingWebSocket from 'reconnecting-websocket';

import { Container, SectionLogon, Button, Input, SectionLogged, ChatArea, ChatCard, SectionChat, TextAreaChat, ChatUser, ContainerChat, SectionChatList, UserListArea, UserCard } from './styles';

import api from '../../services/api'; // Acesso ao HTTPS (conforme seu api.ts)

// --- Funções Auxiliares para Criptografia (Web Crypto API) ---
// Estas funções operam no navegador para criptografia RSA e hash SHA256.

// Converte ArrayBuffer para String Base64
const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
    return btoa(String.fromCharCode(...new Uint8Array(buffer)));
};

// Converte String Base64 para ArrayBuffer
const base64ToArrayBuffer = (base64: string): ArrayBuffer => {
    const binary_string = atob(base64);
    const len = binary_string.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
};

// Converte string HEX para ArrayBuffer
const hexToArrayBuffer = (hexString: string): ArrayBuffer => {
    if (hexString.length % 2 !== 0) {
        throw new Error("String hexadecimal inválida: comprimento ímpar.");
    }
    const bytes = new Uint8Array(hexString.length / 2);
    for (let i = 0; i < hexString.length; i += 2) {
        bytes[i / 2] = parseInt(hexString.substring(i, i + 2), 16);
    }
    return bytes.buffer;
};


// Importa Chave Pública de uma string HEX (que representa um formato SPKI DER)
const importPublicKeyFromHex = async (hex: string): Promise<CryptoKey> => {
    const binaryDer = hexToArrayBuffer(hex);
    return window.crypto.subtle.importKey(
        "spki", // SubjectPublicKeyInfo format
        binaryDer,
        {
            name: "RSA-OAEP", // Algoritmo de criptografia
            hash: { name: "SHA-256" }, // Algoritmo de hash
        },
        true, // Extratora
        ["encrypt"] // Usos da chave: criptografar
    );
};

// Criptografa conteúdo de mensagem com chave pública RSA (fluxo: Mensagem é cifrada com Kp_REMETENTE)
const rsaEncrypt = async (publicKey: CryptoKey, plaintext: string): Promise<string> => {
    const encoded = new TextEncoder().encode(plaintext); // Codifica o texto para ArrayBuffer
    const ciphertextBuffer = await window.crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        publicKey,
        encoded
    );
    return arrayBufferToBase64(ciphertextBuffer); // Retorna o texto cifrado em Base64
};

// Gera hash SHA256 do conteúdo da mensagem (para integridade)
const sha256Hash = async (text: string): Promise<string> => {
    const textEncoder = new TextEncoder();
    const data = textEncoder.encode(text);
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
};
// --- Fim das Funções Auxiliares ---


// --- Interfaces para o Frontend ---

// Interface para um usuário na lista de contatos
interface IUserInList {
    id: string;
    username: string;
    public_key: string; // HEX string da chave pública
    crypto_key_obj?: CryptoKey; // Objeto CryptoKey importado para uso criptográfico
}

// Interface para mensagens recebidas do backend (já descriptografadas)
interface IMessagesDisplay {
    id: string;
    content: string; // Conteúdo já descriptografado pelo backend
    created_at: string;
    sender_id: string;
    sender_username: string;
    recipient_id: string;
    recipient_username: string;
    is_integrity_valid: boolean; // Flag de validade da integridade (do backend)
}

// Interface para a mensagem cifrada que será enviada AO BACKEND
interface IMessageEncryptedOut {
    encrypted_content: string; // Conteúdo cifrado com a chave pública do REMETENTE
    message_hash: string;      // Hash SHA256 do plaintext original
    sender_id: string;
    recipient_id: string;
}

// Interface para mensagens WebSocket recebidas do backend (com um tipo e payload)
interface IWebSocketMessage {
    type: "CHAT_MESSAGE" | "NEW_USER_REGISTERED" | "ERROR";
    payload: any; // Pode ser IMessageDisplay ou IUserInList ou um objeto de erro
}

const MainChat: React.FC = () => {

    const [isLogged, setLogged] = useState(false);
    const [isSelectedUser, setIsSelectUser] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [userId, setUserId] = useState(''); // ID do usuário logado

    // Estado para armazenar a chave pública do usuário logado (formato HEX)
    const [loggedInUserPublicKeyHex, setLoggedInUserPublicKeyHex] = useState<string | null>(null);
    // Ref para o objeto CryptoKey da chave pública do usuário logado (para criptografia)
    const loggedInUserPublicKeyObj = useRef<CryptoKey | null>(null);


    const [usersList, setUsersList] = useState<IUserInList[]>([]); // Lista de todos os usuários para o chat
    const [selectedUser, setSelectedUser] = useState<IUserInList | null>(null); // Usuário selecionado para conversar

    const [currentMessage, setCurrentMessage] = useState('');
    const chatAreaRef = useRef<HTMLDivElement>(null);

    // Estado para as mensagens da conversa atual (já descriptografadas pelo backend)
    const [messages, setMessages] = useState<IMessagesDisplay[]>([]);

    // Ref para a instância do WebSocket - AGORA GERENCIADA AQUI
    const ws = useRef<ReconnectingWebSocket | null>(null);

    const WEBSOCKET_BASE_URL = process.env.REACT_APP_WEBSOCKET_URL || 'wss://localhost:8000/ws'; // URL base do WebSocket

    // Função para lidar com o login do usuário
    const handleLogin = useCallback(async () => {
        try {
            const response = await api.post('/register-or-login', { username, password }); 
            console.log("Login/Registro Response:", response.data);
            if (response.status === 200) {
                const loggedInUser = response.data;
                setUserId(loggedInUser.id);
                setUsername(loggedInUser.username);
                setLoggedInUserPublicKeyHex(loggedInUser.public_key); // Armazena a chave pública do usuário logado em HEX
                localStorage.setItem('userPublicKeyHex', loggedInUser.public_key); // Guarda no localStorage
                localStorage.setItem('userId', loggedInUser.id); // Guarda o userId também
                localStorage.setItem('username', loggedInUser.username); // Guarda o username também

                // Importa a chave pública do usuário logado em um objeto CryptoKey para criptografia
                if (loggedInUser.public_key) {
                    loggedInUserPublicKeyObj.current = await importPublicKeyFromHex(loggedInUser.public_key);
                }
                
                setLogged(true);

                // handleLoadUsers será chamado no useEffect do WebSocket após a conexão
            }
        } catch (error: any) {
            console.error("Erro ao fazer login:", error.response?.data?.detail || error.message);
            alert(`Erro ao entrar ou registrar: ${error.response?.data?.detail || error.message}`);
        }
    }, [username, password]);

    // Função para carregar mensagens entre o usuário logado e o usuário selecionado
    const handleLoadMessages = useCallback(async (selectedUserId: string) => {
        if (isLogged && userId && selectedUserId) {
            try {
                // Novo endpoint para pegar mensagens entre dois usuários
                const { data } = await api.get<IMessagesDisplay[]>(`/messages/${userId}/${selectedUserId}`);
                console.log("Mensagens carregadas (descriptografadas pelo backend):", data);
                setMessages(data);
            } catch (error) {
                console.error("Erro ao carregar mensagens:", error);
                alert("Erro ao carregar mensagens. Verifique o console.");
            }
        }
    }, [isLogged, userId]);

    // Função para selecionar um usuário na lista de chats
    const handleSelectUser = useCallback(async (user: IUserInList) => {
        if (isLogged) {
            setIsSelectUser(true);
            setSelectedUser(user);
            setMessages([]); // Limpa as mensagens da conversa anterior
            handleLoadMessages(user.id); // Carrega mensagens da conversa com o usuário selecionado
        }
    }, [isLogged, handleLoadMessages]);

    // Função para lidar com o logout
    const handleLogout = useCallback(() => {
        setLogged(false);
        setUserId('');
        setUsername('');
        setLoggedInUserPublicKeyHex(null);
        localStorage.removeItem('userPublicKeyHex'); // Remove do localStorage
        localStorage.removeItem('userId'); // Remove do localStorage
        localStorage.removeItem('username'); // Remove do localStorage
        setIsSelectUser(false);
        setSelectedUser(null);
        setUsersList([]);
        setMessages([]);
        ws.current?.close(); // Fecha a conexão WebSocket (agora via useRef)
        ws.current = null; // Limpa a referência
    }, []);


    // Função para enviar mensagem (agora com criptografia RSA e hash)
    const handleSendMessage = useCallback(async () => {
        // Verifica se há um usuário logado, um usuário selecionado e uma mensagem para enviar
        // A chave pública necessária para criptografar é a do PRÓPRIO REMETENTE (loggedInUserPublicKeyObj)
        if (!userId || !selectedUser || !currentMessage.trim() || !loggedInUserPublicKeyObj.current) {
            console.warn("Não é possível enviar mensagem: Usuário não logado, nenhum destinatário selecionado, mensagem vazia ou chave pública do REMETENTE ausente.");
            alert("Erro: Dados do remetente incompletos para enviar mensagem. Tente fazer login novamente.");
            return;
        }
        
        // Verifica se o WebSocket está conectado
        if (ws.current?.readyState !== WebSocket.OPEN) {
            console.warn("WebSocket não está pronto para enviar mensagem.");
            alert("Conexão com o chat não está ativa. Tente novamente em alguns instantes.");
            return;
        }

        try {
            // 1. Gera o hash SHA256 do conteúdo da mensagem (plaintext)
            const messageHash = await sha256Hash(currentMessage);

            // 2. Criptografa o conteúdo da mensagem (plaintext) usando a CHAVE PÚBLICA do PRÓPRIO REMETENTE
            const encryptedContent = await rsaEncrypt(loggedInUserPublicKeyObj.current, currentMessage);

            // Objeto da mensagem cifrada para enviar ao backend
            const messagePayload: IMessageEncryptedOut = {
                encrypted_content: encryptedContent,
                message_hash: messageHash,
                sender_id: userId,          // ID do remetente (você)
                recipient_id: selectedUser.id // ID do destinatário (usuário selecionado)
            };

            // Encapsula a mensagem de chat com um tipo para o WebSocket
            const wsMessage = {
                type: "CHAT_MESSAGE",
                payload: messagePayload
            };

            // Envia a mensagem cifrada como uma string JSON via WebSocket
            ws.current.send(JSON.stringify(wsMessage)); 
            
            // NOVO: Adiciona a mensagem imediatamente à tela do remetente
            // Cria uma representação da mensagem como se tivesse vindo do backend (já descriptografada)
            const selfSentMessage: IMessagesDisplay = {
                id: uuidv4(), // Gera um ID temporário ou pode ser ajustado se o backend retornar o ID real
                content: currentMessage, // Usa o conteúdo plaintext original
                created_at: new Date().toISOString(), // Data/hora atual
                sender_id: userId,
                sender_username: username, // Nome de usuário do remetente
                recipient_id: selectedUser.id,
                recipient_username: selectedUser.username, // Nome de usuário do destinatário
                is_integrity_valid: true // Assumimos que é válida já que você acabou de criar
            };

            setMessages((prevMessages) => [...prevMessages, selfSentMessage]);

            setCurrentMessage(''); // Limpa o campo de entrada

        } catch (error) {
            console.error("Erro ao enviar mensagem cifrada:", error);
            alert("Erro ao enviar mensagem cifrada. Verifique o console.");
        }
    }, [userId, username, selectedUser, currentMessage, loggedInUserPublicKeyObj.current]); // Dependências da chave pública do usuário logado

    // Função para carregar a lista de todos os usuários (exceto o próprio)
    const handleLoadUsers = useCallback(async () => {
        if (isLogged && userId) { // Garante que o usuário esteja logado
            try {
                const { data } = await api.get<IUserInList[]>('/users'); 
                // Filtra o próprio usuário da lista e importa as chaves públicas
                const otherUsers = await Promise.all(
                    data.filter(u => u.id !== userId && u.public_key) // Apenas usuários com chave pública
                        .map(async (u) => ({
                            ...u,
                            crypto_key_obj: await importPublicKeyFromHex(u.public_key) // <-- Importa de HEX
                        }))
                );
                setUsersList(otherUsers);
                console.log("Lista de usuários carregada:", otherUsers);
            } catch (error) {
                console.error("Erro ao carregar lista de usuários:", error);
            }
        }
    }, [isLogged, userId]);


    // Efeito para carregar credenciais do localStorage na montagem
    // E, se houver, importar a chave pública do usuário logado.
    useEffect(() => {
        const storedUserId = localStorage.getItem('userId');
        const storedUsername = localStorage.getItem('username');
        const storedUserPublicKeyHex = localStorage.getItem('userPublicKeyHex'); // Chave em HEX

        if (storedUserId && storedUsername && storedUserPublicKeyHex) {
            setUserId(storedUserId);
            setUsername(storedUsername);
            setLoggedInUserPublicKeyHex(storedUserPublicKeyHex);
            
            // Importa a chave pública do usuário logado se estiver no localStorage
            importPublicKeyFromHex(storedUserPublicKeyHex).then(keyObj => { // <-- Importa de HEX
                loggedInUserPublicKeyObj.current = keyObj;
                setLogged(true); // Define como logado após carregar a chave
            }).catch(error => {
                console.error("Erro ao importar chave pública do localStorage:", error);
                // Se a chave estiver corrompida, forçamos o relogin.
                handleLogout(); 
            });
        }
    }, [handleLogout]); // Executa apenas uma vez na montagem do componente, com handleLogout na dependência


    // Efeito para gerenciar a conexão WebSocket e o carregamento inicial de dados
    useEffect(() => {
        // Se o usuário estiver logado E o userId for válido
        if (isLogged && userId) {
            // Se não há instância de WS OU se ela está fechada, cria uma nova
            if (!ws.current || ws.current.readyState === WebSocket.CLOSED) {
                const websocketUrl = `${WEBSOCKET_BASE_URL}/${userId}`;
                console.log(`Tentando conectar WebSocket para o usuário ${userId} em: ${websocketUrl}`);
                ws.current = new ReconnectingWebSocket(websocketUrl);

                ws.current.onopen = () => {
                    console.log(`WebSocket CONECTADO para o usuário ${userId}!`);
                    // Uma vez conectado, carrega a lista de usuários para exibição
                    handleLoadUsers();
                };

                ws.current.onmessage = async (event) => {
                    const wsMessage: IWebSocketMessage = JSON.parse(event.data);
                    console.log("Mensagem WebSocket recebida:", wsMessage);
                    
                    if (wsMessage.type === "CHAT_MESSAGE") {
                        const receivedMessage: IMessagesDisplay = wsMessage.payload;
                        console.log("Mensagem de chat (já descriptografada pelo backend):", receivedMessage);
                        
                        // Adiciona a mensagem à conversa SOMENTE se for para a conversa atual (sender_id ou recipient_id)
                        // E se o usuário selecionado é o mesmo que o remetente ou o destinatário
                        // Verifica se a mensagem é da conversa atual com o selectedUser OU se é uma mensagem do próprio usuário para o selectedUser
                        if (selectedUser && 
                            ((receivedMessage.sender_id === userId && receivedMessage.recipient_id === selectedUser.id) || // Você enviou para o selecionado
                             (receivedMessage.sender_id === selectedUser.id && receivedMessage.recipient_id === userId))) { // O selecionado enviou para você
                            
                            setMessages((prevMessages) => {
                                const exists = prevMessages.some(msg => msg.id === receivedMessage.id);
                                return exists ? prevMessages : [...prevMessages, receivedMessage];
                            });
                        }
                    } else if (wsMessage.type === "NEW_USER_REGISTERED") {
                        const newUser: IUserInList = wsMessage.payload.user; 
                        console.log("NOVO USUÁRIO REGISTRADO:", newUser);
                        // Importa a chave pública do novo usuário e adiciona à lista
                        try {
                            const newUserWithCryptoObj = {
                                ...newUser,
                                crypto_key_obj: await importPublicKeyFromHex(newUser.public_key)
                            };
                            setUsersList(prevUsers => {
                                const exists = prevUsers.some(u => u.id === newUser.id);
                                return exists ? prevUsers : [...prevUsers, newUserWithCryptoObj];
                            });
                        } catch (error) {
                            console.error("Erro ao importar chave pública do novo usuário:", error);
                        }
                    } else if (wsMessage.type === "ERROR") {
                        console.error("Erro do servidor via WebSocket:", wsMessage.payload);
                        alert(`Erro do chat: ${wsMessage.payload.error || JSON.stringify(wsMessage.payload)}`);
                    } else {
                        console.warn("Tipo de mensagem WebSocket desconhecido:", wsMessage.type, wsMessage.payload);
                    }
                };

                ws.current.onclose = (event) => { 
                    console.log('WebSocket DESCONECTADO.', event.code, event.reason);
                };
                ws.current.onerror = (error) => { 
                    console.error('WebSocket ERRO:', error);
                };
            }
            
            // Cleanup function: Fecha o WebSocket quando o componente é desmontado ou as dependências mudam para não-logado
            return () => {
                if (!isLogged && ws.current) { 
                    console.log("Limpeza do useEffect: Fechando WebSocket.");
                    ws.current.close();
                    ws.current = null; 
                }
                if (ws.current) {
                    ws.current.onopen = null;
                    ws.current.onmessage = null;
                    ws.current.onclose = null;
                    ws.current.onerror = null;
                }
            };
        } else {
            // Se não estiver logado, garante que o WebSocket esteja fechado
            if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
                console.log("Usuário não logado ou userId inválido. Fechando WebSocket existente.");
                ws.current.close();
                ws.current = null;
            }
        }
    }, [isLogged, userId, selectedUser, handleLoadUsers, handleLogout, WEBSOCKET_BASE_URL]); // Dependências

    // Efeito para scrollar para o final do chat
    useEffect(() => {
        if (chatAreaRef.current) {
            chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
        }
    }, [messages]); // Rola sempre que novas mensagens chegam

    // Renderização do componente
    return (
        <Container>
            <h1>Safe Chat</h1>
            {!isLogged ? (
                <SectionLogon>
                    <Input
                        type='text'
                        placeholder='Nome de Usuário'
                        value={username}
                        onChange={({ target }) => setUsername(target.value)}
                    />
                    <Input
                        type='password'
                        placeholder='Senha'
                        value={password}
                        onChange={({ target }) => setPassword(target.value)}
                    />
                    <Button type='button' onClick={handleLogin}>Entrar</Button>
                </SectionLogon>
            ) : (
                <SectionLogged>
                    <h2>Olá {username || "Usuário"}</h2>
                    <Button type='button' onClick={handleLogout}>Sair</Button>
                </SectionLogged>
            )}

            {isLogged && (
                <ContainerChat>
                    <SectionChatList>
                        <h2>Lista de usuários</h2>
                        <UserListArea>
                            {
                                usersList.length > 0 ? (
                                    usersList.map(user => (
                                        <UserCard
                                            key={user.id}
                                            type='button'
                                            // Adiciona classe para destacar o usuário selecionado
                                            className={selectedUser?.id === user.id ? 'selected' : ''}
                                            onClick={() => handleSelectUser(user)}
                                        >
                                            {user.username}
                                        </UserCard>
                                    ))
                                ) : (
                                    <p>Nenhum outro usuário disponível.</p>
                                )
                            }
                        </UserListArea>
                    </SectionChatList>
                    <SectionChat>
                        {isSelectedUser && selectedUser ? ( // Verifica se um usuário está selecionado
                            <>
                                <h2>Conversando com: {selectedUser.username}</h2>
                                <ChatArea ref={chatAreaRef}>
                                    {messages.map((item) => (
                                        // isSelfMessage é para estilização, se 'styles.ts' o suportar
                                        // Compara o sender_id com o userId logado
                                        <ChatCard key={item.id} isSelfMessage={item.sender_id === userId}>
                                            <span>{item.sender_username}:</span> {/* Usa sender_username do backend */}
                                            <div>{item.content}</div> {/* Conteúdo já descriptografado */}
                                            {/* Opcional: Adicionar indicador de integridade se quiser */}
                                            {item.is_integrity_valid === false && (
                                                <small style={{ color: 'red' }}>⚠️ Integridade comprometida!</small>
                                            )}
                                            <small>{new Date(item.created_at).toLocaleString()}</small>
                                        </ChatCard>
                                    ))}
                                </ChatArea>

                                <ChatUser>
                                    <TextAreaChat
                                        placeholder='Escreva sua mensagem...'
                                        value={currentMessage}
                                        onChange={({ target }) => setCurrentMessage(target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) { // Permite Shift+Enter para quebra de linha
                                                e.preventDefault(); // Previne quebra de linha padrão
                                                handleSendMessage();
                                            }
                                        }}
                                    />
                                    <Button type='button' onClick={handleSendMessage}>Enviar</Button>
                                </ChatUser>
                            </>
                        ) : (
                            <p>Selecione um usuário na lista para iniciar uma conversa.</p>
                        )}
                    </SectionChat>
                </ContainerChat>
            )}
        </Container>
    );
}

export default MainChat;