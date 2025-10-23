# 🏠 Espacios Con Piscina - Sistema de Gestión

Sistema de gestión completo para la empresa **Espacios Con Piscina ECP, SRL**, que permite manejar reservas, clientes, propietarios, facturación, abonos y gastos, con panel web, app de escritorio (Electron) y API backend (FastAPI).

---

## 🚀 Guía Rápida de Instalación

### 🧩 Requisitos previos
- Python 3.10 o superior
- Node.js 18 o superior
- Yarn (`npm install -g yarn`)
- MongoDB Atlas (o local)

---

## ⚙️ 1. Configuración del Backend (API)
1. Entra a la carpeta del backend:
   ```bash
   cd backend
   ```

2. Crea un entorno virtual y actívalo:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Verifica que tengas un archivo `.env` con las siguientes variables (ya tienes el ejemplo listo):
   ```env
   MONGO_URL=mongodb+srv://<usuario>:<password>@<cluster>/<db>?retryWrites=true&w=majority
   DB_NAME=villa_management
   JWT_SECRET_KEY=clave-super-segura
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

5. Ejecuta el servidor FastAPI:
   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

6. Abre la documentación interactiva en tu navegador:
   👉 http://localhost:8000/docs

---

## 💻 2. Configuración del Frontend (React + Electron)
1. Entra a la carpeta del frontend:
   ```bash
   cd frontend
   ```

2. Instala dependencias:
   ```bash
   yarn install
   ```

3. Asegúrate de tener `.env` con:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

4. Ejecuta el proyecto:
   ```bash
   yarn start
   ```

5. Para abrir la app de escritorio (Electron):
   ```bash
   yarn electron-dev
   ```

6. Para crear el instalador (.exe):
   ```bash
   yarn electron-build-win
   ```

---

## 🧰 3. Scripts rápidos (Windows)
Estos scripts ya están listos para ti:
- **run_backend.bat** → inicia FastAPI
- **run_frontend.bat** → abre React + Electron
- **build_windows_app.bat** → genera el instalador

Solo haz doble clic sobre cada uno.

---

## 🔒 Seguridad Recomendada
- Cambia `JWT_SECRET_KEY` por una cadena larga y única.
- Configura `CORS_ORIGINS` solo con tus dominios reales.
- Usa un usuario MongoDB dedicado, sin permisos globales.
- Activa HTTPS cuando publiques la app.

---

## 📦 Estructura del Proyecto
```
ECP1-main/
├── backend/
│   ├── server.py
│   ├── models.py
│   ├── database.py
│   ├── auth.py
│   ├── requirements.txt
│   ├── .env
│   └── run_backend.bat
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── electron.js
│   ├── package.json
│   ├── .env
│   ├── run_frontend.bat
│   └── build_windows_app.bat
│
└── README.md
```

---

## 💬 Soporte
Si algo no funciona, revisa la consola de tu terminal y asegúrate de que:
- MongoDB esté en línea
- Las variables del `.env` sean correctas
- Los puertos 8000 y 3000 no estén ocupados

---
© 2025 Espacios Con Piscina ECP, SRL
