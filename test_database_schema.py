#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste Específico de Schema do Banco de Dados
Detecta incompatibilidades entre modelos e banco existente
"""

import sys
import os
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestDatabaseSchema(unittest.TestCase):
    """Testes de schema do banco de dados"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
    
    def tearDown(self):
        """Cleanup após cada teste"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_01_create_old_schema(self):
        """Teste 1: Criar schema antigo (sem cor_texto_dark)"""
        print("\n" + "="*80)
        print("Teste 1: Simulando banco de dados ANTIGO (sem cor_texto_dark)")
        print("="*80)
        
        import sqlite3
        
        # Criar banco com schema antigo (SEM cor_texto_dark)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Schema antigo do ThemeSettings (FALTANDO cor_texto_dark)
        cursor.execute('''
            CREATE TABLE theme_settings (
                id INTEGER PRIMARY KEY,
                theme VARCHAR(50),
                cor_primaria_tema1 VARCHAR(7),
                cor_primaria_tema2 VARCHAR(7),
                cor_primaria_tema3 VARCHAR(7),
                cor_primaria_tema4 VARCHAR(7),
                cor_texto VARCHAR(7),
                cor_fundo VARCHAR(7),
                cor_fundo_dark VARCHAR(7),
                cor_fundo_secundario_dark VARCHAR(7)
            )
        ''')
        
        # Inserir dados
        cursor.execute('''
            INSERT INTO theme_settings VALUES
            (1, 'light', '#1a1a1a', '#2a2a2a', '#3a3a3a', '#4a4a4a',
             '#000000', '#ffffff', '#1a1a1a', '#2a2a2a')
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco antigo criado (SEM cor_texto_dark)")
        
        # Verificar colunas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(theme_settings)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        print(f"Colunas no banco antigo: {', '.join(columns)}")
        self.assertNotIn('cor_texto_dark', columns)
        print("✅ Confirmado: cor_texto_dark NÃO existe no banco antigo")
    
    def test_02_detect_missing_column(self):
        """Teste 2: Detectar coluna faltando ao usar modelo novo"""
        print("\n" + "="*80)
        print("Teste 2: Tentando usar modelo NOVO com banco ANTIGO")
        print("="*80)
        
        # Criar banco antigo
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE theme_settings (
                id INTEGER PRIMARY KEY,
                theme VARCHAR(50),
                cor_primaria_tema1 VARCHAR(7),
                cor_primaria_tema2 VARCHAR(7),
                cor_primaria_tema3 VARCHAR(7),
                cor_primaria_tema4 VARCHAR(7),
                cor_texto VARCHAR(7),
                cor_fundo VARCHAR(7),
                cor_fundo_dark VARCHAR(7),
                cor_fundo_secundario_dark VARCHAR(7)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO theme_settings VALUES
            (1, 'light', '#1a1a1a', '#2a2a2a', '#3a3a3a', '#4a4a4a',
             '#000000', '#ffffff', '#1a1a1a', '#2a2a2a')
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco antigo criado")
        
        # Tentar usar modelo novo
        from BelarminoMonteiroAdvogado import create_app
        from BelarminoMonteiroAdvogado.models import db, ThemeSettings
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        with app.app_context():
            try:
                # Tentar ler dados (vai falhar se coluna não existir)
                theme = ThemeSettings.query.first()
                
                # Se chegou aqui, vamos verificar se a coluna existe
                if hasattr(theme, 'cor_texto_dark'):
                    print(f"⚠️ Modelo tem cor_texto_dark: {theme.cor_texto_dark}")
                else:
                    print("❌ Modelo NÃO tem cor_texto_dark")
                
                # Tentar acessar a coluna diretamente
                try:
                    valor = theme.cor_texto_dark
                    print(f"❌ ERRO NÃO DETECTADO! Conseguiu ler cor_texto_dark: {valor}")
                    self.fail("Deveria ter falhado ao acessar cor_texto_dark")
                except Exception as e:
                    print(f"✅ ERRO DETECTADO: {type(e).__name__}: {str(e)}")
                    self.assertIn('cor_texto_dark', str(e).lower())
                    
            except Exception as e:
                print(f"✅ ERRO DETECTADO ao fazer query: {type(e).__name__}")
                print(f"   Mensagem: {str(e)}")
                self.assertIn('cor_texto_dark', str(e).lower())
    
    def test_03_verify_new_schema(self):
        """Teste 3: Verificar que schema novo tem todas as colunas"""
        print("\n" + "="*80)
        print("Teste 3: Verificando schema NOVO (com cor_texto_dark)")
        print("="*80)
        
        from BelarminoMonteiroAdvogado import create_app
        from BelarminoMonteiroAdvogado.models import db, ThemeSettings
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        with app.app_context():
            # Criar schema novo
            db.create_all()
            
            # Verificar colunas
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(theme_settings)")
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            
            print(f"Colunas no banco novo: {', '.join(columns)}")
            
            # Verificar colunas essenciais
            required_columns = [
                'id', 'theme', 'cor_primaria_tema1', 'cor_primaria_tema2',
                'cor_primaria_tema3', 'cor_primaria_tema4', 'cor_texto',
                'cor_fundo', 'cor_texto_dark', 'cor_fundo_dark',
                'cor_fundo_secundario_dark'
            ]
            
            missing = [col for col in required_columns if col not in columns]
            
            if missing:
                print(f"❌ Colunas faltando: {', '.join(missing)}")
                self.fail(f"Colunas faltando: {', '.join(missing)}")
            else:
                print("✅ Todas as colunas presentes no schema novo")
            
            # Testar inserção e leitura
            theme = ThemeSettings(
                theme='light',
                cor_primaria_tema1='#1a1a1a',
                cor_primaria_tema2='#2a2a2a',
                cor_primaria_tema3='#3a3a3a',
                cor_primaria_tema4='#4a4a4a',
                cor_texto='#000000',
                cor_fundo='#ffffff',
                cor_texto_dark='#ffffff',  # Coluna crítica!
                cor_fundo_dark='#1a1a1a',
                cor_fundo_secundario_dark='#2a2a2a'
            )
            
            db.session.add(theme)
            db.session.commit()
            
            # Ler de volta
            theme_read = ThemeSettings.query.first()
            self.assertEqual(theme_read.cor_texto_dark, '#ffffff')
            
            print("✅ Inserção e leitura funcionando corretamente")
    
    def test_04_migration_scenario(self):
        """Teste 4: Simular cenário de migração"""
        print("\n" + "="*80)
        print("Teste 4: Simulando migração de banco antigo para novo")
        print("="*80)
        
        import sqlite3
        
        # 1. Criar banco antigo
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE theme_settings (
                id INTEGER PRIMARY KEY,
                theme VARCHAR(50),
                cor_primaria_tema1 VARCHAR(7),
                cor_primaria_tema2 VARCHAR(7),
                cor_primaria_tema3 VARCHAR(7),
                cor_primaria_tema4 VARCHAR(7),
                cor_texto VARCHAR(7),
                cor_fundo VARCHAR(7),
                cor_fundo_dark VARCHAR(7),
                cor_fundo_secundario_dark VARCHAR(7)
            )
        ''')
        
        cursor.execute('''
            INSERT INTO theme_settings VALUES
            (1, 'light', '#1a1a1a', '#2a2a2a', '#3a3a3a', '#4a4a4a',
             '#000000', '#ffffff', '#1a1a1a', '#2a2a2a')
        ''')
        
        conn.commit()
        
        print("✅ Banco antigo criado com dados")
        
        # 2. Adicionar coluna faltando (migração)
        print("🔄 Executando migração: adicionando cor_texto_dark...")
        
        cursor.execute('''
            ALTER TABLE theme_settings 
            ADD COLUMN cor_texto_dark VARCHAR(7) DEFAULT '#ffffff'
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Migração executada")
        
        # 3. Verificar que agora funciona
        from BelarminoMonteiroAdvogado import create_app
        from BelarminoMonteiroAdvogado.models import db, ThemeSettings
        
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        with app.app_context():
            theme = ThemeSettings.query.first()
            self.assertIsNotNone(theme)
            self.assertEqual(theme.cor_texto_dark, '#ffffff')
            
            print(f"✅ Leitura bem-sucedida: cor_texto_dark = {theme.cor_texto_dark}")
            print("✅ Migração funcionou corretamente!")

def run_tests():
    """Executar todos os testes"""
    print("\n" + "="*80)
    print("TESTE DE SCHEMA DO BANCO DE DADOS")
    print("Detectando incompatibilidades entre modelos e banco existente")
    print("="*80)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDatabaseSchema)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*80)
    print("RESUMO DOS TESTES DE SCHEMA")
    print("="*80)
    
    if result.wasSuccessful():
        print("✅ TODOS OS TESTES PASSARAM!")
        print("✅ Schema do banco está correto")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🚨 Há problemas de compatibilidade de schema")
    
    print("="*80 + "\n")
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
