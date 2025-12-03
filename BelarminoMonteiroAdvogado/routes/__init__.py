# -*- coding: utf-8 -*-
"""
==============================================================================
ARQUIVO POSSIVELMENTE OBSOLETO - NÃO UTILIZADO
==============================================================================

ATENÇÃO: Este arquivo (`routes/__init__.py`) parece conter uma implementação
antiga e duplicada da função `create_app` (Application Factory), que já existe
de forma mais completa no arquivo principal do projeto (`BelarminoMonteiroAdvogado/__init__.py`).

Este arquivo NÃO é importado ou utilizado pela aplicação principal (`main.py`)
e sua presença pode causar grande confusão. Ele inicializa suas próprias
instâncias de extensões (SQLAlchemy, Migrate, LoginManager), o que entraria
em conflito com as instâncias corretas do projeto.

A recomendação é REMOVER este arquivo para evitar problemas de manutenção.

As documentações e comentários abaixo foram apenas levemente ajustados para
clareza, mas o conteúdo do arquivo permanece como estava para análise.
Não se deve basear nenhuma nova implementação neste código.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime

# ATENÇÃO: Estas são instâncias locais e provavelmente em conflito com as globais.
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    """
    Application Factory: Cria e configura a instância da aplicação Flask.
    (Versão aparentemente obsoleta contida neste arquivo).
    """
    app = Flask(__name__)

    # --- 1. CONFIGURAÇÕES ---
    # Chave secreta para proteção de sessões e CSRF.
    # Em produção, DEVE ser carregada de uma variável de ambiente.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_belarmino_advocacia_2025_obsolete')
    
    # Configuração do Banco de Dados. Prefere a variável de ambiente DATABASE_URL,
    # caso contrário, usa um arquivo SQLite local.
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuração para upload de arquivos.
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/images/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Define um limite para o tamanho dos arquivos de upload (ex: 16MB).
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Garante que o diretório de uploads exista no momento da inicialização.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- 2. INICIALIZAÇÃO DE EXTENSÕES ---
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configura o Flask-Login.
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Rota para redirecionar usuários não autenticados.
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # --- 3. PROCESSADORES DE CONTEXTO (Variáveis Globais para Templates) ---
    @app.context_processor
    def inject_global_vars():
        """
        Injeta variáveis globais no contexto de todos os templates Jinja2.
        """
        # Importação tardia para evitar referência circular.
        from ..models import ThemeSettings, ConteudoGeral
        
        # Recupera configurações de tema do banco de dados.
        try:
            theme_settings = ThemeSettings.query.first()
            current_theme = theme_settings.theme if theme_settings else 'option1'
            
            # Recupera configurações gerais do site (título, telefone, etc).
            configs_db = ConteudoGeral.query.all()
            configs = {c.secao: c.conteudo for c in configs_db}
            
            # Garante um valor padrão para o título se o banco de dados estiver vazio.
            if 'site_titulo' not in configs: configs['site_titulo'] = 'Belarmino Monteiro Advogado'
            
        except Exception:
            # Fallback seguro caso o banco de dados não esteja pronto ou acessível.
            current_theme = 'option1'
            configs = {'site_titulo': 'Belarmino Monteiro Advogado'}

        return dict(
            now=datetime.now(),
            current_year=datetime.now().year,
            theme=current_theme,
            configs=configs
        )

    # --- 4. FUNÇÕES AUXILIARES PARA TEMPLATES ---
    
    def render_page(template_name_or_list, page_id=None, **context):
        """
        Função auxiliar para renderização de páginas, centralizando a lógica.
        (Esta é uma implementação local e não a global do projeto).
        """
        from flask import render_template
        return render_template(template_name_or_list, page_id=page_id, **context)
    
    # Disponibiliza a função 'render_page' globalmente nos templates.
    app.jinja_env.globals.update(render_page=render_page)
    
    def get_file_mtime(filename):
        """
        Função para versionamento de arquivos estáticos (Cache Busting).
        Retorna o tempo de modificação de um arquivo para forçar a atualização no navegador.
        """
        try:
            filepath = os.path.join(app.static_folder, filename)
            return int(os.path.getmtime(filepath))
        except OSError:
            # Retorna 0 se o arquivo não for encontrado, evitando que o template quebre.
            return 0
            
    app.jinja_env.globals.update(get_file_mtime=get_file_mtime)


    # --- 5. REGISTRO DE BLUEPRINTS (Módulos de Rotas) ---
    with app.app_context():
        # Importação tardia para evitar referência circular com os módulos de rotas.
        from .main_routes import main_bp
        from .auth_routes import auth_bp
        from .admin_routes import admin_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)

        # A chamada db.create_all() é geralmente desencorajada aqui.
        # Em um ambiente de produção, as migrações (Flask-Migrate) são o método preferido.
        # db.create_all()

    return app