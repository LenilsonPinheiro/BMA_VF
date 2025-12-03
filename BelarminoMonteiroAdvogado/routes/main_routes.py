# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, url_for, abort, current_app, jsonify, Response
from .. import db, render_page
from ..models import AreaAtuacao, MembroEquipe, Depoimento, ConteudoGeral, User, Pagina, ClienteParceiro, SetorAtendido, HomePageSection, CustomHomeSection, ThemeSettings
from ..forms import ContactForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image

main_bp = Blueprint('main', __name__)
"""
Blueprint para rotas principais e públicas do site.
Controla o fluxo de navegação, carregamento de conteúdo dinâmico e interação com formulários públicos.
"""

def allowed_file(filename: str) -> bool:
    """
    Verifica se a extensão do arquivo é permitida para upload, conforme configurado na aplicação.

    Args:
        filename (str): O nome do arquivo a ser verificado.

    Returns:
        bool: True se a extensão for permitida, False caso contrário.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def home():
    """
    Renderiza a página inicial do site, selecionando dinamicamente o template de acordo com o tema.
    Carrega as seções da homepage, áreas de atuação, depoimentos e clientes/parceiros.
    """
    current_app.logger.info("Acessando a página inicial.")
    
    # --- Seleção Dinâmica do Template ---
    # Busca a configuração de tema atual do banco de dados para determinar qual layout usar.
    theme_settings = ThemeSettings.query.first()
    theme = theme_settings.theme if theme_settings else 'option1' # Padrão para 'option1' se não houver configuração.

    # Constrói o nome do template da homepage com base no tema selecionado.
    template_name = f'home/home_{theme}.html'
    
    # --- Carregamento de Seções da Home Page ---
    # Busca todas as seções da Home Page que estão ativas, excluindo a seção 'hero' (tratada separadamente).
    other_sections = HomePageSection.query.filter(
        HomePageSection.section_type != 'hero',
        HomePageSection.is_active == True
    ).all()
    
    # Busca as seções customizadas que estão ativas.
    active_custom_sections = CustomHomeSection.query.filter_by(is_active=True).all()

    # Adiciona um atributo 'type' para diferenciação no template (pré-definida vs customizada).
    for s in other_sections:
        s.type = 'predefined'
    for s in active_custom_sections:
        s.type = 'custom'

    # Combina e ordena todas as seções (exceto a 'hero') pela sua ordem de exibição.
    all_sections = sorted(other_sections + active_custom_sections, key=lambda x: x.order)

    # Prepara o contexto extra que será passado para a página inicial.
    form = ContactForm()
    extra_context = {
        'form': form,
        'all_home_sections': all_sections,
        'lista_areas_atuacao': AreaAtuacao.query.group_by(AreaAtuacao.titulo, AreaAtuacao.slug).order_by(AreaAtuacao.ordem).all(),
        'testimonials': Depoimento.query.filter_by(aprovado=True).order_by(Depoimento.data_criacao.desc()).all(),
        'all_clients': ClienteParceiro.query.order_by(ClienteParceiro.nome).all(),
        'team': MembroEquipe.query.order_by(MembroEquipe.nome).all()
    }
    # Renderiza a página usando a função render_page, que busca o conteúdo dinâmico.
    return render_page(template_name, 'home', **extra_context)

@main_bp.route('/politica-de-privacidade')
def politica_privacidade():
    """
    Renderiza a página de política de privacidade.
    O conteúdo desta página é gerenciado dinamicamente via ConteudoGeral.
    """
    current_app.logger.info("Acessando a página de Política de Privacidade.")
    return render_page('politica_privacidade.html', 'politica_privacidade')


@main_bp.route('/areas-de-atuacao')
def todas_areas_atuacao():
    """
    Renderiza a página que lista todas as áreas de atuação do escritório.
    As áreas são carregadas do banco de dados e exibidas em uma ordem definida.
    """
    current_app.logger.info("Acessando a página 'Todas as Áreas de Atuação'.")
    areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
    # disable_scroll_snap é uma flag para o template, se necessário.
    return render_page('areas_atuacao/todas_areas.html', 'todas_areas', areas=areas, disable_scroll_snap=True)

@main_bp.route('/contato', methods=['GET', 'POST'])
def pagina_contato():
    """
    Renderiza a página de contato e processa as submissões do formulário de contato.
    Envia e-mails utilizando as configurações SMTP armazenadas no banco de dados.
    """
    form = ContactForm()
    
    if form.validate_on_submit():
        nome = form.name.data
        email = form.email.data
        assunto = form.subject.data if form.subject.data else "Nova Mensagem de Contato do Site"
        mensagem = form.message.data

        current_app.logger.info(f"Recebida submissão de formulário de contato de {nome} ({email}).")

        # Busca as configurações de e-mail do banco de dados
        email_settings_db = ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()
        email_config = {item.secao: item.conteudo for item in email_settings_db}

        # Extrai as configurações, com valores padrão seguros em caso de ausência no DB
        SMTP_SERVER = email_config.get('smtp_server')
        try:
            SMTP_PORT = int(email_config.get('smtp_port') or 587)
        except (ValueError, TypeError):
            SMTP_PORT = 587
            current_app.logger.warning("Porta SMTP inválida no DB. Usando padrão 587.")
        SMTP_USER = email_config.get('smtp_user')
        SMTP_PASS = email_config.get('smtp_pass')
        EMAIL_TO = email_config.get('email_to', 'contato@belarminomonteiroadvogado.com.br')

        # Verifica se as configurações essenciais estão presentes
        if not all([SMTP_SERVER, SMTP_USER, SMTP_PASS]):
            current_app.logger.error("Configurações SMTP incompletas no banco de dados. Não foi possível enviar e-mail.")
            return jsonify({'success': False, 'message': 'Ocorreu um erro interno. As configurações de e-mail do servidor estão incompletas. Por favor, entre em contato.'}), 500

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"[{current_app.config.get('SITE_NAME', 'Site Contato')}] {assunto}" # Adiciona nome do site ao assunto
        msg['Reply-To'] = email # Permite responder diretamente ao remetente

        body = f"""Você recebeu uma nova mensagem de contato do site:

