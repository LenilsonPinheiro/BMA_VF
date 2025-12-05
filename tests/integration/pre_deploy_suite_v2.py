#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Suite Completo - Pré-Deploy (Corrigido)
Detecta erros de banco de dados, modelos, rotas e configuração.
Ajustado para refletir os nomes reais das tabelas (plural) e rotas de auth.
"""

import sys
import os
import unittest
from io import StringIO

# ============================================================================
# CONFIGURAÇÃO DE PATH (CRÍTICO)
# ============================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
sys.path.insert(0, PROJECT_ROOT)
# ============================================================================

class TestPreDeploy(unittest.TestCase):
    """Testes completos antes do deploy"""
    
    @classmethod
    def setUpClass(cls):
        """Setup inicial"""
        print("\n" + "="*80)
        print("INICIANDO BATERIA COMPLETA DE TESTES PRÉ-DEPLOY")
        print(f"Diretório Raiz: {PROJECT_ROOT}")
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
                    
                    if model_name == 'ThemeSettings':
                        required_columns = [
                            'id', 'theme', 'cor_primaria_tema1', 'cor_primaria_tema2',
                            'cor_primaria_tema3', 'cor_primaria_tema4', 'cor_texto',
                            'cor_fundo', 'cor_texto_dark', 'cor_fundo_dark',
                            'cor_fundo_secundario_dark'
                        ]
                        missing = [col for col in required_columns if col not in columns]
                        if missing:
                            self.errors.append(f"❌ ThemeSettings faltando colunas: {', '.join(missing)}")
                            print(f"    ❌ Colunas faltando: {', '.join(missing)}")
                
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
                
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                # CORREÇÃO: Nomes das tabelas conforme definido em models.py (alguns são plurais)
                expected_tables = [
                    'user', 
                    'pagina', 
                    'conteudo_geral', 
                    'areas_atuacao',      # Corrigido de area_atuacao
                    'membro_equipe', 
                    'depoimentos',        # Corrigido de depoimento
                    'clientes_parceiros', # Corrigido de cliente_parceiro
                    'setor_atendido', 
                    'home_page_section', 
                    'theme_settings'
                ]
                
                missing_tables = [t for t in expected_tables if t not in tables]
                if missing_tables:
                    self.errors.append(f"❌ Tabelas faltando: {', '.join(missing_tables)}")
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
                theme = ThemeSettings(theme='light')
                db.session.add(theme)
                db.session.commit()
                
                theme_read = ThemeSettings.query.first()
                self.assertIsNotNone(theme_read)
                # Verifica se o listener populou o default corretamente
                self.assertEqual(theme_read.cor_texto_dark, '#ffffff')
                
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
            
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            # CORREÇÃO: Rotas ajustadas para o que realmente existe no código
            # - /admin/login virou /auth/login
            # - /sobre é dinâmica, então verificamos /areas-de-atuacao que é estática
            essential_routes = [
                '/', 
                '/auth/login', 
                '/contato',
                '/areas-de-atuacao'
            ]
            
            missing_routes = []
            for essential in essential_routes:
                if not any(essential in route for route in routes):
                    missing_routes.append(essential)
            
            if missing_routes:
                self.warnings.append(f"⚠️ Rotas faltando: {', '.join(missing_routes)}")
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
            templates_dir = os.path.join(PROJECT_ROOT, 'BelarminoMonteiroAdvogado', 'templates')
            if not os.path.exists(templates_dir):
                raise FileNotFoundError(f"Templates directory not found: {templates_dir}")
            
            template_count = sum(len([f for f in files if f.endswith('.html')]) for _, _, files in os.walk(templates_dir))
            
            essential_templates = ['base.html', 'home/index.html', 'admin/dashboard.html', 'auth/login.html']
            for template in essential_templates:
                if not os.path.exists(os.path.join(templates_dir, template)):
                    self.warnings.append(f"⚠️ Template faltando: {template}")
            
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
            static_dir = os.path.join(PROJECT_ROOT, 'BelarminoMonteiroAdvogado', 'static')
            if not os.path.exists(static_dir):
                raise FileNotFoundError(f"Static directory not found: {static_dir}")
            
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
            static_dir = os.path.join(PROJECT_ROOT, 'BelarminoMonteiroAdvogado', 'static')
            if os.path.exists(os.path.join(static_dir, 'js', 'video-optimizer.js')):
                self.success.append("✅ Sistema de vídeos verificado")
                print("✅ PASSOU: Otimização de vídeos verificada")
            else:
                self.warnings.append("⚠️ video-optimizer.js não encontrado")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar vídeos: {str(e)}")
            print(f"❌ FALHOU: {str(e)}")

    def test_10_requirements(self):
        """Teste 10: Verificar requirements.txt"""
        print("\nTeste 10: Verificando requirements.txt...")
        try:
            req_path = os.path.join(PROJECT_ROOT, 'requirements.txt')
            if os.path.exists(req_path):
                self.success.append("✅ requirements.txt verificado")
                print("✅ PASSOU: Requirements OK")
            else:
                self.errors.append("❌ requirements.txt não encontrado")
        except Exception as e:
            self.errors.append(f"❌ Erro ao verificar requirements: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        print("\n" + "="*80)
        print("RELATÓRIO FINAL DOS TESTES")
        print("="*80 + "\n")
        
        print(f"✅ SUCESSOS: {len(cls.success)}")
        if cls.warnings:
            print(f"\n⚠️ AVISOS: {len(cls.warnings)}")
            for warning in cls.warnings: print(f"  {warning}")
        
        if cls.errors:
            print(f"\n❌ ERROS CRÍTICOS: {len(cls.errors)}")
            for error in cls.errors: print(f"  {error}")
            print("\n🚨 DEPLOY BLOQUEADO! Corrija os erros acima.")
        else:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema pronto para deploy no Google Cloud!")
        print("\n" + "="*80)

if __name__ == '__main__':
    unittest.main(verbosity=0)