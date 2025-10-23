@echo off
title Iniciar Frontend - Espacios Con Piscina
echo =======================================
echo     INICIANDO FRONTEND + ELECTRON
echo =======================================
cd /d "%~dp0"
cd frontend
yarn install
yarn electron-dev
pause
