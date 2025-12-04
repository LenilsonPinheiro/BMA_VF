# -*- coding: utf-8 -*-
"""
==============================================================================
Rotas Públicas Principais
==============================================================================

Este módulo define o Blueprint para as rotas públicas e principais do site,
como a página inicial, páginas de conteúdo dinâmico, formulário de contato,
política de privacidade, e outras páginas acessíveis a todos os visitantes.

Funcionalidades do Blueprint:
-----------------------------
- **Página Inicial (`/`):** Renderiza a home page, selecionando dinamicamente o
  template correto com base na configuração de tema ativa.
- **Páginas Dinâmicas (`/<slug>`):** Uma rota "catch-all" que busca uma página
  no banco de dados pelo seu `slug` e a renderiza com o template associado.
  É a espinha dorsal do sistema de gerenciamento de conteúdo.
- **Contato (`/contato`):** Apresenta e processa o formulário de contato,
  enviando um e-mail para o administrador com as informações submetidas.
- **SEO e Indexação:** Inclui rotas para `robots.txt` e `sitemap.xml`,
  essenciais para a otimização de mecanismos de busca.
- **Service Worker:** Rota para servir o arquivo do service worker, fundamental
  para funcionalidades de PWA (Progressive Web App).

Toda a renderização de páginas é feita através da função `render_page`, que
centraliza a busca de conteúdo no banco de dados, garantindo consistência.
"""
import logging
import traceback
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Imports Flask e Extensões
from flask import Blueprint, render_template, request, url_for, abort, current_app, jsonify, Response, g
from werkzeug.utils import secure_filename
from PIL import Image

# Imports Locais
from .. import db, render_page
from ..models import (
    AreaAtuacao, MembroEquipe, Depoimento, ConteudoGeral, User, Pagina, 
    ClienteParceiro, SetorAtendido, HomePageSection, CustomHomeSection, ThemeSettings
)
from ..forms import ContactForm

# Configuração do Logger
logger = logging.getLogger(__name__)

# --- 1. DEFINIÇÃO DO BLUEPRINT ---
main_bp = Blueprint('main', __name__)

# --- 2. ROTA DE SHOWCASE V5 (X-TUDO) ---
@main_bp.route('/xtudo')
def showcase_v5():
    """
    Rota de Showcase do Framework V5 (X-Tudo).
    Força o tema 'option9' para visualização imediata sem alterar configuração do banco.
    """
    try:
        # LOG OBRIGATÓRIO (Política 2.1)
        logger.info("[MAIN::XTUDO] Iniciando renderização do Showcase V5.0 para IP do solicitante.")
        
        # Renderiza passando 'theme' explicitamente para sobrescrever o default
        return render_template('home/home_option9.html', theme='option9')
        
    except Exception as e:
        # TRATAMENTO DE ERRO COM LOG DETALHADO (Política 2.1)
        logger.exception(f"[MAIN::XTUDO] Erro crítico ao renderizar X-Tudo: {str(e)}")
        return render_template('500.html'), 500

