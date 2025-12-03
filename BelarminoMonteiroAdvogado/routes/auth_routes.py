# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from ..models import User
from ..forms import LoginForm
from .. import db

# ADICIONADO url_prefix='/auth' para evitar conflito com rotas do site
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
"""
Blueprint para rotas de autenticação de usuários.
Gerencia o login, logout e garante a segurança contra redirecionamentos maliciosos.
"""

def is_safe_url(target: str) -> bool:
    """
    Verifica se a URL de redirecionamento fornecida é segura para evitar ataques de Open Redirect.
    Compara o domínio da URL de destino com o domínio da aplicação.

    Args:
        target (str): A URL para a qual o usuário seria redirecionado.

    Returns:
        bool: True se a URL for segura (mesmo domínio), False caso contrário.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    # Verifica se o esquema (http/https) é permitido e se o host é o mesmo da aplicação.
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Controlador da rota de login para acesso administrativo.
    
    Renderiza o formulário de login (GET) e processa a submissão do formulário (POST).
    Autentica o usuário, registra o login, e redireciona para o dashboard
    ou para a página solicitada (`next_page`) se for uma URL segura.
    """
    # Se o usuário já estiver autenticado, redireciona para o dashboard para evitar login duplicado.
    if current_user.is_authenticated:
        flash('Você já está logado.', 'info')
        current_app.logger.info(f"Usuário autenticado '{current_user.username}' tentou acessar a página de login.")
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Verifica as credenciais do usuário.
        # Usa o método `check_password` do modelo User.
        if user is None or not user.check_password(form.password.data):
            current_app.logger.warning(f'Falha de login para usuário: "{form.username.data}" (IP: {request.remote_addr}) - Credenciais inválidas.')
            flash('Credenciais inválidas. Verifique seu usuário e senha e tente novamente.', 'danger')
            return redirect(url_for('auth.login'))

        # Autentica o usuário e inicia a sessão.
        login_user(user)
        current_app.logger.info(f'Login realizado com sucesso para o usuário: "{user.username}" (IP: {request.remote_addr}).')
        
        # Tenta redirecionar para a página anterior ou para o dashboard.
        next_page = request.args.get('next')
        if not next_page or not is_safe_url(next_page):
            next_page = url_for('admin.dashboard')
            current_app.logger.debug(f"Redirecionando para o dashboard após login de '{user.username}'.")
        else:
            current_app.logger.debug(f"Redirecionando para '{next_page}' após login de '{user.username}'.")
            
        flash(f'Bem-vindo(a) de volta, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Encerra a sessão do usuário autenticado.
    Redireciona para a página de login após o logout.
    """
    username = current_user.username # Salva o nome de usuário antes de fazer logout
    logout_user()
    flash(f'Sessão do usuário "{username}" encerrada com sucesso.', 'info')
    current_app.logger.info(f'Logout realizado com sucesso para o usuário: "{username}".')
    return redirect(url_for('auth.login'))