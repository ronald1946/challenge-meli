API REST - Pokemon Challenge Meli

Una API REST construida con Flask que permite interactuar con la PokeAPI para obtener información sobre Pokémon por tipo, seleccionar uno aleatorio, y obtener el de nombre más largo. Incluye autenticación JWT.

🚀 Características

Autenticación con JWT (→ endpoint /login)

Integración con PokéAPI externa

Documentación interactiva con Swagger (accesible en /apidocs)

Trazabilidad completa mediante logging

⚙️ Instalación

# 1. Clonar el repositorio
$ git clone https://github.com/ronald1946/challenge-meli.git
$ cd pokemon-api-meli

# 2. Construir Contenedor
$ docker build --force-rm -t PokemonTypeAPI/latest . --no-cache

# 3. Iniciar Contenedor con variables de Entorno
$ docker run --env=JWT_SECRET_KEY=contratado-meli-2025 --env=USERNAMEAPI=ronald --env=PASSWORD=iam_meli -p 5010:5000 -d --name PokemonTypeAPI PokemonTypeAPI/latest:latest

🔒 Autenticación JWT

Endpoint

POST /login

Body esperado

{
  "username": "test",
  "password": "123456"
}

Respuesta

{
  "access_token": "<JWT Token>"
}

Incluye el token en las peticiones posteriores usando el header:

Authorization: Bearer <token>

🤖 Endpoints Pokémon

GET /pokemon/type/<name> → Obtiene los tipos de un Pokémon

GET /pokemon/type/random/<tipo> → Devuelve un Pokémon aleatorio del tipo indicado

GET /pokemon/type/longer/<tipo> → Devuelve el Pokémon con el nombre más largo de un tipo

🔍 Documentación Swagger

Disponible en:

http://localhost:5010/apidocs

🌐 API Externa utilizada

https://pokeapi.co/

🙏 Agradecimientos

Este proyecto fue desarrollado como parte de un challenge técnico para Mercado Libre.

© 2025
