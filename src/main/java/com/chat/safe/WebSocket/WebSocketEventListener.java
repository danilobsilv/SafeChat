package com.chat.safe.WebSocket;

import com.chat.safe.Chat.ChatMessage;
import com.chat.safe.Chat.MessageType;
import lombok.RequiredArgsConstructor;
import org.springframework.context.event.EventListener;
import org.springframework.messaging.simp.SimpMessageSendingOperations;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.messaging.SessionConnectedEvent;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken; // Importar
import org.springframework.security.core.userdetails.UserDetails; // Importar

@Component
@RequiredArgsConstructor
public class WebSocketEventListener {

    private final SimpMessageSendingOperations messageTemplate;
    private final WebSocketSessionManager sessionManager;

    @EventListener
    public void handleWebSocketConnectListener(SessionConnectedEvent event) {
        StompHeaderAccessor headerAccessor = StompHeaderAccessor.wrap(event.getMessage());

        // Após a autenticação HTTP (seção de segurança), o Principal estará disponível aqui
        // O username virá do Principal, não dos atributos da sessão inicialmente.
        String username = null;
        if (headerAccessor.getUser() instanceof UsernamePasswordAuthenticationToken) {
            username = ((UserDetails) ((UsernamePasswordAuthenticationToken) headerAccessor.getUser()).getPrincipal()).getUsername();
        } else if (headerAccessor.getUser() != null) {
            // Em outros casos, o nome do Principal pode ser o username diretamente
            username = headerAccessor.getUser().getName();
        }


        // A lógica de adição real do usuário ao tópico público ou privado será no controller,
        // dependendo do destino da primeira mensagem STOMP.
        // Aqui, apenas registramos a conexão e o username associado à sessão STOMP.
        if (username != null) {
            String sessionId = headerAccessor.getSessionId();
            // A associação da sessão ao username é feita para rastreamento de desconexão.
            // A adição a um tópico específico é feita no Controller ou no SUBSCRIBE event.
            // Para o public chat, o `addUser` é chamado no controller ao enviar a primeira mensagem.
            System.out.println("User connected via WebSocket: " + username + " (Session ID: " + sessionId + ")");
        }
    }

    @EventListener
    public void handleWebSSocketDisconnectListener(SessionDisconnectEvent event){
        StompHeaderAccessor headerAccessor = StompHeaderAccessor.wrap(event.getMessage());
        String sessionId = headerAccessor.getSessionId();

        // O username é removido do SessionManager.
        // O SessionManager agora remove o usuário de *todos* os tópicos em que ele estava.
        String username = sessionManager.removeUserFromSession(sessionId);

        if (username != null){
            System.out.println("User disconnected: " + username + " (Session ID: " + sessionId + ")");
            // Envia uma mensagem para o tópico público informando a saída
            var chatMessage = ChatMessage.builder()
                    .messageType(MessageType.LEAVE)
                    .sender(username)
                    .build();

            messageTemplate.convertAndSend("/topic/public", chatMessage);
            // Mensagens de desconexão para chats privados teriam que ser tratadas de forma mais complexa
            // se o usuário sair de um chat privado específico. Por enquanto, focamos no público.
        }
    }
}