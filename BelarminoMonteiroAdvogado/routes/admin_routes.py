# BelarminoMonteiroAdvogado/routes/admin_routes.py
# -*- coding: utf-8 -*-

import os
import json
import secrets
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from werkzeug.utils import secure_filename

from .. import db, render_page
from ..models import (
    Pagina, ConteudoGeral, AreaAtuacao, MembroEquipe, 
    Depoimento, ClienteParceiro, ThemeSettings, HomePageSection
)
from ..forms import ChangePasswordForm, ThemeForm, DesignForm
from ..image_processor import process_and_save_image, save_logo

admin_bp = Blueprint('admin', __name__)

# --- HELPERS E FORMS ---

# Formulário vazio genérico para garantir que o CSRF token exista no dashboard
class EmptyForm(FlaskForm):
    pass

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_admin_upload(file, secao_name, page_identifier):
    if not file or not allowed_file(file.filename):
        return False, "Arquivo inválido."
    try:
        filename = secure_filename(file.filename)
        # Adiciona hex para evitar cache e duplicidade de nomes
        safe_filename = f"{secao_name}_{secrets.token_hex(4)}{os.path.splitext(filename)[1]}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder): os.makedirs(upload_folder)
        file.save(os.path.join(upload_folder, safe_filename))
        
        # Salva caminho relativo para o DB (compatível com Linux/Windows)
        db_path = f"images/uploads/{safe_filename}"
        item = ConteudoGeral.query.filter_by(pagina=page_identifier, secao=secao_name).first()
        if item:
            item.conteudo = db_path
            db.session.add(item)
        else:
            db.session.add(ConteudoGeral(pagina=page_identifier, secao=secao_name, conteudo=db_path))
        return True, "Upload realizado."
    except Exception as e:
        return False, str(e)

# --- ROTAS DE COMPATIBILIDADE (FIX CRÍTICO) ---
# Estas rotas redirecionam links antigos do template para o novo local
@admin_bp.route('/manage-areas')
@login_required
def manage_areas():
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/manage-team')
@login_required
def manage_team():
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/manage-clients')
@login_required
def manage_clients():
    return redirect(url_for('admin.dashboard', page='Clients'))

# --- ROTAS PRINCIPAIS ---

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    selected_page = request.args.get('page', 'configuracoes_gerais')
    content_for_page = ConteudoGeral.query.filter_by(pagina=selected_page).all() if selected_page else []
    
    # Carregamento otimizado (sem joinedload redundante)
    all_content_pages = [r[0] for r in db.session.query(ConteudoGeral.pagina).distinct().all()]
    nav_pages = Pagina.query.filter(Pagina.parent_id.is_(None)).order_by(Pagina.ordem).all()
    
    email_settings = {i.secao: i for i in ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()}
    theme_settings = ThemeSettings.query.first()
    
    password_form = ChangePasswordForm()
    theme_form = ThemeForm()
    # Cria um formulário vazio para satisfazer {{ form.hidden_tag() }} no template dashboard.html
    generic_form = EmptyForm()
    
    if theme_settings: theme_form.theme.data = theme_settings.theme

    return render_template('admin/dashboard.html', 
                           selected_page=selected_page,
                           content_for_page=content_for_page,
                           all_content_pages=all_content_pages,
                           nav_pages_admin=nav_pages,
                           home_sections_list=HomePageSection.query.order_by(HomePageSection.order).all(),
                           email_settings_dict=email_settings,
                           all_services=AreaAtuacao.query.order_by(AreaAtuacao.titulo).all(),
                           all_team=MembroEquipe.query.order_by(MembroEquipe.nome).all(),
                           all_testimonials=Depoimento.query.order_by(Depoimento.data_criacao.desc()).all(),
                           all_clients=ClienteParceiro.query.order_by(ClienteParceiro.nome).all(),
                           password_form=password_form,
                           theme_form=theme_form,
                           form=generic_form, # Passa o form genérico
                           all_content=ConteudoGeral.query.all())

