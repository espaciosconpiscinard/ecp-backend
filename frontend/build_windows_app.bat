@echo off
title Generar Instalador Windows - Espacios Con Piscina
echo =======================================
echo     CONSTRUYENDO APLICACIÓN .EXE
echo =======================================
cd /d "%~dp0"
cd frontend
yarn electron-build-win
pause
