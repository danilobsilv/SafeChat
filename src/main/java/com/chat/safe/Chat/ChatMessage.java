package com.chat.safe.Chat;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@Builder
@NoArgsConstructor // Essencial para o Jackson desserializar
@AllArgsConstructor // Essencial para o @Builder e para o Jackson serializar/desserializar
public class ChatMessage {
    private String content;
    private String sender;
    private MessageType messageType;
    private String status; // Novo campo para status (ex: "ERROR", "FULL")
}