#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Suite Completo - Pré-Deploy
Detecta erros de banco de dados, modelos, rotas e configuração
"""

import sys
import os
import unittest
from io import StringIO

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPreDeploy(unittest.TestCase):
    """Testes completos antes do deploy"""
    
    @classmethod
    def setUpClass(cls):
        """Setup inicial"""
        print("\n" + "="*80)
        print("INICIANDO BATERIA COMPLETA DE TESTES PRÉ-DEPLOY")
        print("="*80 + "\n")
        cls.errors = []
        cls.warnings = []
        cls.success = []
    
    def test_01_import_app(self):
        """Teste 1: Importar aplicação"""
        print("Teste 1: Importando aplicação...")
        try:
            from BelarminoMonteiroAdvogado import create_app
            app = create_app()
            self.assertIsNotNone(app)
            self.success.append("✅ Aplicação importada com sucesso")
            print("✅ PASSOU: Aplicação importada")
        except Exception as e:
            self.errors.append(f"❌ Erro ao importar aplicação: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_02_database_models(self):
        """Teste 2: Verificar modelos do banco de dados"""
        print("\nTeste 2: Verificando modelos do banco de dados...")
        try:
            from BelarminoMonteiroAdvogado import create_app
            from BelarminoMonteiroAdvogado.models import (
                db, User, Pagina, ConteudoGeral, AreaAtuacao,
                MembroEquipe, Depoimento, ClienteParceiro,
                SetorAtendido, HomePageSection, ThemeSettings
            )
            
            app = create_app()
            with app.app_context():
                # Verificar se todos os modelos têm as colunas esperadas
                models_to_check = {
                    'User': User,
                    'Pagina': Pagina,
                    'ConteudoGeral': ConteudoGeral,
                    'AreaAtuacao': AreaAtuacao,
                    'MembroEquipe': MembroEquipe,
                    'Depoimento': Depoimento,
                    'ClienteParceiro': ClienteParceiro,
                    'SetorAtendido': SetorAtendido,
                    'HomePageSection': HomePageSection,
                    'ThemeSettings': ThemeSettings
                }
                
                for model_name, model_class in models_to_check.items():
                    columns = [c.name for c in model_class.__table__.columns]
                    print(f"  - {model_name}: {len(columns)} colunas")
                    
                    # Verificação especial para ThemeSettings
                    if model_name == 'ThemeSettings':
                        required_columns = [
                            'id', 'theme', 'cor_primaria_tema1', 'cor_primaria_tema2',
                            'cor_primaria_tema3', 'cor_primaria_tema4', 'cor_texto',
                            'cor_fundo', 'cor_texto_dark', 'cor_fundo_dark',
                            'cor_fundo_secundario_dark'
                        ]
                        missing = [col for col in required_columns if col not in columns]
                        if missing:
                            self.errors.append(
                                f"❌ ThemeSettings faltando colunas: {', '.join(missing)}"
                            )
                            print(f"    ❌ Colunas faltando: {', '.join(missing)}")
                        else:
                            print(f"    ✅ Todas as colunas presentes")
                
                self.success.append("✅ Modelos do banco verificados")
                print("✅ PASSOU: Modelos verificados")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar modelos: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_03_database_creation(self):
        """Teste 3: Criar banco de dados"""
        print("\nTeste 3: Criando banco de dados de teste...")
        try:
            from BelarminoMonteiroAdvogado import create_app
            from BelarminoMonteiroAdvogado.models import db
            
            app = create_app()
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            
            with app.app_context():
                db.create_all()
                
                # Verificar se as tabelas foram criadas
                tables = db.engine.table_names()
                expected_tables = [
                    'user', 'pagina', 'conteudo_geral', 'area_atuacao',
                    'membro_equipe', 'depoimento', 'cliente_parceiro',
                    'setor_atendido', 'home_page_section', 'theme_settings'
                ]
                
                missing_tables = [t for t in expected_tables if t not in tables]
                if missing_tables:
                    self.errors.append(
                        f"❌ Tabelas faltando: {', '.join(missing_tables)}"
                    )
                    print(f"❌ Tabelas faltando: {', '.join(missing_tables)}")
                else:
                    print(f"✅ Todas as {len(tables)} tabelas criadas")
                
                self.success.append("✅ Banco de dados criado com sucesso")
                print("✅ PASSOU: Banco criado")
        except Exception as e:
            self.errors.append(f"❌ Erro ao criar banco: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_04_theme_settings_columns(self):
        """Teste 4: Verificar colunas específicas do ThemeSettings"""
        print("\nTeste 4: Verificando colunas do ThemeSettings...")
        try:
            from BelarminoMonteiroAdvogado import create_app
            from BelarminoMonteiroAdvogado.models import db, ThemeSettings
            
            app = create_app()
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            
            with app.app_context():
                db.create_all()
                
                # Tentar criar um registro com todas as colunas
                theme = ThemeSettings(
                    theme='light',
                    cor_primaria_tema1='#1a1a1a',
                    cor_primaria_tema2='#2a2a2a',
                    cor_primaria_tema3='#3a3a3a',
                    cor_primaria_tema4='#4a4a4a',
                    cor_texto='#000000',
                    cor_fundo='#ffffff',
                    cor_texto_dark='#ffffff',  # Coluna que estava faltando!
                    cor_fundo_dark='#1a1a1a',
                    cor_fundo_secundario_dark='#2a2a2a'
                )
                
                db.session.add(theme)
                db.session.commit()
                
                # Tentar ler o registro
                theme_read = ThemeSettings.query.first()
                self.assertIsNotNone(theme_read)
                self.assertEqual(theme_read.cor_texto_dark, '#ffffff')
                
                print("✅ Todas as colunas do ThemeSettings funcionando")
                self.success.append("✅ ThemeSettings com todas as colunas")
                print("✅ PASSOU: ThemeSettings OK")
        except Exception as e:
            self.errors.append(f"❌ Erro no ThemeSettings: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_05_routes_import(self):
        """Teste 5: Importar todas as rotas"""
        print("\nTeste 5: Importando rotas...")
        try:
            from BelarminoMonteiroAdvogado.routes import main_routes, admin_routes, auth_routes
            
            self.assertIsNotNone(main_routes)
            self.assertIsNotNone(admin_routes)
            self.assertIsNotNone(auth_routes)
            
            print("✅ Todas as rotas importadas")
            self.success.append("✅ Rotas importadas com sucesso")
            print("✅ PASSOU: Rotas OK")
        except Exception as e:
            self.errors.append(f"❌ Erro ao importar rotas: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_06_app_routes(self):
        """Teste 6: Verificar rotas registradas"""
        print("\nTeste 6: Verificando rotas registradas...")
        try:
            from BelarminoMonteiroAdvogado import create_app
            
            app = create_app()
            
            # Listar todas as rotas
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(str(rule))
            
            print(f"  Total de rotas: {len(routes)}")
            
            # Verificar rotas essenciais
            essential_routes = ['/', '/admin/login', '/sobre', '/contato']
            missing_routes = [r for r in essential_routes if r not in routes]
            
            if missing_routes:
                self.warnings.append(
                    f"⚠️ Rotas faltando: {', '.join(missing_routes)}"
                )
                print(f"⚠️ Rotas faltando: {', '.join(missing_routes)}")
            else:
                print("✅ Todas as rotas essenciais presentes")
            
            self.success.append(f"✅ {len(routes)} rotas registradas")
            print("✅ PASSOU: Rotas registradas")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar rotas: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_07_templates_exist(self):
        """Teste 7: Verificar existência de templates"""
        print("\nTeste 7: Verificando templates...")
        try:
            templates_dir = 'BelarminoMonteiroAdvogado/templates'
            
            if not os.path.exists(templates_dir):
                self.errors.append(f"❌ Diretório de templates não encontrado")
                print(f"❌ Diretório não encontrado")
                raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
            
            # Contar templates
            template_count = 0
            for root, dirs, files in os.walk(templates_dir):
                template_count += len([f for f in files if f.endswith('.html')])
            
            print(f"  Total de templates: {template_count}")
            
            # Verificar templates essenciais
            essential_templates = [
                'base.html',
                'home/index.html',
                'admin/dashboard.html',
                'auth/login.html'
            ]
            
            for template in essential_templates:
                template_path = os.path.join(templates_dir, template)
                if not os.path.exists(template_path):
                    self.warnings.append(f"⚠️ Template faltando: {template}")
                    print(f"  ⚠️ Faltando: {template}")
            
            self.success.append(f"✅ {template_count} templates encontrados")
            print("✅ PASSOU: Templates verificados")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar templates: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_08_static_files(self):
        """Teste 8: Verificar arquivos estáticos"""
        print("\nTeste 8: Verificando arquivos estáticos...")
        try:
            static_dir = 'BelarminoMonteiroAdvogado/static'
            
            if not os.path.exists(static_dir):
                self.errors.append(f"❌ Diretório static não encontrado")
                print(f"❌ Diretório não encontrado")
                raise FileNotFoundError(f"Static directory not found: {static_dir}")
            
            # Verificar subdiretórios
            subdirs = ['css', 'js', 'images']
            for subdir in subdirs:
                subdir_path = os.path.join(static_dir, subdir)
                if os.path.exists(subdir_path):
                    file_count = len([f for f in os.listdir(subdir_path) 
                                    if os.path.isfile(os.path.join(subdir_path, f))])
                    print(f"  {subdir}/: {file_count} arquivos")
                else:
                    self.warnings.append(f"⚠️ Subdiretório faltando: {subdir}")
                    print(f"  ⚠️ Faltando: {subdir}/")
            
            self.success.append("✅ Arquivos estáticos verificados")
            print("✅ PASSOU: Arquivos estáticos OK")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar static: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
            raise
    
    def test_09_video_optimizer(self):
        """Teste 9: Verificar sistema de otimização de vídeos"""
        print("\nTeste 9: Verificando otimização de vídeos...")
        try:
            video_optimizer_js = 'BelarminoMonteiroAdvogado/static/js/video-optimizer.js'
            video_optimizer_css = 'BelarminoMonteiroAdvogado/static/css/video-optimizer.css'
            
            if os.path.exists(video_optimizer_js):
                print("  ✅ video-optimizer.js encontrado")
            else:
                self.warnings.append("⚠️ video-optimizer.js não encontrado")
                print("  ⚠️ video-optimizer.js não encontrado")
            
            if os.path.exists(video_optimizer_css):
                print("  ✅ video-optimizer.css encontrado")
            else:
                self.warnings.append("⚠️ video-optimizer.css não encontrado")
                print("  ⚠️ video-optimizer.css não encontrado")
            
            self.success.append("✅ Sistema de vídeos verificado")
            print("✅ PASSOU: Otimização de vídeos verificada")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar vídeos: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
    
    def test_10_requirements(self):
        """Teste 10: Verificar requirements.txt"""
        print("\nTeste 10: Verificando requirements.txt...")
        try:
            if not os.path.exists('requirements.txt'):
                self.errors.append("❌ requirements.txt não encontrado")
                print("❌ requirements.txt não encontrado")
                raise FileNotFoundError("requirements.txt not found")
            
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            
            essential_packages = [
                'Flask', 'Flask-SQLAlchemy', 'Flask-Login',
                'Flask-Migrate', 'Flask-WTF', 'gunicorn'
            ]
            
            missing_packages = []
            for package in essential_packages:
                if package not in requirements:
                    missing_packages.append(package)
            
            if missing_packages:
                self.warnings.append(
                    f"⚠️ Pacotes faltando: {', '.join(missing_packages)}"
                )
                print(f"  ⚠️ Faltando: {', '.join(missing_packages)}")
            else:
                print("  ✅ Todos os pacotes essenciais presentes")
            
            self.success.append("✅ requirements.txt verificado")
            print("✅ PASSOU: Requirements OK")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar requirements: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")
    
    @classmethod
    def tearDownClass(cls):
        """Relatório final"""
        print("\n" + "="*80)
        print("RELATÓRIO FINAL DOS TESTES")
        print("="*80 + "\n")
        
        print(f"✅ SUCESSOS: {len(cls.success)}")
        for success in cls.success:
            print(f"  {success}")
        
        if cls.warnings:
            print(f"\n⚠️ AVISOS: {len(cls.warnings)}")
            for warning in cls.warnings:
                print(f"  {warning}")
        
        if cls.errors:
            print(f"\n❌ ERROS: {len(cls.errors)}")
            for error in cls.errors:
                print(f"  {error}")
            print("\n🚨 DEPLOY BLOQUEADO! Corrija os erros antes de fazer deploy.")
        else:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema pronto para deploy!")
        
        print("\n" + "="*80)

def run_tests():
    """Executar todos os testes"""
    # Criar test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPreDeploy)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de saída
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
