import re
import os
import json
import requests
from flask import Blueprint, request, jsonify, session, current_app, url_for
from .short_captioner import ShortCaptioner
from .short_video_processor import ShortVideoProcessor
from .thumb_generator import ThumbGenerator


# Criar o blueprint
clips_bp = Blueprint('clips', __name__)

# Configurações das APIs
TRANSCRIPTION_API_WORD = "http://localhost:8010/transcribe-word/"
SHORTS_FOLDER = 'C:\\CORTES\\SHORTS'


def timestamp_to_seconds(timestamp):
    """Converte timestamp no formato HH:MM:SS.mmm para segundos."""
    try:
        # Formato esperado: HH:MM:SS.mmm
        parts = timestamp.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return round(total_seconds, 2)
    except Exception as e:
        print(f"Erro ao converter timestamp {timestamp}: {e}")
        return 0.0


def parametros_corte_padrao():
    """Retorna parâmetros de corte padrão."""
    parametros_corte = {
        "x1": 640,                 # 427 * 1.5
        "y1": 0,
        "x2": 640 + 640,          # x1 + width (mantém consistência)
        "y2": 1080,               # 720 * 1.5
        "x_center": 303,          # 202 * 1.5
        "y_center": 540,          # 360 * 1.5
        "width": 640,             # 427 * 1.5 (aprox)
        "height": 1080,           # 720 * 1.5
        "top_face": 390,          # 260 * 1.5
        "bottom_face": 690,       # 460 * 1.5
        "largura_media_rosto": 300,  # 200 * 1.5
        "altura_media_rosto": 300   # 200 * 1.5
    }
    session['parametros_corte'] = parametros_corte
    return parametros_corte


