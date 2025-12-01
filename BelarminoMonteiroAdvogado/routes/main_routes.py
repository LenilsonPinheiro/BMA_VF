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

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/')
def home():
    # --- Dynamic Template Selection ---
    theme_settings = ThemeSettings.query.first()
    theme = theme_settings.theme if theme_settings else 'option1'

    if theme == 'option4':
        template_name = 'home/home_option4.html'
    elif theme == 'option3':
        template_name = 'home/home_option3.html'
    elif theme == 'option2':
        template_name = 'home/home_option2.html'
    else:
        # Default to option1 layout for option1
        template_name = 'home/home_option1.html'
    # --- End of Dynamic Template Selection ---

    # Busca as outras seções da home page que estão ativas e ordenadas
    other_sections = HomePageSection.query.filter(
        HomePageSection.section_type != 'hero',
        HomePageSection.is_active == True
    ).all()
    active_custom_sections = CustomHomeSection.query.filter_by(is_active=True).all()

    # Adiciona um atributo 'type' para diferenciação no template
    for s in other_sections:
        s.type = 'predefined'
    for s in active_custom_sections:
        s.type = 'custom'

    # Combina e ordena todas as seções, exceto a 'hero'
    all_sections = sorted(other_sections + active_custom_sections, key=lambda x: x.order)

    # Prepara o contexto extra que será passado para a página
    form = ContactForm()
    extra_context = {
        'form': form,
        'all_home_sections': all_sections,
        'lista_areas_atuacao': AreaAtuacao.query.group_by(AreaAtuacao.titulo, AreaAtuacao.slug).order_by(AreaAtuacao.ordem).all(),
        'testimonials': Depoimento.query.filter_by(aprovado=True).order_by(Depoimento.data_criacao.desc()).all(),
        'all_clients': ClienteParceiro.query.order_by(ClienteParceiro.nome).all(),
        'team': MembroEquipe.query.order_by(MembroEquipe.nome).all()
    }
    return render_page(template_name, 'home', **extra_context)

@main_bp.route('/politica-de-privacidade')
def politica_privacidade():
    """Renderiza a página de política de privacidade."""
    return render_page('politica_privacidade.html', 'politica_privacidade')


@main_bp.route('/areas-de-atuacao')
def todas_areas_atuacao():
    """Renderiza a página com todas as áreas de atuação."""
    areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
    return render_page('areas_atuacao/todas_areas.html', 'todas_areas', areas=areas, disable_scroll_snap=True)

@main_bp.route('/contato', methods=['GET', 'POST'])
def pagina_contato():
    form = ContactForm()
    if form.validate_on_submit():
        nome = form.name.data
        email = form.email.data
        assunto = "Novo Contato do Site"
        mensagem = form.message.data

        # Busca as configurações de e-mail do banco de dados
        email_settings_db = ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()
        email_config = {item.secao: item.conteudo for item in email_settings_db}

        SMTP_SERVER = email_config.get('smtp_server', 'smtp.example.com')
        try:
            SMTP_PORT = int(email_config.get('smtp_port', 587))
        except (ValueError, TypeError):
            SMTP_PORT = 587
        SMTP_USER = email_config.get('smtp_user', 'seu-email@example.com')
        SMTP_PASS = email_config.get('smtp_pass', '')
        EMAIL_TO = email_config.get('email_to', 'contato@belarmimonteiroadvogado.com.br')

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"Novo Contato do Site: {assunto}"

        body = f"""Você recebeu uma nova mensagem de contato:

Nome: {nome}
Email: {email}

Mensagem:
{mensagem}"""
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            text = msg.as_string()
            server.sendmail(SMTP_USER, EMAIL_TO, text)
            server.quit()
            return jsonify({'success': True, 'message': 'Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.'})
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Ocorreu um erro ao tentar enviar sua mensagem. Por favor, tente novamente mais tarde.'}), 500

    return render_page('contato/contato.html', 'contato', form=form)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        areas_encontradas = AreaAtuacao.query.filter(AreaAtuacao.titulo.ilike(f'%{query}%')).all()
        for area in areas_encontradas:
            results.append({'titulo': area.titulo, 'url': url_for('main.pagina_dinamica', slug=area.slug), 'descricao': area.descricao})

        setores_encontrados = SetorAtendido.query.filter(SetorAtendido.titulo.ilike(f'%{query}%')).all()
        for setor in setores_encontrados:
            results.append({'titulo': setor.titulo, 'url': url_for('main.pagina_dinamica', slug=setor.slug), 'descricao': f"Assessoria jurídica especializada para o setor de {setor.titulo}."})

    return render_template('search_results.html', query=query, results=results)

