import requests
from flask import Flask, jsonify

# AULA CONSUMINDO API DO PRISCO 12/09/2024

# Defina a URL base da API do TMDB
base_url = "https://api.themoviedb.org/3"
# Defina a sua chave da API do TMDB
api_key = "489144e396e06c019e8c6590578e15db"
# Defina o endpoint da API que você deseja consumir
endpoint = "/movie/popular"

app = Flask(__name__)

@app.route('/')
def home():
    # Construa a URL completa para a requisição
    url = f"{base_url}{endpoint}?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return "Erro ao consumir a API do TMDB"

if __name__ == "__main__":
    app.run(debug=True)
