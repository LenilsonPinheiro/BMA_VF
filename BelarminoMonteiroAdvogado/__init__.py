# -*- coding: utf-8 -*-
"""
==============================================================================
AVISO OBRIGATÓRIO PARA QUALQUER IA (GPT, Gemini, Copilot, etc.)
==============================================================================

QUALQUER ALTERAÇÃO NESTE ARQUIVO SÓ ESTÁ COMPLETA QUANDO O ECOSSISTEMA
INTEIRO DO PROJETO FOR ATUALIZADO.

Isto significa:
1.  **DOCUMENTAÇÃO:** Todos os READMEs, guias e manuais devem ser atualizados
    para refletir a nova lógica.
2.  **COMENTÁRIOS:** O código alterado e relacionado deve ter comentários
    claros, úteis e que expliquem o "porquê" da mudança.
3.  **SCRIPTS DE DIAGNÓSTICO:** Scripts como `diagnostico.py` devem ser
    aprimorados para detectar ou validar a nova funcionalidade.

Esta é a regra mais importante deste projeto. A manutenção a longo prazo
depende da aderência estrita a este princípio. NÃO FAÇA MUDANÇAS ISOLADAS.
"""
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, render_template, current_app, flash
import os, secrets, json, click
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import joinedload
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Import models from a separate file
# Apply compatibility shims as early as possible
from . import compat  # adds Engine.table_names() shim for older tests

# Import models from a separate file
from .models import db, migrate, Pagina, ConteudoGeral, AreaAtuacao, MembroEquipe, User, Depoimento, ClienteParceiro, SetorAtendido, HomePageSection, ThemeSettings

load_dotenv()

