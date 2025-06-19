package com.chat.safe.WebSocket;

import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class WebSocketSessionManager {

    // Mapa para rastrear usuários em cada tópico/sala
    // Chave: Nome do Tópico (ex: "/topic/public", "/topic/private.user1.user2")
    // Valor: Set de usernames conectados a esse tópico
    private final Map<String, Set<String>> connectedUsersByTopic = new ConcurrentHashMap<>();

    // Mapa para rastrear qual sessão STOMP pertence a qual usuário (para desconexão, agora por username)
    // Chave: ID da sessão STOMP
    // Valor: Username
    private final Map<String, String> sessionToUserMap = new ConcurrentHashMap<>();


    // Podemos ter diferentes limites para tópicos públicos e privados.
    // Para simplificar, mantenha o limite de 2 para o chat público (se ele ainda existir)
    // Chats privados não terão um limite fixo aqui, eles são 1:1 por natureza
    private final int MAX_USERS_PUBLIC_TOPIC = 2; // Exemplo para o chat público

    /**
     * Adiciona um usuário a um tópico.
     * @param topic O tópico/sala.
     * @param username O nome de usuário a ser adicionado.
     * @param sessionId O ID da sessão STOMP.
     * @return true se o usuário foi adicionado com sucesso, false se a sala estiver cheia (apenas para tópicos públicos).
     */
    public boolean addUserToTopic(String topic, String username, String sessionId) {
        // Se o tópico for privado, não aplicamos limite de usuários aqui.
        // A lógica de "chat reservado" é no controller (verificar amizade).
        if (topic.startsWith("/topic/private.")) { // Exemplo de prefixo para tópicos privados
             Set<String> users = connectedUsersByTopic.computeIfAbsent(topic, k -> Collections.synchronizedSet(new HashSet<>()));
             users.add(username);
             sessionToUserMap.put(sessionId, username);
             System.out.println("User " + username + " added to private topic " + topic + " (Session ID: " + sessionId + "). Current users: " + users.size());
             return true;
        }

        // Para tópicos públicos (como /topic/public)
        Set<String> users = connectedUsersByTopic.computeIfAbsent(topic, k -> Collections.synchronizedSet(new HashSet<>()));

        synchronized (users) { // Sincroniza para evitar condições de corrida
            if (users.size() >= MAX_USERS_PUBLIC_TOPIC && !users.contains(username)) {
                // Sala cheia E usuário não está na sala (evita rejeitar o mesmo usuário que já está conectado)
                return false;
            }
            users.add(username);
            sessionToUserMap.put(sessionId, username);
            System.out.println("User " + username + " added to topic " + topic + " (Session ID: " + sessionId + "). Current users: " + users.size());
            return true;
        }
    }

    /**
     * Remove um usuário de um tópico e da sessão mapeada.
     * @param sessionId O ID da sessão STOMP que desconectou.
     * @return O username removido, ou null se não for encontrado.
     */
    public String removeUserFromSession(String sessionId) {
        String username = sessionToUserMap.remove(sessionId); // Remove o mapeamento de sessão para usuário

        if (username != null) {
            // Itera sobre todos os tópicos para remover o usuário
            connectedUsersByTopic.forEach((topic, users) -> {
                synchronized (users) {
                    if (users.remove(username)) {
                        System.out.println("User " + username + " removed from topic " + topic + ". Current users: " + users.size());
                    }
                }
            });
        }
        return username;
    }

    /**
     * Obtém o número atual de usuários em um tópico.
     * @param topic O tópico/sala.
     * @return O número de usuários.
     */
    public int getUsersCount(String topic) {
        Set<String> users = connectedUsersByTopic.get(topic);
        return (users != null) ? users.size() : 0;
    }

    /**
     * Verifica se um usuário já está conectado em um tópico.
     * @param topic O tópico/sala.
     * @param username O nome de usuário a ser verificado.
     * @return true se o usuário já estiver conectado, false caso contrário.
     */
    public boolean isUserConnected(String topic, String username) {
        Set<String> users = connectedUsersByTopic.get(topic);
        return users != null && users.contains(username);
    }
}