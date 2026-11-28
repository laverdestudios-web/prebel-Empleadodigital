@echo off
REM Abre el chat de pruebas del Empleado Digital en http://localhost:8000/prueba
REM Requisitos: Python 3.10+ y server\.env con GEMINI_API_KEY (copiar de .env.example).
setlocal
cd /d "%~dp0.."

if not exist "server\.env" (
  echo [ERROR] Falta server\.env. Copia server\.env.example a server\.env y escribe tu GEMINI_API_KEY.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual .venv ...
  python -m venv .venv || (echo [ERROR] No se encontro Python en el PATH. & pause & exit /b 1)
)

echo Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install -q -r server\requirements.txt || (pause & exit /b 1)

set CHAT_PRUEBAS=1
start "" http://localhost:8000/prueba
echo Servidor en http://localhost:8000/prueba  (Ctrl+C para detener)
".venv\Scripts\python.exe" -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --env-file server\.env
endlocal
