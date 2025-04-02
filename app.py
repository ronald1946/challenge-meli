from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta
import requests
from requests.exceptions import RequestException
import random
import os
from flasgger import Swagger
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

app = Flask(__name__)

# Config JWT
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Config Swagger
app.config['SWAGGER'] = {
    'title': 'API Pokemon Challenge Meli',
    'uiversion': 3
}
Swagger(app)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

# Endpoint para login
@app.route('/login', methods=['POST'])
def login():
    #Documentacion de la API en Swagger
    """
    Obtiene el BearerToken para consumo de API
    ---
    tags:
      - Autenticación
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Credenciales de acceso
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: test
            password:
              type: string
              example: 123456
    responses:
      200:
        description: Retorna el token de acceso para consumo de Endpoints
        examples:
          application/json:           
             "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
      400:
        description: 'Faltan campos username o password'
        examples:
          application/json:             
              'error': 'Faltan campos username o password'      
      401:
        description: 'Usuario o Contrasena Invalidos'
        examples:
          application/json:             
              'error': 'Usuario o Contrasena Invalidos'      
      500:
        description: 'Error inesperado'
        examples:
          application/json:             
              'error': 'Error inesperado'      
    """
    try:
        logging.info("Inicia solicitud de login")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        logging.debug(f"Datos recibidos - Username: {username}")

        # Validación de entrada
        if not username or not password:
            logging.warning("Faltan campos en la solicitud de login")
            return jsonify({'error': 'Faltan campos username o password'}), 400             

        if username == os.getenv("USERNAMEAPI") and password == os.getenv("PASSWORD"):
            logging.info("Login exitoso")
            access_token = create_access_token(identity=username,expires_delta=timedelta(minutes=5))
            return jsonify(access_token=access_token), 200
        else:
            logging.warning("Usuario y contrasena invalidos")
            return jsonify(msg='Usuario o Contrasena Invalidos'), 401
    except Exception as e:
        logging.exception("Error inesperado durante el login")
        return jsonify({'error': f'Error inesperado durante el login: {str(e)}'}), 500
    

#Endpoint Obtener tipo pokemon
@app.route('/pokemon/type/<string:name>', methods=['GET'])
@jwt_required()
def get_pokemon_types(name):
#Documentacion de la API en Swagger
    """
    Obtiene el tipo de Pokemon
    ---
    tags:
      - Types
    responses:
      200:
        description: Retorna el o los tipos del nombre de pokemon enviado
        examples:
          application/json:           
            name: "pikachu"
            types: [
            "electric"
            ]
           
      404:
        description: 'Pokemon no registrado en API'
        examples:
          application/json:             
              'error': 'Pokemon no registrado en API'
      503:
        description: 'Error al conectar con PokeAPI'
        examples:
          application/json:             
              'error': 'Error al conectar con PokéAPI'
      500:
        description: 'Error inesperado'
        examples:
          application/json:             
              'error': 'Error inesperado'      
    """
    try:
        #Consumo de API Pokemon
        logging.info(f"Obteniendo tipos de Pokemon para: {name}")
        response = requests.get(f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}")
        if response.status_code != 200:
            return jsonify({'error': 'Pokemon no registrado en API'}), 404

        data = response.json()
        types = [t['type']['name'] for t in data['types']]
        logging.info(f"Tipos encontrados para {name}: {types}")
        return jsonify({'name': name, 'types': types})
    except RequestException:
        logging.error("Error de conexión con PokeAPI")
        return jsonify({'error': 'Error al conectar con PokeAPI'}), 503
    except Exception as e:
        logging.exception("Error inesperado en get_pokemon_types")
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

#Endpont Obtener pokemon random por tipo
@app.route('/pokemon/type/random/<string:tipo>', methods=['GET'])
@jwt_required()
def get_random_pokemon_by_type(tipo):
#Documentacion de la API en Swagger
    """
    Obtiene un Pokemon random segun el tipo enviado
    ---
    tags:
      - Types
    responses:
      200:
        description: Retorna el nombre de un pokemon segun el tipo
        examples:
          application/json:             
              name: "charjabug"
      404:
        description: 'Error si: el tipo de Pokemon no se encuentra, o el tipo no tiene pokemones'
        examples:
          application/json:             
              'error': 'Tipo no encontrado'
      503:
        description: 'Error al conectar con PokeAPI'
        examples:
          application/json:             
              'error': 'Error al conectar con PokéAPI'
      500:
        description: 'Error inesperado'
        examples:
          application/json:             
              'error': 'Error inesperado'  
    """
    try:
        #Consumo de API pokemon
        logging.info(f"Obteniendo Pokemon random del tipo: {tipo}")
        response = requests.get(f"{POKEAPI_BASE_URL}/type/{tipo.lower()}")
        if response.status_code != 200:
            logging.warning(f"Tipo de Pokemon '{tipo}' no encontrado")
            return jsonify({'error': 'Tipo no encontrado'}), 404

        data = response.json()
        pokemons = data['pokemon']
        if not pokemons:
            return jsonify({'error': 'No hay Pokemon de ese tipo'}), 404

        selected = random.choice(pokemons)['pokemon']
        logging.info(f"Pokemon seleccionado: {selected['name']}")
        return jsonify({'nombre': selected['name']})
    except RequestException:
        logging.error("Error de conexión con PokéAPI")
        return jsonify({'error': 'Error al conectar con PokeAPI'}), 503
    except Exception as e:
        logging.exception("Error inesperado en get_random_pokemon_by_type")
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

#Endpoint obtener pokemon con el nombre mas largo
@app.route('/pokemon/type/longer/<string:tipo>', methods=['GET'])
@jwt_required()
def get_longer_name_pokemon_by_type(tipo):
    #Documentacion de la API en Swagger
    """
    Obtiene el Pokemon con el nombre más largo segun el tipo
    ---
    tags:
      - Types
    responses:
      200:
        description: Retorna el Pokemon con el nombre más largo segun el tipo
        examples:
          application/json:             
              name: "toxtricity-low-key-gmax"
      404:
        description: 'Error si: el tipo de Pokemon no se encuentra, o el tipo no tiene pokemones'
        examples:
          application/json:             
              'error': 'Tipo no encontrado'
      503:
        description: 'Error al conectar con PokeAPI'
        examples:
          application/json:             
              'error': 'Error al conectar con PokéAPI'
      500:
        description: 'Error inesperado'
        examples:
          application/json:             
              'error': 'Error inesperado'  
    """
    
    try:
        #Consumo de API Pokemon
        logging.info(f"Buscando Pokemon con nombre más largo del tipo: {tipo}")
        response = requests.get(f"{POKEAPI_BASE_URL}/type/{tipo.lower()}")
        if response.status_code != 200:
            logging.warning(f"Tipo de Pokemon '{tipo}' no encontrado")
            return jsonify({'error': 'Tipo no encontrado'}), 404

        data = response.json()
        pokemons = data['pokemon']
        if not pokemons:
            return jsonify({'error': 'No hay Pokémon de ese tipo'}), 404

        longer = max(pokemons, key=lambda p: len(p['pokemon']['name']))
        logging.info(f"Pokemon con nombre mas largo: {longer['pokemon']['name']}")
        return jsonify({'nombre': longer['pokemon']['name']})
    except RequestException:
        logging.error("Error de conexion con PokeAPI")
        return jsonify({'error': 'Error al conectar con PokéAPI'}), 503
    except Exception as e:
        logging.exception("Error inesperado en get_longer_name_pokemon_by_type")
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)