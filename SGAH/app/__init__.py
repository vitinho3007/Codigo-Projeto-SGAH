import os
import logging

from flask import Flask, render_template


def create_app():
    app = Flask(__name__, template_folder='views')
    app.secret_key = os.environ.get('SECRET_KEY', 'chave-secreta-so-para-desenvolvimento')
    app.logger.setLevel(logging.INFO)

    from app.controllers.auth_controller import auth_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.suprimento_controller import suprimento_bp
    from app.controllers.abrigo_controller import abrigo_bp
    from app.controllers.operacao_controller import operacao_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(suprimento_bp)
    app.register_blueprint(abrigo_bp)
    app.register_blueprint(operacao_bp)

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template('erro.html', codigo=404,
                               titulo='Página não encontrada',
                               mensagem='O endereço que você tentou acessar não existe.'), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        app.logger.error("Erro interno: %s", erro)
        return render_template('erro.html', codigo=500,
                               titulo='Algo deu errado',
                               mensagem='Aconteceu um erro no servidor. Tente de novo em instantes.'), 500

    return app
