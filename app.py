import os
from flask import Flask, send_from_directory, request, make_response
from flask_cors import CORS
from config import Config
from controllers.auth_controller import auth_bp
from controllers.api_controller import api_bp
from models.user_model import Database

def create_app():
    # Inicializa Flask apontando os arquivos estáticos para o diretório atual
    app = Flask(__name__, static_folder='.', static_url_path='')
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Configuração de cookies de sessão para comunicação entre portas locais
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Permitir em HTTP local

    # Configuração robusta de CORS para suportar o Live Server (:5500) e portas locais
    allowed_origins = [
        Config.FRONTEND_URL,
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5000",
        "http://localhost:5000"
    ]
    
    CORS(app, supports_credentials=True, origins=allowed_origins)

    # Middleware de contingência para garantir cabeçalhos CORS em todas as respostas (inclusive OPTIONS)
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

    # Registra os Blueprints de autenticação e jogo
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Rota raiz: serve o index.html caso o backend seja acessado diretamente
    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')

    # Inicializa verificação de banco de dados
    Database.get_db()

    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 70)
    print("SKIN TRADER SIMULATOR - SERVIDOR BACKEND FLASK ATIVO")
    print("=" * 70)
    print(f"Backend API:   http://127.0.0.1:{Config.PORT}")
    print(f"Frontend App:  {Config.FRONTEND_URL} (Live Server)")
    print(f"MongoDB URI:   {Config.MONGODB_URI}")
    print(f"GitHub OAuth:  {'Configurado' if Config.GITHUB_CLIENT_ID and not Config.GITHUB_CLIENT_ID.startswith('seu_') else 'Modo Demonstracao / Teste Ativo'}")
    print("=" * 70)
    print("Como executar:")
    print("   1. Backend:  python app.py (porta 5000)")
    print("   2. Frontend: Abrir index.html no VS Code com Live Server (porta 5500)")
    print("=" * 70 + "\n")
    app.run(host='127.0.0.1', port=Config.PORT, debug=Config.DEBUG)
