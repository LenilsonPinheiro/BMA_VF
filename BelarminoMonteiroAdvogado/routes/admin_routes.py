# BelarminoMonteiroAdvogado/routes/admin_routes.py
# -*- coding: utf-8 -*-
"""
==============================================================================
Rotas do Painel Administrativo (`/admin`)
==============================================================================

Este módulo define todas as rotas relacionadas ao painel de administração
do site. Ele é registrado como um Blueprint e todas as suas rotas são
prefixadas com `/admin`.

O acesso a todas as rotas é protegido pela anotação `@login_required`,
garantindo que apenas usuários autenticados possam acessá-las.

Funcionalidades Principais:
---------------------------
- **Dashboard Central:** Uma visão geral que agrega todas as funcionalidades
  de gerenciamento.
- **Gerenciamento de Conteúdo:** Rotas para criar, editar, excluir e reordenar
  entidades como Páginas, Áreas de Atuação, Membros da Equipe, Depoimentos, etc.
- **Gerenciamento de Aparência:** Rotas para selecionar o tema visual do site
  e personalizar a paleta de cores.
- **Configurações:** Gerenciamento de configurações de e-mail e segurança, como
  a alteração de senha do administrador.
- **Upload de Arquivos:** Lógica para lidar com o upload de imagens e outros
  arquivos, incluindo otimização automática.
- **Rotas de Compatibilidade:** Redirecionamentos de URLs antigas para as novas,
  garantindo que links legados não quebrem.

A maior parte da lógica de negócios do painel administrativo está contida
neste arquivo, interagindo diretamente com os modelos do banco de dados
e os formulários de WTForms.
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
import secrets
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from ..models import (
    db, Pagina, ConteudoGeral, AreaAtuacao, MembroEquipe, User, Depoimento, 
    ClienteParceiro, HomePageSection, ThemeSettings
)
from ..forms import (
    ChangePasswordForm, ThemeForm, DesignForm, MembroEquipeForm as TeamMemberForm
)
from ..image_processor import save_logo, process_and_save_image, image_processor

admin_bp = Blueprint('admin', __name__)

# --- HELPERS E FORMS ---

class EmptyForm(FlaskForm):
    """
    Formulário vazio genérico, usado principalmente para satisfazer a necessidade de
    `{{ form.hidden_tag() }}` em templates Jinja2 que precisam de proteção CSRF,
    mas não possuem campos de formulário explícitos.
    """
    pass

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

def save_admin_upload(file, secao_name: str, page_identifier: str) -> tuple[bool, str]:
    """
    Processa e salva um arquivo enviado pelo painel, otimizando se for uma imagem.

    Esta função centraliza a lógica de upload de arquivos para o `ConteudoGeral`.
    Ela verifica a permissão do arquivo, gera um nome único, utiliza o
    `ImageProcessor` para otimizar imagens, e atualiza ou cria o registro
    correspondente no banco de dados com o caminho do novo arquivo.

    Args:
        file (werkzeug.datastructures.FileStorage): O objeto de arquivo do formulário.
        secao_name (str): O nome da seção de `ConteudoGeral` a ser atualizada.
        page_identifier (str): O identificador da página (`ConteudoGeral.pagina`).

    Returns:
        tuple[bool, str]: Uma tupla contendo (sucesso, mensagem de status).
    """
    if not file or not file.filename:
        current_app.logger.warning("Tentativa de salvar upload sem arquivo ou nome de arquivo. Seção: %s, Página: %s", secao_name, page_identifier)
        return False, "Nenhum arquivo ou nome de arquivo inválido."
    
    if not allowed_file(file.filename):
        current_app.logger.warning("Arquivo com extensão não permitida. Seção: %s, Página: %s, Arquivo: %s", secao_name, page_identifier, file.filename)
        return False, "Tipo de arquivo não permitido."
    
    try:
        original_filename = secure_filename(file.filename)
        # Gera um nome de arquivo único para evitar colisões e problemas de cache.
        unique_filename_base = f"{secao_name}_{secrets.token_hex(4)}"
        
        # Usa o image_processor se for uma imagem permitida, caso contrário, salva diretamente.
        # As extensões permitidas já são definidas em ALLOWED_EXTENSIONS
        # image_processor.process_and_save_image já lida com WebP e otimização
        
        upload_path_relative_to_static = Path(current_app.config['UPLOAD_FOLDER']).relative_to(Path(current_app.static_folder))
        final_file_path_relative = None
        
        # Tenta otimizar se for uma imagem, senão salva o arquivo original
        if original_filename.lower().endswith(tuple(['.png', '.jpg', '.jpeg', '.webp', '.gif'])):
            # A função save_logo já lida com a otimização e retorna o caminho relativo
            final_file_path_relative = save_logo(file, unique_filename_base)
            if not final_file_path_relative:
                raise Exception("Falha ao otimizar e salvar a imagem.")
        else:
            # Para outros tipos de arquivo (ex: .ico, .mp4, .webm)
            full_upload_folder = Path(current_app.static_folder) / upload_path_relative_to_static
            full_upload_folder.mkdir(parents=True, exist_ok=True)
            
            final_filename = f"{unique_filename_base}{Path(file.filename).suffix}"
            final_absolute_path = full_upload_folder / final_filename
            file.save(str(final_absolute_path))
            final_file_path_relative = str(upload_path_relative_to_static / final_filename).replace('\\', '/')
        
        if not final_file_path_relative:
            raise Exception("Caminho final do arquivo não gerado.")

        # Atualiza o ConteudoGeral no banco de dados com o novo caminho do arquivo.
        item = ConteudoGeral.query.filter_by(pagina=page_identifier, secao=secao_name).first()
        if item:
            item.conteudo = final_file_path_relative
            db.session.add(item)
            current_app.logger.info(f"Conteúdo '{secao_name}' da página '{page_identifier}' atualizado com o arquivo: {final_file_path_relative}")
        else:
            new_content = ConteudoGeral(pagina=page_identifier, secao=secao_name, conteudo=final_file_path_relative)
            db.session.add(new_content)
            current_app.logger.info(f"Novo ConteudoGeral '{secao_name}' criado para a página '{page_identifier}' com o arquivo: {final_file_path_relative}")
        
        return True, "Upload e atualização realizados com sucesso."
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar upload para seção '{secao_name}' da página '{page_identifier}': {str(e)}", exc_info=True)
        return False, f"Erro interno ao processar o upload: {str(e)}"

# --- ROTAS DE COMPATIBILIDADE (FIX CRÍTICO) ---
# Estas rotas redirecionam links antigos do template para o novo local,
# garantindo que URLs legadas não quebrem a experiência do usuário.
@admin_bp.route('/manage-areas')
@login_required
def manage_areas():
    """
    Redireciona a rota antiga de gerenciamento de áreas para o dashboard de serviços.
    """
    current_app.logger.info("Redirecionando de /manage-areas para /dashboard?page=Services")
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/manage-team')
@login_required
def manage_team():
    """
    Redireciona a rota antiga de gerenciamento de equipe para o dashboard de equipe.
    """
    current_app.logger.info("Redirecionando de /manage-team para /dashboard?page=Team")
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/manage-clients')
@login_required
def manage_clients():
    """
    Redireciona a rota antiga de gerenciamento de clientes para o dashboard de clientes.
    """
    current_app.logger.info("Redirecionando de /manage-clients para /dashboard?page=Clients")
    return redirect(url_for('admin.dashboard', page='Clients'))

# --- ROTAS PRINCIPAIS ---

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Renderiza o painel administrativo principal.
    
    Carrega dinamicamente o conteúdo e as opções de gerenciamento com base na página selecionada.
    Exibe formulários para alterar senha, tema, e gerenciar seções da homepage, serviços,
    membros da equipe, depoimentos e clientes/parceiros.
    """
    # Determina qual sub-seção do dashboard será exibida com base no parâmetro 'page' da URL.
    selected_page = request.args.get('page', 'configuracoes_gerais')
    
    # Carrega o conteúdo específico para a página selecionada do modelo ConteudoGeral.
    content_for_page = ConteudoGeral.query.filter_by(pagina=selected_page).all() if selected_page else []
    
    # Lista de todas as 'páginas' de ConteudoGeral existentes para navegação no painel.
    # Usa distinct para evitar duplicatas e carrega apenas o campo 'pagina'.
    all_content_pages = [r[0] for r in db.session.query(ConteudoGeral.pagina).distinct().all()]
    
    # Carrega as páginas principais para o menu de navegação do admin (sem filhos).
    nav_pages = Pagina.query.filter(Pagina.parent_id.is_(None)).order_by(Pagina.ordem).all()
    
    # Carrega configurações de e-mail e tema.
    email_settings = {i.secao: i for i in ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()}
    theme_settings = ThemeSettings.query.first()
    
    # Instancia os formulários a serem utilizados no dashboard.
    password_form = ChangePasswordForm()
    theme_form = ThemeForm()
    design_form = DesignForm() # Incluindo o DesignForm
    
    # Cria um formulário vazio para satisfazer {{ form.hidden_tag() }} no template dashboard.html
    # Isso é necessário para proteção CSRF em seções que não possuem um formulário específico.
    generic_form = EmptyForm()
    
    # Preenche o ThemeForm com o tema atualmente selecionado, se existir.
    if theme_settings: 
        theme_form.theme.data = theme_settings.theme
        # Preenche o DesignForm com as cores atuais do tema
        for field in design_form:
            if hasattr(theme_settings, field.name):
                field.data = getattr(theme_settings, field.name)

    current_app.logger.info(f"Acessando dashboard, página selecionada: {selected_page}")

    return render_template('admin/dashboard.html', 
                           selected_page=selected_page,
                           content_for_page=content_for_page,
                           all_content_pages=all_content_pages,
                           nav_pages_admin=nav_pages,
                           home_sections_list=HomePageSection.query.order_by(HomePageSection.order).all(),
                           email_settings_dict=email_settings,
                           all_services=AreaAtuacao.query.order_by(AreaAtuacao.titulo).all(),
                           all_team=MembroEquipe.query.order_by(MembroEquipe.nome).all(),
                           all_testimonials=Depoimento.query.filter(Depoimento.aprovado==True).order_by(Depoimento.data_criacao.desc()).all(), # Adicionado filtro por aprovado
                           all_pending_testimonials=Depoimento.query.filter(Depoimento.aprovado==False).order_by(Depoimento.data_criacao.desc()).all(), # Depoimentos pendentes
                           all_clients=ClienteParceiro.query.order_by(ClienteParceiro.nome).all(),
                           password_form=password_form,
                           theme_form=theme_form,
                           design_form=design_form, # Passando o DesignForm
                           form=generic_form, 
                           all_content=ConteudoGeral.query.all())

