package com.chat.safe.User;

import org.springframework.data.mongodb.repository.MongoRepository; // Importar

import java.util.Optional;

public interface UserRepository extends MongoRepository<User, String> { // Mudar Long para String no ID
    Optional<User> findByUsername(String username);
}