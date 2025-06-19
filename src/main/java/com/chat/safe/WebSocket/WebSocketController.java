package com.chat.safe.WebSocket;

import com.chat.safe.Chat.ChatMessage;
import com.chat.safe.Chat.MessageType;
import lombok.RequiredArgsConstructor;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessageHeaderAccessor;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.security.core.userdetails.UserDetails; // Importar
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken; // Importar

import java.security.Principal; // Importar

@Controller
@RequiredArgsConstructor
public class WebSocketController {

    private final SimpMessagingTemplate messagingTemplate;
    private final WebSocketSessionManager sessionManager;

    @MessageMapping("/chat.sendMessage")
    @SendTo("/topic/public") // Envia a mensagem para todos que subscrevem em /topic/public
    public ChatMessage sendMessage(@Payload ChatMessage chatMessage, Principal principal){
        // O sender agora é o usuário autenticado, e não pode ser manipulado pelo cliente
        String authenticatedSender = principal.getName();
        chatMessage.setSender(authenticatedSender); // Garante que o sender é o usuário autenticado

        System.out.println("Received chat message from user: " + chatMessage.getSender() + ": " + chatMessage.getContent());
        return chatMessage;
    }

    @MessageMapping("/chat.addUser")
    public void addUser(@Payload ChatMessage chatMessage, SimpMessageHeaderAccessor headerAccessor, Principal principal){
        String username = principal.getName(); // O username é do usuário autenticado
        String sessionId = headerAccessor.getSessionId();
        String topic = "/topic/public";

        // Aqui, o chatMessage.getSender() *deveria* ser igual ao username do principal, mas usamos o principal para segurança.
        // Atualiza o chatMessage para refletir o usuário autenticado
        chatMessage.setSender(username);

        // 1. Verificar se o usuário já está conectado (para evitar duplicidade na lista de ativos)
        if (sessionManager.isUserConnected(topic, username)) {
            System.out.println("User " + username + " is already connected to public chat. Not re-adding.");
            // Opcional: Enviar uma mensagem de erro específica de volta ao cliente
            // Se o usuário já está conectado, pode ser apenas um refresh de página, não necessariamente um erro.
            return;
        }

        // 2. Verificar se a sala pública está cheia
        if (!sessionManager.addUserToTopic(topic, username, sessionId)) {
            System.out.println("Join rejected for " + username + ". Topic " + topic + " is full.");
            // Enviar mensagem de erro de volta ao cliente que tentou entrar
            messagingTemplate.convertAndSendToUser(sessionId, "/queue/errors",
                    ChatMessage.builder().sender("System").content("O chat público está cheio. Tente novamente mais tarde.").messageType(MessageType.ERROR).status("ROOM_FULL").build());
            return;
        }

        // Se o usuário foi adicionado com sucesso, adicione-o aos atributos da sessão e envie a mensagem JOIN
        headerAccessor.getSessionAttributes().put("username", username); // Ainda útil para listener de desconexão
        headerAccessor.getSessionAttributes().put("topic", topic);

        System.out.println("User " + username + " successfully joined " + topic + ". Current users: " + sessionManager.getUsersCount(topic));

        // Envia a mensagem JOIN para todos os usuários no tópico
        messagingTemplate.convertAndSend(topic, chatMessage);
    }
}