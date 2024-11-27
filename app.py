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