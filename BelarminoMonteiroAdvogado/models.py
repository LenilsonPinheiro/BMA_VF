# -*- coding: utf-8 -*-
"""
==============================================================================
Definição dos Modelos de Dados (SQLAlchemy)
==============================================================================

Este arquivo contém a definição de todos os modelos de banco de dados da
aplicação, utilizando a extensão Flask-SQLAlchemy. Cada classe neste arquivo
representa uma tabela no banco de dados e define suas colunas, relacionamentos
e comportamentos.

Modelos Principais:
-------------------
- **User:** Representa um usuário administrador com credenciais para acessar o
        painel de controle.
- **Pagina:** Modelo flexível para criar páginas de conteúdo dinâmico,
          controlando sua exibição, ordem e hierarquia no menu.
- **AreaAtuacao:** Define os serviços jurídicos oferecidos pelo escritório.
- **MembroEquipe:** Armazena informações sobre os advogados e outros membros
               da equipe.
- **ConteudoGeral:** Um modelo chave-valor genérico para armazenar qualquer
                 tipo de conteúdo (textos, links de imagens, configurações)
                 associado a uma página ou seção.
- **Depoimento:** Armazena depoimentos de clientes.
- **ClienteParceiro:** Gerencia os logos e links de clientes ou parceiros.
- **HomePageSection:** Controla a visibilidade e ordem das seções na página
                     inicial.
- **ThemeSettings:** Armazena as configurações de design, como o tema ativo e
                 a paleta de cores.

Além dos modelos, este arquivo também inicializa as instâncias `db`
(SQLAlchemy) and `migrate` (Flask-Migrate) e inclui lógica de compatibilidade
e listeners de eventos para garantir a integridade dos dados e o funcionamento
correto de funcionalidades específicas.
"""
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
    """
    Wrapper robusto para `db.create_all` que garante a criação de tabelas
    no banco de dados correto, especialmente em ambientes de teste dinâmicos.

    Problema Resolvido:
    --------------------
    Em testes, a URI do banco de dados (`SQLALCHEMY_DATABASE_URI`) é frequentemente
    modificada após a criação da aplicação. O engine padrão do Flask-SQLAlchemy
    pode permanecer "preso" ao banco de dados original, fazendo com que
    `db.create_all()` opere no arquivo errado.

    Estratégia:
    -----------
    1.  **Verificação de URI:** Compara a URI do engine atual com a URI
        desejada no `current_app.config`.
    2.  **Descarte de Engine:** Se as URIs forem diferentes, o engine existente
        é descartado (`dispose()`), forçando o SQLAlchemy a criar um novo na
        próxima operação.
    3.  **Criação Proativa:** Tenta criar as tabelas diretamente no banco de
        dados de destino usando um engine temporário. Isso serve como uma
        garantia de que o schema seja aplicado corretamente.
    4.  **Fallback:** Se a chamada original a `db.create_all()` falhar,
        uma última tentativa de criação de metadados é feita antes de
        relançar a exceção original.
    """
    try:
        from flask import current_app
        desired_db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        app_context_available = True
    except RuntimeError: # Working outside of application context
        desired_db_uri = None
        app_context_available = False
        
    if app_context_available and current_app:
        current_app.logger.debug(f"[_safe_create_all] Desired DB URI: {desired_db_uri}")

    try:
        eng = getattr(db, 'engine', None)
        if eng is not None and desired_db_uri is not None:
            try:
                current_url = str(eng.url)
            except Exception as e:
                current_url = None
                if app_context_available:
                    current_app.logger.debug(f"[_safe_create_all] Não foi possível obter a URL do engine atual: {e}")
            
            if current_url and current_url != desired_db_uri:
                if app_context_available:
                    current_app.logger.info(f"[_safe_create_all] URI do engine diferente. Descartando engine existente. "
                                            f"Atual: {current_url}, Desejado: {desired_db_uri}")
                try:
                    eng.dispose()
                except Exception as e:
                    if app_context_available:
                        current_app.logger.warning(f"[_safe_create_all] Erro ao descartar engine existente: {e}")
            
            # Proativamente tenta criar tabelas no DB desejado usando um engine temporário.
            # Isso garante que o arquivo do DB receba o schema, mesmo se o engine principal
            # do Flask-SQLAlchemy estiver ligado a outro lugar.
            try:
                from sqlalchemy import create_engine
                temp_eng = create_engine(desired_db_uri)
                db.metadata.create_all(bind=temp_eng)
                temp_eng.dispose()
                if app_context_available:
                    current_app.logger.debug(f"[_safe_create_all] Tabelas criadas proativamente no DB em '{desired_db_uri}'.")
            except Exception as e:
                if app_context_available:
                    current_app.logger.warning(f"[_safe_create_all] Erro ao criar tabelas proativamente no DB: {e}")
        elif app_context_available:
            current_app.logger.debug("[_safe_create_all] Nenhum engine existente ou URI desejada não definida, pulando descarte/criação proativa.")

    except Exception as e:
        if app_context_available:
            current_app.logger.error(f"[_safe_create_all] Erro inesperado na lógica de gerenciamento do engine: {e}")

    # Após garantir que as tabelas existam no DB desejado, chama o `create_all` original
    # para que o Flask-SQLAlchemy finalize qualquer configuração restante.
    try:
        return _original_create_all(*args, **kwargs)
    except Exception as e:
        if app_context_available:
            current_app.logger.warning(f"[_safe_create_all] Falha na chamada original de db.create_all(): {e}")
        # Como último recurso, tenta criar o metadata diretamente novamente
        try:
            if desired_db_uri:
                from sqlalchemy import create_engine
                temp_eng = create_engine(desired_db_uri)
                db.metadata.create_all(bind=temp_eng)
                temp_eng.dispose()
                if app_context_available:
                    current_app.logger.info(f"[_safe_create_all] db.create_all() finalizado via fallback direto para metadata.")
                return True
        except Exception as fallback_e:
            if app_context_available:
                current_app.logger.error(f"[_safe_create_all] Erro crítico no fallback de db.create_all(): {fallback_e}")
            # Se tudo falhar, relança o erro original para que a exceção não seja engolida
            raise e
        raise # Relaunch the original exception if fallback also fails

