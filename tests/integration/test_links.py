"""
Testes de integração para links e rotas

Este módulo contém testes para verificar o funcionamento correto das rotas e links
em diferentes temas do site Belarmino Monteiro Advogado.
"""

def test_theme_routes(client, theme_number, theme_name, theme_option):
    """Testa as rotas principais com um tema específico"""
    # Rotas para testar
    routes = [
        ('/', 'Home'),
        ('/sobre-nos', 'Sobre'),
        ('/contato', 'Contato'),
        ('/politica-de-privacidade', 'Política')
    ]
    
    for route, name in routes:
        response = client.get(route)
        assert response.status_code == 200, f"Falha ao acessar {name} com tema {theme_name} ({theme_option})"
        assert b'<!DOCTYPE html>' in response.data, f"Resposta de {name} não contém HTML válido"
        
        # Verifica se o CSS do tema está sendo carregado
        theme_css = f'css/theme-{theme_name.lower()}.css'.encode()
        assert theme_css in response.data or b'css/theme-light.css' in response.data, \
            f"CSS do tema {theme_name} não encontrado na resposta de {name}"

def test_navigation_links(client, theme_name):
    """Testa os links de navegação na página inicial"""
    response = client.get('/')
    assert response.status_code == 200
    
    # Verifica se os links principais estão presentes
    assert b'href="/"' in response.data
    assert b'href="/sobre"' in response.data or b'href="/sobre-nos"' in response.data
    assert b'href="/contato"' in response.data
    
    # Verifica se o CSS do tema está sendo carregado
    theme_css = f'css/theme-{theme_name.lower()}.css'.encode()
    assert theme_css in response.data or b'css/theme-light.css' in response.data, \
        f"CSS do tema {theme_name} não encontrado na resposta"

def test_static_resources(client):
    """Verifica se os recursos estáticos estão acessíveis"""
    # Verifica se o CSS principal está acessível
    response = client.get('/static/css/style.css')
    assert response.status_code == 200
    assert b'text/css' in response.headers.get('Content-Type', '').encode()
    
    # Verifica se o JavaScript principal está acessível
    response = client.get('/static/js/main.js')
    assert response.status_code == 200
    assert b'application/javascript' in response.headers.get('Content-Type', '').encode()

def test_form_actions(client):
    """Testa as ações dos formulários"""
    # Testa o formulário de contato
    response = client.get('/contato')
    assert response.status_code == 200
    assert b'name="nome"' in response.data
    assert b'name="email"' in response.data
    assert b'name="mensagem"' in response.data
    
    # Testa o envio do formulário (POST)
    response = client.post('/contato', data={
        'nome': 'Teste',
        'email': 'teste@example.com',
        'mensagem': 'Mensagem de teste',
        'assunto': 'Contato',
        'telefone': '123456789'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Verifica se há uma mensagem de sucesso ou redirecionamento
    assert b'mensagem enviada' in response.data.lower() or b'sucesso' in response.data.lower()

def test_all_themes(client, theme_option):
    """Testa a aplicação com todos os temas"""
    response = client.get('/')
    assert response.status_code == 200
    # Verifica se o tema está sendo aplicado
    assert theme_option.encode() in response.data, f"Tema {theme_option} não encontrado na resposta"

def main():
    """Executa todos os testes de links e rotas"""
    print_header("VERIFICAÇÃO COMPLETA DE LINKS E ROTAS")
    print_info(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SEÇÃO 1: TESTES DE TEMAS
    print_header("1. TESTES DE TODOS OS TEMAS (1-8)")
    test_all_themes(client="localhost", theme_option="Tema 1")
    
    # SEÇÃO 2: TESTES DE NAVEGAÇÃO
    print_header("2. TESTES DE LINKS DE NAVEGAÇÃO")
    test_navigation_links(client="localhost", theme_option="Tema 1")
    
    # SEÇÃO 3: TESTES DE RECURSOS ESTÁTICOS
    print_header("3. TESTES DE RECURSOS ESTÁTICOS")
    test_static_resources(client="localhost")
    
    # SEÇÃO 4: TESTES DE FORMULÁRIOS
    print_header("4. TESTES DE FORMULÁRIOS")
    test_form_actions(client="localhost")
    
    # RELATÓRIO FINAL
    print_header("RELATÓRIO FINAL")
    print(f"\nTotal de testes: {total_tests}")
    print_success(f"Passou: {passed_tests}")
    print_error(f"Falhou: {failed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nTaxa de sucesso: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print_header(" TODOS OS LINKS E ROTAS FUNCIONANDO! ")
        return 0
    else:
        print_header(" ALGUNS LINKS/ROTAS COM PROBLEMAS! ")
        return 1

if __name__ == '__main__':
    sys.exit(main())