# Rota para reordenar seções da home (nome alinhado com o template)
@admin_bp.route('/reorder-home-sections', methods=['POST'])
@login_required
def reorder_home_sections():
    """
    Atualiza a ordem de exibição das seções da página inicial.
    Recebe uma lista ordenada de IDs de seções via AJAX e persiste as mudanças no DB.
    """
    try:
        data = json.loads(request.form.get('order'))
        current_app.logger.info(f"Recebida solicitação para reordenar seções da Home: {data}")
        for item in data:
            s = HomePageSection.query.get(int(item['id']))
            if s: 
                s.order = item['order']
                db.session.add(s) # Marca o objeto para ser persistido
        db.session.commit()
        flash('Ordem das seções da Home atualizada com sucesso!', 'success')
        current_app.logger.info("Ordem das seções da Home atualizada com sucesso.")
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reordenar seções da Home: {e}', 'danger')
        current_app.logger.error(f"Erro ao reordenar seções da Home: {e}", exc_info=True)
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/update-content', methods=['POST'])
@login_required
def update_content():
    """
    Atualiza o conteúdo de uma página específica, seja texto ou arquivos de mídia.
    Processa campos de texto de formulário e uploads de arquivos, otimizando imagens.
    """
    page_identifier = request.form.get('page_identifier')
    current_app.logger.info(f"Iniciando atualização de conteúdo para a página: {page_identifier}")
    try:
        # Processa campos de texto
        for key, value in request.form.items():
            if key.startswith('content-'):
                try:
                    # O ID do ConteudoGeral é extraído do nome do campo 'content-<id>'
                    item_id = int(key.split('-')[1])
                    item = ConteudoGeral.query.get(item_id)
                    if item: 
                        item.conteudo = value
                        db.session.add(item)
                        current_app.logger.debug(f"Conteúdo de texto '{item.secao}' atualizado para '{page_identifier}'.")
                except ValueError:
                    current_app.logger.warning(f"Campo de conteúdo inválido encontrado: {key}. Ignorando.")
                except Exception as e:
                    current_app.logger.error(f"Erro ao atualizar campo de texto '{key}' para '{page_identifier}': {e}", exc_info=True)
        
        # Processa uploads de arquivos
        for key, file in request.files.items():
            if file and file.filename != '':
                if key.startswith('content-'):
                    try:
                        item_id = int(key.split('-')[1])
                        item = ConteudoGeral.query.get(item_id)
                        if item:
                            # Otimiza e salva a imagem, atualizando o campo 'conteudo' com o novo caminho.
                            # A função `process_and_save_image` agora é um alias para `optimize_uploaded_image`
                            # que retorna (success, path, message).
                            success, file_path, msg = process_and_save_image(file, current_app.config['UPLOAD_FOLDER'])
                            if success:
                                item.conteudo = file_path # Caminho relativo já retornado
                                db.session.add(item)
                                current_app.logger.info(f"Arquivo '{item.secao}' atualizado e otimizado para '{page_identifier}': {file_path}")
                            else:
                                flash(f"Falha ao processar arquivo para {item.secao}: {msg}", 'danger')
                                current_app.logger.warning(f"Falha ao processar arquivo '{item.secao}' para '{page_identifier}': {msg}")
                    except ValueError:
                        current_app.logger.warning(f"Campo de arquivo inválido encontrado: {key}. Ignorando.")
                    except Exception as e: 
                        flash(f"Erro ao salvar arquivo para campo {key}: {e}", 'danger')
                        current_app.logger.error(f"Erro ao salvar arquivo '{key}' para '{page_identifier}': {e}", exc_info=True)
                else:
                    # Caso para uploads genéricos que não são ConteudoGeral direto, como logos de configuração
                    success, msg = save_admin_upload(file, key.replace('_file', ''), page_identifier)
                    if not success: 
                        flash(msg, 'warning')
                        current_app.logger.warning(f"Falha no upload genérico para '{key}' na página '{page_identifier}': {msg}")
        
        db.session.commit()
        flash('Conteúdo atualizado com sucesso!', 'success')
        current_app.logger.info(f"Conteúdo da página '{page_identifier}' atualizado com sucesso.")
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar conteúdo: {e}', 'danger')
        current_app.logger.error(f"Erro ao atualizar conteúdo para '{page_identifier}': {e}", exc_info=True)
    return redirect(url_for('admin.dashboard', page=page_identifier))