@clips_bp.route('/process-clip', methods=['POST'])
def process_clip():
    """Processa um clipe viral específico."""
    try:
        data = request.get_json()
        clip_id = int(data.get('clip_id'))
        
        print(f"[DEBUG] process_clip chamado com clip_id: {clip_id}")
        
        # Obter dados necessários da sessão
        filename = session.get('filename')
        parametros_corte = session.get('parametros_corte', {})

        if not filename:
            return jsonify({'status': 'error', 'message': 'Arquivo não encontrado na sessão'}), 400

        # Carregar os dados dos trechos do arquivo JSON
        base_name = os.path.splitext(filename)[0]
        clips_data_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
        
        if not os.path.exists(clips_data_path):
            return jsonify({'status': 'error', 'message': 'Dados dos clipes não encontrados no servidor'}), 404
            
        with open(clips_data_path, 'r', encoding='utf-8') as f:
            viral_clips = json.load(f)
        
        print(f"[DEBUG] Dados dos clipes carregados de: {clips_data_path}")

        clip_encontrado = None
        
        if 'cortes_virais' in viral_clips:
            print(f"[DEBUG] Número de cortes virais: {len(viral_clips['cortes_virais'])}")
            for i, clip in enumerate(viral_clips['cortes_virais']):
                print(f"[DEBUG] Clip {i}: ID={clip.get('id')} (tipo: {type(clip.get('id'))})")
                if clip.get('id') == int(clip_id):
                    clip_encontrado = clip
                    session['clip_encontrado'] = clip_encontrado
                    print(f"[DEBUG] Clip encontrado: {clip_encontrado}")
                    break
        else:
            print(f"[DEBUG] 'cortes_virais' não encontrado em viral_clips")
        
        if not clip_encontrado:
            print(f"[DEBUG] Clip com ID {clip_id} não foi encontrado")
            return jsonify({'status': 'error', 'message': 'Trecho não encontrado'}), 404
        
        # Se parametros_corte for vazio, usar valores padrão
        if not parametros_corte:
            parametros_corte = parametros_corte_padrao()

        # Converter timestamps para segundos
        start_time = timestamp_to_seconds(clip_encontrado['timestamp_inicio'])
        end_time = timestamp_to_seconds(clip_encontrado['timestamp_fim'])

        print(f"Tempo em timestamp: {clip_encontrado['timestamp_inicio']} - em segundos: {start_time}")
        print(f"Tempo em timestamp: {clip_encontrado['timestamp_fim']} - em segundos: {end_time}")
        
        # Criar diretório de shorts se não existir
        shorts_dir = "shorts"
        os.makedirs(shorts_dir, exist_ok=True)
        
        # Processar o vídeo
        video_path = os.path.join("uploads", filename)
        
        titulo = clip_encontrado["titulo_sugestivo"]
        # Remover caracteres especiais do titulo com regex
        titulo = re.sub(r'[^a-zA-Z0-9]', '', titulo)

        output_filename = f"{titulo}.mp4"
        output_path = os.path.join(SHORTS_FOLDER, output_filename)
        
        print(f"[DEBUG] Caminho do vídeo de entrada: {video_path}")
        print(f"[DEBUG] Caminho de saída do short: {output_path}")
        
        processor = ShortVideoProcessor(video_path, output_path)
        
        # Carregar vídeo
        if not processor.load_video():
            return jsonify({'status': 'error', 'message': 'Erro ao carregar o vídeo'}), 500
        
        # Criar short
        temp_shorts = processor.create_short_video(
            start_time=start_time,
            end_time=end_time,
            parametros_corte=parametros_corte
        )
        
        if temp_shorts:
            # Salvar informações do trecho processado na sessão
            session['trecho_processado'] = {
                'clip_id': clip_id,
                'output_path': output_path,
                'start_time': clip_encontrado['timestamp_inicio'],
                'end_time': clip_encontrado['timestamp_fim'],
                'title': clip_encontrado['titulo_sugestivo']
            }

            # Abrir o arquivo de vídeo processado para envio
            with open(temp_shorts, 'rb') as video_file:
                files = {'file': (os.path.basename(temp_shorts), video_file, 'video/mp4')}
                print(f"[DEBUG] Enviando arquivo para transcrição de palavras: {os.path.basename(temp_shorts)}")
                words = requests.post(TRANSCRIPTION_API_WORD, files=files, timeout=600)
                
                # Converter a resposta de texto para JSON
                words_data = json.loads(words.text)

            size = {"720": 35, "1080": 70}
            height = size[str(parametros_corte['height'])]


            captioner = ShortCaptioner(
                video_path=temp_shorts,
                font_path=os.path.join(current_app.config['FONTS_PATH'], "GothamBlack.ttf"),
                font_size=height,
                font_color="yellow",
                stroke_color="black",
                stroke_width=3,
                margin_bottom=parametros_corte['bottom_face']-200,

            )
            
            # Chama o método para criar o vídeo final
            captioner.create_captioned_video(words_data, output_path)
            
            # Retorna a URL do vídeo final
            final_video_url = url_for('download_file', filename=output_path)



            thumbnail_details = {
                "titulo": clip_encontrado['texto_thumb'],
                "clima": clip_encontrado['clima'],
                "expressao_facial": clip_encontrado['expressao_facial'],
                "texto_gerar_thumbnail": clip_encontrado['texto_gerar_thumbnail']
            }


            thumbnail_creator = ThumbGenerator()
            thumbnail_creator.create_thumbnail(output_path,thumbnail_details)

            os.remove(temp_shorts)
            return jsonify({'status': 'success', 'video_url': final_video_url})

        else:
            return jsonify({'status': 'error', 'message': 'Erro ao processar o vídeo'}), 500
            
    except Exception as e:
        print(f"Erro ao processar trecho: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500







@clips_bp.route('/update_clip_timestamps', methods=['PUT'])
def update_clip_timestamps():
    """Atualiza os timestamps de um clipe viral e persiste no arquivo JSON."""
    try:
        data = request.get_json(force=True)
        clip_id = data.get('clip_id')
        start_sec = float(data.get('start_sec', 0))
        end_sec = float(data.get('end_sec', 0))

        if not clip_id or start_sec < 0 or end_sec <= start_sec:
            return jsonify({'status': 'error', 'message': 'Parâmetros inválidos.'}), 400

        filename = session.get('filename')
        if not filename:
            return jsonify({'status': 'error', 'message': 'Arquivo não encontrado na sessão.'}), 400

        # Carregar dados dos clipes do arquivo JSON
        base_name = os.path.splitext(filename)[0]
        clips_data_path = os.path.join(current_app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
        
        if not os.path.exists(clips_data_path):
            return jsonify({'status': 'error', 'message': 'Dados dos clipes não encontrados.'}), 404
            
        with open(clips_data_path, 'r', encoding='utf-8') as f:
            viral_clips = json.load(f)

        # Busca o clipe pelo ID
        clip_encontrado = None
        for clip in viral_clips.get('cortes_virais', []):
            if clip.get('id') == clip_id:
                clip_encontrado = clip
                break

        if not clip_encontrado:
            return jsonify({'status': 'error', 'message': 'Clipe não encontrado.'}), 404

        # Converter segundos para timestamp format (HH:MM:SS.mmm)
        def seconds_to_timestamp(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milliseconds = round((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"

        # Atualiza timestamps no clipe específico
        clip_encontrado['timestamp_inicio'] = seconds_to_timestamp(start_sec)
        clip_encontrado['timestamp_fim'] = seconds_to_timestamp(end_sec)
        
        # Recalcula duração
        duration_seconds = end_sec - start_sec
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)
        clip_encontrado['duracao_minutos_segundos'] = f"{minutes}:{seconds:02d}"

        # Persiste no arquivo JSON
        with open(clips_data_path, 'w', encoding='utf-8') as f:
            json.dump(viral_clips, f, ensure_ascii=False, indent=4)

        return jsonify({
            'status': 'success', 
            'clip': {
                'id': clip_encontrado['id'],
                'timestamp_inicio': clip_encontrado['timestamp_inicio'],
                'timestamp_fim': clip_encontrado['timestamp_fim'],
                'duracao_minutos_segundos': clip_encontrado['duracao_minutos_segundos'],
                'start_sec': start_sec,
                'end_sec': end_sec
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Falha ao atualizar timestamps: {e}'}), 500