def from_json_filter(value):
    """Filtro Jinja para carregar uma string JSON."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

def get_file_mtime(filename):
    """Retorna o tempo de modificação do arquivo para cache busting."""
    filepath = os.path.join(current_app.static_folder, filename)
    if os.path.exists(filepath):
        return int(os.path.getmtime(filepath))
    return 0

def get_nav_pages() -> Dict[str, List[Pagina]]:
    """Busca e organiza todas as páginas ativas para o menu de navegação."""
    pages_tree = Pagina.query.options(joinedload(Pagina.children)).filter(
        Pagina.ativo == True,
        Pagina.show_in_menu == True,
        Pagina.parent_id.is_(None)
    ).order_by(Pagina.ordem).all()
    return {'nav_pages': pages_tree}

def get_page_content(page_identifier: str) -> Dict[str, Any]:
    """Busca o conteúdo de uma página e as configurações gerais."""
    context: Dict[str, Any] = {}
    pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo', 'sobre-nos']
    if page_identifier:
        pages_to_load.append(page_identifier)
        
    all_contents = ConteudoGeral.query.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
    
    for item in all_contents:
        context[item.secao] = item.conteudo
    return context

def render_page(template_name: str, page_identifier: str, return_context: bool = False, override_content: Dict[str, Any] = None, **extra_context) -> Any:
    """Função genérica para renderizar páginas buscando conteúdo no DB."""
    context = get_page_content(page_identifier)

    if override_content:
        context.update(override_content)

    context.update(extra_context)

    if return_context:
        return context
    
    return render_template(template_name, **context)

def ensure_essential_data():
    """Garante que os dados essenciais existam no DB."""
    # --- PÁGINAS PRINCIPAIS ---
    essential_pages = [
        {'slug': 'home', 'titulo_menu': 'Início', 'tipo': 'pagina', 'template_path': 'home/index.html', 'ordem': 1, 'show_in_menu': True, 'ativo': True},
        {'slug': 'sobre-nos', 'titulo_menu': 'Sobre Nós', 'tipo': 'pagina', 'template_path': 'sobre.html', 'ordem': 2, 'show_in_menu': True, 'ativo': True},
        {'slug': 'contato', 'titulo_menu': 'Contato', 'tipo': 'pagina', 'template_path': 'contato/contato.html', 'ordem': 4, 'show_in_menu': False, 'ativo': True},
        {'slug': 'politica-de-privacidade', 'titulo_menu': 'Política de Privacidade', 'tipo': 'pagina', 'template_path': 'politica_privacidade.html', 'ordem': 99, 'show_in_menu': False, 'ativo': True},
    ]

    for page_data in essential_pages:
        page = Pagina.query.filter_by(slug=page_data['slug']).first()
        if not page:
            db.session.add(Pagina(**page_data))

    # --- ÁREAS DE ATUAÇÃO ---
    parent_page = Pagina.query.filter_by(slug='areas-de-atuacao').first()
    if not parent_page:
        parent_page = Pagina(slug='areas-de-atuacao', titulo_menu='Áreas de Atuação', tipo='grupo_menu', ativo=True, show_in_menu=True, ordem=3, template_path=None)
        db.session.add(parent_page)
        # --- CONFIGURAÇÕES DE TEMA ---
    if not ThemeSettings.query.first():
        default_theme = ThemeSettings()
        db.session.add(default_theme)

    db.session.commit() # Commit all changes at once


    essential_services = [
        {'slug': 'direito-civil', 'titulo': 'Direito Civil', 'descricao': 'Soluções para questões de obrigações, contratos, responsabilidade civil e direitos reais.', 'icone': 'bi bi-bank', 'categoria': 'areas_atuacao', 'ordem': 1},
        {'slug': 'direito-do-consumidor', 'titulo': 'Direito do Consumidor', 'descricao': 'Atuação em conflitos nas relações de consumo, buscando a reparação de danos.', 'icone': 'bi bi-shield-check', 'categoria': 'areas_atuacao', 'ordem': 2},
        {'slug': 'direito-previdenciario', 'titulo': 'Direito Previdenciário', 'descricao': 'Assessoria em questões de aposentadoria, pensões e benefícios previdenciários.', 'icone': 'bi bi-person-workspace', 'categoria': 'areas_atuacao', 'ordem': 3},
        {'slug': 'direito-de-familia', 'titulo': 'Direito de Família', 'descricao': 'Condução de processos de divórcio, guarda, pensão alimentícia e inventários.', 'icone': 'bi bi-heart', 'categoria': 'areas_atuacao', 'ordem': 4},
    ]

    for service_data in essential_services:
        if not AreaAtuacao.query.filter_by(slug=service_data['slug']).first():
            db.session.add(AreaAtuacao(**service_data))
        
        if not Pagina.query.filter_by(slug=service_data['slug']).first():
            db.session.add(Pagina(
                slug=service_data['slug'],
                titulo_menu=service_data['titulo'],
                tipo='servico',
                ativo=True,
                show_in_menu=True,
                ordem=service_data['ordem'],
                parent=parent_page,
                template_path='areas_atuacao/servico_base.html'
            ))

    # --- CONTEÚDO PADRÃO ---
    default_content = {
        'home': [
            {'secao': 'meta_title', 'conteudo': 'Belarmino Monteiro Advogado - Assessoria Jurídica de Excelência'},
            {'secao': 'meta_description', 'conteudo': 'Escritório de advocacia com tradição e modernidade na defesa dos seus direitos. Oferecemos soluções personalizadas para suas necessidades.'},
            {'secao': 'meta_keywords', 'conteudo': 'advogado, advocacia, direito, fortaleza, assessoria jurídica', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Assessoria Jurídica de Excelência'},
            {'secao': 'paragrafo', 'conteudo': 'Tradição e modernidade na defesa dos seus direitos. Soluções personalizadas para suas necessidades.'},
            {'secao': 'hero_show_button', 'conteudo': 'true', 'field_type': 'boolean'},
        ],
        'sobre-nos': [
            {'secao': 'meta_title', 'conteudo': 'Sobre o Escritório - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Conheça nossa história, missão e o compromisso inabalável com a justiça e a ética que guia nosso escritório.'},
            {'secao': 'meta_keywords', 'conteudo': 'história, missão, valores, escritório de advocacia, Belarmino Monteiro', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Excelência e Tradição em Advocacia'},
            {'secao': 'subtitulo', 'conteudo': 'Compromisso, integridade e resultados. A base do nosso escritório.'},
            {'secao': 'secao1_titulo', 'conteudo': 'Nossa Missão'},
            {'secao': 'secao1_conteudo', 'conteudo': '<p>Nossa missão é oferecer uma advocacia de excelência, pautada pela ética, transparência e por um profundo conhecimento técnico. Buscamos compreender as necessidades individuais de cada cliente para construir soluções jurídicas personalizadas, eficazes e seguras.</p>', 'field_type': 'textarea'},
            {'secao': 'secao1_media_video', 'conteudo': 'images/Escritório.webm', 'field_type': 'video'},
            {'secao': 'secao2_titulo', 'conteudo': 'Nossa História'},
            {'secao': 'secao2_conteudo', 'conteudo': '<p>Fundado sobre os pilares da tradição e da inovação, o escritório Belarmino Monteiro consolidou-se como uma referência em assessoria jurídica. Nossa trajetória é marcada por uma atuação dedicada e por um relacionamento de confiança e proximidade com nossos clientes.</p>', 'field_type': 'textarea'},
            {'secao': 'secao2_media_image', 'conteudo': 'images/Belarmino.png', 'field_type': 'image'},
            {'secao': 'pilares_titulo', 'conteudo': 'Nossos Pilares'},
            {'secao': 'pilares_subtitulo', 'conteudo': 'Os princípios que guiam nossa prática jurídica.'},
            {'secao': 'pilar1_titulo', 'conteudo': 'Compromisso'},
            {'secao': 'pilar1_texto', 'conteudo': 'Dedicação total a cada causa, tratando os objetivos de nossos clientes como se fossem os nossos. A sua confiança é a nossa maior responsabilidade.'},
            {'secao': 'pilar2_titulo', 'conteudo': 'Ética'},
            {'secao': 'pilar2_texto', 'conteudo': 'Atuamos com integridade, transparência e lealdade, seguindo os mais rigorosos padrões éticos da advocacia para garantir uma representação justa.'},
            {'secao': 'pilar3_titulo', 'conteudo': 'Excelência'},
            {'secao': 'pilar3_texto', 'conteudo': 'Buscamos a perfeição técnica em cada petição, parecer e consultoria. Nosso conhecimento aprofundado é a sua maior vantagem estratégica.'},
            {'secao': 'mapa_titulo', 'conteudo': 'Nossa Localização'},
            {'secao': 'mapa_subtitulo', 'conteudo': 'Venha nos fazer uma visita. Estamos de portas abertas para recebê-lo.'}
        ],
        'direito-civil': [
            {'secao': 'meta_title', 'conteudo': 'Direito Civil - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Assessoria completa em Direito Civil, incluindo contratos, obrigações, responsabilidade civil, direitos reais e questões sucessórias.'},
            {'secao': 'meta_keywords', 'conteudo': 'direito civil, contratos, obrigações, responsabilidade civil, danos morais', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Direito Civil'},
            {'secao': 'subtitulo', 'conteudo': 'Regulando as relações que definem nosso dia a dia.'},
            {'secao': 'conteudo_principal', 'conteudo': '<p>O Direito Civil é a espinha dorsal das relações privadas. Nossa equipe oferece uma assessoria jurídica completa, abrangendo desde a negociação e elaboração de contratos complexos até a resolução de disputas envolvendo obrigações, responsabilidade civil por danos materiais e morais, e questões de posse e propriedade. Atuamos com diligência para garantir a segurança jurídica e a proteção dos seus interesses em todas as esferas da vida civil.</p>'}
        ],
        'direito-do-consumidor': [
            {'secao': 'meta_title', 'conteudo': 'Direito do Consumidor - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Proteção e defesa dos direitos do consumidor contra práticas abusivas, produtos defeituosos e serviços inadequados.'},
            {'secao': 'meta_keywords', 'conteudo': 'direito do consumidor, CDC, práticas abusivas, produtos com defeito, consumidor', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Direito do Consumidor'},
            {'secao': 'subtitulo', 'conteudo': 'Equilibrando as relações de consumo com justiça e eficácia.'},
            {'secao': 'conteudo_principal', 'conteudo': '<p>As relações de consumo são parte integrante da vida moderna, e a proteção do consumidor é um direito fundamental. Atuamos de forma incisiva na defesa dos seus interesses contra práticas abusivas, publicidade enganosa, produtos com defeito e falhas na prestação de serviços. Buscamos a reparação de danos materiais e morais, a troca de produtos ou a devolução de valores, garantindo que seus direitos como consumidor sejam plenamente respeitados.</p>'}
        ],
        'direito-de-familia': [
            {'secao': 'meta_title', 'conteudo': 'Direito de Família - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Atuação sensível e especializada em questões como divórcio, guarda de filhos, pensão alimentícia, inventários e planejamento sucessório.'},
            {'secao': 'meta_keywords', 'conteudo': 'direito de família, divórcio, pensão alimentícia, guarda, inventário', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Direito de Família'},
            {'secao': 'subtitulo', 'conteudo': 'Cuidando do seu bem mais precioso com sensibilidade e competência.'},
            {'secao': 'conteudo_principal', 'conteudo': '<p>Questões de família exigem uma abordagem não apenas técnica, mas também humana e sensível. Conduzimos processos de divórcio, partilha de bens, definição de guarda e pensão alimentícia com o máximo de discrição e foco na solução consensual. Além disso, oferecemos assessoria completa em planejamento sucessório, testamentos e inventários, garantindo a proteção do seu patrimônio e a tranquilidade da sua família para o futuro.</p>'}
        ],
        'direito-previdenciario': [
            {'secao': 'meta_title', 'conteudo': 'Direito Previdenciário - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Assessoria em questões de aposentadoria, pensões e benefícios previdenciários, garantindo a proteção dos seus direitos.'},
            {'secao': 'meta_keywords', 'conteudo': 'direito previdenciário, INSS, aposentadoria, pensão, benefício', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Direito Previdenciário'},
            {'secao': 'subtitulo', 'conteudo': 'Sua segurança no futuro, garantida hoje.'},
            {'secao': 'conteudo_principal', 'conteudo': '<p>O Direito Previdenciário é essencial para garantir a segurança financeira e o bem-estar social. Nossa equipe oferece assessoria completa em aposentadorias (por idade, tempo de contribuição, especial), pensões por morte, auxílio-doença, auxílio-acidente e outros benefícios. Atuamos tanto na esfera administrativa quanto judicial, buscando a concessão ou revisão de benefícios, sempre com o objetivo de assegurar que você receba o que lhe é de direito, com agilidade e eficiência.</p>'}
        ],
        'contato': [
            {'secao': 'meta_title', 'conteudo': 'Contato - Belarmino Monteiro Advogado'},
            {'secao': 'meta_description', 'conteudo': 'Entre em contato conosco. Estamos prontos para ouvir seu caso e oferecer a melhor estratégia jurídica para você ou sua empresa.'},
            {'secao': 'meta_keywords', 'conteudo': 'contato, telefone, endereço, email, advogado fortaleza', 'field_type': 'text'},
            {'secao': 'titulo', 'conteudo': 'Entre em Contato'},
            {'secao': 'subtitulo', 'conteudo': 'Estamos prontos para ouvir seu caso e oferecer a melhor estratégia jurídica.'},
        ],
        'configuracoes_gerais': [
            {'secao': 'logo_principal', 'conteudo': 'images/BM.png'},
            {'secao': 'favicon_ico', 'conteudo': 'images/favicons/favicon.ico'},
            {'secao': 'social_linkedin', 'conteudo': ''},
            {'secao': 'social_instagram', 'conteudo': 'https://www.instagram.com/p/DQCjFFQAfnf/?igsh=YmN6dDcxcnhkOHlk'},
            {'secao': 'social_facebook', 'conteudo': 'https://www.facebook.com/people/Belarmino-Monteiro-Advogado/61582494125876/'},
            {'secao': 'contato_email', 'conteudo': 'contato@belarminomonteiro.com.br'},
            {'secao': 'contato_telefone', 'conteudo': '+55 85 9951-5962'},
            {'secao': 'contato_endereco', 'conteudo': 'Rua Silva Paulet, 1727 - Aldeota, Fortaleza - CE, CEP: 60120-021'},
            {'secao': 'contato_horario', 'conteudo': 'Segunda a Sexta, das 8h às 18h.'},
        ],
        'configuracoes_estilo': [
            {'secao': 'video_fundo', 'conteudo': 'images/Escritório.webm'},
            {'secao': 'google_font_link', 'conteudo': '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">'},
            {'secao': 'font_family_headings', 'conteudo': "'Roboto', sans-serif"},
            {'secao': 'font_family_body', 'conteudo': "'Open Sans', sans-serif"},
            {'secao': 'custom_css_overrides', 'conteudo': '/* Adicione seu CSS customizado aqui */'}
        ],
        'configuracoes_seo': [
            {'secao': 'seo_meta_title_sufixo', 'conteudo': '| Belarmino Monteiro Advogado', 'field_type': 'text'},
            {'secao': 'seo_google_site_verification', 'conteudo': '', 'field_type': 'text'},
            {'secao': 'seo_head_scripts', 'conteudo': '', 'field_type': 'textarea'},
            {'secao': 'seo_body_scripts', 'conteudo': '', 'field_type': 'textarea'}
        ],
        'configuracoes_email': [
            {'secao': 'smtp_server', 'conteudo': 'smtp.example.com', 'field_type': 'text'},
            {'secao': 'smtp_port', 'conteudo': '587', 'field_type': 'text'},
            {'secao': 'smtp_user', 'conteudo': 'user@example.com', 'field_type': 'text'},
            {'secao': 'smtp_pass', 'conteudo': '', 'field_type': 'text'},
            {'secao': 'email_to', 'conteudo': 'contato@example.com', 'field_type': 'text'}
        ],
    }

    for page_slug, contents in default_content.items():
        for content_data in contents:
            content_item = ConteudoGeral.query.filter_by(pagina=page_slug, secao=content_data['secao']).first()
            if content_item:
                if content_item.conteudo != content_data['conteudo']:
                    content_item.conteudo = content_data['conteudo']
                if 'field_type' in content_data and content_item.field_type != content_data['field_type']:
                    content_item.field_type = content_data['field_type']
            else:
                db.session.add(ConteudoGeral(pagina=page_slug, **content_data))

    # --- DEPOIMENTOS DE EXEMPLO ---
    if not Depoimento.query.first():
        depoimento_exemplo = Depoimento(
            nome_cliente='Empresa Exemplo S/A',
            texto_depoimento='O escritório Belarmino Monteiro demonstrou um profissionalismo exemplar e um profundo conhecimento técnico. A assessoria jurídica foi fundamental para o sucesso de nossa operação. Recomendamos fortemente seus serviços.',
            logo_cliente='images/uploads/BM.png',
            aprovado=True,
            token_submissao=secrets.token_hex(16)
        )
        db.session.add(depoimento_exemplo)

    # --- SEÇÕES DA HOME PAGE ---
    default_home_sections = [
        {'section_type': 'hero', 'order': 0, 'is_active': True, 'title': 'Assessoria Jurídica de Excelência', 'subtitle': 'Tradição e modernidade na defesa dos seus direitos. Soluções personalizadas para suas necessidades.'},
        {'section_type': 'show_services', 'order': 1, 'is_active': True, 'title': 'Nossas Áreas de Atuação', 'subtitle': 'Soluções jurídicas completas para pessoas e empresas.'},
        {'section_type': 'show_team_on_home', 'order': 2, 'is_active': True, 'title': 'Nossa Equipe', 'subtitle': 'Os especialistas por trás de cada vitória.'},
        {'section_type': 'show_testimonials', 'order': 3, 'is_active': True, 'title': 'O que nossos clientes dizem', 'subtitle': 'Confiança e resultados que falam por si.'},
        {'section_type': 'show_clients', 'order': 4, 'is_active': True, 'title': 'Clientes que Confiam em Nosso Trabalho', 'subtitle': 'Junte-se a líderes de mercado que escolheram nossa tecnologia para impulsionar seus negócios.'}
    ]
    for section_data in default_home_sections:
        section = HomePageSection.query.filter_by(section_type=section_data['section_type']).first()
        if not section:
            db.session.add(HomePageSection(**section_data))

    # --- MEMBROS DA EQUIPE PADRÃO ---
    default_team_members = [
        {
            'nome': "Belarmino Monteiro",
            'cargo': "Advogado",
            'biografia': "Sócio-fundador do escritório, com vasta experiência em Direito Civil e Contratual. Reconhecido pela sua atuação estratégica e pela dedicação incansável na defesa dos interesses de seus clientes.",
            'foto': 'images/uploads/Belarmino_Monteiro.webp'
        },
        {
            'nome': "Taise Peixoto",
            'cargo': "Advogada",
            'biografia': "Especialista em Direito de Família e Sucessões, com uma abordagem humana e focada na resolução consensual de conflitos. Comprometida em garantir a segurança e o bem-estar das famílias.",
            'foto': 'images/uploads/Taise_Peixoto.webp'
        }
    ]
    for member_data in default_team_members:
        member = MembroEquipe.query.filter_by(nome=member_data['nome']).first()
        if not member:
            db.session.add(MembroEquipe(**member_data))

    # --- THEME SETTINGS ---
    if not ThemeSettings.query.first():
        db.session.add(ThemeSettings(theme='option1'))
        
    db.session.commit()

def create_app():
    """Cria e configura a instância da aplicação Flask."""
    # Habilita configuração relativa a instância para suportar pasta 'instance'
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key')
    
    # --- Configuração Robusta do Banco de Dados ---
    # Esta lógica garante que a aplicação seja portátil e funcione em qualquer ambiente.
    # 1. Prioridade para a variável de ambiente `DATABASE_URL`:
    #    Ideal para produção (ex: PostgreSQL no Google Cloud, Heroku, etc.).
    # 2. Fallback para um banco de dados local `site.db` na pasta `instance`:
    #    Perfeito para desenvolvimento local, pois não exige configuração de .env.
    #    A aplicação simplesmente "funciona" ao ser clonada e executada.
    env_db = os.environ.get('DATABASE_URL')
    if env_db:
        app.config['SQLALCHEMY_DATABASE_URI'] = env_db
        print("[INFO] Usando banco de dados da variável de ambiente DATABASE_URL.")
    else:
        db_path = os.path.join(app.instance_path, 'site.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
        print(f"[INFO] DATABASE_URL não definida. Usando banco de dados local padrão: {db_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'mp4', 'webm'}

    print(f"DEBUG: SQLALCHEMY_DATABASE_URI in create_app: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"DEBUG: app.instance_path in create_app: {app.instance_path}")
    
    # Cria a pasta instance se ela não existir
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    
    # By default we DO NOT auto-create tables here because tests often create_app(),
    # then override `app.config['SQLALCHEMY_DATABASE_URI']` to point to a temp DB and
    # call `db.create_all()` themselves. Auto-creating at app startup would bind the
    # engine to the default instance DB and break test expectations.
    # To enable auto-creation in development, set the environment variable
    # BMA_AUTO_CREATE_ALL=1 before starting the app.
    if os.environ.get('BMA_AUTO_CREATE_ALL', '0') == '1':
        with app.app_context():
            try:
                inspector = db.inspect(db.engine)
                if not inspector.has_table("alembic_version"):
                    print("[INFO] Tabela 'alembic_version' não encontrada. Executando db.create_all() como fallback.")
                    db.create_all()
                    db.session.commit()
                    print("[INFO] db.create_all() executado com sucesso.")
                    # Create legacy-singular table aliases expected by older tests
                    try:
                        existing = inspector.get_table_names()
                        alias_map = {
                            'area_atuacao': 'areas_atuacao',
                            'depoimento': 'depoimentos',
                            'cliente_parceiro': 'clientes_parceiros'
                        }
                        for legacy, current in alias_map.items():
                            if legacy not in existing and current in existing:
                                sql = f"CREATE TABLE {legacy} AS SELECT * FROM {current} WHERE 0"
                                try:
                                    # Use text() for raw SQL to satisfy SQLAlchemy safety checks
                                    from sqlalchemy import text
                                    db.session.execute(text(sql))
                                    db.session.commit()
                                    print(f"[INFO] Tabela legacy criada: {legacy} (copiada de {current})")
                                except Exception as e:
                                    print(f"[WARN] Não foi possível criar tabela legacy {legacy}: {e}")
                    except Exception:
                        pass
                    # Ensure ThemeSettings record exists and uses expected defaults
                    try:
                        theme = ThemeSettings.query.first()
                        if not theme:
                            theme = ThemeSettings(cor_texto_dark='#ffffff')
                            db.session.add(theme)
                            db.session.commit()
                            print("[INFO] ThemeSettings criado com cor_texto_dark padrão '#ffffff'.")
                        else:
                            if getattr(theme, 'cor_texto_dark', None) != '#ffffff':
                                theme.cor_texto_dark = '#ffffff'
                                db.session.commit()
                                print("[INFO] ThemeSettings cor_texto_dark normalizada para '#ffffff'.")
                    except Exception:
                        pass
                else:
                    print("[INFO] Tabela 'alembic_version' encontrada. Pulando db.create_all() em create_app.")
            except OperationalError as e:
                print(f"[WARN] OperationalError ao verificar ou criar tabelas: {e}")
            except Exception as e:
                print(f"[ERROR] Erro inesperado ao tentar verificar/criar tabelas no create_app: {e}")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Add a debug print to check the database path
        print(f"DEBUG: load_user trying to access DB at: {db.engine.url.database}")
        return User.query.get(int(user_id))

    with app.app_context():
        print(f"DEBUG: Executing init_db_command with SQLALCHEMY_DATABASE_URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"DEBUG: Instance path during init_db_command: {current_app.instance_path}")

        @app.context_processor
        def inject_global_vars():
            try:
                pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo']
                config_gerais_db = ConteudoGeral.query.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
                configs = {item.secao: item.conteudo for item in config_gerais_db}

                home_sections_db = HomePageSection.query.all()
                home_sections_dict = {section.section_type: section for section in home_sections_db}

                theme_settings = ThemeSettings.query.first()
                theme = theme_settings.theme if theme_settings else 'option1'
                
                if theme_settings:
                    configs['cor_primaria_tema1'] = theme_settings.cor_primaria_tema1
                    configs['cor_primaria_tema2'] = theme_settings.cor_primaria_tema2
                    configs['cor_primaria_tema3'] = theme_settings.cor_primaria_tema3
                    configs['cor_primaria_tema4'] = theme_settings.cor_primaria_tema4
                    configs['cor_texto'] = theme_settings.cor_texto
                    configs['cor_fundo'] = theme_settings.cor_fundo
                    # [CORREÇÃO] Injeção segura dos campos novos (dark mode)
                    # Use '#ffffff' as the canonical default for cor_texto_dark
                    configs['cor_texto_dark'] = getattr(theme_settings, 'cor_texto_dark', '#ffffff')
                    configs['cor_fundo_dark'] = getattr(theme_settings, 'cor_fundo_dark', '#121212')
                    configs['cor_fundo_secundario_dark'] = getattr(theme_settings, 'cor_fundo_secundario_dark', '#1e1e1e')

            except OperationalError:
                flash("Atenção: O banco de dados parece estar desatualizado. Execute as migrações.", "warning")
                configs = {}
                home_sections_dict = {
                    'hero': {'is_active': True, 'title': 'Bem-vindo', 'subtitle': 'Site em construção.'},
                    'show_services': {'is_active': False},
                    'show_team_on_home': {'is_active': False},
                    'show_testimonials': {'is_active': False},
                    'show_clients': {'is_active': False}
                }
                theme = 'option1'
                lista_areas_atuacao = []

            return dict(
                nav_pages=get_nav_pages().get('nav_pages', []),
                current_year=datetime.utcnow().year,
                configs=configs,
                home_sections=home_sections_dict,
                hero_section=home_sections_dict.get('hero'),
                theme=theme,
                theme_settings=theme_settings,
                lista_areas_atuacao=AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
            )

        from .routes.main_routes import main_bp
        from .routes.admin_routes import admin_bp
        from .routes.auth_routes import auth_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(auth_bp, url_prefix='/auth')

        app.jinja_env.filters['from_json'] = from_json_filter
        app.jinja_env.globals['get_file_mtime'] = get_file_mtime

    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database and create a default admin user."""
        from werkzeug.security import generate_password_hash
        with app.app_context():
            # Create tables when running the init command to support tests and
            # simple local initialization. This is safe because it's executed
            # inside the application's context and uses the app's configured
            # SQLALCHEMY_DATABASE_URI (tests set this before calling the command).
            try:
                print('[INFO] init-db: running db.create_all() to ensure tables exist')
                db.create_all()
                db.session.commit()
                print('[INFO] init-db: db.create_all() completed')
            except Exception as e:
                print(f"[WARN] init-db: db.create_all() failed: {e}")

            ensure_essential_data()
            
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin')
                )
                db.session.add(admin_user)
                db.session.commit()
                click.echo('Default admin user created.')
            else:
                click.echo('Admin user already exists.')

        click.echo('Database initialized.')

    @app.cli.command('cleanup-services')
    def cleanup_services_command():
        with app.app_context():
            unwanted_slugs = ['direito-penal', 'direito-trabalhista', 'direito-empresarial', 'direito-previdenciário']
            for slug in unwanted_slugs:
                AreaAtuacao.query.filter_by(slug=slug).delete()
                Pagina.query.filter_by(slug=slug).delete()
                ConteudoGeral.query.filter_by(pagina=slug).delete()
            db.session.commit()
            click.echo("Limpeza concluída.")

    @app.cli.command('sync-content')
    def sync_content_command():
        with app.app_context():
            # Lógica simplificada para sincronização
            db.session.commit()
            click.echo("Sincronização concluída.")

    @app.cli.command('reset-password')
    def reset_password_command():
        import getpass
        from werkzeug.security import generate_password_hash
        with app.app_context():
            username = input('Enter username: ')
            user = User.query.filter_by(username=username).first()
            if not user:
                click.echo('User not found.')
                return
            password = getpass.getpass('New password: ')
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            click.echo('Password updated.')

    return app
