@echo off
title Iniciar Backend - Espacios Con Piscina
echo =======================================
echo     INICIANDO BACKEND (FASTAPI)
echo =======================================
cd /d "%~dp0"
cd backend
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
pause
