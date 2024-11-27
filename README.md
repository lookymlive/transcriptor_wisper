# Whisper (Transcribe tu audio) en local

# ¿Qué es Whisper?

**Whisper** es un sistema de reconocimiento de voz automático entrenado con 680,000 horas de audio en varios idiomas y acentos. 

Utiliza una arquitectura de Transformers para transcribir audio a texto y traducirlo al inglés si es necesario. 

El sistema detecta el idioma, divide el audio en segmentos de 30 segundos, y transcribe utilizando codificadores y decodificadores. 

Además de transcribir, Whisper puede identificar idiomas, marcar tiempos y procesar voz multilingüe. 

Está diseñado para ser escalable y manejar grandes cantidades de audio con características avanzadas de procesamiento de lenguaje natural.

# Creación de Aplicación Paso a Paso:

## **Objetivo de la Aplicación**

Crear una aplicación web que permita:

- **Subir un archivo de audio o video en formatos MP3, WAV, MP4**.
- **Convertirlo a un formato reconocible por Whisper**.
- **Seleccionar el idioma del audio para transcribir**.
- **Descargar la transcripción en un archivo de texto y también en formato SRT**.

## **Herramientas y Tecnologías Necesarias que vamos a utilizar**

- **Python**: Lenguaje de programación para el backend.
- **Visual Studio Code (VS Code)**: Editor de código.
- **Flask**: Framework web para Python.
- **Whisper**: Modelo de OpenAI para transcripción de audio.
- **FFmpeg**: Herramienta para manejar archivos de audio.
- **Bootstrap**: Framework CSS para mejorar la interfaz de usuario.

## **Paso 1: Instalar Python**

### **Descargar  e Instalar Python**:

