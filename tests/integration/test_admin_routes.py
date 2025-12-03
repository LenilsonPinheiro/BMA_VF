"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Testes Automatizados para Rotas do Painel Administrativo
Testa todas as rotas, formulários e funcionalidades do admin
"""

import requests
from urllib.parse import urljoin

# Configurações
BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

class Colors:
    """
    Definição de Colors.
    Componente essencial para a arquitetura do sistema.
    """
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class AdminTester:
    """
    Definição de AdminTester.
    Componente essencial para a arquitetura do sistema.
    """
    def __init__(self):
        """
        Definição de __init__.
        Componente essencial para a arquitetura do sistema.
        """
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        self.csrf_token = None
    
    def print_header(self, text):
        """
        Definição de print_header.
        Componente essencial para a arquitetura do sistema.
        """
        print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}{text.center(70)}{Colors.END}")
        print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    def print_test(self, name, status, message=""):
        """
        Definição de print_test.
        Componente essencial para a arquitetura do sistema.
        """
        if status == "PASS":
            self.results['passed'] += 1
            print(f"{Colors.GREEN}{Colors.END} {name}")
            if message:
                print(f"  {Colors.GREEN}→{Colors.END} {message}")
        elif status == "FAIL":
            self.results['failed'] += 1
            print(f"{Colors.RED}{Colors.END} {name}")
            if message:
                print(f"  {Colors.RED}→{Colors.END} {message}")
        elif status == "WARN":
            self.results['warnings'] += 1
            print(f"{Colors.YELLOW}⚠{Colors.END} {name}")
            if message:
                print(f"  {Colors.YELLOW}→{Colors.END} {message}")
    
    def login(self):
        """Faz login no painel administrativo"""
        self.print_header("AUTENTICAÇÃO")
        
        try:
            # Primeiro, pega a página de login para obter o CSRF token
            response = self.session.get(urljoin(BASE_URL, "/auth/login"))
            
            if response.status_code == 200:
                self.print_test("GET /auth/login", "PASS", f"Status: {response.status_code}")
                
                # Extrai o CSRF token do formulário de login
                import re
                match = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="([^"]+)">', response.text)
                if not match:
                    self.print_test("CSRF Token", "FAIL", "Não foi possível encontrar o token CSRF na página de login.")
                    return False
                
                self.csrf_token = match.group(1)
                self.print_test("CSRF Token", "PASS", "Token extraído com sucesso.")

                # Tenta fazer login
                login_data = {
                    'username': ADMIN_USERNAME,
                    'password': ADMIN_PASSWORD,
                    'csrf_token': self.csrf_token
                }
                
                response = self.session.post(
                    urljoin(BASE_URL, "/auth/login"),
                    data=login_data,
                    allow_redirects=False
                )
                
                if response.status_code in [200, 302]:
                    self.print_test("POST /auth/login", "PASS", "Login bem-sucedido")
                    return True
                else:
                    self.print_test("POST /auth/login", "FAIL", f"Status: {response.status_code}")
                    return False
            else:
                self.print_test("GET /auth/login", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("Login", "FAIL", str(e))
            return False
    
    def test_dashboard_routes(self):
        """Testa todas as rotas do dashboard"""
        self.print_header("ROTAS DO DASHBOARD")
        
        routes = [
            ("/admin/dashboard", "Dashboard Principal"),
            ("/admin/dashboard#Content", "Seção: Conteúdo Geral"),
            ("/admin/dashboard#HomeSections", "Seção: Home Page"),
            ("/admin/dashboard#Navigation", "Seção: Navegação"),
            ("/admin/dashboard#Services", "Seção: Serviços"),
            ("/admin/dashboard#Team", "Seção: Equipe"),
            ("/admin/dashboard#Testimonials", "Seção: Depoimentos"),
            ("/admin/dashboard#Clients", "Seção: Clientes"),
            ("/admin/dashboard#EmailSettings", "Seção: E-mail"),
            ("/admin/dashboard#Security", "Seção: Segurança"),
            ("/admin/dashboard#SEO", "Seção: SEO"),
            ("/admin/dashboard#Theme", "Seção: Aparência"),
        ]
        
        for route, description in routes:
            try:
                response = self.session.get(urljoin(BASE_URL, route))
                
                if response.status_code == 200:
                    self.print_test(description, "PASS", f"GET {route}")
                elif response.status_code == 302:
                    self.print_test(description, "WARN", "Redirecionado (pode precisar de login)")
                else:
                    self.print_test(description, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(description, "FAIL", str(e))
    
    def test_design_editor(self):
        """Testa o editor de design"""
        self.print_header("EDITOR DE DESIGN")
        
        try:
            response = self.session.get(urljoin(BASE_URL, "/admin/design-editor"))
            
            if response.status_code == 200:
                self.print_test("GET /admin/design-editor", "PASS")
                
                # Verifica se contém elementos esperados
                if b'color' in response.content.lower():
                    self.print_test("Campos de cor presentes", "PASS")
                else:
                    self.print_test("Campos de cor presentes", "WARN", "Não encontrados")
            else:
                self.print_test("GET /admin/design-editor", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Editor de Design", "FAIL", str(e))
    
    def test_public_routes(self):
        """Testa rotas públicas do site"""
        self.print_header("ROTAS PÚBLICAS (VERIFICAÇÃO)")
        
        routes = [
            ("/", "Homepage"),
            ("/sobre-nos", "Sobre Nós"),
            ("/contato", "Contato"),
            ("/areas-de-atuacao", "Áreas de Atuação"),
            ("/politica-de-privacidade", "Política de Privacidade"),
            ("/robots.txt", "Robots.txt"),
            ("/sitemap.xml", "Sitemap XML"),
        ]
        
        for route, description in routes:
            try:
                response = self.session.get(urljoin(BASE_URL, route))
                
                if response.status_code == 200:
                    self.print_test(description, "PASS", f"GET {route}")
                else:
                    self.print_test(description, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(description, "FAIL", str(e))
    
    def test_service_routes(self):
        """Testa rotas de serviços jurídicos"""
        self.print_header("ROTAS DE SERVIÇOS JURÍDICOS")
        
        services = [
            "direito-civil",
            "direito-do-consumidor",
            "direito-previdenciario",
            "direito-de-familia",
        ]
        
        for service in services:
            try:
                response = self.session.get(urljoin(BASE_URL, f"/{service}"))
                
                if response.status_code == 200:
                    self.print_test(f"Serviço: {service}", "PASS")
                elif response.status_code == 404:
                    self.print_test(f"Serviço: {service}", "WARN", "Não encontrado (pode não estar cadastrado)")
                else:
                    self.print_test(f"Serviço: {service}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"Serviço: {service}", "FAIL", str(e))
    
    def test_admin_protection(self):
        """Testa se rotas admin estão protegidas"""
        self.print_header("SEGURANÇA - PROTEÇÃO DE ROTAS")
        
        # Cria uma nova sessão sem login
        unauth_session = requests.Session()
        
        protected_routes = [
            "/admin/dashboard",
            "/admin/design-editor",
        ]
        
        for route in protected_routes:
            try:
                response = unauth_session.get(urljoin(BASE_URL, route), allow_redirects=False)
                
                if response.status_code == 302:
                    self.print_test(f"Proteção: {route}", "PASS", "Redireciona para login")
                elif response.status_code == 401:
                    self.print_test(f"Proteção: {route}", "PASS", "Acesso negado")
                elif response.status_code == 200:
                    self.print_test(f"Proteção: {route}", "FAIL", "Rota desprotegida!")
                else:
                    self.print_test(f"Proteção: {route}", "WARN", f"Status inesperado: {response.status_code}")
            except Exception as e:
                self.print_test(f"Proteção: {route}", "FAIL", str(e))
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        self.print_header("RESUMO DOS TESTES")
        
        total = self.results['passed'] + self.results['failed'] + self.results['warnings']
        
        print(f"Total de testes: {total}")
        print(f"{Colors.GREEN} Aprovados: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED} Falhados: {self.results['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}⚠ Avisos: {self.results['warnings']}{Colors.END}")
        
        if self.results['failed'] == 0:
            print(f"\n{Colors.GREEN}{'='*70}")
            print(f" TODOS OS TESTES PASSARAM! ".center(70))
            print(f"{'='*70}{Colors.END}\n")
        else:
            print(f"\n{Colors.RED}{'='*70}")
            print(f"  ALGUNS TESTES FALHARAM  ".center(70))
            print(f"{'='*70}{Colors.END}\n")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print(f"\n{Colors.BLUE}{'='*70}")
        print(f" INICIANDO TESTES DO PAINEL ADMINISTRATIVO ".center(70))
        print(f"{'='*70}{Colors.END}\n")
        
        print(f"URL Base: {BASE_URL}")
        print(f"Usuário: {ADMIN_USERNAME}\n")
        
        # Testa proteção de rotas primeiro (sem login)
        self.test_admin_protection()
        
        # Faz login
        if not self.login():
            print(f"\n{Colors.RED}ERRO: Não foi possível fazer login. Verifique as credenciais.{Colors.END}")
            print(f"{Colors.YELLOW}Continuando com testes públicos...{Colors.END}\n")
        
        # Testa rotas do dashboard
        self.test_dashboard_routes()
        
        # Testa editor de design
        self.test_design_editor()
        
        # Testa rotas públicas
        self.test_public_routes()
        
        # Testa rotas de serviços
        self.test_service_routes()
        
        # Imprime resumo
        self.print_summary()

if __name__ == "__main__":
    tester = AdminTester()
    tester.run_all_tests()
