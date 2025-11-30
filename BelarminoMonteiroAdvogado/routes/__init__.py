# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime

# Inicialização das Extensões (Global)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """
    Application Factory: Cria e configura a instância da aplicação Flask.
    """
    app = Flask(__name__)

    # --- 1. CONFIGURAÇÕES ---
    # Chave secreta para sessões (use variável de ambiente em produção)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_belarmino_advocacia_2025')
    
    # Banco de Dados (SQLite para dev, adaptável para PostgreSQL)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Limite de Upload (ex: 16MB)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Garante que a pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- 2. INICIALIZAÇÃO DE EXTENSÕES ---
    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Rota para redirecionar se não logado
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # --- 3. CONTEXT PROCESSORS (Variáveis Globais para Templates) ---
    @app.context_processor
    def inject_global_vars():
        # Importar modelos aqui para evitar ciclo
        from .models import ThemeSettings, ConteudoGeral
        
        # Recupera configurações de tema
        try:
            theme_settings = ThemeSettings.query.first()
            current_theme = theme_settings.theme if theme_settings else 'option1'
            
            # Recupera configurações gerais do site (título, telefone, etc)
            # Assumindo que você tem uma tabela ConteudoGeral chave-valor
            configs_db = ConteudoGeral.query.all()
            configs = {c.secao: c.conteudo for c in configs_db}
            
            # Garante valores padrão se o banco estiver vazio
            if 'site_titulo' not in configs: configs['site_titulo'] = 'Belarmino Monteiro Advogado'
            
        except Exception:
            # Fallback seguro se o banco não estiver pronto
            current_theme = 'option1'
            configs = {}

        return dict(
            now=datetime.now(),
            current_year=datetime.now().year,
            theme=current_theme,
            configs=configs
        )

    # --- 4. FUNÇÃO AUXILIAR DE RENDERIZAÇÃO (Theme-Aware) ---
    # Injetamos essa função no app para ser usada nas rotas
    def render_page(template_name_or_list, page_id=None, **context):
        from flask import render_template
        # Aqui você pode adicionar lógica global antes de renderizar
        return render_template(template_name_or_list, page_id=page_id, **context)
    
    # Disponibiliza a função 'render_page' globalmente (opcional, ou importe direto nas rotas)
    app.jinja_env.globals.update(render_page=render_page)
    
    # Função para versionamento de arquivos estáticos (Cache Busting)
    def get_file_mtime(filename):
        try:
            filepath = os.path.join(app.static_folder, filename)
            return int(os.path.getmtime(filepath))
        except OSError:
            return 0
            
    app.jinja_env.globals.update(get_file_mtime=get_file_mtime)


    # --- 5. REGISTRO DE BLUEPRINTS (Rotas) ---
    with app.app_context():
        # Importação tardia para evitar Circular Import
        from .routes.main_routes import main_bp
        from .routes.auth_routes import auth_bp
        from .routes.admin_routes import admin_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)

        # Criação das tabelas (Apenas para Dev/SQLite rápido)
        # Em produção, use Flask-Migrate (flask db upgrade)
        # db.create_all()

    return app