# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL

# --- 0. FORMULÁRIO BASE (PARA CSRF) ---
class BaseForm(FlaskForm):
    """
    Formulário base que inclui apenas o token CSRF.
    Útil para formulários simples que precisam de proteção CSRF sem campos adicionais.
    """
    pass

# --- 1. AUTENTICAÇÃO E SEGURANÇA ---

class LoginForm(FlaskForm):
    """
    Formulário de login para autenticação de usuários administradores.
    Inclui validações para garantir que os campos de usuário e senha não estejam vazios.
    """
    username = StringField('Usuário ou E-mail', validators=[DataRequired("O usuário ou e-mail é obrigatório.")])
    password = PasswordField('Senha', validators=[DataRequired("A senha é obrigatória.")])
    submit = SubmitField('Acessar Painel')

class RegistrationForm(FlaskForm):
    """
    Formulário de registro para criar novos usuários administradores.
    Validações incluem comprimento do nome de usuário, formato de e-mail e força da senha.
    """
    username = StringField('Usuário', validators=[
        DataRequired("O usuário é obrigatório."), 
        Length(min=4, max=25, message="O usuário deve ter entre 4 e 25 caracteres.")
    ])
    email = StringField('E-mail', validators=[
        DataRequired("O e-mail é obrigatório."), 
        Email(message="Insira um e-mail válido.")
    ])
    password = PasswordField('Senha', validators=[
        DataRequired("A senha é obrigatória."),
        Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired("A confirmação de senha é obrigatória."),
        EqualTo('password', message='As senhas não conferem.')
    ])
    submit = SubmitField('Criar Administrador')

class ChangePasswordForm(FlaskForm):
    """
    Formulário para alteração de senha de um usuário existente.
    Exige a senha atual para segurança e valida a nova senha.
    """
    current_password = PasswordField('Senha Atual', validators=[DataRequired("A senha atual é obrigatória.")])
    new_password = PasswordField('Nova Senha', validators=[
        DataRequired("A nova senha é obrigatória."),
        Length(min=6, message="A nova senha deve ter no mínimo 6 caracteres.")
    ])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired("A confirmação da nova senha é obrigatória."),
        EqualTo('new_password', message='As senhas não conferem.')
    ])
    submit = SubmitField('Atualizar Senha')

# --- 2. SITE PÚBLICO ---

class ContactForm(FlaskForm):
    """
    Formulário de contato para visitantes do site.
    Coleta nome, e-mail, assunto e mensagem, com validações apropriadas.
    """
    name = StringField('Nome Completo', validators=[DataRequired("Por favor, informe seu nome.")])
    email = StringField('E-mail', validators=[
        DataRequired("O e-mail é obrigatório."), 
        Email("Insira um e-mail válido.")
    ])
    message = TextAreaField('Mensagem', validators=[
        DataRequired("Escreva sua mensagem."),
        Length(min=10, message="Sua mensagem deve ter pelo menos 10 caracteres.")
    ])
    subject = StringField('Assunto', validators=[Optional()]) # Campo opcional para selecionar assunto no front-end
    submit = SubmitField('Enviar Solicitação')

# --- 3. GERENCIAMENTO DE CONTEÚDO (ADMIN) ---

class AreaAtuacaoForm(FlaskForm):
    """
    Formulário para adicionar ou editar Áreas de Atuação do escritório.
    Permite definir título, slug, ícone, descrição e conteúdo detalhado.
    """
    titulo = StringField('Título da Área', validators=[DataRequired("O título da área é obrigatório.")])
    slug = StringField('Slug (URL Amigável)', validators=[
        DataRequired("O slug é obrigatório."),
        Length(max=100, message="O slug não deve exceder 100 caracteres.")
    ], description="Ex: direito-civil (sem espaços, acentos ou caracteres especiais, usado na URL)")
    icone = StringField('Ícone (Bootstrap Icons)', default='bi-shield-check', 
                       description="Classe do ícone do Bootstrap (ex: bi-briefcase, bi-heart). Consulte a documentação do Bootstrap Icons.")
    descricao = TextAreaField('Resumo (Home/Listagem)', validators=[
        DataRequired("A descrição resumida é obrigatória."),
        Length(max=300, message="O resumo deve ser breve (máx 300 caracteres) para exibição em listagens.")
    ], description="Breve descrição da área para ser exibida na página inicial ou em listagens.")
    conteudo_html = TextAreaField('Conteúdo Completo (Página Detalhe)', validators=[Optional()], 
                                  description="O conteúdo detalhado da área de atuação. Pode incluir HTML.")
    imagem_capa = FileField('Imagem de Capa', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens (JPG, PNG, JPEG, WEBP) são permitidas.')
    ], description="Imagem que representará a área de atuação. Opcional.")
    ordem = IntegerField('Ordem de Exibição', default=0, description="Número para definir a ordem de exibição das áreas (menor primeiro).")
    submit = SubmitField('Salvar Área')

class MembroEquipeForm(FlaskForm):
    """
    Formulário para adicionar ou editar membros da equipe.
    Gerencia informações como nome, cargo, biografia e foto de perfil.
    """
    nome = StringField('Nome Completo', validators=[DataRequired("O nome do membro da equipe é obrigatório.")])
    cargo = StringField('Cargo / Especialidade', validators=[DataRequired("O cargo ou especialidade é obrigatório.")])
    biografia = TextAreaField('Biografia', validators=[Optional()], description="Uma breve biografia ou descrição das qualificações do membro.")
    foto = FileField('Foto de Perfil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens (JPG, PNG, JPEG, WEBP) são permitidas para a foto de perfil!')
    ], description="Foto do membro da equipe.")
    ordem = IntegerField('Ordem', default=0, description="Número para definir a ordem de exibição dos membros na equipe (menor primeiro).")
    submit = SubmitField('Salvar Membro')