@admin_bp.route('/update-nav-order', methods=['POST'])
@login_required
def update_nav_order():
    """
    Atualiza a ordem e a hierarquia (parent_id) das páginas de navegação.
    Recebe uma estrutura de dados JSON com os IDs das páginas, suas ordens e IDs de pais.
    """
    try:
        data = json.loads(request.form.get('order'))
        current_app.logger.info(f"Recebida solicitação para reordenar navegação: {data}")
        for item in data:
            p = Pagina.query.get(int(item['id']))
            if p:
                p.ordem = item['order']
                p.parent_id = int(item['parent_id']) if item.get('parent_id') else None
                db.session.add(p) # Marca o objeto para ser persistido
        db.session.commit()
        flash('Menu de navegação atualizado com sucesso!', 'success')
        current_app.logger.info("Menu de navegação atualizado com sucesso.")
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao reordenar menu de navegação: {e}', 'danger')
        current_app.logger.error(f"Erro ao reordenar menu de navegação: {e}", exc_info=True)
    return redirect(url_for('admin.dashboard') + '#Navigation')

@admin_bp.route('/toggle-page-status/<int:id>/<string:field>', methods=['GET', 'POST'])
@login_required
def toggle_page_status(id: int, field: str):
    """
    Alterna o status de um campo booleano de uma página (ex: 'ativo', 'show_in_menu').
    
    Args:
        id (int): O ID da página a ser modificada.
        field (str): O nome do campo booleano ('ativo' ou 'show_in_menu').
    """
    p = Pagina.query.get_or_404(id)
    if field in ['ativo', 'show_in_menu']:
        old_status = getattr(p, field)
        setattr(p, field, not old_status)
        db.session.commit()
        flash(f'Status "{field}" da página "{p.titulo_menu}" alterado para {not old_status}.', 'success')
        current_app.logger.info(f"Status '{field}' da página '{p.titulo_menu}' (ID: {id}) alterado para {not old_status}.")
    else:
        flash(f'Campo "{field}" inválido para alternar status.', 'danger')
        current_app.logger.warning(f"Tentativa de alternar campo inválido '{field}' para página ID: {id}.")
    return redirect(url_for('admin.dashboard') + '#Navigation')

