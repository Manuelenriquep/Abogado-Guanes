@echo off
title 🦉 ARRANQUE MAESTRO - GUANES IA
echo ==========================================
echo 🦉 INICIANDO ECOSISTEMA ABOGADO VIRTUAL...
echo ==========================================
cd /d c:\AbogadoVirtual
echo.
echo [1/2] Levantando Cerebro Local (Puerto 8000)...
start "PUENTE" py servidor_puente.py
timeout /t 3
echo [2/3] Levantando Tablero Interno (Puerto 5000)...
start "TABLERO" py 08_Tablero_Interno/app_dashboard.py
timeout /t 2
echo [3/3] Abriendo Túnel Seguro (Ngrok)...
start "TUNEL" ngrok http --url=hematozoic-icebound-ninfa.ngrok-free.dev 8000
echo.
echo ==========================================
echo ✅ SISTEMA LISTO Y OPERATIVO
echo Revisa el Chat en: abogado.guanes.biz
echo ==========================================
pause
