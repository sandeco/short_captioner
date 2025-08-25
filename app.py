# /app.py - VERSÃO COMPLETA E FINAL COM KARAOKÊ ATIVADO

import os
import requests
import uuid
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from short_captioner import ShortCaptioner  # Sua classe de legendagem
from ajust_caption import CaptionProcessor    # Sua classe de processamento de frases

# --- CONFIGURAÇÃO ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
TRANSCRIPTION_API_URL = "http://localhost:8010/transcribe-word-parallel/"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}})
app.config.from_mapping(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    OUTPUT_FOLDER=OUTPUT_FOLDER,
    SECRET_KEY='uma-chave-secreta-muito-forte',
    MAX_CONTENT_LENGTH=100 * 1024 * 1024  # Limite de 100 MB
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi', 'mkv'}

# --- ENDPOINTS ---

@app.route('/')
def index():
    """Serve a página principal da aplicação."""
    return render_template('index.html')

# ETAPA 1: Apenas faz o upload do vídeo
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado'}), 400
    file = request.files['video']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Arquivo inválido ou não selecionado'}), 400
    
    filename = secure_filename(file.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)
    video_url = url_for('get_uploaded_file', filename=filename)
    return jsonify({'status': 'success', 'filename': filename, 'video_url': video_url})

# ETAPA 2: Apenas transcreve e retorna as frases
@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'status': 'error', 'message': 'Nome do arquivo não fornecido'}), 400

    filename = data['filename']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(video_path):
        return jsonify({'status': 'error', 'message': 'Arquivo de vídeo não encontrado'}), 404

    try:
        with open(video_path, 'rb') as f:
            files = {'file': (filename, f, 'video/mp4')}
            response = requests.post(TRANSCRIPTION_API_URL, files=files, timeout=300)
        response.raise_for_status()
        words_data = response.json()

        caption_processor = CaptionProcessor(words_per_line=4, gap_threshold=0.8)
        _, phrases = caption_processor.process_caption_data(words_data)
        
        return jsonify({'status': 'success', 'phrases': phrases})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ETAPA 3: Recebe o texto editado e renderiza o vídeo
@app.route('/caption', methods=['POST'])
def caption_video():
    data = request.get_json()
    if not data or 'filename' not in data or 'phrases' not in data:
        return jsonify({'status': 'error', 'message': 'Dados incompletos para legendagem'}), 400

    filename = data['filename']
    phrases = data['phrases']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(video_path):
        return jsonify({'status': 'error', 'message': 'Arquivo de vídeo não encontrado'}), 404
    
    captioner = None
    try:
        output_filename = f"captioned_{uuid.uuid4().hex[:8]}_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Instancia sua classe ShortCaptioner com a cor de destaque
        captioner = ShortCaptioner(
            video_path="shorts-enxame.mp4",
            font_path="GothamBlack.ttf",
            font_size=70,
            font_color="white",
            stroke_color="black",
            stroke_width=3,
            position=("center", "bottom"),
            margin_bottom=700
        )
        
        # Chama o método com o parâmetro karaoke=True
        captioner.create_captioned_video_from_phrases(phrases, output_path, karaoke=True)
        
        final_video_url = url_for('download_file', filename=output_filename)
        return jsonify({'status': 'success', 'video_url': final_video_url})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        # Garante que o arquivo de vídeo original seja fechado e removido
        if captioner and hasattr(captioner, 'video') and captioner.video:
            captioner.video.close()
            
        if os.path.exists(video_path):
            os.remove(video_path)

# --- ROTAS AUXILIARES ---

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Serve o vídeo original para pré-visualização."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/download/<filename>')
def download_file(filename):
    """Serve o vídeo final (legendado) para download."""
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)

# --- EXECUÇÃO ---

if __name__ == '__main__':
    app.run(debug=True, port=5000)