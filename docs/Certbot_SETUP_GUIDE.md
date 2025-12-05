# Guia de Instalação e Configuração do Certbot

## Introdução
Este guia fornece instruções passo a passo para instalar e configurar o Certbot, uma ferramenta gratuita que facilita a obtenção e renovação automática de certificados SSL/TLS usando Let's Encrypt.

## Documentação Técnica

### 1. Instalação do Certbot
Certbot é compatível com várias plataformas web server, incluindo Apache, Nginx, etc. Vamos considerar o uso com o servidor web Apache como exemplo.

#### 1.1 Atualizar os Pacotes do Sistema:
Antes de instalar o Certbot, certifique-se de que seus pacotes estão atualizados.
```bash
sudo apt update
sudo apt upgrade -y
```

#### 1.2 Instalar o Certbot e o Plugin Apache:
O plugin Apache permitirá que o Certbot se integre automaticamente com seu servidor web.
```bash
sudo apt install certbot python3-certbot-apache -y
```

### 2. Configuração do Certificado SSL/TLS
Agora, você pode usar o Certbot para obter e instalar um certificado SSL/TLS.

#### 2.1 Executar o Certbot:
Execute o seguinte comando, substituindo `seu_dominio.com` pelo seu domínio.
```bash
sudo certbot --apache -d seu_dominio.com
```

- O Certbot irá perguntar algumas informações durante a execução. Siga as instruções na tela.
- Você será solicitado a escolher como deseja configurar o redirecionamento HTTP para HTTPS. Recomenda-se selecionar a opção que redireciona todas as requisições de HTTP para HTTPS.

#### 2.2 Verificação do Certificado:
Depois de concluir a execução, você pode verificar se o certificado foi instalado corretamente acessando seu site via `https://seu_dominio.com`.

### 3. Renovação Automática dos Certificados
Os certificados Let's Encrypt são válidos por 90 dias e devem ser renovados regularmente. O Certbot configura um cron job ou systemd timer para renovar automaticamente os certificados antes de expirarem.

#### 3.1 Testando a Renovação Automática:
Você pode testar o processo de renovação manualmente com o seguinte comando:
```bash
sudo certbot renew --dry-run
```

- Se não houver erros, isso indica que sua configuração está correta e os certificados serão renovados automaticamente no futuro.

## Checklist de Implementação
- [ ] Atualizar pacotes do sistema
- [ ] Instalar Certbot e plugin Apache
- [ ] Executar Certbot para obter o certificado SSL/TLS
- [ ] Verificar a instalação do certificado
- [ ] Testar a renovação automática dos certificados

## Exemplos de Logs
Aqui estão exemplos de logs que você pode esperar ver durante a configuração do Certbot.

#### Log de Execução:
```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Plugins selected: Authenticator apache, Installer apache
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for seu_dominio.com
Waiting for verification...
Cleaning up challenges
Generating key (rsa 4096 bits): /etc/letsencrypt/live/seu_dominio.com/privkey.pem
Creating fullchain certificates is deprecated. Please use --fullchain.
Deploying Certificate to VirtualHost /etc/apache2/sites-available/000-default-le-ssl.conf
Enabling available site: /etc/apache2/sites-available/default-ssl.conf
```

#### Log de Renovação:
```
Processing /etc/letsencrypt/renewal/seu_dominio.com.conf
Cert not due for renewal, but simulating renewal for dry run
Plugins selected: Authenticator apache, Installer apache
Renewing an existing certificate for seu_dominio.com
Performing the following challenges:
http-01 challenge for seu_dominio.com
Waiting for verification...
Cleaning up challenges
Generating key (rsa 4096 bits): /etc/letsencrypt/live/seu_dominio.com/privkey.pem
Creating fullchain certificates is deprecated. Please use --fullchain.
Deploying Certificate to VirtualHost /etc/apache2/sites-available/default-ssl.conf
```

## Links Úteis para Ferramentas Externas
- **Certbot**: [Documentação Oficial](https://certbot.org/docs/)
- **Let's Encrypt**: [Documentação](https://letsencrypt.org/docs/)
