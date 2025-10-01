from flask import Flask

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    """
    app = Flask(__name__)


    # Importa o blueprint de rotas
    from .routes.resumidor_routes import resumidor_bp

    # Registra o blueprint na aplicação
    app.register_blueprint(resumidor_bp)

    return app