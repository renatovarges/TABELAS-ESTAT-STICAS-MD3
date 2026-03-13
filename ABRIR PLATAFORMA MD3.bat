@echo off
:: Navega para a pasta onde o arquivo .bat está localizado
cd /d "%~dp0"
title Abrindo Plataforma MD3...
echo Iniciando o motor de dados e a interface visual...
:: Usa o comando streamlit run direto no arquivo local para evitar problemas de acentuação no caminho
streamlit run app.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Ocorreu um erro ao iniciar. Verifique se o Python e o Streamlit estao instalados.
    pause
)
