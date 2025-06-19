package com.chat.safe.Auth;

import com.chat.safe.User.User;
import com.chat.safe.User.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin("http://localhost:5500/index.html")
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/register")
    public ResponseEntity<String> registerUser(@RequestBody Map<String, String> payload) {
        String username = payload.get("username");
        String password = payload.get("password");

        if (username == null || username.isEmpty() || password == null || password.isEmpty()) {
            return ResponseEntity.badRequest().body("Username and password are required.");
        }

        if (userRepository.findByUsername(username).isPresent()) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body("Username is already taken.");
        }

        User newUser = User.builder()
                .username(username)
                .password(passwordEncoder.encode(password)) // Encripta a senha
                .build();
        userRepository.save(newUser);

        return ResponseEntity.ok("User registered successfully!");
    }

    // Para login, o Spring Security geralmente cuida disso com um filtro padrão para /login.
    // Você pode criar um endpoint /api/auth/login customizado se precisar de mais controle
    // sobre a resposta, mas para começar, o padrão é suficiente.
    // Um POST para /login com "username" e "password" no body funcionaria.
    // No entanto, para um chat de rede social, você provavelmente vai querer JWT ou Oauth2.
    // Por enquanto, manteremos simples e faremos o cliente enviar as credenciais no header para cada requisição segura.
}