import React, {useCallback, useState, useEffect, useRef} from 'react';

import { Container, SectionLogon, Button, Input, SectionLogged, ChatArea, ChatCard, SectionChat, TextAreaChat, ChatUser } from './styles';

import api from '../../services/api';
import socket from '../../services/socket';

interface IMessages {
  id: string;
  content: string;
  created_at: string;
  username: string;
}

const MainChat: React.FC = () => {

  const [isLogged, setLogged]  = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [userId, setUserId] = useState('');

  const [currentMessage, setCurrentMessage] = useState(''); 
  const chatAreaRef = useRef<HTMLDivElement>(null); 




  const [messages, setMessages] = useState<IMessages[]>([])

  const handleLogin = useCallback(async () => {
        try {
            const response = await api.post('/register-or-login', { username, password });
            console.log("Login/Registro Response:", response.data);
            if (response.status === 200) {
                setUserId(response.data.id);
                setLogged(true);
            }
        } catch (error) {
            console.error("Erro ao fazer login:", error);
            alert("Erro ao entrar ou registrar. Verifique o console.");
        }
  }, [username, password]);

  const handleLoadMessages = useCallback(async () => {
        if (isLogged) {
            try {
                const { data } = await api.get<IMessages[]>('/messages');
                console.log(data)
                setMessages(data);
            } catch (error) {
                console.error("Erro ao carregar mensagens:", error);
                alert("Erro ao carregar mensagens. Verifique o console.");
            }
        }
  }, [isLogged]);

  const handleLogout = useCallback(() => {
        setLogged(false);
        setUserId('');
        setMessages([]);
        socket.close();
  }, []);


  const handleSendMessage = useCallback(() => {
        console.log(currentMessage, userId, socket)
        if (socket.readyState === WebSocket.OPEN && currentMessage.trim() && userId) {
            const messageToSend = {
                content: currentMessage,
                user_id: userId
            };
            socket.send(JSON.stringify(messageToSend));
            setCurrentMessage(''); // Limpa a área de texto
        } else {
            console.warn("WebSocket não está pronto ou mensagem/userId vazio.");
        }
  }, [currentMessage, userId]);

  // Efeito para gerenciar a conexão WebSocket
  useEffect(() => {
      if (isLogged && userId) {
          socket.onopen = () => {
              console.log('WebSocket conectado!');
          };

          socket.onmessage = (event) => {
              const receivedMessage: IMessages = JSON.parse(event.data);
              console.log("Mensagem recebida:", receivedMessage);
              setMessages((prevMessages) => [...prevMessages, receivedMessage]);
          };

          socket.onclose = () => {
              console.log('WebSocket desconectado.');
          };

          socket.onerror = (error) => {
              console.error('WebSocket erro:', error);
          };

          return () => {
              socket.onopen = null;
              socket.onmessage = null;
              socket.onclose = null;
              socket.onerror = null;
          };
      }
  }, [isLogged, userId]);

  // Efeito para carregar mensagens quando o login for bem-sucedido
  useEffect(() => {
      if (isLogged) {
          handleLoadMessages();
      }
  }, [isLogged, handleLoadMessages]);

  // Efeito para scrollar para o final do chat
  useEffect(() => {
      if (chatAreaRef.current) {
          chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
      }
  }, [messages]); // Scrolls sempre que novas mensagens chegam


  return( 
     <Container>
        <h1>Safe Chat</h1>
        {!isLogged ? (
            <SectionLogon>
                <Input
                    type='text'
                    placeholder='Username'
                    value={username}
                    onChange={({ target }) => setUsername(target.value)}
                />
                <Input
                    type='password'
                    placeholder='Password'
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
            <SectionChat>
                <ChatArea ref={chatAreaRef}>
                    {messages.map((item) => (
                        <ChatCard key={item.id} isSelfMessage={item.username===username}>
                            <span>{item.username}:</span>
                            <div>{item.content}</div>
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
            </SectionChat>
        )}
    </Container>
  );
}

export default MainChat;