- Ve a [python.org/downloads](https://www.python.org/downloads/) y descarga la última versión de Python 3.x para Windows.
- Video de Apoyo:
    
    [🐍 Como Descargar e Instalar PYTHON (3.X) - Tutorial en Español - En menos de 3 Minutos](https://youtu.be/eoY4MXVez0k)
    

## **Paso 2: Instalar Visual Studio Code**

### **Descargar e Instalar VS Code**:

- Ve a [code.visualstudio.com/download](https://code.visualstudio.com/download) y descarga la versión para Windows.
- Video de Apoyo:
    
    [🟦 Como Descargar e Instalar VISUAL STUDIO CODE (VSCode) en menos de 4 Minutos](https://youtu.be/JcHR-4vZD4Q)
    

## Paso 3: Configuración de Visual Studio Code para Python

### **Instalar la Extensión de Python**:

- Instala las extensiones en VS Code) para Python.
- Video de Apoyo:
    
    [Las 5 🟡 EXTENSIONES para VISUAL STUDIO CODE de Python que Necesitas](https://youtu.be/uEMXf0Qt7YY)
    

## Paso 4: Revisar la Política de Ejecución en PowerShell

### **Verifica la política de ejecución de Windows PowerShell:**

- Debes tenerlo configurado en  **`RemoteSigned`**
- Video de Apoyo:
    
    [🟦 PowerShell - Como Habilitar y Activar en Windows PowerShell - Tutorial](https://youtu.be/WBhMrouALPk)
    

## **Paso 5: Instalar y configurar FFmpeg**

Whisper requiere FFmpeg para procesar archivos de audio.

### **Descarga e instala FFmpeg**:

- Link de descarga directa https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip y descarga el archivo ZIP.
- Video de Apoyo:
    
    [🟢 Como Instalar FFMPEG y configurar en WINDOWS - Guía Completa - 👣 Paso a Paso](https://youtu.be/WNjEISfzcYM)
    

## **Paso 6: Crear el Entorno de Trabajo**

**Crear una Carpeta para tu Proyecto**:

- Por ejemplo, en tu escritorio, crea una carpeta llamada `transcriptor_whisper`.

**Abrir la Carpeta en VS Code**:

- Ve a **"Archivo" > "Abrir carpeta..."** y selecciona la carpeta `transcriptor_whisper`.

## **Paso 7: Configurar un Entorno Virtual**

Un entorno virtual te permite aislar las dependencias de tu proyecto.

1. **Abrir la Terminal en VS Code**:
    - Ve a **"Terminal" > "Nueva terminal"**.
2. **Crear el Entorno Virtual**:
    - En la terminal, ejecuta:
    
    ```bash
    python -m venv venv
    ```
    
3. **Activar el Entorno Virtual**:
    - Ejecuta:
        
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
        
        Verás que en la terminal aparece `(venv)` al inicio de la línea, indicando que el entorno virtual está activo.
        

## **Paso 8: Instalar las Dependencias Necesarias**

Con el entorno virtual activado, instalaremos las librerías necesarias.

### **Actualizar pip** (opcional pero recomendado):

```bash
python -m pip install --upgrade pip
```

### **Instalar Flask**:

```bash
pip install flask
```

### **Instalar Whisper**:

```bash
pip install openai-whisper
```

### **Instalar PyTorch (requerido por Whisper)**:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### **Instalar moviepy** (para manejar archivos de video y audio):

```bash
pip install moviepy
```

**Verificar la Instalación de las Librerías**:

```bash
pip list
```

Asegúrate de que `flask`, `openai-whisper`, `torch`, `torchvision`, `torchaudio` y `moviepy` estén en la lista.

## **Paso 9: Crear la Estructura del Proyecto**

Crearemos esta estractura en el proyecto

```arduino
transcriptor_whisper/
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── styles.css
├── venv/
```

## **Paso 10: Escribir el Código de la Aplicación**

### **Código de `app.py`**

```python
import os
from flask import Flask, render_template, request, jsonify, send_file
import whisper
import tempfile
import subprocess
from datetime import timedelta

app = Flask(__name__)

# Cargar el modelo de Whisper
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribir', methods=['POST'])
def transcribir_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo de audio'}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        # Validar que el archivo es de un formato aceptado
        allowed_extensions = ['.mp3', '.wav', '.mp4']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'El archivo debe ser en formato MP3, WAV o MP4'}), 400

        # Guardar el archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_input:
            file.save(temp_input.name)
            input_path = temp_input.name

        # Convertir el archivo a formato WAV usando FFmpeg
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_output:
            output_path = temp_output.name

        # Ejecutar FFmpeg para convertir el archivo a WAV mono de 16kHz
        command = [
            'ffmpeg', '-i', input_path,
            '-ar', '16000', '-ac', '1',
            '-c:a', 'pcm_s16le', output_path,
            '-y'  # Sobrescribir si el archivo existe
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Eliminar el archivo de entrada temporal
        os.remove(input_path)

        # Obtener el idioma seleccionado
        language = request.form.get('language')

        # Realizar la transcripción con Whisper
        result = model.transcribe(output_path, language=language)

        # Eliminar el archivo de audio convertido temporal
        os.remove(output_path)

        # Guardar la transcripción en archivos de texto y SRT temporalmente
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode='w', encoding='utf-8') as temp_transcript_txt:
            temp_transcript_txt.write(result['text'])
            transcript_txt_path = temp_transcript_txt.name

        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode='w', encoding='utf-8') as temp_transcript_srt:
            srt_content = generate_srt(result['segments'])
            temp_transcript_srt.write(srt_content)
            transcript_srt_path = temp_transcript_srt.name

        # Preparar la respuesta para descargar los archivos
        response_format = request.form.get('response_format')

        if response_format == 'srt':
            return send_file(transcript_srt_path, as_attachment=True, download_name="transcripcion.srt")
        else:
            return send_file(transcript_txt_path, as_attachment=True, download_name="transcripcion.txt")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(td.microseconds / 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

if __name__ == "__main__":
    app.run(debug=True)
```

### **Código de `index.html`**

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Transcriptor de Audio con Whisper</title>
    <!-- Meta viewport para responsividad -->
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <!-- Hoja de estilos personalizada -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Transcriptor de Audio con Whisper</h1>
        <div class="card p-4 shadow">
            <form id="uploadForm" enctype="multipart/form-data">
                <!-- Subir archivo -->
                <div class="form-group">
                    <label for="audio">Selecciona un archivo de audio o video:</label>
                    <input type="file" class="form-control-file" id="audio" name="audio" accept="audio/*,video/*" required>
                </div>
                <!-- Seleccionar idioma -->
                <div class="form-group">
                    <label for="language">Selecciona el idioma del audio:</label>
                    <select class="form-control" id="language" name="language">
                        <option value="es">Español</option>
                        <option value="en">Inglés</option>
                        <!-- Agrega más idiomas si lo deseas -->
                    </select>
                </div>
                <!-- Seleccionar formato de descarga -->
                <div class="form-group">
                    <label for="response_format">Selecciona el formato de descarga:</label>
                    <select class="form-control" id="response_format" name="response_format">
                        <option value="txt">Texto (.txt)</option>
                        <option value="srt">Subtítulos (.srt)</option>
                    </select>
                </div>
                <!-- Botón de transcripción -->
                <button type="submit" class="btn btn-primary">Transcribir</button>
            </form>
            <!-- Mensajes de resultado -->
            <div id="result" class="mt-3"></div>
        </div>
    </div>

    <!-- Scripts de Bootstrap y dependencias -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <!-- Script personalizado -->
    <script>
        // Manejar envío del formulario
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="alert alert-info">Procesando... Por favor, espera.</div>';

            try {
                const response = await fetch('/transcribir', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const contentDisposition = response.headers.get('Content-Disposition');
                    let filename = 'transcripcion.txt';

                    const match = contentDisposition ? contentDisposition.match(/filename="(.+)"/) : null;
                    if (match && match.length === 2)
                        filename = match[1];

                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    resultDiv.innerHTML = '<div class="alert alert-success">Transcripción completada. El archivo ha sido descargado.</div>';
                } else {
                    const errorData = await response.json();
                    resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${errorData.error}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>

```

### **Código de `styles.css`**

```css
body {
    background-color: #f0f8ff; /* Un suave color azul */
}

h1 {
    color: #0C4B8D; /* Azul oscuro */
}

.btn-primary {
    background-color: #FFB02E; /* Naranja */
    border-color: #FFB02E;
}

.btn-primary:hover {
    background-color: #e09b28; /* Naranja oscuro */
    border-color: #e09b28;
}

.card {
    border: 1px solid #0C4B8D; /* Borde azul oscuro */
}
```

## **Paso 11: Ejecutar la Aplicación**

**Activa el Entorno Virtual**:

```bash
venv\Scripts\activate
```

**Ejecuta la Aplicación**:

```bash
python app.py
```

**Verificar que la Aplicación Está Corriendo**:

```vbnet
* Serving Flask app "app" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

**Abrir el Navegador**:

Abre tu navegador web y visita http://127.0.0.1:5000/.

## **Paso 11: Probar la Aplicación**

**Subir un Archivo MP3, WAV O MP4**:

En la página web, haz clic en **"Selecciona un archivo MP3"** y elige un archivo desde tu computadora.

Selecciona el **idioma del audio** en el menú desplegable.

Haz clic en **"Transcribir"**.

**Esperar la Transcripción**:

Verás un mensaje que indica que se está procesando.

Una vez completado, se descargará automáticamente un archivo llamado nombra y puedes utilizar cualquiera de estas extensiones .txt o .srt.

**Verificar la Transcripción**:

Abre el archivo descargado y verifica que el texto corresponde al audio proporcionado.