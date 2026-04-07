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
- También puedes usar `Probar 200 desplazamientos` para ver 200 descifrados posibles de César.
- La opción `Identificar cifrado` hace un análisis heurístico para sugerir si el texto parece César o Atbash.
- Define el conjunto de caracteres (o usa el botón de ASCII imprimible).
- Escribe el texto y presiona **Procesar**.

> Nota: Si un carácter del texto no está en el conjunto definido, se deja sin cambios.

