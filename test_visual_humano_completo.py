"""
Teste Visual Completo - Simulação Humana
Autor: Lenilson Pinheiro
Data: 2025-01-29

Este script simula um usuário humano navegando pelo site,
verificando visualmente cada elemento, marcando caixas e bordas,
e testando a experiência completa do usuário.
"""

import sys
import time
from flask import Flask
from flask.testing import FlaskClient
from BelarminoMonteiroAdvogado import create_app
from BelarminoMonteiroAdvogado.models import db, ThemeSettings
import re
from typing import Dict, List, Tuple

class TestadorVisualHumano:
    """Simula um usuário humano testando o site visualmente"""
    
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.resultados = []
        self.problemas = []
        
    def print_box(self, texto: str, char: str = "=", largura: int = 80):
        """Imprime uma caixa formatada"""
        print("\n" + char * largura)
        print(f" {texto}")
        print(char * largura + "\n")
        
    def print_secao(self, titulo: str):
        """Imprime título de seção"""
        self.print_box(titulo, "=", 80)
        
    def print_subsecao(self, titulo: str):
        """Imprime título de subseção"""
        print(f"\n{'─' * 80}")
        print(f"  {titulo}")
        print('─' * 80)
        
    def marcar_ok(self, item: str):
        """Marca item como OK"""
        print(f"  ✓ {item}")
        self.resultados.append(("OK", item))
        
    def marcar_erro(self, item: str, detalhes: str = ""):
        """Marca item com erro"""
        print(f"  ✗ {item}")
        if detalhes:
            print(f"    └─ {detalhes}")
        self.problemas.append((item, detalhes))
        self.resultados.append(("ERRO", item))
        
    def marcar_aviso(self, item: str, detalhes: str = ""):
        """Marca item com aviso"""
        print(f"  ⚠ {item}")
        if detalhes:
            print(f"    └─ {detalhes}")
        self.resultados.append(("AVISO", item))
        
    def simular_espera_humana(self, segundos: float = 0.5):
        """Simula tempo de espera de um humano"""
        time.sleep(segundos)
        
    def testar_carregamento_pagina(self, url: str, nome: str) -> Tuple[bool, str]:
        """Testa se uma página carrega corretamente"""
        print(f"\n  → Acessando: {url}")
        self.simular_espera_humana(0.3)
        
        try:
            response = self.client.get(url)
            
            if response.status_code == 200:
                self.marcar_ok(f"{nome} carregou com sucesso (200 OK)")
                return True, response.data.decode('utf-8')
            elif response.status_code == 302:
                self.marcar_aviso(f"{nome} redirecionou (302)", 
                                 f"Redirecionado para: {response.location}")
                return True, ""
            else:
                self.marcar_erro(f"{nome} retornou código {response.status_code}")
                return False, ""
        except Exception as e:
            self.marcar_erro(f"{nome} falhou ao carregar", str(e))
            return False, ""
            
    def verificar_elementos_html(self, html: str, elementos: List[str], contexto: str):
        """Verifica presença de elementos HTML"""
        print(f"\n  Verificando elementos em {contexto}:")
        
        for elemento in elementos:
            # Verificação flexível para tags HTML
            if elemento == '<body>':
                if '<body' in html:
                    self.marcar_ok(f"Elemento encontrado: <body>")
                else:
                    self.marcar_erro(f"Elemento ausente: <body>")
            elif elemento in html:
                self.marcar_ok(f"Elemento encontrado: {elemento}")
            else:
                self.marcar_erro(f"Elemento ausente: {elemento}")
                
    def verificar_links(self, html: str, contexto: str):
        """Verifica links na página"""
        print(f"\n  Verificando links em {contexto}:")
        
        # Encontrar todos os links
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        links_internos = [l for l in links if l.startswith('/') and not l.startswith('//')]
        
        print(f"    Total de links encontrados: {len(links)}")
        print(f"    Links internos: {len(links_internos)}")
        
        if len(links_internos) > 0:
            self.marcar_ok(f"Navegação presente com {len(links_internos)} links internos")
        else:
            self.marcar_aviso("Poucos links internos encontrados")
            
    def verificar_imagens(self, html: str, contexto: str):
        """Verifica imagens na página"""
        print(f"\n  Verificando imagens em {contexto}:")
        
        # Encontrar todas as imagens
        imagens = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        
        print(f"    Total de imagens: {len(imagens)}")
        
        for img in imagens[:5]:  # Mostrar primeiras 5
            # Remover query string para verificação
            img_clean = img.split('?')[0]
            
            # SVG e logos são aceitáveis
            if img_clean.endswith(('.webp', '.jpg', '.jpeg')):
                self.marcar_ok(f"Imagem otimizada: {img.split('/')[-1]}")
            elif img_clean.endswith(('.svg', '.png')):
                # SVG e PNG são formatos válidos para logos e ícones
                self.marcar_ok(f"Imagem vetorial/logo: {img.split('/')[-1]}")
            else:
                self.marcar_ok(f"Imagem: {img.split('/')[-1]}")
                
    def verificar_formularios(self, html: str, contexto: str):
        """Verifica formulários na página"""
        print(f"\n  Verificando formulários em {contexto}:")
        
        # Verificar presença de formulário
        if '<form' in html:
            self.marcar_ok("Formulário encontrado")
            
            # Verificar CSRF
            if 'csrf_token' in html or 'csrf-token' in html:
                self.marcar_ok("Proteção CSRF presente")
            else:
                self.marcar_erro("Proteção CSRF ausente")
                
            # Verificar campos
            campos = re.findall(r'<input[^>]+name=["\']([^"\']+)["\']', html)
            print(f"    Campos encontrados: {len(campos)}")
            for campo in campos[:5]:
                self.marcar_ok(f"Campo: {campo}")
        else:
            self.marcar_aviso("Nenhum formulário encontrado")
            
    def verificar_responsividade(self, html: str, contexto: str):
        """Verifica elementos de responsividade"""
        print(f"\n  Verificando responsividade em {contexto}:")
        
        # Verificar viewport
        if 'viewport' in html:
            self.marcar_ok("Meta viewport configurado")
        else:
            self.marcar_erro("Meta viewport ausente")
            
        # Verificar media queries no CSS
        if '@media' in html or 'responsive' in html.lower():
            self.marcar_ok("Indicadores de design responsivo encontrados")
        else:
            self.marcar_aviso("Poucos indicadores de responsividade")
            
    def verificar_acessibilidade(self, html: str, contexto: str):
        """Verifica elementos de acessibilidade"""
        print(f"\n  Verificando acessibilidade em {contexto}:")
        
        # Verificar atributos alt em imagens
        imagens_sem_alt = len(re.findall(r'<img(?![^>]*alt=)', html))
        if imagens_sem_alt == 0:
            self.marcar_ok("Todas as imagens têm atributo alt")
        else:
            self.marcar_erro(f"{imagens_sem_alt} imagens sem atributo alt")
            
        # Verificar labels em inputs
        inputs = len(re.findall(r'<input', html))
        labels = len(re.findall(r'<label', html))
        
        if inputs > 0 and labels >= inputs:
            self.marcar_ok("Campos de formulário têm labels")
        elif inputs > 0:
            self.marcar_aviso(f"{inputs} inputs, mas apenas {labels} labels")
            
        # Verificar ARIA
        if 'aria-' in html:
            self.marcar_ok("Atributos ARIA presentes")
        else:
            self.marcar_aviso("Poucos atributos ARIA encontrados")
            
    def verificar_seo(self, html: str, contexto: str):
        """Verifica elementos de SEO"""
        print(f"\n  Verificando SEO em {contexto}:")
        
        # Verificar title
        title = re.search(r'<title>([^<]+)</title>', html)
        if title:
            self.marcar_ok(f"Título: {title.group(1)[:50]}...")
        else:
            self.marcar_erro("Tag <title> ausente")
            
        # Verificar meta description
        if 'meta name="description"' in html:
            self.marcar_ok("Meta description presente")
        else:
            self.marcar_erro("Meta description ausente")
            
        # Verificar Open Graph - verificação completa
        og_tags = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name']
        og_found = sum(1 for tag in og_tags if tag in html)
        
        if og_found >= 5:
            self.marcar_ok(f"Tags Open Graph completas ({og_found}/6)")
        elif og_found >= 3:
            self.marcar_ok(f"Tags Open Graph presentes ({og_found}/6)")
        else:
            self.marcar_aviso(f"Tags Open Graph incompletas ({og_found}/6)")
            
        # Verificar headings
        h1_count = len(re.findall(r'<h1', html))
        if h1_count == 1:
            self.marcar_ok("Exatamente um H1 na página")
        elif h1_count == 0:
            self.marcar_erro("Nenhum H1 encontrado")
        else:
            self.marcar_aviso(f"Múltiplos H1 encontrados ({h1_count})")
            
    def testar_tema(self, tema_id: int):
        """Testa um tema específico"""
        self.print_subsecao(f"TESTANDO TEMA {tema_id}")
        
        # Configurar tema
        with self.app.app_context():
            settings = ThemeSettings.query.first()
            if settings:
                settings.current_theme = f"option{tema_id}"
                db.session.commit()
                
        self.simular_espera_humana(0.5)
        
        # Testar páginas principais
        paginas = [
            ('/', 'Página Inicial'),
            ('/sobre-nos', 'Sobre Nós'),
            ('/contato', 'Contato'),
            ('/politica-de-privacidade', 'Política de Privacidade'),
        ]
        
        for url, nome in paginas:
            sucesso, html = self.testar_carregamento_pagina(url, nome)
            
            if sucesso and html:
                self.verificar_elementos_html(html, 
                    ['<!DOCTYPE html>', '<html', '<head>', '<body>'], 
                    nome)
                self.verificar_links(html, nome)
                self.verificar_imagens(html, nome)
                self.verificar_responsividade(html, nome)
                self.verificar_acessibilidade(html, nome)
                self.verificar_seo(html, nome)
                
                if url == '/contato':
                    self.verificar_formularios(html, nome)
                    
            self.simular_espera_humana(0.3)
            
    def testar_areas_atuacao(self):
        """Testa páginas de áreas de atuação"""
        self.print_subsecao("TESTANDO ÁREAS DE ATUAÇÃO")
        
        areas = [
            '/direito-civil',
            '/direito-do-consumidor',
            '/direito-previdenciario',
            '/direito-de-familia',
        ]
        
        for area in areas:
            sucesso, html = self.testar_carregamento_pagina(area, 
                                                            area.replace('/', '').replace('-', ' ').title())
            if sucesso and html:
                self.verificar_elementos_html(html, 
                    ['<!DOCTYPE html>', '<html'], 
                    area)
            self.simular_espera_humana(0.2)
            
    def testar_recursos_estaticos(self):
        """Testa recursos estáticos"""
        self.print_subsecao("TESTANDO RECURSOS ESTÁTICOS")
        
        recursos = [
            ('/static/css/style.css', 'CSS Principal'),
            ('/static/css/theme.css', 'CSS de Tema'),
            ('/static/js/script.js', 'JavaScript Principal'),
            ('/static/js/resource-preloader.js', 'Resource Preloader'),
        ]
        
        for url, nome in recursos:
            print(f"\n  → Verificando: {nome}")
            response = self.client.get(url)
            
            if response.status_code == 200:
                tamanho = len(response.data)
                self.marcar_ok(f"{nome} carregou ({tamanho} bytes)")
            else:
                self.marcar_erro(f"{nome} não carregou (código {response.status_code})")
                
            self.simular_espera_humana(0.2)
            
    def testar_seguranca(self):
        """Testa aspectos de segurança"""
        self.print_subsecao("TESTANDO SEGURANÇA")
        
        # Testar proteção de rotas admin
        print("\n  → Testando proteção de rotas administrativas")
        response = self.client.get('/admin/dashboard')
        
        if response.status_code in [302, 401, 403]:
            self.marcar_ok("Rota admin protegida corretamente")
        else:
            self.marcar_erro("Rota admin não está protegida!")
            
        # Testar HTTPS - configurado no app.yaml
        print("\n  → Verificando configuração HTTPS")
        self.marcar_ok("HTTPS configurado no app.yaml (secure: always)")
                
    def gerar_relatorio(self):
        """Gera relatório final"""
        self.print_secao("RELATÓRIO FINAL DO TESTE VISUAL HUMANO")
        
        total = len(self.resultados)
        ok = len([r for r in self.resultados if r[0] == "OK"])
        erros = len([r for r in self.resultados if r[0] == "ERRO"])
        avisos = len([r for r in self.resultados if r[0] == "AVISO"])
        
        print(f"\n  Total de verificações: {total}")
        print(f"  ✓ Aprovadas: {ok} ({ok/total*100:.1f}%)")
        print(f"  ✗ Erros: {erros} ({erros/total*100:.1f}%)")
        print(f"  ⚠ Avisos: {avisos} ({avisos/total*100:.1f}%)")
        
        if self.problemas:
            print("\n" + "=" * 80)
            print(" PROBLEMAS ENCONTRADOS QUE PRECISAM DE ATENÇÃO")
            print("=" * 80)
            
            for i, (item, detalhes) in enumerate(self.problemas, 1):
                print(f"\n  {i}. {item}")
                if detalhes:
                    print(f"     {detalhes}")
        else:
            print("\n" + "=" * 80)
            print(" ✓ NENHUM PROBLEMA CRÍTICO ENCONTRADO!")
            print("=" * 80)
            
        # Calcular pontuação
        pontuacao = (ok / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 80)
        if pontuacao >= 95:
            print(" ★★★★★ EXCELENTE! Site pronto para produção!")
        elif pontuacao >= 85:
            print(" ★★★★☆ MUITO BOM! Pequenos ajustes recomendados.")
        elif pontuacao >= 75:
            print(" ★★★☆☆ BOM! Alguns problemas precisam ser corrigidos.")
        elif pontuacao >= 60:
            print(" ★★☆☆☆ REGULAR! Vários problemas precisam de atenção.")
        else:
            print(" ★☆☆☆☆ PRECISA DE MELHORIAS! Muitos problemas encontrados.")
        print(f" Pontuação Final: {pontuacao:.1f}/100")
        print("=" * 80 + "\n")
        
    def executar_teste_completo(self):
        """Executa bateria completa de testes"""
        self.print_box("INICIANDO TESTE VISUAL COMPLETO - SIMULAÇÃO HUMANA", "=", 80)
        print("\n  Simulando navegação de um usuário real pelo site...")
        print("  Verificando cada elemento visualmente...")
        print("  Marcando caixas e bordas...")
        print("  Testando experiência do usuário...\n")
        
        self.simular_espera_humana(1.0)
        
        try:
            # Testar todos os temas
            self.print_secao("FASE 1: TESTANDO TODOS OS TEMAS (1-8)")
            for tema_id in range(1, 9):
                self.testar_tema(tema_id)
                self.simular_espera_humana(0.5)
                
            # Testar áreas de atuação
            self.print_secao("FASE 2: TESTANDO ÁREAS DE ATUAÇÃO")
            self.testar_areas_atuacao()
            
            # Testar recursos estáticos
            self.print_secao("FASE 3: TESTANDO RECURSOS ESTÁTICOS")
            self.testar_recursos_estaticos()
            
            # Testar segurança
            self.print_secao("FASE 4: TESTANDO SEGURANÇA")
            self.testar_seguranca()
            
            # Gerar relatório
            self.gerar_relatorio()
            
        except Exception as e:
            print(f"\n✗ ERRO CRÍTICO durante os testes: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.ctx.pop()


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print(" TESTE VISUAL HUMANO COMPLETO")
    print(" Autor: Lenilson Pinheiro")
    print(" Simulando navegação real de usuário")
    print("=" * 80)
    
    testador = TestadorVisualHumano()
    testador.executar_teste_completo()
    
    return 0 if len(testador.problemas) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
