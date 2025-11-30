# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from ..models import User
from ..forms import LoginForm
from .. import db

# ADICIONADO url_prefix='/auth' para evitar conflito com rotas do site
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def is_safe_url(target):
    """
    Proteção contra Open Redirects.
    Garante que o redirecionamento após login permaneça no mesmo domínio.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Controlador de Acesso Administrativo.
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # CORREÇÃO CRÍTICA: O método no models.py é 'check_password', não 'verify_password'
        if user is None or not user.check_password(form.password.data):
            current_app.logger.warning(f'Falha de login para: {form.username.data} IP: {request.remote_addr}')
            flash('Credenciais inválidas. Verifique usuário e senha.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        current_app.logger.info(f'Login realizado: {user.username}')
        
        next_page = request.args.get('next')
        if not next_page or not is_safe_url(next_page):
            next_page = url_for('admin.dashboard')
            
        flash(f'Bem-vindo de volta, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Encerra a sessão.
    """
    logout_user()
    flash('Sessão encerrada.', 'info')
    return redirect(url_for('auth.login'))