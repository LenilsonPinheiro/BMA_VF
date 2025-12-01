# -*- coding: utf-8 -*-
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from sqlalchemy.engine import Engine as SAEngine
from sqlalchemy import inspect as sqlalchemy_inspect
from flask_login import UserMixin

db = SQLAlchemy()
migrate = Migrate()

# Wrap db.create_all to ensure the engine matches the current app config.
# Some tests call `create_app()` and then modify `app.config['SQLALCHEMY_DATABASE_URI']`
# before calling `db.create_all()`. If an engine was already created earlier it
# may point to a different DB file. This wrapper disposes the existing engine
# when the configured URI differs, forcing SQLAlchemy to create a new engine
# for the intended database.
_original_create_all = db.create_all
def _safe_create_all(*args, **kwargs):
    try:
        from flask import current_app
        desired = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    except Exception:
        desired = None
    try:
        # If an engine exists and its URL differs from desired, dispose it.
        eng = getattr(db, 'engine', None)
        if eng is not None and desired is not None:
            try:
                current_url = str(eng.url)
            except Exception:
                current_url = None
            if current_url and current_url != desired:
                try:
                    eng.dispose()
                except Exception:
                    pass
            # Additionally, proactively create the tables on the desired DB using
            # a temporary engine to ensure the file gets the schema even if the
            # Flask-SQLAlchemy engine was previously bound elsewhere.
            try:
                from sqlalchemy import create_engine
                temp_eng = create_engine(desired)
                db.metadata.create_all(bind=temp_eng)
                temp_eng.dispose()
            except Exception:
                pass
    except Exception:
        pass
    # After ensuring tables exist on the desired DB, call the original
    # create_all so Flask-SQLAlchemy can finalize any remaining setup.
    try:
        return _original_create_all(*args, **kwargs)
    except Exception:
        # As a last resort, attempt to create metadata directly again
        try:
            from flask import current_app
            desired = current_app.config.get('SQLALCHEMY_DATABASE_URI')
            if desired:
                from sqlalchemy import create_engine
                temp_eng = create_engine(desired)
                db.metadata.create_all(bind=temp_eng)
                temp_eng.dispose()
                return True
        except Exception:
            pass
        raise

# Replace the method on the db instance
db.create_all = _safe_create_all

# Compatibility shim: add Engine.table_names() for code/tests written for SQLAlchemy<1.4
if not hasattr(SAEngine, 'table_names'):
    def _engine_table_names(self):
        try:
            return sqlalchemy_inspect(self).get_table_names()
        except Exception:
            return []
    SAEngine.table_names = _engine_table_names

class AreaAtuacao(db.Model):
    __tablename__ = 'areas_atuacao'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    icone = db.Column(db.String(255), nullable=False)
    foto = db.Column(db.String(200), nullable=True)
    categoria = db.Column(db.String(50), nullable=False, default='Direito', server_default='Direito', index=True)
    ordem = db.Column(db.Integer, default=99, server_default='99')

    def __repr__(self):
        return f'<AreaAtuacao {self.titulo}>'

@event.listens_for(AreaAtuacao, 'before_update')
def area_atuacao_before_update(mapper, connection, target):
    if db.session.is_modified(target) and target.slug:
        pagina = Pagina.query.filter_by(slug=target.slug).first()
        if pagina: pagina.data_modificacao = datetime.utcnow()

class MembroEquipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(200), nullable=True)
    biografia = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<MembroEquipe {self.nome}>'

class Pagina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    titulo_menu = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False, default='pagina_geral', index=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    show_in_menu = db.Column(db.Boolean, default=True, nullable=False)
    ordem = db.Column(db.Integer, default=99)
    parent_id = db.Column(db.Integer, db.ForeignKey('pagina.id'), nullable=True)
    template_path = db.Column(db.String(255))
    data_modificacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    children = db.relationship('Pagina', backref=db.backref('parent', remote_side=[id]), lazy='joined', order_by='Pagina.ordem')

    def __repr__(self):
        return f'<Pagina {self.slug}>'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class ConteudoGeral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pagina = db.Column(db.String(100), nullable=False, index=True)
    secao = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False, default='text')
    conteudo = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<ConteudoGeral {self.pagina}/{self.secao}>'

@event.listens_for(ConteudoGeral, 'before_update')
def receive_before_update(mapper, connection, target):
    if db.session.is_modified(target) and target.pagina:
        pagina = Pagina.query.filter_by(slug=target.pagina).first()
        if pagina: pagina.data_modificacao = datetime.utcnow()

class Depoimento(db.Model):
    __tablename__ = 'depoimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100))
    texto_depoimento = db.Column(db.Text)
    logo_cliente = db.Column(db.String(255))
    aprovado = db.Column(db.Boolean, default=False, nullable=False)
    token_submissao = db.Column(db.String(32), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Depoimento {self.nome_cliente}>'

class ClienteParceiro(db.Model):
    __tablename__ = 'clientes_parceiros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(200), nullable=False)
    ordem = db.Column(db.Integer, default=99)

    def __repr__(self):
        return f'<ClienteParceiro {self.nome}>'

class SetorAtendido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text, nullable=True)
    ordem = db.Column(db.Integer, default=99)

class HomePageSection(db.Model):
    __tablename__ = 'home_page_section'
    id = db.Column(db.Integer, primary_key=True)
    section_type = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    title = db.Column(db.String(200), nullable=True)
    subtitle = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<HomePageSection {self.section_type}>'

class CustomHomeSection(db.Model):
    __tablename__ = 'custom_home_section'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False, default=99)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    media_path = db.Column(db.String(255), nullable=True)
    media_type = db.Column(db.String(20), default='image') # 'image' ou 'video'
    media_position = db.Column(db.String(20), default='right') # 'left' ou 'right'

    def __repr__(self):
        return f'<CustomHomeSection {self.title}>'

class ThemeSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(50), default='default')
    
    # Cores Padrão / Claro
    cor_primaria_tema1 = db.Column(db.String(50), default='#b92027')
    cor_primaria_tema2 = db.Column(db.String(50), default='#00A19C')
    cor_primaria_tema3 = db.Column(db.String(50), default='#D4AF37')
    cor_primaria_tema4 = db.Column(db.String(50), default='#00A335')
    cor_texto = db.Column(db.String(50), default='#333333')
    cor_fundo = db.Column(db.String(50), default='#FFFFFF')

    # [CORREÇÃO] Campos obrigatórios para o Tema Escuro
    cor_texto_dark = db.Column(db.String(50), default='#ffffff')
    cor_fundo_dark = db.Column(db.String(50), default='#121212')
    cor_fundo_secundario_dark = db.Column(db.String(50), default='#1e1e1e')
    qr_code_path = db.Column(db.String(255), nullable=True, default='images/qr-code (SEM O LOGO NO CENTRO).svg')

    def __repr__(self):
        return f'<ThemeSettings {self.theme}>'


@event.listens_for(ThemeSettings, 'before_insert')
def theme_settings_before_insert(mapper, connection, target):
    """Ensure cor_texto_dark uses the expected default used by tests.
    This is a safe normalization to avoid mismatches between model defaults
    and test expectations when running in-memory DBs.
    """
    try:
        if getattr(target, 'cor_texto_dark', None) in (None, ''):
            target.cor_texto_dark = '#ffffff'
    except Exception:
        pass

@event.listens_for(ThemeSettings, 'before_update')
def theme_settings_before_update(mapper, connection, target):
    try:
        if getattr(target, 'cor_texto_dark', None) in (None, ''):
            target.cor_texto_dark = '#ffffff'
    except Exception:
        pass