@admin_bp.route('/toggle-section-status/<int:id>', methods=['GET', 'POST'])
@login_required
def toggle_section_status(id: int):
    """
    Alterna o status de ativação de uma seção da página inicial.
    
    Args:
        id (int): O ID da seção da Home Page a ser modificada.
    """
    s = HomePageSection.query.get_or_404(id)
    old_status = s.is_active
    s.is_active = not old_status
    db.session.commit()
    flash(f'Seção "{s.title}" atualizada para {"ativa" if s.is_active else "inativa"}.', 'success')
    current_app.logger.info(f"Status da seção da Home '{s.title}' (ID: {id}) alterado para {s.is_active}.")
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/update-section-text', methods=['POST'])
@login_required
def update_section_text():
    """
    Atualiza o título e subtítulo de uma seção da página inicial.
    """
    section_id = request.form.get('section_id')
    current_app.logger.info(f"Recebida solicitação para atualizar texto da seção ID: {section_id}")
    s = HomePageSection.query.get_or_404(section_id)
    s.title = request.form.get('title')
    s.subtitle = request.form.get('subtitle')
    db.session.commit()
    flash('Texto da seção atualizado com sucesso!', 'success')
    current_app.logger.info(f"Texto da seção da Home '{s.title}' (ID: {section_id}) atualizado.")
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/add-area-atuacao', methods=['POST'])
@login_required
def add_area_atuacao():
    """
    Adiciona uma nova área de atuação ao sistema e cria uma página associada.
    """
    titulo = request.form.get('titulo')
    slug = request.form.get('slug')
    descricao = request.form.get('descricao')
    icone = request.form.get('icone')
    
    current_app.logger.info(f"Tentando adicionar nova área de atuação: '{titulo}' com slug '{slug}'.")

    if AreaAtuacao.query.filter_by(slug=slug).first():
        flash('Slug já existe. Por favor, escolha um slug único para a área de atuação.', 'danger')
        current_app.logger.warning(f"Falha ao adicionar área de atuação. Slug '{slug}' já existe.")
        return redirect(url_for('admin.dashboard', page='Services'))
    
    foto = None
    if request.files.get('foto'):
        try: 
            # save_logo já lida com otimização e nomes seguros
            foto = save_logo(request.files['foto'], secure_filename(slug)) 
            current_app.logger.info(f"Foto para área de atuação '{titulo}' salva: {foto}")
        except Exception as e: 
            current_app.logger.error(f"Erro ao salvar foto para área de atuação '{titulo}': {e}", exc_info=True)
            flash(f"Erro ao salvar imagem para a área de atuação: {e}", 'danger')
            
    nova_area = AreaAtuacao(
        titulo=titulo,
        slug=slug,
        descricao=descricao,
        icone=icone,
        foto=foto
    )
    db.session.add(nova_area)
    
    # Busca ou cria a página pai 'areas-de-atuacao'
    parent = Pagina.query.filter_by(slug='areas-de-atuacao').first()
    if not parent:
        # Cria um placeholder se a página pai não existir, o que não deveria acontecer se ensure_essential_data for executado.
        current_app.logger.warning("Página pai 'areas-de-atuacao' não encontrada. Criando placeholder.")
        parent = Pagina(slug='areas-de-atuacao', titulo_menu='Áreas de Atuação', tipo='grupo_menu', ativo=True, show_in_menu=False, ordem=3)
        db.session.add(parent)
        db.session.commit() # Commit para que o parent tenha um ID
        
    nova_pagina = Pagina(
        slug=slug,
        titulo_menu=titulo,
        tipo='servico',
        parent_id=parent.id, # Associa à página pai
        template_path='areas_atuacao/servico_base.html'
    )
    db.session.add(nova_pagina)
    
    db.session.commit()
    flash(f'Área de Atuação "{titulo}" criada com sucesso!', 'success')
    current_app.logger.info(f"Área de Atuação '{titulo}' (slug: {slug}) e página associada criadas.")
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/delete-area-atuacao', methods=['POST'])
@login_required
def delete_area_atuacao():
    """
    Exclui uma área de atuação, sua página associada e qualquer ConteudoGeral relacionado.
    """
    slug_to_delete = request.form.get('slug')
    current_app.logger.info(f"Tentando excluir área de atuação com slug: {slug_to_delete}")
    try:
        # Exclui a área de atuação
        area = AreaAtuacao.query.filter_by(slug=slug_to_delete).first()
        if area:
            db.session.delete(area)
            current_app.logger.debug(f"AreaAtuacao '{slug_to_delete}' excluída.")
        
        # Exclui a página associada
        pagina = Pagina.query.filter_by(slug=slug_to_delete).first()
        if pagina:
            db.session.delete(pagina)
            current_app.logger.debug(f"Página '{slug_to_delete}' excluída.")

        # Exclui ConteudoGeral relacionado
        conteudo_geral_itens = ConteudoGeral.query.filter_by(pagina=slug_to_delete).all()
        for item in conteudo_geral_itens:
            db.session.delete(item)
            current_app.logger.debug(f"ConteudoGeral '{item.secao}' para '{slug_to_delete}' excluído.")

        db.session.commit()
        flash(f'Área de Atuação "{slug_to_delete}" e conteúdo relacionado removidos com sucesso!', 'success')
        current_app.logger.info(f"Área de Atuação '{slug_to_delete}' e conteúdo relacionado removidos.")
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover área de atuação: {e}', 'danger')
        current_app.logger.error(f"Erro ao remover área de atuação '{slug_to_delete}': {e}", exc_info=True)
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/edit-service/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_service(slug: str):
    """
    Edita uma área de atuação existente e seu conteúdo associado.
    Permite atualizar detalhes da área, conteúdo de texto e imagens/mídias.
    """
    service_to_edit = AreaAtuacao.query.filter_by(slug=slug).first_or_404()
    current_app.logger.info(f"Acessando edição para serviço: '{slug}'")

    if request.method == 'POST':
        current_app.logger.info(f"Submissão POST para editar serviço: '{slug}'")
        service_to_edit.titulo = request.form['titulo']
        service_to_edit.descricao = request.form['descricao']
        service_to_edit.icone = request.form['icone']
        
        # Atualiza o título da página associada, se existir
        page_associated = Pagina.query.filter_by(slug=slug).first()
        if page_associated: 
            page_associated.titulo_menu = service_to_edit.titulo
            db.session.add(page_associated)
            current_app.logger.debug(f"Título da página '{slug}' atualizado para '{service_to_edit.titulo}'.")
        
        # Atualiza campos de ConteudoGeral (texto)
        for k, v in request.form.items():
            if k.startswith('content-'):
                secao_name = k.replace('content-', '')
                item = ConteudoGeral.query.filter_by(pagina=slug, secao=secao_name).first()
                if not item: # Se não existe, cria um novo item de conteúdo
                    item = ConteudoGeral(pagina=slug, secao=secao_name)
                item.conteudo = v
                db.session.add(item)
                current_app.logger.debug(f"Conteúdo de texto '{secao_name}' atualizado para serviço '{slug}'.")
                
        # Atualiza campos de ConteudoGeral (arquivos/imagens)
        for k, f in request.files.items():
            if f and f.filename != '' and k.startswith('content-'):
                secao_name = k.replace('content-', '')
                try:
                    # process_and_save_image retorna (success, path, message)
                    success, file_path, msg = process_and_save_image(f, current_app.config['UPLOAD_FOLDER'])
                    if success:
                        item = ConteudoGeral.query.filter_by(pagina=slug, secao=secao_name).first()
                        if not item:
                            item = ConteudoGeral(pagina=slug, secao=secao_name)
                        item.conteudo = file_path # Caminho relativo já retornado
                        db.session.add(item)
                        current_app.logger.info(f"Arquivo '{secao_name}' atualizado e otimizado para serviço '{slug}': {file_path}")
                    else:
                        flash(f"Falha ao processar arquivo para {secao_name}: {msg}", 'danger')
                        current_app.logger.warning(f"Falha ao processar arquivo '{secao_name}' para serviço '{slug}': {msg}")
                except Exception as e: 
                    flash(f"Erro ao salvar arquivo para campo {secao_name}: {e}", 'danger')
                    current_app.logger.error(f"Erro ao salvar arquivo '{secao_name}' para serviço '{slug}': {e}", exc_info=True)
                
        db.session.commit()
        flash(f'Área de Atuação "{service_to_edit.titulo}" atualizada com sucesso!', 'success')
        current_app.logger.info(f"Área de Atuação '{slug}' atualizada com sucesso.")
        return redirect(url_for('admin.dashboard', page='Services'))
        
    # GET request: prepara o contexto para o template de edição
    content = {i.secao: i.conteudo for i in ConteudoGeral.query.filter_by(pagina=slug).all()}
    return render_template('admin/edit_service.html', service=service_to_edit, service_content=content)

