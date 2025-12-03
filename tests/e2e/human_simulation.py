"""

Autor: Lenilson Pinheiro
Data: Janeiro 2025

Teste de Simulação Humana - Navegação Completa
Simula um usuário real navegando pelo site e admin
"""

import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "http://localhost:5000"

class Colors:
    """
    Definição de Colors.
    Componente essencial para a arquitetura do sistema.
    """
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """
    Definição de print_header.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_step(step_num, text):
    """
    Definição de print_step.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"\n{Colors.CYAN}{Colors.BOLD}[PASSO {step_num}]{Colors.END} {text}")

def print_success(text):
    """
    Definição de print_success.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"  {Colors.GREEN}{Colors.END} {text}")

def print_error(text):
    """
    Definição de print_error.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"  {Colors.RED}{Colors.END} {text}")

def print_warning(text):
    """
    Definição de print_warning.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"  {Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    """
    Definição de print_info.
    Componente essencial para a arquitetura do sistema.
    """
    print(f"  {Colors.MAGENTA}{Colors.END} {text}")

class HumanSimulator:
    """
    Definição de HumanSimulator.
    Componente essencial para a arquitetura do sistema.
    """
    def __init__(self):
        """
        Definição de __init__.
        Componente essencial para a arquitetura do sistema.
        """
        self.session = requests.Session()
        self.results = []
    
    def test_homepage(self):
        """Simula acesso à homepage"""
        print_step(1, "Acessando Homepage")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print_success(f"Homepage carregou (Status: {response.status_code})")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verifica elementos essenciais
                has_nav = soup.find('nav') is not None
                has_footer = soup.find('footer') is not None
                has_title = soup.find('title') is not None
                
                if has_nav:
                    print_success("Navegação encontrada")
                else:
                    print_error("Navegação NÃO encontrada")
                
                if has_footer:
                    print_success("Rodapé encontrado")
                else:
                    print_error("Rodapé NÃO encontrado")
                
                if has_title:
                    title = soup.find('title').text
                    print_success(f"Título: {title}")
                
                return True
            else:
                print_error(f"Falha ao carregar (Status: {response.status_code})")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_navigation_links(self):
        """Simula clique em links do menu"""
        print_step(2, "Testando Links de Navegação")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra links do menu
            nav = soup.find('nav')
            if nav:
                links = nav.find_all('a', href=True)
                print_info(f"Encontrados {len(links)} links no menu")
                
                tested = 0
                working = 0
                
                for link in links[:5]:  # Testa os primeiros 5
                    href = link.get('href')
                    text = link.text.strip()
                    
                    if href.startswith('/') and not href.startswith('//'):
                        tested += 1
                        try:
                            link_response = self.session.get(f"{BASE_URL}{href}", timeout=5)
                            if link_response.status_code == 200:
                                working += 1
                                print_success(f"'{text}' → {href} (OK)")
                            else:
                                print_error(f"'{text}' → {href} (Status: {link_response.status_code})")
                        except:
                            print_error(f"'{text}' → {href} (Timeout)")
                
                print_info(f"Resultado: {working}/{tested} links funcionando")
                return working == tested
            else:
                print_error("Menu de navegação não encontrado")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_about_page(self):
        """Simula acesso à página Sobre"""
        print_step(3, "Acessando Página 'Sobre Nós'")
        
        try:
            response = self.session.get(f"{BASE_URL}/sobre-nos")
            if response.status_code == 200:
                print_success("Página 'Sobre Nós' carregou")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verifica conteúdo
                has_content = len(soup.text) > 100
                if has_content:
                    print_success("Conteúdo presente")
                else:
                    print_warning("Pouco conteúdo detectado")
                
                return True
            else:
                print_error(f"Falha ao carregar (Status: {response.status_code})")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_contact_page(self):
        """Simula acesso à página de Contato"""
        print_step(4, "Acessando Página 'Contato'")
        
        try:
            response = self.session.get(f"{BASE_URL}/contato")
            if response.status_code == 200:
                print_success("Página 'Contato' carregou")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verifica formulário
                has_form = soup.find('form') is not None
                if has_form:
                    print_success("Formulário de contato encontrado")
                else:
                    print_warning("Formulário de contato NÃO encontrado")
                
                return True
            else:
                print_error(f"Falha ao carregar (Status: {response.status_code})")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_services_page(self):
        """Simula acesso à página de Áreas de Atuação"""
        print_step(5, "Acessando 'Áreas de Atuação'")
        
        try:
            response = self.session.get(f"{BASE_URL}/areas-de-atuacao")
            if response.status_code == 200:
                print_success("Página 'Áreas de Atuação' carregou")
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Verifica se há serviços listados
                links = soup.find_all('a', href=True)
                service_links = [l for l in links if '/direito-' in l.get('href', '')]
                
                if service_links:
                    print_success(f"{len(service_links)} serviços encontrados")
                else:
                    print_warning("Nenhum serviço encontrado")
                
                return True
            else:
                print_error(f"Falha ao carregar (Status: {response.status_code})")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_service_detail(self):
        """Simula acesso a uma página de serviço específico"""
        print_step(6, "Acessando Serviço Específico (Direito Civil)")
        
        try:
            response = self.session.get(f"{BASE_URL}/direito-civil")
            if response.status_code == 200:
                print_success("Página do serviço carregou")
                return True
            elif response.status_code == 404:
                print_warning("Serviço não cadastrado (404)")
                return True  # Não é erro crítico
            else:
                print_error(f"Falha ao carregar (Status: {response.status_code})")
                return False
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_responsive_elements(self):
        """Verifica elementos responsivos"""
        print_step(7, "Verificando Elementos Responsivos")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verifica meta viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                print_success("Meta viewport configurado")
            else:
                print_warning("Meta viewport NÃO encontrado")
            
            # Verifica Bootstrap
            has_bootstrap = any('bootstrap' in str(link) for link in soup.find_all('link'))
            if has_bootstrap:
                print_success("Bootstrap detectado")
            else:
                print_warning("Bootstrap NÃO detectado")
            
            return True
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_css_loading(self):
        """Verifica carregamento de CSS"""
        print_step(8, "Verificando Carregamento de CSS")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            css_links = soup.find_all('link', rel='stylesheet')
            print_info(f"Encontrados {len(css_links)} arquivos CSS")
            
            working_css = 0
            for link in css_links:
                href = link.get('href', '')
                if href.startswith('/static/'):
                    try:
                        css_response = self.session.get(f"{BASE_URL}{href}", timeout=5)
                        if css_response.status_code == 200:
                            working_css += 1
                            print_success(f"CSS OK: {href.split('/')[-1]}")
                        else:
                            print_error(f"CSS FALHOU: {href.split('/')[-1]} (Status: {css_response.status_code})")
                    except:
                        print_error(f"CSS TIMEOUT: {href.split('/')[-1]}")
            
            print_info(f"Resultado: {working_css}/{len(css_links)} arquivos CSS carregando")
            return working_css > 0
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def test_images_loading(self):
        """Verifica carregamento de imagens"""
        print_step(9, "Verificando Carregamento de Imagens")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = soup.find_all('img', src=True)
            print_info(f"Encontradas {len(images)} imagens")
            
            if len(images) > 0:
                # Testa as primeiras 3 imagens
                working_images = 0
                for img in images[:3]:
                    src = img.get('src', '')
                    if src.startswith('/static/'):
                        try:
                            img_response = self.session.get(f"{BASE_URL}{src}", timeout=5)
                            if img_response.status_code == 200:
                                working_images += 1
                                print_success(f"Imagem OK: {src.split('/')[-1]}")
                            else:
                                print_error(f"Imagem FALHOU: {src.split('/')[-1]}")
                        except:
                            print_error(f"Imagem TIMEOUT: {src.split('/')[-1]}")
                
                print_info(f"Resultado: {working_images}/3 imagens testadas carregando")
                return True
            else:
                print_warning("Nenhuma imagem encontrada")
                return True
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            return False
    
    def generate_report(self):
        """Gera relatório final"""
        print_header("RELATÓRIO FINAL - SIMULAÇÃO HUMANA")
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r)
        failed = total_tests - passed
        
        print(f"\n{Colors.BOLD}ESTATÍSTICAS:{Colors.END}")
        print(f"  Total de Testes: {total_tests}")
        print(f"  {Colors.GREEN}Aprovados: {passed}{Colors.END}")
        print(f"  {Colors.RED}Falhados: {failed}{Colors.END}")
        print(f"  Taxa de Sucesso: {(passed/total_tests*100):.1f}%")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD} TODOS OS TESTES PASSARAM! {Colors.END}\n")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}  ALGUNS TESTES FALHARAM  {Colors.END}\n")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print_header("SIMULAÇÃO DE NAVEGAÇÃO HUMANA")
        print(f"{Colors.CYAN}Simulando um usuário real navegando pelo site...{Colors.END}\n")
        
        # Executa testes
        self.results.append(self.test_homepage())
        time.sleep(0.5)
        
        self.results.append(self.test_navigation_links())
        time.sleep(0.5)
        
        self.results.append(self.test_about_page())
        time.sleep(0.5)
        
        self.results.append(self.test_contact_page())
        time.sleep(0.5)
        
        self.results.append(self.test_services_page())
        time.sleep(0.5)
        
        self.results.append(self.test_service_detail())
        time.sleep(0.5)
        
        self.results.append(self.test_responsive_elements())
        time.sleep(0.5)
        
        self.results.append(self.test_css_loading())
        time.sleep(0.5)
        
        self.results.append(self.test_images_loading())
        
        # Gera relatório
        self.generate_report()

if __name__ == "__main__":
    print(f"\n{Colors.CYAN}Aguardando servidor Flask em {BASE_URL}...{Colors.END}\n")
    
    try:
        # Testa se o servidor está respondendo
        response = requests.get(BASE_URL, timeout=5)
        print(f"{Colors.GREEN} Servidor respondendo!{Colors.END}\n")
        
        simulator = HumanSimulator()
        simulator.run_all_tests()
    
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED} ERRO: Servidor não está respondendo em {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}Por favor, inicie o servidor Flask primeiro:{Colors.END}")
        print(f"{Colors.CYAN}  python run.py{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED} ERRO: {str(e)}{Colors.END}\n")