# --- 3. FUNÇÕES AUXILIARES ---
def allowed_file(filename: str) -> bool:
    """
    Verifica se a extensão do arquivo é permitida para upload.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- 4. ROTAS PADRÃO DO SISTEMA ---
@main_bp.route('/')
def home():
    """
    Renderiza a página inicial, FORÇANDO o carregamento do template de conteúdo (home_optionX.html).
    """
    current_app.logger.info("Acessando Home Page.")
    
    # 1. Recupera o tema
    try:
        theme_settings = ThemeSettings.query.first()
        theme = theme_settings.theme if theme_settings else 'option1'
    except Exception:
        theme = 'option1'

    # [CORREÇÃO DE ARQUITETURA] 
    # Nunca renderizar 'base_option1.html' diretamente, pois ele é apenas a casca.
    # Devemos renderizar 'home/home_option1.html', que herda da casca e injeta o conteúdo.
    if theme == 'option1':
        template_name = 'home/home_option1.html'
    else:
        template_name = f'home/home_{theme}.html'

    # 2. Carrega os dados (Mantendo sua lógica)
    try:
        home_sections = HomePageSection.query.filter_by(is_active=True).all()
        active_custom = CustomHomeSection.query.filter_by(is_active=True).all()
        
        # Organiza e ordena
        for s in home_sections: s.type = 'predefined'
        for s in active_custom: s.type = 'custom'
        
        all_sections = sorted(home_sections + active_custom, key=lambda x: x.order)
        
        # Dados auxiliares
        areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
        depos = Depoimento.query.filter_by(aprovado=True).order_by(Depoimento.data_criacao.desc()).all()
        clientes = ClienteParceiro.query.order_by(ClienteParceiro.nome).all()
        equipe = MembroEquipe.query.order_by(MembroEquipe.nome).all()

        extra_context = {
            'form': ContactForm(),
            'all_home_sections': all_sections,
            'lista_areas_atuacao': areas,
            'testimonials': depos,
            'all_clients': clientes,
            'team': equipe
        }
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar dados da Home: {e}")
        return render_template('500.html'), 500

    current_app.logger.info(f"Renderizando Home com template final: {template_name}")
    return render_page(template_name, 'home', **extra_context)

@main_bp.route('/politica-de-privacidade')
def politica_privacidade():
    """
    Definição de politica_privacidade.
    Componente essencial para a arquitetura do sistema.
    """
    current_app.logger.info("Acessando a página de Política de Privacidade.")
    return render_page('politica_privacidade.html', 'politica_privacidade')

@main_bp.route('/areas-de-atuacao')
def todas_areas_atuacao():
    """
    Definição de todas_areas_atuacao.
    Componente essencial para a arquitetura do sistema.
    """
    current_app.logger.info("Acessando a página 'Todas as Áreas de Atuação'.")
    areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
    return render_page('areas_atuacao/todas_areas.html', 'todas_areas', areas=areas, disable_scroll_snap=True)

@main_bp.route('/contato', methods=['GET', 'POST'])
def pagina_contato():
    """
    Definição de pagina_contato.
    Componente essencial para a arquitetura do sistema.
    """
    form = ContactForm()
    
    if form.validate_on_submit():
        nome = form.name.data
        email = form.email.data
        assunto = form.subject.data if form.subject.data else "Nova Mensagem de Contato do Site"
        mensagem = form.message.data

        current_app.logger.info(f"Recebida submissão de formulário de contato de {nome} ({email}).")

        try:
            email_settings_db = ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()
            email_config = {item.secao: item.conteudo for item in email_settings_db}

            SMTP_SERVER = email_config.get('smtp_server')
            try:
                SMTP_PORT = int(email_config.get('smtp_port') or 587)
            except (ValueError, TypeError):
                SMTP_PORT = 587
                current_app.logger.warning("Porta SMTP inválida no DB. Usando padrão 587.")
            
            SMTP_USER = email_config.get('smtp_user')
            SMTP_PASS = email_config.get('smtp_pass')
            EMAIL_TO = email_config.get('email_to', 'contato@belarminomonteiroadvogado.com.br')

            if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS]):
                current_app.logger.error("Configurações SMTP incompletas no banco de dados.")
                return jsonify({'success': False, 'message': 'Erro interno: Configurações de e-mail incompletas.'}), 500

            msg = MIMEMultipart()
            msg['From'] = SMTP_USER
            msg['To'] = EMAIL_TO
            msg['Subject'] = f"[{current_app.config.get('SITE_NAME', 'Site Contato')}] {assunto}"
            msg['Reply-To'] = email

            body = f"""Nova mensagem do site:
Nome: {nome}
Email: {email}
Assunto: {assunto}
Mensagem:
{mensagem}
---
Enviado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
IP: {request.remote_addr}
"""
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
            
            current_app.logger.info(f"E-mail enviado com sucesso para {EMAIL_TO}.")
            return jsonify({'success': True, 'message': 'Mensagem enviada com sucesso!'})
            
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar e-mail: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Erro ao enviar mensagem. Tente novamente.'}), 500

    return render_page('contato/contato.html', 'contato', form=form)

@main_bp.route('/search')
def search():
    """
    Definição de search.
    Componente essencial para a arquitetura do sistema.
    """
    query = request.args.get('q', '').strip()
    current_app.logger.info(f"Busca realizada: '{query}'")
    results = []
    if query:
        areas = AreaAtuacao.query.filter(AreaAtuacao.titulo.ilike(f'%{query}%')).all()
        for area in areas:
            results.append({'titulo': area.titulo, 'url': url_for('main.pagina_dinamica', slug=area.slug), 'descricao': area.descricao, 'tipo': 'Área de Atuação'})

        setores = SetorAtendido.query.filter(SetorAtendido.titulo.ilike(f'%{query}%')).all()
        for setor in setores:
            results.append({'titulo': setor.titulo, 'url': url_for('main.pagina_dinamica', slug=setor.slug), 'descricao': f"Setor: {setor.titulo}", 'tipo': 'Setor Atendido'})
            
    return render_template('search_results.html', query=query, results=results)

@main_bp.route('/service-worker.js')
def service_worker():
    """
    Serve o arquivo JavaScript do Service Worker.
    
    Esta rota é essencial para as funcionalidades de Progressive Web App (PWA),
    como caching offline e notificações. Os headers da resposta são ajustados
    para garantir que o navegador trate o arquivo corretamente.
    """
    response = current_app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@main_bp.route('/robots.txt')
def robots_txt():
    """
    Gera e serve o arquivo robots.txt para os mecanismos de busca.
    
    Renderiza o template 'robots.txt' e o serve como texto plano, instruindo
    os crawlers (como o do Google) sobre quais páginas eles podem ou não indexar.
    """
    return Response(render_template('robots.txt'), mimetype='text/plain')

@main_bp.route('/sitemap.xml')
def sitemap():
    """
    Gera dinamicamente o sitemap.xml do site.
    
    Busca todas as páginas ativas no banco de dados e cria um mapa do site
    em formato XML. Isso ajuda os mecanismos de busca a descobrir e indexar
    todas as páginas importantes do site de forma mais eficiente.
    """
    urls = []
    today = datetime.now().strftime('%Y-%m-%d')
    pages = Pagina.query.filter_by(ativo=True).all()
    for page in pages:
        if page.tipo == 'grupo_menu' or not page.template_path:
            continue
        
        if page.slug == 'home':
            loc = url_for('main.home', _external=True)
        else:
            loc = url_for('main.pagina_dinamica', slug=page.slug, _external=True)

        urls.append({
            'loc': loc,
            'lastmod': today,
            'changefreq': 'weekly',
            'priority': '0.8' if page.slug == 'home' else '0.6'
        })

    return Response(render_template('sitemap.xml', urls=urls), mimetype='application/xml')

@main_bp.route('/depoimento/submit/<token>', methods=['GET', 'POST'])
def submit_depoimento(token: str):
    """
    Processa a submissão de um depoimento de cliente através de um link único.
    
    Valida o token de segurança, exibe o formulário de submissão (GET) e
    processa os dados enviados (POST), incluindo o upload opcional de um logotipo.
    
    Args:
        token (str): O token de segurança único que autoriza a submissão.
    """
    depoimento_entry = Depoimento.query.filter_by(token_submissao=token, aprovado=False).first()

    if not depoimento_entry:
        abort(404)

    if request.method == 'POST':
        depoimento_entry.nome_cliente = request.form.get('client_name')
        depoimento_entry.texto_depoimento = request.form.get('testimonial_text')
        
        file = request.files.get('client_logo')
        if file and file.filename != '':
            from ..image_processor import save_logo
            try:
                logo_filename_base = secure_filename(f"{depoimento_entry.nome_cliente}_{token[:8]}")
                logo_path_relative = save_logo(file, logo_filename_base)
                
                if logo_path_relative:
                    depoimento_entry.logo_cliente = logo_path_relative
            except Exception as e:
                current_app.logger.error(f"Erro ao processar logo: {e}", exc_info=True)
        
        db.session.commit()
        return render_template('depoimentos/thank_you.html')

    return render_template('depoimentos/submit.html')

@main_bp.route('/<path:slug>')
def pagina_dinamica(slug: str):
    """
    Definição de pagina_dinamica.
    Componente essencial para a arquitetura do sistema.
    """
    page = Pagina.query.filter_by(slug=slug, ativo=True).first_or_404()
    
    if not page.template_path:
        abort(404)

    template_path = page.template_path
    content_id = slug
    
    if page.tipo == 'servico':
        if not template_path.startswith('areas_atuacao/'):
            template_path = f'areas_atuacao/{template_path}'

    return render_page(template_path, content_id, disable_scroll_snap=True)