@admin_bp.route('/add-membro-equipe', methods=['POST'])
@login_required
def add_membro_equipe():
    """
    Adiciona um novo membro à equipe.
    Processa o upload da foto e salva as informações no banco de dados.
    """
    nome = request.form.get('nome')
    cargo = request.form.get('cargo')
    biografia = request.form.get('biografia')
    
    current_app.logger.info(f"Tentando adicionar novo membro da equipe: {nome}")

    foto_path = None
    if request.files.get('foto'):
        try: 
            foto_path = save_logo(request.files['foto'], secure_filename(nome))
            current_app.logger.info(f"Foto para {nome} salva: {foto_path}")
        except Exception as e: 
            current_app.logger.error(f"Erro ao salvar foto para '{nome}': {e}", exc_info=True)
            flash(f"Erro ao salvar foto para o membro da equipe: {e}", 'danger')
            
    novo_membro = MembroEquipe(nome=nome, cargo=cargo, biografia=biografia, foto=foto_path)
    db.session.add(novo_membro)
    db.session.commit()
    flash(f'Membro da equipe "{nome}" adicionado com sucesso!', 'success')
    current_app.logger.info(f"Membro da equipe '{nome}' adicionado.")
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/delete-membro-equipe', methods=['POST'])
@login_required
def delete_membro_equipe():
    """
    Exclui um membro da equipe do banco de dados.
    """
    member_id = request.form.get('id')
    current_app.logger.info(f"Tentando excluir membro da equipe com ID: {member_id}")
    membro = MembroEquipe.query.get(member_id)
    if membro:
        db.session.delete(membro)
        db.session.commit()
        flash(f'Membro "{membro.nome}" removido com sucesso!', 'success')
        current_app.logger.info(f"Membro da equipe '{membro.nome}' (ID: {member_id}) removido.")
    else:
        flash('Membro não encontrado.', 'danger')
        current_app.logger.warning(f"Tentativa de excluir membro da equipe não existente com ID: {member_id}")
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/edit-membro/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_membro(id: int):
    """
    Edita as informações de um membro da equipe existente.
    """
    membro = MembroEquipe.query.get_or_404(id)
    current_app.logger.info(f"Acessando edição para membro da equipe: {membro.nome} (ID: {id})")

    if request.method == 'POST':
        current_app.logger.info(f"Submissão POST para editar membro da equipe: {membro.nome}")
        membro.nome = request.form['nome']
        membro.cargo = request.form['cargo']
        membro.biografia = request.form['biografia']
        
        # Lógica para remover a foto existente
        if request.form.get('remover_foto'): 
            # Opcional: remover o arquivo físico da foto antiga
            if membro.foto:
                # Exemplo: os.remove(os.path.join(current_app.static_folder, membro.foto))
                current_app.logger.info(f"Foto antiga de '{membro.nome}' removida: {membro.foto}")
            membro.foto = None
        # Lógica para fazer upload de uma nova foto
        elif request.files.get('foto'):
            try: 
                membro.foto = save_logo(request.files['foto'], secure_filename(membro.nome))
                current_app.logger.info(f"Nova foto para '{membro.nome}' salva: {membro.foto}")
            except Exception as e: 
                current_app.logger.error(f"Erro ao salvar nova foto para '{membro.nome}': {e}", exc_info=True)
                flash(f"Erro ao salvar nova foto para o membro: {e}", 'danger')

        db.session.commit()
        flash(f'Membro "{membro.nome}" atualizado com sucesso!', 'success')
        current_app.logger.info(f"Membro da equipe '{membro.nome}' (ID: {id}) atualizado.")
        return redirect(url_for('admin.dashboard', page='Team'))
        
    return render_template('admin/edit_membro.html', member=membro)

