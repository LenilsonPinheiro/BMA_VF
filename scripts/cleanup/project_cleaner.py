#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para limpar o projeto:
- Remove referencias a IAs (
- Remove emojis
- Simplifica comentarios
- Adiciona autoria correta: Lenilson Pinheiro
"""

import os
import re
from pathlib import Path

# Autor correto
AUTOR = "Lenilson Pinheiro"
DATA = "Janeiro 2025"

# Padroes para remover
PADROES_IA = [
    r'
    r'
    r'
    r'
    r'GPT-[0-9][^\n]*',
    r'
    r'
    r'
    r'
]

# Emojis comuns
EMOJIS = [
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', ''
]

def remover_emojis(texto):
    """Remove todos os emojis do texto"""
    for emoji in EMOJIS:
        texto = texto.replace(emoji, '')
    # Remove outros emojis unicode
    texto = re.sub(r'[\U00010000-\U0010ffff]', '', texto)
    return texto

def remover_referencias_ia(texto):
    """Remove referencias a IAs"""
    for padrao in PADROES_IA:
        texto = re.sub(padrao, '', texto, flags=re.IGNORECASE)
    return texto

def adicionar_autoria(texto, arquivo):
    """Adiciona autoria correta"""
    # Se for arquivo Python
    if arquivo.endswith('.py'):
        if 'Autor:' not in texto and 'Author:' not in texto:
            linhas = texto.split('\n')
            # Procura pelo docstring
            for i, linha in enumerate(linhas):
                if '"""' in linha and i < 10:
                    linhas.insert(i+1, f'\nAutor: {AUTOR}')
                    linhas.insert(i+2, f'Data: {DATA}\n')
                    break
            texto = '\n'.join(linhas)
    
    # Se for arquivo Markdown
    elif arquivo.endswith('.md'):
        if 'Autor:' not in texto and 'Author:' not in texto:
            texto += f'\n\n---\n\nAutor: {AUTOR}  \nData: {DATA}\n'
    
    return texto

def simplificar_comentarios(texto):
    """Simplifica comentarios tecnicos"""
    # Substitui termos tecnicos por explicacoes simples
    substituicoes = {
        'sistema de banco de dados': 'sistema de banco de dados',
        'sistema de atualizacao do banco': 'sistema de atualizacao do banco',
        'protecao contra ataques': 'protecao contra ataques',
        'protecao contra scripts maliciosos': 'protecao contra scripts maliciosos',
        'protecao contra invasao do banco': 'protecao contra invasao do banco',
        'padrao de acessibilidade': 'padrao de acessibilidade',
        'velocidade do site': 'velocidade do site',
        'servidor de arquivos rapido': 'servidor de arquivos rapido',
        'memoria temporaria': 'memoria temporaria',
        'publicacao': 'publicacao',
        'rota': 'rota',
        'modelo de pagina': 'modelo de pagina',
        'mostrar': 'mostrar',
        'busca': 'busca',
    }
    
    for tecnico, simples in substituicoes.items():
        # Substitui em comentarios Python
        texto = re.sub(f'# .*{tecnico}.*', lambda m: m.group(0).replace(tecnico, simples), texto)
        # Substitui em docstrings
        texto = re.sub(f'""".*{tecnico}.*"""', lambda m: m.group(0).replace(tecnico, simples), texto, flags=re.DOTALL)
    
    return texto

def processar_arquivo(caminho):
    """Processa um arquivo"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Aplica transformacoes
        conteudo = remover_emojis(conteudo)
        conteudo = remover_referencias_ia(conteudo)
        conteudo = adicionar_autoria(conteudo, str(caminho))
        conteudo = simplificar_comentarios(conteudo)
        
        # Salva arquivo
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f'Processado: {caminho}')
        return True
    except Exception as e:
        print(f'Erro em {caminho}: {e}')
        return False

def main():
    """Processa todos os arquivos do projeto"""
    print('Iniciando limpeza do projeto...')
    print(f'Autor: {AUTOR}')
    print(f'Data: {DATA}')
    print()
    
    # Diretorios para processar
    diretorios = [
        'BelarminoMonteiroAdvogado',
        '.'
    ]
    
    # Extensoes para processar
    extensoes = ['.py', '.md', '.txt', '.html', '.js', '.css']
    
    # Arquivos para ignorar
    ignorar = [
        'limpar_projeto.py',
        '__pycache__',
        'venv',
        'env',
        'node_modules',
        'migrations'
    ]
    
    total = 0
    processados = 0
    
    for diretorio in diretorios:
        for raiz, dirs, arquivos in os.walk(diretorio):
            # Remove diretorios ignorados
            dirs[:] = [d for d in dirs if d not in ignorar]
            
            for arquivo in arquivos:
                # Verifica extensao
                if any(arquivo.endswith(ext) for ext in extensoes):
                    caminho = Path(raiz) / arquivo
                    total += 1
                    if processar_arquivo(caminho):
                        processados += 1
    
    print()
    print(f'Concluido!')
    print(f'Total de arquivos: {total}')
    print(f'Processados com sucesso: {processados}')
    print(f'Falhas: {total - processados}')

if __name__ == '__main__':
    main()
