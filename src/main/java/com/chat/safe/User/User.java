package com.chat.safe.User; // Certifique-se de que o pacote está correto

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id; // Usar esta anotação @Id
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document; // Importar
//import org.springframework.data.mongodb.core.mapping.Indexed; // Importar para índices
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "users") // Mapeia para a coleção 'users' no MongoDB
public class User implements UserDetails {

    @Id // Para MongoDB, o ID é tipicamente String ou ObjectId
    private String id; // Mudou para String para compatibilidade com o ID gerado pelo MongoDB

    @Indexed(unique = true) // Cria um índice único para o username
    private String username;

    private String password;

    // Métodos UserDetails permanecem os mesmos
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return List.of(new SimpleGrantedAuthority("ROLE_USER"));
    }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return true; }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return true; }
}