@admin_bp.route('/add_cliente_parceiro', methods=['POST'])
@login_required
def add_cliente_parceiro():
    """
    Adiciona um novo cliente ou parceiro ao banco de dados, incluindo o upload do logotipo.
    """
    nome = request.form.get('nome')
    site_url = request.form.get('site_url')
    current_app.logger.info(f"Tentando adicionar novo cliente/parceiro: {nome}")

    if request.files.get('logo'):
        try:
            logo_path = save_logo(request.files['logo'], secure_filename(nome))
            novo_cliente = ClienteParceiro(nome=nome, logo_path=logo_path, site_url=site_url)
            db.session.add(novo_cliente)
            db.session.commit()
            flash(f'Cliente/Parceiro "{nome}" adicionado com sucesso!', 'success')
            current_app.logger.info(f"Cliente/Parceiro '{nome}' adicionado com logo: {logo_path}")
        except Exception as e: 
            db.session.rollback()
            flash(f"Erro ao adicionar cliente/parceiro: {e}", 'danger')
            current_app.logger.error(f"Erro ao adicionar cliente/parceiro '{nome}': {e}", exc_info=True)
    else:
        flash('É necessário fazer upload de um logotipo para o cliente/parceiro.', 'danger')
        current_app.logger.warning(f"Tentativa de adicionar cliente/parceiro '{nome}' sem logotipo.")
    return redirect(url_for('admin.dashboard', page='Clients'))

@admin_bp.route('/delete_cliente_parceiro', methods=['POST'])
@login_required
def delete_cliente_parceiro():
    """
    Exclui um cliente ou parceiro do banco de dados.
    """
    client_id = request.form.get('id')
    current_app.logger.info(f"Tentando excluir cliente/parceiro com ID: {client_id}")
    cliente = ClienteParceiro.query.get(client_id)
    if cliente:
        db.session.delete(cliente)
        db.session.commit()
        flash(f'Cliente/Parceiro "{cliente.nome}" removido com sucesso!', 'success')
        current_app.logger.info(f"Cliente/Parceiro '{cliente.nome}' (ID: {client_id}) removido.")
    else:
        flash('Cliente/Parceiro não encontrado.', 'danger')
        current_app.logger.warning(f"Tentativa de excluir cliente/parceiro não existente com ID: {client_id}")
    return redirect(url_for('admin.dashboard', page='Clients'))

