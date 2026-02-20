# Web de Cifrado/Descifrado en Python

Aplicación web en Flask con dos módulos:

- César (cifrar y descifrar con desplazamiento)
- Atbash (simétrico)

Ambos usan un **conjunto de caracteres configurable** por el usuario (por defecto: ASCII imprimible `32-126`).

## Requisitos

- Python 3.10+

## Ejecución

1. Crear entorno virtual (opcional):
   - Windows PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

2. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

3. Ejecutar la app:
   ```powershell
   python app.py
   ```

4. Abrir en el navegador:
   - `http://127.0.0.1:5000/`

## Uso

- Selecciona el módulo: `César` o `Atbash`.
- Selecciona operación: `Cifrar` o `Descifrar`.
- Define el conjunto de caracteres (o usa el botón de ASCII imprimible).
- Escribe el texto y presiona **Procesar**.

> Nota: Si un carácter del texto no está en el conjunto definido, se deja sin cambios.

## Despliegue en Render

1. Sube el contenido de esta carpeta a un repositorio de GitHub.
2. En Render, elige **New +** → **Blueprint** y conecta ese repositorio.
3. Render detectará `render.yaml` automáticamente.
4. Espera a que termine el build y abre la URL pública del servicio.

Si prefieres crear el servicio manualmente en Render:

- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
