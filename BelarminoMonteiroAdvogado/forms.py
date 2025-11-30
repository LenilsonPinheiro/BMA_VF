# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL

# --- 0. FORMULÁRIO BASE (PARA CSRF) ---
class BaseForm(FlaskForm):
    """Formulário base que inclui apenas o token CSRF. Útil para formulários simples."""
    pass

# --- 1. AUTENTICAÇÃO E SEGURANÇA ---

class LoginForm(FlaskForm):
    username = StringField('Usuário ou E-mail', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Acessar Painel')

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[
        DataRequired(), 
        Length(min=4, max=25, message="O usuário deve ter entre 4 e 25 caracteres.")
    ])
    email = StringField('E-mail', validators=[
        DataRequired(), 
        Email(message="Insira um e-mail válido.")
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('password', message='As senhas não conferem.')
    ])
    submit = SubmitField('Criar Administrador')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[
        DataRequired(),
        Length(min=6, message="Mínimo de 6 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(),
        EqualTo('new_password', message='As senhas não conferem.')
    ])
    submit = SubmitField('Atualizar Senha')

# --- 2. SITE PÚBLICO ---

class ContactForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired("Por favor, informe seu nome.")])
    email = StringField('E-mail', validators=[
        DataRequired("O e-mail é obrigatório."), 
        Email("Insira um e-mail válido.")
    ])
    message = TextAreaField('Mensagem', validators=[
        DataRequired("Escreva sua mensagem."),
        Length(min=10, message="Sua mensagem deve ter pelo menos 10 caracteres.")
    ])
    # Campo opcional para selecionar assunto no front-end (validado via choices ou texto)
    subject = StringField('Assunto', validators=[Optional()]) 
    submit = SubmitField('Enviar Solicitação')

# --- 3. GERENCIAMENTO DE CONTEÚDO (ADMIN) ---

class AreaAtuacaoForm(FlaskForm):
    titulo = StringField('Título da Área', validators=[DataRequired()])
    slug = StringField('Slug (URL Amigável)', validators=[
        DataRequired(),
        Length(max=100)
    ], description="Ex: direito-civil (sem espaços ou caracteres especiais)")
    icone = StringField('Ícone (Bootstrap Icons)', default='bi-shield-check', 
                       description="Ex: bi-briefcase, bi-heart (Consulte a documentação do Bootstrap Icons)")
    descricao = TextAreaField('Resumo (Home)', validators=[
        DataRequired(),
        Length(max=300, message="O resumo deve ser breve (máx 300 caracteres).")
    ])
    conteudo_html = TextAreaField('Conteúdo Completo (Página Detalhe)', validators=[Optional()])
    imagem_capa = FileField('Imagem de Capa', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens (JPG, PNG, WEBP)')
    ])
    ordem = IntegerField('Ordem de Exibição', default=0)
    submit = SubmitField('Salvar Área')

class MembroEquipeForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired()])
    cargo = StringField('Cargo / Especialidade', validators=[DataRequired()])
    biografia = TextAreaField('Biografia', validators=[Optional()])
    foto = FileField('Foto de Perfil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens!')
    ])
    ordem = IntegerField('Ordem', default=0)
    submit = SubmitField('Salvar Membro')

# Alias para compatibilidade caso algum código antigo use TeamMemberForm
TeamMemberForm = MembroEquipeForm

class DepoimentoForm(FlaskForm):
    nome_cliente = StringField('Nome do Cliente/Empresa', validators=[DataRequired()])
    texto_depoimento = TextAreaField('Depoimento', validators=[DataRequired()])
    logo_cliente = FileField('Logo ou Foto (Opcional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Apenas imagens!')
    ])
    aprovado = BooleanField('Aprovado (Visível no Site)', default=False)
    submit = SubmitField('Salvar Depoimento')

class ClienteParceiroForm(FlaskForm):
    nome = StringField('Nome da Empresa', validators=[DataRequired()])
    logo = FileField('Logotipo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'webp', 'svg'], 'Imagens permitidas')
    ])
    site_url = StringField('Site (URL)', validators=[Optional(), URL()])
    submit = SubmitField('Salvar Parceiro')

class SectionForm(FlaskForm):
    """Para editar títulos e subtítulos das seções da Home Page"""
    title = StringField('Título', validators=[DataRequired()])
    subtitle = StringField('Subtítulo/Descrição', validators=[Optional()])
    content = TextAreaField('Conteúdo Adicional (HTML)', validators=[Optional()])
    is_active = BooleanField('Seção Ativa', default=True)
    order = IntegerField('Ordem', default=0)
    submit = SubmitField('Atualizar Seção')

# --- 4. CONFIGURAÇÃO DE TEMA ---

class ThemeForm(FlaskForm):
    theme = SelectField('Layout do Site', choices=[
        ('option1', 'Option 1: Invisible Luxury (Clássico Moderno)'),
        ('option2', 'Option 2: Titan Executive (Corporativo Sólido)'),
        ('option3', 'Option 3: Golden Boutique (Elegante & Quente)'),
        ('option4', 'Option 4: Future Tech (Inovação & Digital)')
    ], validators=[DataRequired()])
    submit = SubmitField('Aplicar Tema')

class DesignForm(FlaskForm):
    """Editor visual de cores para os temas"""
    # Option 1
    color_opt1_primary = StringField('Cor Destaque (Luxo)', render_kw={"type": "color"})
    
    # Option 2
    color_opt2_primary = StringField('Cor Primária (Titan)', render_kw={"type": "color"})
    color_opt2_secondary = StringField('Cor Secundária (Titan)', render_kw={"type": "color"})
    
    # Option 3
    color_opt3_primary = StringField('Cor Dourada (Boutique)', render_kw={"type": "color"})
    
    # Option 4
    color_opt4_primary = StringField('Cor Neon (Tech)', render_kw={"type": "color"})

    # General Colors (Light Theme)
    cor_texto = StringField('Texto Principal', render_kw={"type": "color"})
    cor_fundo = StringField('Fundo Principal', render_kw={"type": "color"})

    # General Colors (Dark Theme)
    cor_texto_dark = StringField('Texto (Escuro)', render_kw={"type": "color"})
    cor_fundo_dark = StringField('Fundo (Escuro)', render_kw={"type": "color"})
    cor_fundo_secundario_dark = StringField('Fundo Secundário (Escuro)', render_kw={"type": "color"})
    
    submit = SubmitField('Salvar Personalização')