# Rota para reordenar seções da home (nome alinhado com o template)
@admin_bp.route('/reorder-home-sections', methods=['POST'])
@login_required
def reorder_home_sections():
    try:
        data = json.loads(request.form.get('order'))
        for item in data:
            s = HomePageSection.query.get(int(item['id']))
            if s: s.order = item['order']
        db.session.commit()
        flash('Ordem atualizada.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/update-content', methods=['POST'])
@login_required
def update_content():
    page_identifier = request.form.get('page_identifier')
    try:
        # Atualiza campos de texto
        for key, value in request.form.items():
            if key.startswith('content-'):
                try:
                    item = ConteudoGeral.query.get(int(key.split('-')[1]))
                    if item: 
                        item.conteudo = value
                        db.session.add(item)
                except: continue
        
        # Atualiza arquivos
        for key, file in request.files.items():
            if file and file.filename != '':
                if key.startswith('content-'):
                    try:
                        c_id = int(key.split('-')[1])
                        item = ConteudoGeral.query.get(c_id)
                        if item:
                            # Usa processador de imagem para itens de conteúdo
                            item.conteudo = process_and_save_image(file, item.secao, c_id)
                            db.session.add(item)
                    except Exception as e: flash(str(e), 'danger')
                else:
                    # Usa upload genérico para logos/arquivos de configuração
                    success, msg = save_admin_upload(file, key.replace('_file', ''), page_identifier)
                    if not success: flash(msg, 'warning')
        
        db.session.commit()
        flash('Atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('admin.dashboard', page=page_identifier))

@admin_bp.route('/update-nav-order', methods=['POST'])
@login_required
def update_nav_order():
    try:
        data = json.loads(request.form.get('order'))
        for item in data:
            p = Pagina.query.get(int(item['id']))
            if p:
                p.ordem = item['order']
                p.parent_id = int(item['parent_id']) if item.get('parent_id') else None
        db.session.commit()
        flash('Menu reordenado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('admin.dashboard') + '#Navigation')

@admin_bp.route('/toggle-page-status/<int:id>/<string:field>', methods=['GET', 'POST'])
@login_required
def toggle_page_status(id, field):
    p = Pagina.query.get_or_404(id)
    if field in ['ativo', 'show_in_menu']:
        setattr(p, field, not getattr(p, field))
        db.session.commit()
        flash('Status alterado.', 'success')
    return redirect(url_for('admin.dashboard') + '#Navigation')

@admin_bp.route('/toggle-section-status/<int:id>', methods=['GET', 'POST'])
@login_required
def toggle_section_status(id):
    s = HomePageSection.query.get_or_404(id)
    s.is_active = not s.is_active
    db.session.commit()
    flash('Seção atualizada.', 'success')
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/update-section-text', methods=['POST'])
@login_required
def update_section_text():
    s = HomePageSection.query.get_or_404(request.form.get('section_id'))
    s.title = request.form.get('title')
    s.subtitle = request.form.get('subtitle')
    db.session.commit()
    flash('Texto atualizado.', 'success')
    return redirect(url_for('admin.dashboard') + '#HomeSections')

@admin_bp.route('/add-area-atuacao', methods=['POST'])
@login_required
def add_area_atuacao():
    slug = request.form.get('slug')
    if AreaAtuacao.query.filter_by(slug=slug).first():
        flash('Slug já existe.', 'danger')
        return redirect(url_for('admin.dashboard', page='Services'))
    
    foto = None
    if request.files.get('foto'):
        try: foto = save_logo(request.files['foto'], secure_filename(slug))
        except: pass
        
    db.session.add(AreaAtuacao(
        titulo=request.form.get('titulo'), slug=slug,
        descricao=request.form.get('descricao'), icone=request.form.get('icone'),
        foto=foto
    ))
    
    parent = Pagina.query.filter_by(slug='areas-de-atuacao').first()
    db.session.add(Pagina(
        slug=slug, titulo_menu=request.form.get('titulo'), tipo='servico',
        parent_id=parent.id if parent else None, template_path='areas_atuacao/servico_base.html'
    ))
    db.session.commit()
    flash('Serviço criado.', 'success')
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/delete-area-atuacao', methods=['POST'])
@login_required
def delete_area_atuacao():
    slug = request.form.get('slug')
    AreaAtuacao.query.filter_by(slug=slug).delete()
    Pagina.query.filter_by(slug=slug).delete()
    ConteudoGeral.query.filter_by(pagina=slug).delete()
    db.session.commit()
    flash('Removido.', 'success')
    return redirect(url_for('admin.dashboard', page='Services'))

@admin_bp.route('/edit-service/<string:slug>', methods=['GET', 'POST'])
@login_required
def edit_service(slug):
    s = AreaAtuacao.query.filter_by(slug=slug).first_or_404()
    if request.method == 'POST':
        s.titulo = request.form['titulo']
        s.descricao = request.form['descricao']
        s.icone = request.form['icone']
        
        p = Pagina.query.filter_by(slug=slug).first()
        if p: p.titulo_menu = s.titulo
        
        for k, v in request.form.items():
            if k.startswith('content-'):
                secao = k.replace('content-', '')
                item = ConteudoGeral.query.filter_by(pagina=slug, secao=secao).first() or ConteudoGeral(pagina=slug, secao=secao)
                item.conteudo = v
                db.session.add(item)
                
        for k, f in request.files.items():
            if f and k.startswith('content-'):
                secao = k.replace('content-', '')
                try:
                    img = process_and_save_image(f, slug, secao)
                    item = ConteudoGeral.query.filter_by(pagina=slug, secao=secao).first() or ConteudoGeral(pagina=slug, secao=secao)
                    item.conteudo = img
                    db.session.add(item)
                except: pass
                
        db.session.commit()
        flash('Atualizado.', 'success')
        return redirect(url_for('admin.dashboard', page='Services'))
        
    content = {i.secao: i.conteudo for i in ConteudoGeral.query.filter_by(pagina=slug).all()}
    return render_template('admin/edit_service.html', service=s, service_content=content)

@admin_bp.route('/add-membro-equipe', methods=['POST'])
@login_required
def add_membro_equipe():
    foto = None
    if request.files.get('foto'):
        try: foto = save_logo(request.files['foto'], secure_filename(request.form.get('nome')))
        except: pass
    db.session.add(MembroEquipe(nome=request.form.get('nome'), cargo=request.form.get('cargo'), biografia=request.form.get('biografia'), foto=foto))
    db.session.commit()
    flash('Membro adicionado.', 'success')
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/delete-membro-equipe', methods=['POST'])
@login_required
def delete_membro_equipe():
    m = MembroEquipe.query.get(request.form.get('id'))
    if m:
        db.session.delete(m)
        db.session.commit()
        flash('Removido.', 'success')
    return redirect(url_for('admin.dashboard', page='Team'))

@admin_bp.route('/edit-membro/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_membro(id):
    m = MembroEquipe.query.get_or_404(id)
    if request.method == 'POST':
        m.nome = request.form['nome']
        m.cargo = request.form['cargo']
        m.biografia = request.form['biografia']
        if request.form.get('remover_foto'): m.foto = None
        elif request.files.get('foto'):
            try: m.foto = save_logo(request.files['foto'], secure_filename(m.nome))
            except: pass
        db.session.commit()
        flash('Atualizado.', 'success')
        return redirect(url_for('admin.dashboard', page='Team'))
    return render_template('admin/edit_membro.html', member=m)

@admin_bp.route('/add_cliente_parceiro', methods=['POST'])
@login_required
def add_cliente_parceiro():
    if request.files.get('logo'):
        try:
            path = save_logo(request.files['logo'], secure_filename(request.form.get('nome')))
            db.session.add(ClienteParceiro(nome=request.form.get('nome'), logo_path=path))
            db.session.commit()
            flash('Adicionado.', 'success')
        except Exception as e: flash(str(e), 'danger')
    return redirect(url_for('admin.dashboard', page='Clients'))

@admin_bp.route('/delete_cliente_parceiro', methods=['POST'])
@login_required
def delete_cliente_parceiro():
    c = ClienteParceiro.query.get(request.form.get('id'))
    if c:
        db.session.delete(c)
        db.session.commit()
        flash('Removido.', 'success')
    return redirect(url_for('admin.dashboard', page='Clients'))

@admin_bp.route('/generate-depoimento-link', methods=['POST'])
@login_required
def generate_depoimento_link():
    t = secrets.token_hex(16)
    db.session.add(Depoimento(token_submissao=t, aprovado=False))
    db.session.commit()
    flash(url_for("main.submit_depoimento", token=t, _external=True), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve-depoimento/<int:id>', methods=['POST'])
@login_required
def approve_depoimento(id):
    Depoimento.query.get_or_404(id).aprovado = True
    db.session.commit()
    flash('Aprovado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete-depoimento/<int:id>')
@login_required
def delete_depoimento(id):
    Depoimento.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Removido.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/preview', methods=['POST'])
@login_required
def preview():
    ident = request.form.get('page_identifier')
    slug = ident.replace('area_atuacao_', '').replace('_', '-') if ident and 'area_atuacao' in ident else ident
    p = Pagina.query.filter_by(slug=slug).first_or_404()
    # Filtra apenas os campos de conteúdo
    data = {k.split('-', 1)[1]: v for k, v in request.form.items() if k.startswith('content-')}
    return render_page(p.template_path, ident, override_content=data,
        lista_areas_atuacao=AreaAtuacao.query.order_by(AreaAtuacao.ordem).all(),
        testimonials=Depoimento.query.filter_by(aprovado=True).all(),
        all_clients=ClienteParceiro.query.all())

@admin_bp.route('/update-email-settings', methods=['POST'])
@login_required
def update_email_settings():
    for k in ['smtp_server', 'smtp_port', 'smtp_user', 'smtp_pass', 'email_to']:
        v = request.form.get(k)
        if k == 'smtp_pass' and not v: continue
        item = ConteudoGeral.query.filter_by(pagina='configuracoes_email', secao=k).first()
        if item: item.conteudo = v
        else: db.session.add(ConteudoGeral(pagina='configuracoes_email', secao=k, conteudo=v))
    db.session.commit()
    flash('Salvo.', 'success')
    return redirect(url_for('admin.dashboard', page='EmailSettings'))

@admin_bp.route('/test-email', methods=['POST'])
@login_required
def test_email():
    c = {i.secao: i.conteudo for i in ConteudoGeral.query.filter_by(pagina='configuracoes_email').all()}
    try:
        s = smtplib.SMTP(c.get('smtp_server'), int(c.get('smtp_port') or 587))
        s.starttls()
        s.login(c.get('smtp_user'), c.get('smtp_pass'))
        s.sendmail(c.get('smtp_user'), c.get('smtp_user'), f"Subject: Teste\n\nTeste OK {datetime.now()}")
        s.quit()
        return jsonify({'success': True, 'message': 'OK'})
    except Exception as e: return jsonify({'success': False, 'message': str(e)})

@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    f = ChangePasswordForm()
    # Verifica a senha atual antes de alterar
    if f.validate_on_submit() and current_user.check_password(f.current_password.data):
        current_user.set_password(f.new_password.data)
        db.session.commit()
        flash('Senha alterada.', 'success')
    else: flash('Erro na senha.', 'danger')
    return redirect(url_for('admin.dashboard', page='Security'))

@admin_bp.route('/select-theme', methods=['POST'])
@login_required
def select_theme():
    f = ThemeForm()
    if f.validate_on_submit():
        s = ThemeSettings.query.first() or ThemeSettings()
        if not s.id: db.session.add(s)
        s.theme = f.theme.data
        db.session.commit()
        flash('Atualizado.', 'success')
    return redirect(url_for('admin.dashboard', page='Theme'))

@admin_bp.route('/design-editor', methods=['GET', 'POST'])
@login_required
def design_editor():
    f = DesignForm()
    s = ThemeSettings.query.first() or ThemeSettings()
    if not s.id: db.session.add(s); db.session.commit()
    
    if f.validate_on_submit():
        f.populate_obj(s)
        db.session.commit()
        flash('Salvo.', 'success')
        return redirect(url_for('admin.design_editor'))
    
    if request.method == 'GET':
        for field in f:
            if hasattr(s, field.name): field.data = getattr(s, field.name)
            
    return render_template('admin/design_editor.html', form=f, configs=s)