# Alias para compatibilidade caso algum código antigo use TeamMemberForm
TeamMemberForm = MembroEquipeForm

class DepoimentoForm(FlaskForm):
    """
    Formulário para adicionar ou editar depoimentos de clientes.
    Inclui o nome do cliente, o texto do depoimento, um logo opcional e status de aprovação.
    """
    nome_cliente = StringField('Nome do Cliente/Empresa', validators=[DataRequired("O nome do cliente é obrigatório.")])
    texto_depoimento = TextAreaField('Depoimento', validators=[DataRequired("O texto do depoimento é obrigatório.")])
    logo_cliente = FileField('Logo ou Foto (Opcional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens (JPG, PNG, JPEG, WEBP) são permitidas para o logo/foto!')
    ], description="Logo da empresa ou foto do cliente. Opcional.")
    aprovado = BooleanField('Aprovado (Visível no Site)', default=False, 
                            description="Marque para que o depoimento seja exibido publicamente no site.")
    submit = SubmitField('Salvar Depoimento')

class ClienteParceiroForm(FlaskForm):
    """
    Formulário para adicionar ou editar Clientes/Parceiros.
    Permite carregar o logotipo e informar o URL do site do parceiro.
    """
    nome = StringField('Nome da Empresa/Parceiro', validators=[DataRequired("O nome do cliente/parceiro é obrigatório.")])
    logo = FileField('Logotipo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'svg'], 'Imagens permitidas: JPG, PNG, JPEG, WEBP, SVG.')
    ], description="Logotipo do cliente ou parceiro.")
    site_url = StringField('Site (URL)', validators=[Optional(), URL(message="Insira uma URL válida para o site.")], 
                           description="Endereço completo do site do cliente/parceiro (ex: https://www.exemplo.com).")
    submit = SubmitField('Salvar Parceiro')

class SectionForm(FlaskForm):
    """
    Formulário para editar as propriedades de uma seção da Home Page.
    Permite configurar título, subtítulo, conteúdo HTML, status de ativação e ordem de exibição.
    """
    title = StringField('Título', validators=[DataRequired("O título da seção é obrigatório.")])
    subtitle = StringField('Subtítulo/Descrição', validators=[Optional()], description="Um subtítulo ou breve descrição para a seção.")
    content = TextAreaField('Conteúdo Adicional (HTML)', validators=[Optional()], description="Conteúdo HTML extra para a seção (opcional).")
    is_active = BooleanField('Seção Ativa', default=True, description="Marque para que a seção seja exibida na Home Page.")
    order = IntegerField('Ordem', default=0, description="Número para definir a ordem de exibição das seções (menor primeiro).")
    submit = SubmitField('Atualizar Seção')

# --- 4. CONFIGURAÇÃO DE TEMA ---

class ThemeForm(FlaskForm):
    """
    Formulário para selecionar o layout/tema visual do site.
    Permite ao administrador escolher entre os layouts pré-definidos.
    """
    theme = SelectField('Layout do Site', choices=[
        ('option1', 'Layout 1: Clássico (Clean & Profissional)'),
        ('option2', 'Layout 2: Executivo (Corporativo Moderno)'),
        ('option3', 'Layout 3: Boutique (Elegante & Minimalista)'),
        ('option4', 'Layout 4: Tech (Inovador & Dinâmico)'),
        ('option5', 'Layout 5: Moderno (Minimalista & Responsivo)'),
        ('option6', 'Layout 6: Clean (Leve & Objetivo)'),
        ('option7', 'Layout 7: Sofisticado (Detalhes & Experiência)'),
        ('option8', 'Layout 8: Futurista (Tecnologia & Visão)')
    ], validators=[DataRequired()])
    submit = SubmitField('Aplicar Tema')

class DesignForm(FlaskForm):
    """
    Editor visual de cores para os temas globais e variáveis principais.
    Permite a personalização da paleta de cores primárias, secundárias, texto e fundo,
    impactando todos os layouts de forma consistente através de variáveis CSS.
    """
    # Cores Primárias/Destaque
    color_primary = StringField('Cor Principal', render_kw={"type": "color"}, description="Define a cor principal de destaque para todo o site.")
    color_primary_rgb = StringField('Cor Principal RGB', description="Versão RGB da cor principal (ex: 185, 32, 39).")

    # Cores de Texto e Fundo (Modo Claro)
    color_text = StringField('Cor do Texto (Claro)', render_kw={"type": "color"})
    color_background = StringField('Cor do Fundo (Claro)', render_kw={"type": "color"})

    # Cores de Texto e Fundo (Modo Escuro)
    color_dark_text = StringField('Cor do Texto (Escuro)', render_kw={"type": "color"})
    color_dark_background = StringField('Cor do Fundo (Escuro)', render_kw={"type": "color"})
    color_dark_surface = StringField('Cor da Superfície (Escuro)', render_kw={"type": "color"}, description="Cor para cards e elementos elevados no modo escuro.")
    
    # Cores de Componentes Específicos
    color_whatsapp = StringField('Botão WhatsApp', render_kw={"type": "color"}, description="Cor de fundo do botão flutuante do WhatsApp.")
    color_whatsapp_hover = StringField('Botão WhatsApp (Hover)', render_kw={"type": "color"}, description="Cor do botão do WhatsApp ao passar o mouse.")
    
    submit = SubmitField('Salvar Personalização')