@main_bp.route('/service-worker.js')
def service_worker():
    """Serve o Service Worker com headers corretos."""
    response = current_app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@main_bp.route('/robots.txt')
def robots_txt():
    """Gera o robots.txt dinamicamente."""
    response_text = render_template('robots.txt')
    response = Response(response_text, mimetype='text/plain')
    return response

@main_bp.route('/sitemap.xml')
def sitemap():
    """Gera o sitemap.xml dinamicamente."""
    urls = []
    today = datetime.now().strftime('%Y-%m-%d')

    # Páginas estáticas principais
    pages = Pagina.query.filter_by(ativo=True).all()
    for page in pages:
        # Ignora grupos de menu que não são links reais
        if page.tipo == 'grupo_menu':
            continue
        
        # A rota home é um caso especial
        if page.slug == 'home':
            loc = url_for('main.home', _external=True)
        else:
            loc = url_for('main.pagina_dinamica', slug=page.slug, _external=True)

        urls.append({
            'loc': loc,
            'lastmod': today
        })

    sitemap_xml = render_template('sitemap.xml', urls=urls)
    return Response(sitemap_xml, mimetype='application/xml')

@main_bp.route('/depoimento/submit/<token>', methods=['GET', 'POST'])
def submit_depoimento(token):
    depoimento_entry = Depoimento.query.filter_by(token_submissao=token, aprovado=False).first()

    if not depoimento_entry:
        abort(404) # Token inválido ou depoimento já submetido/aprovado

    if request.method == 'POST':
        depoimento_entry.nome_cliente = request.form.get('client_name')
        depoimento_entry.texto_depoimento = request.form.get('testimonial_text')
        
        file = request.files.get('client_logo')
        if file and allowed_file(file.filename):
            # Processar e salvar o logo do cliente
            img = Image.open(file.stream)
            # Garante que a imagem seja convertida para ter um fundo branco (se for PNG com transparência)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, '#FFF')
                background.paste(img, img.split()[-1])
                img = background
            
            # Redimensiona para uma altura padrão, mantendo a proporção
            target_height = 100
            w_percent = (target_height / float(img.size[1]))
            h_size = target_height
            w_size = int((float(img.size[0]) * float(w_percent)))
            img = img.resize((w_size, h_size), Image.LANCZOS)

            filename = secure_filename(f"logo_{depoimento_entry.id}.webp")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            img.save(filepath, 'WEBP', quality=80)
            depoimento_entry.logo_cliente = os.path.join('images/uploads', filename).replace('\\', '/')
        
        db.session.commit()
        return render_template('depoimentos/thank_you.html')

    return render_template('depoimentos/submit.html')

# MODIFICAÇÃO: Rota movida para o final para não sombrear rotas específicas
@main_bp.route('/<path:slug>')
def pagina_dinamica(slug):
    """Rota genérica para renderizar páginas dinâmicas com base no slug."""
    page = Pagina.query.filter_by(slug=slug, ativo=True).first_or_404()
    
    # Se a página não tiver um template (ex: um grupo de menu), é um 404.
    if not page.template_path:
        abort(404)

    template_path = page.template_path
    
    if page.tipo == 'servico':
        # CORREÇÃO: O identificador de conteúdo deve ser o próprio slug,
        # que é como ele está salvo no dicionário 'default_content'.
        content_id = slug
        if not template_path.startswith('areas_atuacao/'):
            template_path = f'areas_atuacao/{template_path}'
    else:
        content_id = slug

    return render_page(template_path, content_id, disable_scroll_snap=True)