@admin_bp.route('/generate-depoimento-link', methods=['POST'])
@login_required
def generate_depoimento_link():
    """
    Gera um link único para submissão de depoimento e o salva no banco de dados.
    Este link pode ser compartilhado para que clientes submetam depoimentos.
    """
    token = secrets.token_hex(16)
    novo_depoimento = Depoimento(token_submissao=token, aprovado=False)
    db.session.add(novo_depoimento)
    db.session.commit()
    submission_link = url_for("main.submit_depoimento", token=token, _external=True)
    flash(f'Link de submissão de depoimento gerado: {submission_link}', 'success')
    current_app.logger.info(f"Link de submissão de depoimento gerado: {submission_link}")
    return redirect(url_for('admin.dashboard', page='Testimonials')) # Redireciona para a aba de depoimentos

@admin_bp.route('/approve-depoimento/<int:id>', methods=['POST'])
@login_required
def approve_depoimento(id: int):
    """
    Aprova um depoimento pendente, tornando-o visível no site.
    """
    depoimento = Depoimento.query.get_or_404(id)
    depoimento.aprovado = True
    db.session.commit()
    flash(f'Depoimento de "{depoimento.nome_cliente}" aprovado com sucesso!', 'success')
    current_app.logger.info(f"Depoimento ID: {id} de '{depoimento.nome_cliente}' aprovado.")
    return redirect(url_for('admin.dashboard', page='Testimonials'))

@admin_bp.route('/delete-depoimento/<int:id>')
@login_required
def delete_depoimento(id: int):
    """
    Exclui um depoimento do banco de dados.
    """
    depoimento = Depoimento.query.get(id)
    if depoimento:
        db.session.delete(depoimento)
        db.session.commit()
        flash(f'Depoimento de "{depoimento.nome_cliente}" removido com sucesso!', 'success')
        current_app.logger.info(f"Depoimento ID: {id} de '{depoimento.nome_cliente}' removido.")
    else:
        flash('Depoimento não encontrado.', 'danger')
        current_app.logger.warning(f"Tentativa de excluir depoimento não existente com ID: {id}")
    return redirect(url_for('admin.dashboard', page='Testimonials'))

@admin_bp.route('/preview', methods=['POST'])
@login_required
def preview():
    """
    Permite visualizar uma página com conteúdo modificado antes de salvar no banco de dados.
    Esta rota é usada para pré-visualização de edições de conteúdo.
    """
    ident = request.form.get('page_identifier')
    # O slug é normalizado para evitar problemas com identificadores de seção que podem ser diferentes.
    slug = ident.replace('area_atuacao_', '').replace('_', '-') if ident and 'area_atuacao' in ident else ident
    
    current_app.logger.info(f"Gerando pré-visualização para a página: {slug}")
    
    # Busca a página pelo slug; retorna 404 se não encontrada.
    p = Pagina.query.filter_by(slug=slug).first_or_404()
    
    # Filtra apenas os campos de conteúdo enviados no formulário de pré-visualização.
    data = {k.split('-', 1)[1]: v for k, v in request.form.items() if k.startswith('content-')}
    
    # Renderiza a página usando o template_path da página e injeta o conteúdo de override.
    return render_page(p.template_path, ident, override_content=data,
        lista_areas_atuacao=AreaAtuacao.query.order_by(AreaAtuacao.ordem).all(),
        testimonials=Depoimento.query.filter_by(aprovado=True).all(),
        all_clients=ClienteParceiro.query.all())

@admin_bp.route('/update-email-settings', methods=['POST'])
@login_required
def update_email_settings():
    """
    Atualiza as configurações de e-mail da aplicação no banco de dados.
    """
    current_app.logger.info("Iniciando atualização das configurações de e-mail.")
    try:
        for key in ['smtp_server', 'smtp_port', 'smtp_user', 'smtp_pass', 'email_to']:
            value = request.form.get(key)
            # Para a senha SMTP, se o campo estiver vazio, não atualiza para não sobrescrever a senha existente com um valor nulo.
            if key == 'smtp_pass' and not value: 
                current_app.logger.debug(f"Campo '{key}' de e-mail vazio, pulando atualização.")
                continue

            item = ConteudoGeral.query.filter_by(pagina='configuracoes_email', secao=key).first()
            if item: 
                item.conteudo = value
                db.session.add(item)
                current_app.logger.debug(f"Configuração de e-mail '{key}' atualizada.")
            else: 
                new_setting = ConteudoGeral(pagina='configuracoes_email', secao=key, conteudo=value)
                db.session.add(new_setting)
                current_app.logger.info(f"Nova configuração de e-mail '{key}' criada.")
        db.session.commit()
        flash('Configurações de e-mail salvas com sucesso!', 'success')
        current_app.logger.info("Configurações de e-mail atualizadas com sucesso.")
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao salvar configurações de e-mail: {e}', 'danger')
        current_app.logger.error(f"Erro ao salvar configurações de e-mail: {e}", exc_info=True)
    return redirect(url_for('admin.dashboard', page='EmailSettings'))

