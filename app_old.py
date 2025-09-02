# /app.py - VERSÃO COMPLETA E FINAL COM KARAOKÊ ATIVADO

import os
import requests
import uuid
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
from short_captioner import ShortCaptioner  # Sua classe de legendagem
from ajust_caption import CaptionProcessor    # Sua classe de processamento de frases
from viral_moments import ViralClipFinder       # Classe para encontrar momentos virais

# --- CONFIGURAÇÃO ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
TRANSCRIPTION_API_URL = "http://localhost:8010/transcribe/"  # Alterado para o novo endpoint
TRANSCRIPTION_API_WORD = "http://localhost:8010/transcribe-word/"  # Alterado para o novo endpoint



app = Flask(__name__)
CORS(app, resources={r"/*": {
    "origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}})


app.config.from_mapping(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    OUTPUT_FOLDER=OUTPUT_FOLDER,
    SECRET_KEY='uma-chave-secreta-muito-forte',
    MAX_CONTENT_LENGTH=1000 * 1024 * 1024  # Limite de 1 GB
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi', 'mkv'}

def srt_to_phrases(srt_content):
    """Converte conteúdo SRT em uma lista de dicionários de frases."""
    phrases = []
    lines = srt_content.strip().split('\n')
    i = 0
    while i < len(lines):
        if lines[i].strip().isdigit():
            try:
                # Pular o número do bloco
                i += 1
                
                # Processar tempo
                time_line = lines[i].replace(',', '.')
                start_str, end_str = [t.strip() for t in time_line.split('-->')]
                
                h, m, s = map(float, start_str.split(':'))
                start_time = h * 3600 + m * 60 + s
                
                h, m, s = map(float, end_str.split(':'))
                end_time = h * 3600 + m * 60 + s
                
                i += 1
                
                # Processar texto
                text_lines = []
                while i < len(lines) and lines[i].strip() != '':
                    text_lines.append(lines[i].strip())
                    i += 1
                text = ' '.join(text_lines)
                
                phrases.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
                
                # Pular linha em branco
                i += 1
                
            except (ValueError, IndexError):
                # Ignora blocos malformados
                i += 1
        else:
            i += 1
    return phrases

# --- ENDPOINTS ---

@app.route('/')
def index():
    """Serve a página principal da aplicação."""
    return render_template('captioner.html')

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


# ETAPA 2: Transcreve (SRT) e converte para frases
@app.route('/transcribe', methods=['POST'])
def transcribe_video_srt():
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
        
        # O serviço retorna um JSON com a chave 'srt'
        transcription_data = response.json()
        srt_content = transcription_data.get('srt', '')
        
        # Converte o SRT para o formato de frases que o frontend espera
        
        
        return jsonify({'status': 'success', 'phrases': phrases})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Endpoint antigo (mantido para referência, mas não usado pelo frontend)
@app.route('/transcribe-word', methods=['POST'])
def transcribe_video_words():
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

        caption_processor = CaptionProcessor(words_per_line=3, 
                                             gap_threshold=0.8)
        words_data, phrases = caption_processor.process_caption_data(words_data)
        
        return jsonify({'status': 'success', 'phrases': phrases})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# NOVO ENDPOINT: Encontra momentos virais
@app.route('/find_shorts', methods=['POST'])
def find_viral_shorts():
    data = request.get_json()
    if not data or 'phrases' not in data:
        return jsonify({'status': 'error', 'message': 'Dados de frases não fornecidos'}), 400

    phrases = data['phrases']
    
    # Concatena todas as frases em um único texto de legenda
    full_subtitle = "\n".join([p['text'] for p in phrases])

    try:
        # Chama o método estático para analisar a legenda
        # Você pode ajustar min_duration e max_duration conforme necessário
        viral_clips = ViralClipFinder.analyze_subtitle(
            subtitle=full_subtitle,
            min_duration=30, 
            max_duration=60
        )
        return jsonify({'status': 'success', 'viral_clips': viral_clips})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ETAPA 3: Recebe o texto editado e renderiza o vídeo
@app.route('/caption', methods=['POST'])
def caption_video():
    print("=== ENDPOINT /caption CHAMADO ===")
    data = request.get_json()
    print(f"Dados recebidos: {data}")
    if not data or 'filename' not in data or 'phrases' not in data:
        print("Erro: Dados incompletos")
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
        
        # Instancia sua classe ShortCaptioner
        captioner = ShortCaptioner(
            video_path=video_path,
            font_path="GothamBlack.ttf",
            font_size=70,
            font_color="yellow",
            stroke_color="black",
            stroke_width=3,
            position=("center", "bottom"),
            margin_bottom=700
        )
        
        # Chama o método sem karaoke
        captioner.create_captioned_video_from_phrases(phrases, output_path)
        
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
    app.run(debug=True, host='0.0.0.0', port=8014)