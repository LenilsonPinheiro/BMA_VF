@echo off
echo.
echo --- INICIANDO TESTE DE DIAGNOSTICO ---
echo Verificando a sintaxe do comando 'if'...
echo.

if exist "instance" (
    echo [SUCESSO] O comando 'if' com parenteses funcionou.
) else (
    echo [SUCESSO] O comando 'if/else' com parenteses funcionou.
)

echo.
echo --- TESTE CONCLUIDO ---
echo Se voce esta vendo esta mensagem, a sintaxe basica do CMD esta OK.
pause