Nome: {nome}
Email: {email}
Assunto: {assunto}

Mensagem:
{mensagem}

---
Enviado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
IP do Remetente: {request.remote_addr}
"""
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls() # Inicia a segurança TLS (Transport Layer Security)
                server.login(SMTP_USER, SMTP_PASS) # Autentica no servidor SMTP
                text = msg.as_string()
                server.sendmail(SMTP_USER, EMAIL_TO, text) # Envia o e-mail
            current_app.logger.info(f"E-mail de contato enviado com sucesso de {email} para {EMAIL_TO}.")
            return jsonify({'success': True, 'message': 'Sua mensagem foi enviada com sucesso! Agradecemos o contato e responderemos em breve.'})
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar e-mail de contato de {email}: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Ocorreu um erro ao tentar enviar sua mensagem. Por favor, verifique seus dados ou tente novamente mais tarde.'}), 500

    current_app.logger.debug("Página de contato renderizada (GET ou validação falhou).")
    return render_page('contato/contato.html', 'contato', form=form)

@main_bp.route('/search')
def search():
    """
    Executa uma busca por áreas de atuação e setores atendidos com base em uma consulta do usuário.
    Retorna uma página com os resultados da busca.
    """
    query = request.args.get('q', '').strip()
    current_app.logger.info(f"Busca realizada com a query: '{query}'")
    results = []
    if query:
        # Busca em Áreas de Atuação
        areas_encontradas = AreaAtuacao.query.filter(AreaAtuacao.titulo.ilike(f'%{query}%')).all()
        for area in areas_encontradas:
            results.append({'titulo': area.titulo, 'url': url_for('main.pagina_dinamica', slug=area.slug), 'descricao': area.descricao, 'tipo': 'Área de Atuação'})

        # Busca em Setores Atendidos
        setores_encontrados = SetorAtendido.query.filter(SetorAtendido.titulo.ilike(f'%{query}%')).all()
        for setor in setores_encontrados:
            results.append({'titulo': setor.titulo, 'url': url_for('main.pagina_dinamica', slug=setor.slug), 'descricao': f"Assessoria jurídica especializada para o setor de {setor.titulo}.", 'tipo': 'Setor Atendido'})
            
        current_app.logger.debug(f"Encontrados {len(results)} resultados para a query '{query}'.")

    return render_template('search_results.html', query=query, results=results)

@main_bp.route('/service-worker.js')
def service_worker():
    """
    Serve o arquivo `service-worker.js` com os cabeçalhos HTTP corretos para registro.
    Essencial para funcionalidades PWA (Progressive Web App) e cache offline.
    """
    current_app.logger.debug("Servindo service-worker.js.")
    response = current_app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/' # Permite que o Service Worker controle todo o escopo do site
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate' # Garante que o service worker seja sempre atualizado
    return response

@main_bp.route('/robots.txt')
def robots_txt():
    """
    Gera e serve o arquivo `robots.txt` dinamicamente.
    Controla como os rastreadores de motores de busca devem indexar o site.
    """
    current_app.logger.debug("Gerando robots.txt.")
    response_text = render_template('robots.txt')
    response = Response(response_text, mimetype='text/plain')
    return response

@main_bp.route('/sitemap.xml')
def sitemap():
    """
    Gera e serve o arquivo `sitemap.xml` dinamicamente com todas as URLs do site.
    Ajuda os motores de busca a descobrir todas as páginas relevantes do site.
    """
    current_app.logger.debug("Gerando sitemap.xml.")
    urls = []
    today = datetime.now().strftime('%Y-%m-%d')

    # Adiciona as páginas dinâmicas principais ao sitemap
    pages = Pagina.query.filter_by(ativo=True).all()
    for page in pages:
        # Ignora grupos de menu que não são links reais ou páginas sem template.
        if page.tipo == 'grupo_menu' or not page.template_path:
            continue
        
        # Lógica para URLs externas vs. internas
        if page.slug == 'home':
            loc = url_for('main.home', _external=True)
        else:
            loc = url_for('main.pagina_dinamica', slug=page.slug, _external=True)

        urls.append({
            'loc': loc,
            'lastmod': today,
            'changefreq': 'weekly', # Exemplo: frequência de mudança
            'priority': '0.8' if page.slug == 'home' else '0.6' # Exemplo: prioridade de indexação
        })

    sitemap_xml = render_template('sitemap.xml', urls=urls)
    return Response(sitemap_xml, mimetype='application/xml')

@main_bp.route('/depoimento/submit/<token>', methods=['GET', 'POST'])
def submit_depoimento(token: str):
    """
    Permite a submissão de um depoimento de cliente através de um link de token único.
    Valida o token, processa os dados do formulário e o logo do cliente.
    """
    current_app.logger.info(f"Acessando submissão de depoimento com token: {token}")
    depoimento_entry = Depoimento.query.filter_by(token_submissao=token, aprovado=False).first()

    if not depoimento_entry:
        current_app.logger.warning(f"Tentativa de acesso com token inválido ou depoimento já processado: {token}")
        abort(404) # Token inválido, já submetido ou aprovado

    if request.method == 'POST':
        current_app.logger.info(f"Recebida submissão POST para depoimento com token: {token}")
        depoimento_entry.nome_cliente = request.form.get('client_name')
        depoimento_entry.texto_depoimento = request.form.get('testimonial_text')
        
        file = request.files.get('client_logo')
        if file and file.filename != '':
            from ..image_processor import save_logo # Importa localmente para evitar circular
            try:
                # Usa a função save_logo do image_processor para otimização e salvamento.
                # O nome do arquivo será baseado no nome do cliente e token.
                logo_filename_base = secure_filename(f"{depoimento_entry.nome_cliente}_{token[:8]}")
                logo_path_relative = save_logo(file, logo_filename_base)
                
                if logo_path_relative:
                    depoimento_entry.logo_cliente = logo_path_relative
                    current_app.logger.info(f"Logo do cliente salvo para depoimento {token}: {logo_path_relative}")
                else:
                    current_app.logger.warning(f"Falha ao salvar/otimizar logo para depoimento {token}. Nenhuma imagem anexada.")
                    # Opcional: flash('Erro ao salvar logo. Tente novamente.', 'danger')
            except Exception as e:
                current_app.logger.error(f"Erro ao processar logo para depoimento {token}: {e}", exc_info=True)
                # Opcional: flash('Erro no processamento da imagem.', 'danger')
        
        db.session.commit()
        current_app.logger.info(f"Depoimento com token {token} submetido e salvo.")
        return render_template('depoimentos/thank_you.html')

    return render_template('depoimentos/submit.html')

@main_bp.route('/<path:slug>')
def pagina_dinamica(slug: str):
    """
    Rota genérica para renderizar páginas dinâmicas com base no seu slug.
    Busca a página no banco de dados, verifica seu status e template,
    e renderiza-a com o conteúdo dinâmico.
    """
    current_app.logger.info(f"Acessando página dinâmica com slug: '{slug}'")
    page = Pagina.query.filter_by(slug=slug, ativo=True).first_or_404()
    
    # Se a página não tiver um template associado (ex: um grupo de menu),
    # significa que não é uma página renderizável diretamente.
    if not page.template_path:
        current_app.logger.warning(f"Tentativa de acessar página dinâmica '{slug}' sem template_path. Abortando com 404.")
        abort(404)

    template_path = page.template_path
    content_id = slug # Por padrão, o identificador de conteúdo é o próprio slug da página
    
    # Lógica específica para páginas de serviço, que podem ter um template padrão
    # e um identificador de conteúdo diferente se forem geradas a partir de AreaAtuacao.
    if page.tipo == 'servico':
        # Para serviços, o content_id é o slug do serviço, que corresponde ao 'pagina' em ConteudoGeral.
        if not template_path.startswith('areas_atuacao/'):
            # Garante que templates de serviço usem o prefixo correto se não for especificado.
            template_path = f'areas_atuacao/{template_path}'
        current_app.logger.debug(f"Página '{slug}' é do tipo 'servico'. Usando template '{template_path}'.")
    else:
        current_app.logger.debug(f"Página '{slug}' é do tipo '{page.tipo}'. Usando template '{template_path}'.")

    return render_page(template_path, content_id, disable_scroll_snap=True)