# Replace the method on the db instance
db.create_all = _safe_create_all

# Compatibility shim: add Engine.table_names() for code/tests written for SQLAlchemy<1.4
if not hasattr(SAEngine, 'table_names'):
    def _engine_table_names(self):
        """
        Adiciona compatibilidade para `engine.table_names()` em versões mais recentes do SQLAlchemy.
        Para versões do SQLAlchemy < 1.4, `engine.table_names()` era um método direto.
        A partir de 1.4, deve-se usar `inspect(engine).get_table_names()`.
        Este shim permite que códigos e testes antigos continuem funcionando.
        """
        try:
            return sqlalchemy_inspect(self).get_table_names()
        except Exception as e:
            # Fallback: tenta ler nomes de tabelas do dialeto se possível
            try:
                from flask import current_app
                current_app.logger.warning(f"[_engine_table_names] Erro ao usar inspect(). Tentando fallback via dialeto: {e}")
                return list(self.dialect.get_table_names(self))
            except Exception as fallback_e:
                from flask import current_app
                current_app.logger.error(f"[_engine_table_names] Erro no fallback de dialeto para get_table_names: {fallback_e}")
                return []
    SAEngine.table_names = _engine_table_names

class AreaAtuacao(db.Model):
    """
    Modelo para representar uma área de atuação jurídica do escritório.
    Define as características de um serviço oferecido, como título, descrição,
    ícone e ordem de exibição, e está vinculada a uma página no site.
    """
    __tablename__ = 'areas_atuacao' # Nome da tabela no banco de dados
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True,
                     comment="Identificador único e amigável para URLs (ex: 'direito-civil').")
    titulo = db.Column(db.String(100), nullable=False,
                       comment="Título exibido da área de atuação (ex: 'Direito Civil').")
    descricao = db.Column(db.String(255), nullable=False,
                          comment="Breve descrição da área, para uso em listagens ou resumos.")
    icone = db.Column(db.String(255), nullable=False,
                      comment="Classe de ícone (ex: 'bi-briefcase' para Bootstrap Icons).")
    foto = db.Column(db.String(200), nullable=True,
                     comment="Caminho do arquivo da imagem ou foto associada à área.")
    categoria = db.Column(db.String(50), nullable=False, default='Direito', server_default='Direito', index=True,
                         comment="Categoria geral da área (ex: 'Direito', 'Serviço').")
    ordem = db.Column(db.Integer, default=99, server_default='99',
                     comment="Número para definir a ordem de exibição (menor valor primeiro).")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<AreaAtuacao {self.titulo}>'

