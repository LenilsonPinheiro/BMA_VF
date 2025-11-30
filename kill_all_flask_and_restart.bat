@echo off
echo ================================================================================
echo MATANDO TODOS OS PROCESSOS FLASK E PYTHON
echo ================================================================================

echo.
echo [1/3] Matando todos os processos Python...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul

echo.
echo [2/3] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Iniciando servidor Flask limpo...
echo.
echo ================================================================================
echo SERVIDOR INICIANDO - Acesse: http://localhost:5000
echo ================================================================================
echo.

python run.py

pause
