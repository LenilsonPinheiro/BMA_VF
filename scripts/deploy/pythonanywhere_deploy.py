"""
Deploy Automático para PythonAnywhere via API
Belarmino Monteiro Advogado
"""

import requests
import os
import subprocess
import time

# Configurações
USERNAME = 'bmadv'
API_TOKEN = '59a5fbe2b30772b26b21a8773ec5a5d90867f2bc'
DOMAIN = 'bmadv.pythonanywhere.com'


def setup_environment_on_pa():
    """Atualiza código no PythonAnywhere via API"""
    print_step(3, "CONFIGURAR AMBIENTE NO PYTHONANYWHERE")
    
    # Executar comando via console API
    console_data = {
        'executable': 'bash',
        'arguments': '',
        'working_directory': f'/home/{USERNAME}'
    }
    
    response = api_request('POST', '/consoles/', json=console_data)
    
    if response:
        console_id = response.json()['id']
        print(f"✅ Console criado: {console_id}")
        
        # Comandos para executar
        commands = [
            f'cd /home/{USERNAME}/BelarminoMonteiroAdvogado',
            'source venv/bin/activate',
            'pip install -r requirements.txt --quiet',
            'flask db upgrade'
        ]
        
        for cmd in commands:
            print(f"Executando: {cmd}")
            api_request('POST', f'/consoles/{console_id}/send_input/', 
                       json={'input': cmd + '\n'})
            time.sleep(2)
        
        return True
    
    return False

def reload_webapp():
    """Recarrega a aplicação web"""
    print_step(4, "RECARREGAR APLICAÇÃO WEB")
    
    response = api_request('POST', f'/webapps/{DOMAIN}/reload/')
    
    if response:
        print(f"✅ Aplicação recarregada: https://{DOMAIN}")
        return True
    
    return False

def verify_deployment():
    """Verifica se o deploy funcionou"""
    print_step(5, "VERIFICAR DEPLOY")
    
    try:
        response = requests.get(f'https://{DOMAIN}', timeout=10)
        if response.status_code == 200:
            print(f"✅ Site está online: https://{DOMAIN}")
            print(f"✅ Status Code: {response.status_code}")
            return True
        else:
            print(f"⚠️ Site retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   DEPLOY AUTOMÁTICO PARA PYTHONANYWHERE                 ║
    ║   Belarmino Monteiro Advogado                           ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"""
    Configurações:
    - Usuário: {USERNAME}
    - Domínio: {DOMAIN}
    - API Token: {'*' * 20}{API_TOKEN[-10:]}
    """)
    
    input("Pressione ENTER para iniciar a configuração do ambiente e deploy...")
    
    # Passo 1: Configurar ambiente no PythonAnywhere
    if not setup_environment_on_pa():
        print("⚠️ Falha ao configurar o ambiente via API")
        print("\nExecute manualmente no console do PythonAnywhere:")
        print(f"""
        cd /home/{USERNAME}/BelarminoMonteiroAdvogado
        source venv/bin/activate
        pip install -r requirements.txt
        flask db upgrade
        """)
        input("\nPressione ENTER após executar os comandos...")
    
    # Passo 2: Reload da aplicação
    if not reload_webapp():
        print("⚠️ Falha ao recarregar via API")
        print(f"\nRecarregue manualmente em:")
        print(f"https://www.pythonanywhere.com/user/{USERNAME}/webapps/#{DOMAIN}")
        input("\nPressione ENTER após recarregar...")
    
    # Passo 3: Verificar
    time.sleep(5)  # Aguardar reload
    verify_deployment()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║   ✅ PROCESSO CONCLUÍDO!                                   ║
    ╚══════════════════════════════════════════════════════════╝
    
    🌐 Acesse seu site: https://{DOMAIN}
    
    📝 Próximos passos:
    1. Teste o site
    2. Limpe o cache do navegador (Ctrl+Shift+Delete)
    3. Verifique se está funcionando corretamente
    
    🔧 Se houver problemas:
    - Logs de erro: https://www.pythonanywhere.com/user/{USERNAME}/files/var/log
    - Console: https://www.pythonanywhere.com/user/{USERNAME}/consoles/
    """)
    
    return 0

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Deploy cancelado pelo usuário")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        exit(1)