@event.listens_for(AreaAtuacao, 'before_update')
def area_atuacao_before_update(mapper, connection, target):
    """
    Listener para o evento 'before_update' do modelo AreaAtuacao.
    Atualiza a 'data_modificacao' da página associada quando a área de atuação é modificada,
    garantindo que o cache da página seja invalidado, se necessário.
    """
    from flask import current_app # Importa aqui para evitar import circular
    if db.session.is_modified(target) and target.slug:
        pagina = Pagina.query.filter_by(slug=target.slug).first()
        if pagina:
            pagina.data_modificacao = datetime.utcnow()
            current_app.logger.debug(f"Atualizando data_modificacao para a página '{pagina.slug}' devido à modificação da Área de Atuação.")

class MembroEquipe(db.Model):
    """
    Modelo para representar um membro da equipe do escritório.
    Armazena informações como nome, cargo, foto e uma breve biografia.
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, comment="Nome completo do membro da equipe.")
    cargo = db.Column(db.String(100), nullable=False, comment="Cargo ou especialidade do membro (ex: 'Advogado', 'Paralegal').")
    foto = db.Column(db.String(200), nullable=True, comment="Caminho do arquivo da foto de perfil do membro.")
    biografia = db.Column(db.Text, nullable=True, comment="Biografia detalhada do membro da equipe.")
    ordem = db.Column(db.Integer, default=99, server_default='99',
                     comment="Número para definir a ordem de exibição na lista de equipe (menor valor primeiro).")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<MembroEquipe {self.nome}>'

class Pagina(db.Model):
    """
    Modelo para gerenciar páginas dinâmicas do site.
    Permite criar páginas, sub-páginas, grupos de menu e definir seu comportamento
    (ativo, visível no menu, ordem, template a ser usado).
    """
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True,
                     comment="Identificador único da página para URLs amigáveis.")
    titulo_menu = db.Column(db.String(100), nullable=False,
                            comment="Título da página exibido nos menus de navegação.")
    tipo = db.Column(db.String(50), nullable=False, default='pagina_geral', index=True,
                     comment="Tipo da página (ex: 'pagina_geral', 'servico', 'grupo_menu').")
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True,
                      comment="Indica se a página está ativa e visível no site.")
    show_in_menu = db.Column(db.Boolean, default=True, nullable=False,
                             comment="Indica se a página deve ser exibida nos menus de navegação.")
    ordem = db.Column(db.Integer, default=99,
                     comment="Número para definir a ordem de exibição em menus ou listagens.")
    parent_id = db.Column(db.Integer, db.ForeignKey('pagina.id'), nullable=True,
                          comment="ID da página pai, para criar hierarquias de menu.")
    template_path = db.Column(db.String(255), comment="Caminho do template Jinja2 a ser usado para renderizar esta página.")
    data_modificacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                 comment="Timestamp da última modificação da página.")
    
    # Relacionamento de auto-referência para páginas aninhadas (menu hierárquico)
    children = db.relationship('Pagina', backref=db.backref('parent', remote_side=[id]), lazy='joined', order_by='Pagina.ordem')

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<Pagina {self.slug}>'

class User(db.Model, UserMixin):
    """
    Modelo para usuários administradores, usado para autenticação e acesso ao painel.
    Armazena o nome de usuário e um hash seguro da senha.
    Herda de `UserMixin` para integração com `Flask-Login`.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment="Nome de usuário único para login.")
    password_hash = db.Column(db.String(256), nullable=False, comment="Hash seguro da senha do usuário, gerado por werkzeug.security.")

    def set_password(self, password: str):
        """
        Define a senha do usuário, gerando um hash seguro e armazenando-o.

        Args:
            password (str): A senha em texto plano a ser hashada.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida em texto plano corresponde ao hash armazenado.

        Args:
            password (str): A senha em texto plano a ser verificada.

        Returns:
            bool: True se as senhas coincidirem, False caso contrário.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<User {self.username}>'

class ConteudoGeral(db.Model):
    """
    Modelo chave-valor para armazenar qualquer tipo de conteúdo dinâmico.

    Esta é uma das tabelas mais importantes, pois permite que o conteúdo de
    quase todo o site seja editável através do painel de administração sem
    a necessidade de alterar o código. Funciona como um grande dicionário
    persistente.

    Exemplos de uso:
    - `pagina='home', secao='hero_title', conteudo='Bem-vindo ao nosso site'`
    - `pagina='configuracoes_gerais', secao='logo_path', conteudo='/static/img/logo.png'`
    - `pagina='sobre-nos', secao='meta_description', conteudo='Conheça nossa história.'`
    """
    id = db.Column(db.Integer, primary_key=True)
    pagina = db.Column(db.String(100), nullable=False, index=True,
                       comment="Slug da página ou identificador de grupo ao qual o conteúdo pertence (ex: 'home', 'sobre-nos', 'configuracoes_gerais').")
    secao = db.Column(db.String(100), nullable=False,
                      comment="Identificador único da seção de conteúdo dentro da página/grupo (ex: 'meta_title', 'hero_text', 'logo_principal').")
    field_type = db.Column(db.String(50), nullable=False, default='text',
                            comment="Tipo de campo para renderização no admin (ex: 'text', 'textarea', 'image', 'color', 'boolean').")
    conteudo = db.Column(db.Text, nullable=False,
                        comment="O conteúdo real armazenado, que pode ser texto, URL de imagem, HTML, valor booleano, etc.")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<ConteudoGeral {self.pagina}/{self.secao}>'

@event.listens_for(ConteudoGeral, 'before_update')
def receive_before_update(mapper, connection, target):
    """
    Listener para o evento 'before_update' do modelo ConteudoGeral.
    Quando um item de ConteudoGeral é modificado, este listener verifica se a `pagina`
    associada é um slug de uma `Pagina` existente. Se for, a `data_modificacao`
    da `Pagina` correspondente é atualizada. Isso é útil para mecanismos de cache,
    indicando que o conteúdo da página foi alterado.
    """
    from flask import current_app # Importa aqui para evitar import circular e garantir o contexto da app
    if db.session.is_modified(target) and target.pagina:
        # Verifica se 'target.pagina' corresponde a um slug de uma Página real
        # para evitar atualização desnecessária de páginas que não são gerenciadas.
        if Pagina.query.filter_by(slug=target.pagina).first():
            pagina = Pagina.query.filter_by(slug=target.pagina).first()
            if pagina:
                pagina.data_modificacao = datetime.utcnow()
                current_app.logger.debug(f"Atualizando data_modificacao para a página '{pagina.slug}' devido à modificação do ConteudoGeral '{target.secao}'.")
        else:
            current_app.logger.debug(f"ConteudoGeral para '{target.pagina}' alterado, mas nenhuma Página correspondente encontrada para atualizar data_modificacao.")

class Depoimento(db.Model):
    """
    Modelo para armazenar depoimentos de clientes sobre os serviços do escritório.
    Inclui informações como o nome do cliente, o texto do depoimento,
    um logo opcional, e um status de aprovação para exibição pública.
    """
    __tablename__ = 'depoimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), comment="Nome do cliente ou empresa que forneceu o depoimento.")
    texto_depoimento = db.Column(db.Text, comment="O conteúdo completo do depoimento.")
    logo_cliente = db.Column(db.String(255), comment="Caminho do arquivo do logo da empresa ou foto do cliente.")
    aprovado = db.Column(db.Boolean, default=False, nullable=False,
                         comment="Indica se o depoimento foi aprovado para ser exibido publicamente no site.")
    token_submissao = db.Column(db.String(32), unique=True, nullable=False,
                                comment="Token único gerado para cada submissão de depoimento, usado para gerenciamento interno.")
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow,
                             comment="Timestamp da data e hora em que o depoimento foi criado.")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<Depoimento {self.nome_cliente}>'

class ClienteParceiro(db.Model):
    """
    Modelo para gerenciar e exibir informações sobre clientes ou parceiros do escritório.
    Armazena o nome, o logotipo do cliente/parceiro e, opcionalmente, o URL do seu site.
    """
    __tablename__ = 'clientes_parceiros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, comment="Nome do cliente ou parceiro.")
    logo_path = db.Column(db.String(200), nullable=False, comment="Caminho do arquivo do logotipo do cliente/parceiro.")
    site_url = db.Column(db.String(255), nullable=True, comment="URL do site do cliente ou parceiro (ex: 'https://www.exemplo.com').")
    ordem = db.Column(db.Integer, default=99, comment="Número para definir a ordem de exibição na listagem de clientes/parceiros.")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<ClienteParceiro {self.nome}>'

class SetorAtendido(db.Model):
    """
    Modelo para listar e gerenciar os setores de mercado ou tipos de clientes que o escritório atende.
    Isso ajuda a segmentar e destacar a expertise do escritório em diferentes nichos.
    """
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False, comment="Título do setor (ex: 'Tecnologia', 'Agronegócio', 'Startups').")
    slug = db.Column(db.String(100), nullable=False, unique=True, comment="Identificador único e amigável para URLs do setor.")
    descricao = db.Column(db.Text, nullable=True, comment="Breve descrição sobre a atuação do escritório neste setor.")
    ordem = db.Column(db.Integer, default=99, comment="Número para definir a ordem de exibição dos setores.")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<SetorAtendido {self.titulo}>'

class HomePageSection(db.Model):
    """
    Modelo para configurar as seções dinâmicas que aparecem na Home Page.
    Permite controlar a ativação, ordem, título e subtítulo de cada seção,
    possibilitando a customização da página inicial através do painel administrativo.
    """
    __tablename__ = 'home_page_section'
    id = db.Column(db.Integer, primary_key=True)
    section_type = db.Column(db.String(50), nullable=False,
                             comment="Tipo de seção (ex: 'hero', 'show_services', 'show_team_on_home'). Usado para identificar qual template renderizar.")
    order = db.Column(db.Integer, nullable=False, comment="Ordem de exibição da seção na Home Page (menor valor primeiro).")
    is_active = db.Column(db.Boolean, nullable=False, default=True,
                           comment="Indica se a seção está ativa e deve ser exibida no site.")
    title = db.Column(db.String(200), nullable=True, comment="Título principal da seção, exibido no frontend.")
    subtitle = db.Column(db.String(500), nullable=True, comment="Subtítulo ou descrição breve da seção.")
    # Campo para conteúdo HTML customizado dentro da seção, se aplicável.
    content = db.Column(db.Text, nullable=True, comment="Conteúdo HTML customizado para a seção (opcional).")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<HomePageSection {self.section_type}>'

class CustomHomeSection(db.Model):
    """
    Modelo para seções personalizadas da Home Page com conteúdo e mídia específicos.
    Permite ao administrador criar blocos de conteúdo mais flexíveis na página inicial,
    com opções para título, conteúdo HTML, caminho de mídia, tipo e posição da mídia.
    """
    __tablename__ = 'custom_home_section'
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False, default=99, comment="Ordem de exibição da seção na Home Page.")
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment="Indica se a seção personalizada está ativa e deve ser exibida.")
    title = db.Column(db.String(200), nullable=False, comment="Título principal da seção personalizada.")
    content = db.Column(db.Text, nullable=True, comment="Conteúdo HTML detalhado da seção personalizada.")
    media_path = db.Column(db.String(255), nullable=True, comment="Caminho do arquivo para a mídia associada (imagem ou vídeo).")
    media_type = db.Column(db.String(20), default='image', comment="Tipo de mídia ('image' ou 'video').")
    media_position = db.Column(db.String(20), default='right', comment="Posição da mídia em relação ao texto ('left' ou 'right').")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<CustomHomeSection {self.title}>'

class ThemeSettings(db.Model):
    """
    Modelo para armazenar as configurações de tema e cores globais do site.
    Controla o layout ativo e a paleta de cores para os modos claro e escuro,
    permitindo a personalização visual da aplicação através do painel administrativo.
    """
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(50), default='option1',
                      comment="O layout de tema ativo (ex: 'option1', 'option2').")
    
    # Cores Primárias/Destaque para compatibilidade ou uso em lógica de backend.
    # Estes são os defaults visuais para cada "option" original e devem ser consistentes
    # com os valores definidos nos arquivos `theme-optionX.css` para evitar discrepâncias.
    cor_primaria_tema1 = db.Column(db.String(50), default='#b92027', comment="Cor primária para o Tema 1.")
    cor_primaria_tema2 = db.Column(db.String(50), default='#002F49', comment="Cor primária para o Tema 2 (Titan Navy).")
    cor_primaria_tema3 = db.Column(db.String(50), default='#D4AF37', comment="Cor primária para o Tema 3 (Golden Primary).")
    cor_primaria_tema4 = db.Column(db.String(50), default='#0f172a', comment="Cor primária para o Tema 4 (Tech Dark).") # Corrigido para consistência
    
    # Cores Gerais (Modo Claro)
    cor_texto = db.Column(db.String(50), default='#333333', comment="Cor padrão para o texto no modo claro.")
    cor_fundo = db.Column(db.String(50), default='#FFFFFF', comment="Cor padrão para o fundo no modo claro.")

    # Cores Gerais (Modo Escuro) - Campos obrigatórios e com defaults consistentes
    cor_texto_dark = db.Column(db.String(50), nullable=False, default='#ffffff',
                               comment="Cor padrão para o texto no modo escuro.")
    cor_fundo_dark = db.Column(db.String(50), nullable=False, default='#121212',
                               comment="Cor padrão para o fundo no modo escuro.")
    cor_fundo_secundario_dark = db.Column(db.String(50), nullable=False, default='#1e1e1e',
                                          comment="Cor de fundo secundário para elementos como cards no modo escuro.")
    
    # Outras configurações de tema
    qr_code_path = db.Column(db.String(255), nullable=True, default='images/qr-code (SEM O LOGO NO CENTRO).svg',
                             comment="Caminho para a imagem do QR Code para vCard no footer.")

    def __repr__(self):
        """
        Definição de __repr__.
        Componente essencial para a arquitetura do sistema.
        """
        return f'<ThemeSettings {self.theme}>'


@event.listens_for(ThemeSettings, 'before_insert')
def theme_settings_before_insert(mapper, connection, target):
    """
    Listener executado antes da inserção de um novo objeto ThemeSettings no banco de dados.
    Garante que o campo 'cor_texto_dark' seja '#ffffff' se estiver vazio ou None,
    assegurando a consistência com as expectativas dos testes e a exibição no frontend.
    Adiciona logging para depuração.
    """
    from flask import current_app # Importa aqui para evitar import circular
    try:
        if getattr(target, 'cor_texto_dark', None) in (None, ''):
            target.cor_texto_dark = '#ffffff'
            current_app.logger.debug("Normalizando 'cor_texto_dark' para '#ffffff' em ThemeSettings antes da inserção.")
    except Exception as e:
        current_app.logger.warning(f"Erro ao normalizar 'cor_texto_dark' antes da inserção de ThemeSettings: {e}")

@event.listens_for(ThemeSettings, 'before_update')
def theme_settings_before_update(mapper, connection, target):
    """
    Listener executado antes da atualização de um objeto ThemeSettings existente.
    Garante que o campo 'cor_texto_dark' seja '#ffffff' se estiver vazio ou None,
    assegurando a consistência com as expectativas dos testes e a exibição no frontend.
    Adiciona logging para depuração.
    """
    from flask import current_app # Importa aqui para evitar import circular
    try:
        if getattr(target, 'cor_texto_dark', None) in (None, ''):
            target.cor_texto_dark = '#ffffff'
            current_app.logger.debug("Normalizando 'cor_texto_dark' para '#ffffff' em ThemeSettings antes da atualização.")
    except Exception as e:
        current_app.logger.warning(f"Erro ao normalizar 'cor_texto_dark' antes da atualização de ThemeSettings: {e}")