@admin_bp.route('/test-email', methods=['POST'])
@login_required
def test_email():
    """
    Envia um e-mail de teste usando as configurações SMTP salvas.
    Retorna um JSON indicando sucesso ou falha.
    """
    current_app.logger.info("Iniciando teste de envio de e-mail.")
    configs_email = {i.secao: i.conteudo for i in ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()}
    
    try:
        # Tenta conectar ao servidor SMTP e enviar um e-mail.
        smtp_server = configs_email.get('smtp_server')
        smtp_port = int(configs_email.get('smtp_port') or 587)
        smtp_user = configs_email.get('smtp_user')
        smtp_pass = configs_email.get('smtp_pass')

        if not all([smtp_server, smtp_user, smtp_pass]):
            raise ValueError("Configurações SMTP incompletas. Verifique servidor, usuário e senha.")

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # Habilita TLS para comunicação segura
            server.login(smtp_user, smtp_pass)
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = smtp_user # Envia para si mesmo para teste
            msg['Subject'] = f"Email de Teste - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText(f"Este é um e-mail de teste enviado do seu painel administrativo. Se você o recebeu, suas configurações SMTP estão corretas. Data/Hora: {datetime.now()}", 'plain'))
            
            server.sendmail(smtp_user, smtp_user, msg.as_string())
        
        current_app.logger.info("Teste de e-mail enviado com sucesso.")
        return jsonify({'success': True, 'message': 'E-mail de teste enviado com sucesso!'})
    except Exception as e: 
        current_app.logger.error(f"Falha no envio do e-mail de teste: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Falha ao enviar e-mail de teste: {str(e)}'})

@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Processa a requisição para alterar a senha do usuário logado.
    Utiliza o `ChangePasswordForm` para validação e `werkzeug.security` para hashing de senha.
    """
    form = ChangePasswordForm() # Renomeado para 'form' para clareza
    current_app.logger.info(f"Tentativa de mudança de senha para o usuário: {current_user.username}")

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Sua senha foi alterada com sucesso!', 'success')
            current_app.logger.info(f"Senha do usuário '{current_user.username}' alterada com sucesso.")
        else: 
            flash('A senha atual está incorreta. Por favor, tente novamente.', 'danger')
            current_app.logger.warning(f"Falha na mudança de senha para '{current_user.username}': senha atual incorreta.")
    else: 
        # Extrai mensagens de erro de validação do formulário
        errors = [f"{field.label.text}: {', '.join(field.errors)}" for field in form if field.errors]
        flash(f'Erro(s) de validação: {"; ".join(errors)}', 'danger')
        current_app.logger.warning(f"Falha na mudança de senha para '{current_user.username}': {form.errors}")
    
    return redirect(url_for('admin.dashboard', page='Security'))

@admin_bp.route('/select-theme', methods=['POST'])
@login_required
def select_theme():
    """
    Permite ao administrador selecionar o tema/layout ativo do site.
    O tema selecionado é armazenado em `ThemeSettings` no banco de dados.
    """
    form = ThemeForm() # Renomeado para 'form' para clareza
    current_app.logger.info("Tentativa de seleção de tema.")

    if form.validate_on_submit():
        theme_settings_obj = ThemeSettings.query.first()
        if not theme_settings_obj:
            theme_settings_obj = ThemeSettings()
            db.session.add(theme_settings_obj)
            current_app.logger.info("Nenhuma configuração de tema existente. Criando uma nova.")
        
        theme_settings_obj.theme = form.theme.data
        db.session.commit()
        flash(f'Tema do site atualizado para "{form.theme.data}"!', 'success')
        current_app.logger.info(f"Tema do site atualizado para: {form.theme.data}.")
    else:
        errors = [f"{field.label.text}: {', '.join(field.errors)}" for field in form if field.errors]
        flash(f'Erro(s) de validação ao selecionar tema: {"; ".join(errors)}', 'danger')
        current_app.logger.warning(f"Falha na seleção de tema: {form.errors}")

    return redirect(url_for('admin.dashboard', page='Theme'))

@admin_bp.route('/design-editor', methods=['GET', 'POST'])
@login_required
def design_editor():
    """
    Permite ao administrador personalizar as cores globais do tema via formulário.
    As cores são armazenadas em `ThemeSettings` e injetadas via variáveis CSS.
    """
    form = DesignForm() # Renomeado para 'form' para clareza
    theme_settings_obj = ThemeSettings.query.first()
    
    # Se não houver ThemeSettings, cria um com defaults.
    if not theme_settings_obj:
        theme_settings_obj = ThemeSettings()
        db.session.add(theme_settings_obj)
        db.session.commit()
        current_app.logger.info("Nenhuma configuração de Design existente. Criando uma nova com defaults.")
    
    if request.method == 'POST' and form.validate_on_submit():
        current_app.logger.info("Submissão POST para Design Editor.")
        try:
            # Popula o objeto ThemeSettings com os dados do formulário
            form.populate_obj(theme_settings_obj)
            db.session.commit()
            flash('Configurações de design salvas com sucesso!', 'success')
            current_app.logger.info("Configurações de design atualizadas com sucesso.")
            return redirect(url_for('admin.design_editor'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar configurações de design: {e}', 'danger')
            current_app.logger.error(f"Erro ao salvar configurações de design: {e}", exc_info=True)
            return redirect(url_for('admin.design_editor')) # Redireciona para evitar reenvio do form
    
    if request.method == 'GET':
        # Preenche o formulário com os dados atuais do ThemeSettings ao carregar a página.
        for field in form:
            if hasattr(theme_settings_obj, field.name):
                field.data = getattr(theme_settings_obj, field.name)
            
    # Não passa o objeto ThemeSettings diretamente como `configs` (templates esperam um dict).
    # O processador de contexto global já fornece `configs` como um dicionário construído a partir de ConteudoGeral.
    return render_template('admin/design_editor.html', form=form)