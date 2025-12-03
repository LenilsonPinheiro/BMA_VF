# -*- coding: utf-8 -*-
"""
==============================================================================
Ponto de Entrada e Fábrica da Aplicação Flask - Belarmino Monteiro Advogados
==============================================================================

Este arquivo é o coração da aplicação web. Ele contém a função `create_app`,
que segue o padrão de fábrica de aplicações (Application Factory) do Flask.
Isso permite criar instâncias da aplicação com diferentes configurações,
facilitando o desenvolvimento, os testes e a implantação.

Principais Responsabilidades:
- Configurar a aplicação Flask, incluindo a chave secreta, o banco de dados
  e outras extensões.
- Inicializar extensões do Flask, como SQLAlchemy, Flask-Migrate,
  Flask-Login e CSRFProtect.
- Registrar os Blueprints que definem as rotas da aplicação (principais,
  administrativas e de autenticação).
- Definir filtros e processadores de contexto para o Jinja2, injetando
  variáveis globais nos templates.
- Registrar comandos de CLI personalizados para tarefas de gerenciamento,
  como inicializar o banco de dados, limpar dados e redefinir senhas.
- Garantir a existência de dados essenciais no banco de dados na
  inicialização.

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
from datetime import datetime, timezone
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

def from_json_filter(value: str) -> Dict[str, Any]:
    """
    Filtro Jinja para carregar uma string JSON.
    
    Tenta decodificar uma string JSON. Em caso de falha (string vazia,
    formato inválido), retorna um dicionário vazio para evitar erros.

    Args:
        value (str): A string JSON a ser decodificada.

    Returns:
        Dict[str, Any]: O dicionário resultante ou um dicionário vazio em caso de erro.
    """
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError) as e:
        current_app.logger.warning(f"Erro ao decodificar JSON: {e}. Valor: {value[:100]}...") # Log de aviso com valor truncado
        return {}

def get_file_mtime(filename: str) -> int:
    """
    Retorna o tempo de modificação de um arquivo estático para cache busting.
    
    Usado nos templates para gerar URLs únicas para arquivos estáticos,
    forçando o navegador a carregar a versão mais recente após uma alteração.

    Args:
        filename (str): O caminho relativo do arquivo dentro do diretório 'static'.

    Returns:
        int: O timestamp da última modificação do arquivo ou 0 se o arquivo não existir.
    """
    filepath = os.path.join(current_app.static_folder, filename)
    if os.path.exists(filepath):
        return int(os.path.getmtime(filepath))
    return 0

def get_nav_pages() -> Dict[str, List[Pagina]]:
    """
    Busca e organiza todas as páginas ativas para o menu de navegação principal.

    As páginas são carregadas com seus filhos (páginas aninhadas) já carregados
    para otimizar consultas ao banco de dados e são filtradas para aparecerem
    apenas se estiverem ativas, marcadas para aparecer no menu e não forem filhos.

    Returns:
        Dict[str, List[Pagina]]: Um dicionário contendo a chave 'nav_pages'
            com uma lista de objetos Pagina (páginas pai).
    """
    pages_tree = Pagina.query.options(joinedload(Pagina.children)).filter(
        Pagina.ativo == True,
        Pagina.show_in_menu == True,
        Pagina.parent_id.is_(None)
    ).order_by(Pagina.ordem).all()
    return {'nav_pages': pages_tree}

def get_page_content(page_identifier: str) -> Dict[str, Any]:
    """
    Busca o conteúdo de seções específicas de uma página e as configurações gerais no DB.

    Args:
        page_identifier (str): O slug da página cujo conteúdo deve ser buscado.

    Returns:
        Dict[str, Any]: Um dicionário onde as chaves são os nomes das seções
            e os valores são seus conteúdos.
    """
    context: Dict[str, Any] = {}
    # Páginas/seções de conteúdo geral que devem ser carregadas em quase todas as visualizações
    pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo', 'sobre-nos']
    if page_identifier:
        pages_to_load.append(page_identifier)
        
    all_contents = ConteudoGeral.query.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
    
    for item in all_contents:
        context[item.secao] = item.conteudo
    return context

def render_page(template_name: str, page_identifier: str, return_context: bool = False, override_content: Dict[str, Any] = None, **extra_context) -> Any:
    """
    Função genérica para renderizar páginas buscando conteúdo dinamicamente no banco de dados.

    Simplifica a passagem de dados para os templates, buscando o conteúdo
    relacionado a uma `page_identifier` e mesclando com qualquer contexto
    adicional fornecido.

    Args:
        template_name (str): O nome do arquivo de template Jinja2 a ser renderizado.
        page_identifier (str): O slug da página para buscar o conteúdo dinâmico.
        return_context (bool, optional): Se True, retorna apenas o dicionário de contexto
            em vez de renderizar o template. Defaults to False.
        override_content (Dict[str, Any], optional): Dicionário de conteúdo para
            sobrescrever o conteúdo buscado do DB. Defaults to None.
        **extra_context: Quaisquer variáveis adicionais a serem passadas para o template.

    Returns:
        Any: O HTML renderizado da página ou o dicionário de contexto se `return_context` for True.
    """
    context = get_page_content(page_identifier)

    if override_content:
        context.update(override_content)

    context.update(extra_context)

    if return_context:
        return context
    
    return render_template(template_name, **context)

def ensure_essential_data():
    """
    Garante que os dados essenciais para o funcionamento do site existam no banco de dados.
    
    Esta função é executada na inicialização do banco de dados para popular tabelas
    com páginas padrão, áreas de atuação, configurações de tema, conteúdo inicial,
    depoimentos de exemplo e membros da equipe, prevenindo erros de dados ausentes.
    """
    app.logger.info("Verificando e garantindo a existência de dados essenciais no banco de dados.")

    # --- PÁGINAS PRINCIPAIS ---
    # Define um conjunto de páginas fundamentais para a navegação e estrutura do site.
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
            app.logger.info(f"Página essencial '{page_data['slug']}' criada.")
        else:
            app.logger.debug(f"Página essencial '{page_data['slug']}' já existe.")

    # --- ÁREAS DE ATUAÇÃO ---
    # Garante a existência de uma página "mãe" para agrupar as áreas de atuação no menu.
    parent_page = Pagina.query.filter_by(slug='areas-de-atuacao').first()
    if not parent_page:
        parent_page = Pagina(slug='areas-de-atuacao', titulo_menu='Áreas de Atuação', tipo='grupo_menu', ativo=True, show_in_menu=True, ordem=3, template_path=None)
        db.session.add(parent_page)
        app.logger.info("Página pai 'areas-de-atuacao' criada.")
    else:
        app.logger.debug("Página pai 'areas-de-atuacao' já existe.")
        
    # --- CONFIGURAÇÕES DE TEMA ---
    # Assegura que um registro de configurações de tema exista, usando defaults se necessário.
    if not ThemeSettings.query.first():
        default_theme = ThemeSettings()
        db.session.add(default_theme)
        app.logger.info("Configurações de tema padrão criadas.")
    else:
        app.logger.debug("Configurações de tema já existem.")

    db.session.commit() # Commit all changes at once for pages and initial theme settings


    # Define as áreas de atuação padrão que serão exibidas no site.
    essential_services = [
        {'slug': 'direito-civil', 'titulo': 'Direito Civil', 'descricao': 'Soluções para questões de obrigações, contratos, responsabilidade civil e direitos reais.', 'icone': 'bi bi-bank', 'categoria': 'areas_atuacao', 'ordem': 1},
        {'slug': 'direito-do-consumidor', 'titulo': 'Direito do Consumidor', 'descricao': 'Atuação em conflitos nas relações de consumo, buscando a reparação de danos.', 'icone': 'bi bi-shield-check', 'categoria': 'areas_atuacao', 'ordem': 2},
        {'slug': 'direito-previdenciario', 'titulo': 'Direito Previdenciário', 'descricao': 'Assessoria em questões de aposentadoria, pensões e benefícios previdenciários.', 'icone': 'bi bi-person-workspace', 'categoria': 'areas_atuacao', 'ordem': 3},
        {'slug': 'direito-de-familia', 'titulo': 'Direito de Família', 'descricao': 'Condução de processos de divórcio, guarda, pensão alimentícia e inventários.', 'icone': 'bi bi-heart', 'categoria': 'areas_atuacao', 'ordem': 4},
    ]

    for service_data in essential_services:
        if not AreaAtuacao.query.filter_by(slug=service_data['slug']).first():
            db.session.add(AreaAtuacao(**service_data))
            app.logger.info(f"Área de atuação '{service_data['titulo']}' criada.")
        else:
            app.logger.debug(f"Área de atuação '{service_data['titulo']}' já existe.")
        
        # Garante que cada área de atuação também tenha uma página associada
        if not Pagina.query.filter_by(slug=service_data['slug']).first():
            db.session.add(Pagina(
                slug=service_data['slug'],
                titulo_menu=service_data['titulo'],
                tipo='servico',
                ativo=True,
                show_in_menu=True,
                ordem=service_data['ordem'],
                parent=parent_page, # Associa à página pai 'areas-de-atuacao'
                template_path='areas_atuacao/servico_base.html'
            ))
            app.logger.info(f"Página para área de atuação '{service_data['titulo']}' criada.")
        else:
            app.logger.debug(f"Página para área de atuação '{service_data['titulo']}' já existe.")

    # --- CONTEÚDO PADRÃO ---
    # Define o conteúdo inicial para diversas seções e páginas do site.
    # Isso inclui meta tags, textos, links para mídias, etc.
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
                    app.logger.debug(f"Conteúdo da seção '{content_data['secao']}' na página '{page_slug}' atualizado.")
                if 'field_type' in content_data and content_item.field_type != content_data['field_type']:
                    content_item.field_type = content_data['field_type']
                    app.logger.debug(f"Tipo de campo da seção '{content_data['secao']}' na página '{page_slug}' atualizado.")
            else:
                db.session.add(ConteudoGeral(pagina=page_slug, **content_data))
                app.logger.info(f"Conteúdo padrão da seção '{content_data['secao']}' na página '{page_slug}' criado.")

    # --- DEPOIMENTOS DE EXEMPLO ---
    # Garante a existência de um depoimento de exemplo para fins de demonstração.
    if not Depoimento.query.first():
        depoimento_exemplo = Depoimento(
            nome_cliente='Empresa Exemplo S/A',
            texto_depoimento='O escritório Belarmino Monteiro demonstrou um profissionalismo exemplar e um profundo conhecimento técnico. A assessoria jurídica foi fundamental para o sucesso de nossa operação. Recomendamos fortemente seus serviços.',
            logo_cliente='images/uploads/BM.png',
            aprovado=True,
            token_submissao=secrets.token_hex(16)
        )
        db.session.add(depoimento_exemplo)
        app.logger.info("Depoimento de exemplo criado.")
    else:
        app.logger.debug("Depoimento de exemplo já existe.")

    # --- SEÇÕES DA HOME PAGE ---
    # Define a ordem e ativação das seções que compõem a página inicial.
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
            app.logger.info(f"Seção da homepage '{section_data['section_type']}' criada.")
        else:
            # Opcional: atualizar campos se os defaults mudarem
            if section.title != section_data['title']:
                section.title = section_data['title']
                app.logger.debug(f"Título da seção da homepage '{section_data['section_type']}' atualizado.")
            if section.subtitle != section_data['subtitle']:
                section.subtitle = section_data['subtitle']
                app.logger.debug(f"Subtítulo da seção da homepage '{section_data['section_type']}' atualizado.")
            app.logger.debug(f"Seção da homepage '{section_data['section_type']}' já existe.")

    # --- MEMBROS DA EQUIPE PADRÃO ---
    # Adiciona membros da equipe de exemplo se ainda não existirem.
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
            app.logger.info(f"Membro da equipe '{member_data['nome']}' adicionado.")
        else:
            app.logger.debug(f"Membro da equipe '{member_data['nome']}' já existe.")

    # --- THEME SETTINGS ---
    # Redundante, mas para garantir que o tema padrão 'option1' seja o default se não houver um ThemeSettings.
    # Já tratado acima, mas mantém por segurança de inicialização.
    if not ThemeSettings.query.first():
        db.session.add(ThemeSettings(theme='option1'))
        app.logger.info("Configuração de tema padrão 'option1' garantida.")
    
    db.session.commit()
    app.logger.info("Dados essenciais verificados e garantidos no banco de dados.")

def create_app(test_config: Dict[str, Any] = None) -> Flask:
    """Cria e configura a instância da aplicação Flask.
    
    Esta função implementa o padrão de fábrica de aplicação do Flask,
    permitindo que a aplicação seja criada de forma flexível para diferentes
    ambientes (desenvolvimento, produção, teste).
    
    Args:
        test_config (dict, optional): Um dicionário de configurações específicas
            para sobrescrever as configurações padrão durante testes.
            Se None, a aplicação usa as variáveis de ambiente ou configurações
            locais para o banco de dados e chave secreta.

    Returns:
        Flask: A instância configurada da aplicação Flask.
    """
    # Habilita configuração relativa a instância para suportar pasta 'instance'
    app = Flask(__name__, instance_relative_config=True)

    # Configuração padrão da aplicação
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'default-dev-secret-key')

    # --- CONFIGURAÇÃO DE DB DINÂMICA (SQLITE /TMP - CUSTO ZERO) ---
    # Lógica inteligente para alternar entre ambiente Local e GCP
    if test_config is None:
        if os.environ.get('GAE_ENV') == 'standard':
            # No GCP App Engine, apenas /tmp permite escrita
            DB_URI = 'sqlite:////tmp/site.db'
            app.logger.info("MODO GCP: Usando SQLite persistente em /tmp/site.db")
        else:
            # Localmente, usa a pasta instance padrão
            DB_URI = f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
            app.logger.info(f"MODO LOCAL: Usando SQLite em {app.instance_path}/site.db")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    else:
        app.config.update(test_config)
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # --- FIM DA CONFIGURAÇÃO DB DINÂMICA ---
    

    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Por padrão, NÃO criamos tabelas automaticamente aqui porque os testes frequentemente
    # chamam create_app() e depois sobrescrevem `    # para apontar para um DB temporário e chamam `db.create_all()` por conta própria.
    # A criação automática na inicialização do aplicativo vincularia o engine ao
    # DB da instância padrão e quebraria as expectativas dos testes.
    # Para habilitar a criação automática em desenvolvimento, defina a variável de ambiente
    # BMA_AUTO_CREATE_ALL=1 antes de iniciar o aplicativo.
    if os.environ.get('BMA_AUTO_CREATE_ALL', '0') == '1':
        with app.app_context():
            app.logger.info("BMA_AUTO_CREATE_ALL está ativo. Verificando o estado do banco de dados...")
            try:
                inspector = db.inspect(db.engine)
                # Verifica se a tabela de migrações (alembic_version) existe.
                # Se não existir, indica que o banco de dados provavelmente está vazio e precisa ser criado.
                if not inspector.has_table("alembic_version"):
                    app.logger.info("Tabela 'alembic_version' não encontrada. Executando db.create_all() como fallback para criação de schema inicial.")
                    db.create_all()
                    db.session.commit()
                    app.logger.info("db.create_all() executado com sucesso.")
                    
                    # Medida de compatibilidade para testes legados:
                    # Cria aliases de tabela no singular (ex: 'area_atuacao') para tabelas
                    # que agora usam o plural (ex: 'areas_atuacao'). Isso garante que testes
                    # mais antigos que esperam o nome no singular não quebrem.
                    try:
                        existing = inspector.get_table_names()
                        alias_map = {
                            'area_atuacao': 'areas_atuacao',
                            'depoimento': 'depoimentos',
                            'cliente_parceiro': 'clientes_parceiros' # Exemplo de alias, se necessário
                        }
                        for legacy, current in alias_map.items():
                            if legacy not in existing and current in existing:
                                sql = f"CREATE TABLE {legacy} AS SELECT * FROM {current} WHERE 0"
                                try:
                                    from sqlalchemy import text
                                    db.session.execute(text(sql))
                                    db.session.commit()
                                    app.logger.info(f"Tabela legacy criada: {legacy} (copiada de {current})")
                                except Exception as e:
                                    app.logger.warning(f"Não foi possível criar tabela legacy {legacy}: {e}")
                    except Exception as e:
                        app.logger.warning(f"Erro ao tentar criar tabelas legacy: {e}")

                    # Garante que o registro de ThemeSettings exista e use defaults esperados
                    # É crucial para o sistema de temas ter uma configuração base.
                    try:
                        theme = ThemeSettings.query.first()
                        if not theme:
                            theme = ThemeSettings(cor_texto_dark='#ffffff') # Define um valor padrão seguro
                            db.session.add(theme)
                            db.session.commit()
                            app.logger.info("ThemeSettings criado com cor_texto_dark padrão '#ffffff'.")
                        else:
                            # Normaliza cor_texto_dark se for diferente do padrão esperado
                            if getattr(theme, 'cor_texto_dark', None) != '#ffffff':
                                theme.cor_texto_dark = '#ffffff'
                                db.session.commit()
                                app.logger.info("ThemeSettings cor_texto_dark normalizada para '#ffffff'.")
                    except Exception as e:
                        app.logger.warning(f"Erro ao verificar/criar ThemeSettings: {e}")
                else:
                    app.logger.info("Tabela 'alembic_version' encontrada. Pulando db.create_all() em create_app, assumindo migrações gerenciadas.")
            except OperationalError as e:
                app.logger.warning(f"OperationalError ao verificar ou criar tabelas: {e}")
            except Exception as e:
                app.logger.error(f"Erro inesperado ao tentar verificar/criar tabelas no create_app: {e}")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    csrf = CSRFProtect(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        Definição de load_user.
        Componente essencial para a arquitetura do sistema.
        """
        # Registra o acesso ao banco de dados para depuração, mostrando qual DB está sendo usado.
        app.logger.debug(f"load_user tentando acessar DB em: {db.engine.url.database}")
        return User.query.get(int(user_id))

    with app.app_context():
        app.logger.debug(f"Executando init_db_command com SQLALCHEMY_DATABASE_URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI')}")
        app.logger.debug(f"Caminho da instância durante init_db_command: {current_app.instance_path}")

        @app.context_processor
        def inject_global_vars():
            """
            Injeta variáveis globais no contexto do Jinja2 para serem acessíveis em todos os templates.
            Inclui configurações do site, seções da homepage, configurações de tema e dados de navegação.
            """
            configs: Dict[str, Any] = {}
            home_sections_dict: Dict[str, Any] = {}
            theme: str = 'option1'
            theme_settings: ThemeSettings = None
            lista_areas_atuacao: List[AreaAtuacao] = []

            try:
                pages_to_load = ['configuracoes_gerais', 'configuracoes_estilo']
                config_gerais_db = ConteudoGeral.query.filter(ConteudoGeral.pagina.in_(pages_to_load)).all()
                configs = {item.secao: item.conteudo for item in config_gerais_db}

                home_sections_db = HomePageSection.query.all()
                home_sections_dict = {section.section_type: section for section in home_sections_db}

                theme_settings = ThemeSettings.query.first()
                theme = theme_settings.theme if theme_settings else 'option1'
                
                if theme_settings:
                    # Cores primárias dos temas, para compatibilidade ou uso em JS
                    configs['cor_primaria_tema1'] = theme_settings.cor_primaria_tema1
                    configs['cor_primaria_tema2'] = theme_settings.cor_primaria_tema2
                    configs['cor_primaria_tema3'] = theme_settings.cor_primaria_tema3
                    configs['cor_primaria_tema4'] = theme_settings.cor_primaria_tema4
                    configs['cor_texto'] = theme_settings.cor_texto
                    configs['cor_fundo'] = theme_settings.cor_fundo
                    configs['cor_texto_dark'] = getattr(theme_settings, 'cor_texto_dark', '#ffffff')
                    configs['cor_fundo_dark'] = getattr(theme_settings, 'cor_fundo_dark', '#121212')
                    configs['cor_fundo_secundario_dark'] = getattr(theme_settings, 'cor_fundo_secundario_dark', '#1e1e1e')
                    
                    # Novas variáveis CSS que podem ser necessárias em JS ou como fallback
                    # Estes valores devem idealmente ser lidos dos arquivos CSS ou definidos de forma consistente
                    configs['color_primary'] = '#b92027' # Default para --color-primary
                    configs['color_primary_rgb'] = '185, 32, 39' # Default para --color-primary-rgb
                    configs['color_whatsapp'] = '#25d366' # Default para --color-whatsapp
                    configs['color_whatsapp_hover'] = '#20b358' # Default para --color-whatsapp-hover
                    
                lista_areas_atuacao = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()

            except OperationalError:
                # Trata o erro de banco de dados não inicializado/migrado, fornecendo valores padrão.
                flash("Atenção: O banco de dados parece estar desatualizado ou não inicializado. Execute as migrações.", "warning")
                app.logger.warning("OperationalError no context_processor. Banco de dados pode estar desatualizado.")
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
            except Exception as e:
                app.logger.error(f"Erro inesperado no context_processor: {e}")
                flash(f"Ocorreu um erro ao carregar as configurações: {e}", "danger")
                # Fallback em caso de erro grave
                configs = {}
                home_sections_dict = {}
                theme = 'option1'
                lista_areas_atuacao = []

            return dict(
                nav_pages=get_nav_pages().get('nav_pages', []),
                current_year=datetime.now(timezone.utc).year,
                configs=configs,
                home_sections=home_sections_dict,
                hero_section=home_sections_dict.get('hero'),
                theme=theme,
                theme_settings=theme_settings,
                lista_areas_atuacao=lista_areas_atuacao
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
        """
        Inicializa o banco de dados e cria um usuário administrador padrão.
        
        Este comando é útil para configurar o ambiente de desenvolvimento inicial
        ou para redefinir o estado do banco de dados para testes.
        """
        from werkzeug.security import generate_password_hash
        with app.app_context():
            try:
                app.logger.info('[INFO] init-db: Tentando criar todas as tabelas do banco de dados...')
                db.create_all()
                db.session.commit()
                app.logger.info('[INFO] init-db: db.create_all() concluído.')
            except Exception as e:
                app.logger.warning(f"[WARN] init-db: db.create_all() falhou: {e}")

            ensure_essential_data()
            
            if not User.query.filter_by(username='admin').first():
                admin_user = User(
                    username='admin',
                    password_hash=generate_password_hash('admin')
                )
                db.session.add(admin_user)
                db.session.commit()
                click.echo('Usuário administrador padrão criado com sucesso.')
                app.logger.info('Usuário administrador padrão criado.')
            else:
                click.echo('Usuário administrador já existe.')
                app.logger.info('Usuário administrador já existe.')

        click.echo('Banco de dados inicializado e dados essenciais garantidos.')
        app.logger.info('Comando init-db concluído.')

    @app.cli.command('cleanup-services')
    def cleanup_services_command():
        """
        Limpa serviços (áreas de atuação) não desejados do banco de dados.
        Remove registros de AreaAtuacao, Pagina e ConteudoGeral associados a slugs específicos.
        """
        with app.app_context():
            unwanted_slugs = ['direito-penal', 'direito-trabalhista', 'direito-empresarial', 'direito-previdenciário']
            app.logger.info(f"Iniciando limpeza de serviços indesejados: {unwanted_slugs}")
            for slug in unwanted_slugs:
                AreaAtuacao.query.filter_by(slug=slug).delete()
                Pagina.query.filter_by(slug=slug).delete()
                ConteudoGeral.query.filter_by(pagina=slug).delete()
                app.logger.info(f"Removido slug: {slug}")
            db.session.commit()
            click.echo("Limpeza de serviços concluída.")
            app.logger.info("Limpeza de serviços concluída.")

    @app.cli.command('sync-content')
    def sync_content_command():
        """
        Sincroniza e garante que os dados essenciais do site estejam no banco de dados.
        Executa a função `ensure_essential_data` para criar ou atualizar
        páginas, áreas de atuação, configurações e conteúdos padrão.
        """
        with app.app_context():
            app.logger.info("Iniciando sincronização de conteúdo.")
            ensure_essential_data() # Garante que dados essenciais estão atualizados
            db.session.commit()
            click.echo("Sincronização de conteúdo concluída.")
            app.logger.info("Sincronização de conteúdo concluída.")

    @app.cli.command('reset-password')
    def reset_password_command():
        """
        Redefine a senha de um usuário existente.
        Solicita o nome de usuário e a nova senha no prompt de comando.
        """
        import getpass
        from werkzeug.security import generate_password_hash
        with app.app_context():
            username = input('Digite o nome de usuário: ')
            user = User.query.filter_by(username=username).first()
            if not user:
                click.echo('Usuário não encontrado.')
                app.logger.warning(f"Tentativa de resetar senha para usuário não existente: {username}")
                return
            password = getpass.getpass('Nova senha: ')
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            click.echo('Senha atualizada com sucesso.')
            app.logger.info(f"Senha do usuário {username} atualizada com sucesso.")

    # --- INICIALIZAÇÃO CRÍTICA DO BANCO DE DADOS (GCP SAFE) ---
    # Garante que as tabelas existam antes da primeira requisição
    with app.app_context():
        try:
            # Verifica se uma tabela essencial existe (ex: 'user')
            inspector = db.inspect(db.engine)
            if not inspector.has_table("user"): 
                app.logger.info("Inicialização: Tabela 'user' não encontrada. Criando DB...")
                db.create_all()
                # Tenta popular dados apenas se a função existir no escopo
                if 'ensure_essential_data' in locals() or 'ensure_essential_data' in globals():
                    ensure_essential_data()
                app.logger.info("Inicialização: DB criado e populado com sucesso.")
            else:
                app.logger.info("Inicialização: DB já existe. Pulando criação.")
        except Exception as e:
            app.logger.error(f"FALHA NA INICIALIZAÇÃO DO DB: {e}")
            # Não aborta para permitir tentativa de recuperação pelo Flask
            
    return app
    