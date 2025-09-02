import re
import os
from dotenv import load_dotenv

import requests
import uuid
import json
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for, session

from viral_moments import ViralClipFinder
from flask_cors import CORS
from short_captioner import ShortCaptioner
from short_video_processor import ShortVideoProcessor

# --- CONFIGURAÇÃO ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
SHORTS_FOLDER = 'C:\\CORTES\\SHORTS'
TRANSCRIPTION_API_URL = "http://localhost:8010/transcribe/"  # Alterado para o novo endpoint
TRANSCRIPTION_API_WORD = "http://localhost:8010/transcribe-word/"  # Alterado para o novo endpoint
RESIZE_VIDEO_API = "http://localhost:8013/analyze_face/"  # Alterado para o novo endpoint


app = Flask(__name__)
# SECRET_KEY será configurado abaixo
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


@app.route('/')
def index():
    """Serve a página principal da aplicação."""
    return render_template('index.html')



def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'mov', 'avi', 'mkv'}


def parametros_corte_padrao():

    parametros_corte = {
        "x1" : 427,
        "y1" : 0,
        "x2" : 427 + 427,
        "y2" : 720,
        "x_center": 202,
        "y_center": 360,
        "width": 427,
        "height": 720,
        "top_face": 260,
        "bottom_face": 460,
        "largura_media_rosto": 200,
        "altura_media_rosto": 200
    }
    session['parametros_corte'] = parametros_corte
    return parametros_corte


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



# ETAPA 1: Upload e Transcrição Automática
@app.route('/upload', methods=['POST'])
def upload_and_transcribe():
    if 'video' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado'}), 400

    file = request.files['video']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Arquivo inválido ou não selecionado'}), 400

    # Gera um nome de arquivo único para evitar conflitos
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4()
    session['unique_id'] = unique_id
    filename = f"{unique_id}.{ext}"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(video_path)

    # ETAPA 2: Transcrição automática após o upload
    try:
        print(f"[DEBUG] Enviando arquivo para transcrição: {filename}")
        with open(video_path, 'rb') as f:
            files = {'file': (filename, f, 'video/mp4')}
            response = requests.post(TRANSCRIPTION_API_URL, files=files, timeout=600) # Timeout aumentado
        
        print(f"[DEBUG] Status da resposta da API: {response.status_code}")
        response.raise_for_status()
        
        transcription_data = response.json()
        print(f"[DEBUG] Dados recebidos da API: {transcription_data}")
        
        # Verifica se a resposta contém o campo 'srt'
        if 'srt' not in transcription_data:
            print(f"[ERROR] Campo 'srt' não encontrado na resposta da API. Campos disponíveis: {list(transcription_data.keys())}")
            return jsonify({'status': 'error', 'message': 'API de transcrição não retornou o campo SRT esperado'}), 500
        
        srt_content = transcription_data.get('srt', '')
        print(f"[DEBUG] Conteúdo SRT extraído (primeiros 200 chars): {srt_content[:200] if srt_content else 'VAZIO'}")
        
        # Verifica se o conteúdo SRT não está vazio
        if not srt_content or srt_content.strip() == '':
            print(f"[ERROR] Conteúdo SRT está vazio ou contém apenas espaços em branco")
            return jsonify({'status': 'error', 'message': 'A transcrição retornou conteúdo vazio. Verifique se o vídeo contém áudio'}), 500
        
        # Salva SRT em arquivo e guarda apenas o filename na sessão
        base_name = os.path.splitext(filename)[0]
        srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.srt")
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write(srt_content)
        session['filename'] = filename
        print(f"[DEBUG] SRT salvo em: {srt_path} | Tamanho: {len(srt_content)}")
        
        video_url = url_for('get_uploaded_file', filename=filename)

    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': f'Falha na transcrição: {e}'}), 500

    return jsonify({
        'status': 'success',
        'filename': filename,
        'video_url': video_url,
        'srt_content': srt_content
    })


#ETAPA 2 : Busca de trechos virais e Análise Facial
@app.route('/find_shorts', methods=['POST'])
def find_viral_shorts():
    
    print(f"[DEBUG] Verificando sessão no find_viral_shorts...")
    print(f"[DEBUG] Chaves na sessão: {list(session.keys())}")
    
    filename = session.get('filename')
    if not filename:
        return jsonify({'status': 'error', 'message': 'Arquivo não encontrado na sessão.'}), 400
    
    base_name = os.path.splitext(filename)[0]
    srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.srt")
    try:
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()
        print(f"[DEBUG] SRT carregado de {srt_path} | Tamanho: {len(srt_content)}")
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Não foi possível ler o SRT: {e}'}), 500
    
    if not srt_content:
        return jsonify({'status': 'error', 'message': 'Conteúdo da legenda vazio.'}), 400

    try:
        # Chama o método estático para analisar a legenda
        viral_clips = ViralClipFinder.analyze_subtitle(
            subtitle=srt_content,
            min_duration=30,
            max_duration=60
        )
        
        print(f"[DEBUG] Viral clips retornados pela API: {viral_clips}")
        print(f"[DEBUG] Tipo de viral_clips: {type(viral_clips)}")
        print(f"[DEBUG] Chaves em viral_clips: {list(viral_clips.keys()) if isinstance(viral_clips, dict) else 'N/A'}")
        
        # Adicionar IDs únicos aos trechos virais
        if 'cortes_virais' in viral_clips:
            for i, clip in enumerate(viral_clips['cortes_virais']):
                # Só adiciona ID se não existir
                if 'id' not in clip:
                    clip['id'] = f"clip_{uuid.uuid4().hex[:8]}"
                clip['index'] = i
            print(f"[DEBUG] IDs adicionados aos trechos: {len(viral_clips['cortes_virais'])} clipes")
            print(f"[DEBUG] Primeiro clipe: {viral_clips['cortes_virais'][0] if viral_clips['cortes_virais'] else 'N/A'}")

            # Salva os trechos em um arquivo JSON em vez de na sessão
            base_name = os.path.splitext(filename)[0]
            clips_data_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
            
            with open(clips_data_path, 'w', encoding='utf-8') as f:
                json.dump(viral_clips, f, ensure_ascii=False, indent=4)
            
            print(f"[DEBUG] Trechos virais salvos no arquivo: {clips_data_path}")

            # Mantenha os parâmetros de corte na sessão, pois são pequenos

        else:
            print(f"[DEBUG] AVISO: 'cortes_virais' não encontrado em viral_clips")
            print(f"[DEBUG] Estrutura completa: {viral_clips}")
        
        # Salva os trechos na sessão
        print(f"[DEBUG] Trechos virais salvos na sessão: {len(viral_clips.get('cortes_virais', []))} clipes")
        
        # ETAPA 2: Análise facial automática para redimensionamento
        print(f"[DEBUG] Iniciando análise facial automática...")
        try:
            # Verificar se o arquivo ainda existe
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(video_path):
                print(f"[WARN] Arquivo de vídeo não encontrado para análise facial: {video_path}")
                return jsonify({    
                    'status': 'success',
                    'viral_clips': viral_clips,
                    'parametros_corte': None
                })
            
            # Preparar dados para envio (usando valores padrão)
            with open(video_path, 'rb') as video_file:
                files = {'video': (filename, video_file, 'video/mp4')}
                data = {
                    'tempo_analise': '00:10'  # Analisa apenas os primeiros 10 segundos
                }
                
                print(f"[DEBUG] Enviando vídeo para análise facial: {filename}")
                print(f"[DEBUG] Parâmetros: {data}")
                
                # Fazer requisição para o serviço de análise facial
                response = requests.post(
                    RESIZE_VIDEO_API, 
                    files=files, 
                    data=data,
                    timeout=300  # 5 minutos de timeout
                )
            
            print(f"[DEBUG] Status da resposta da API de análise facial: {response.status_code}")
            response.raise_for_status()
            
            # Obter dados de retorno
            parametros_corte = response.json()
            print(f"[DEBUG] Parâmetros de corte recebidos: {parametros_corte}")
            
            # Salvar parâmetros de corte na sessão
            session['parametros_corte'] = parametros_corte
            
            print(f"[DEBUG] Retornando resposta com viral_clips: {viral_clips}")
            print(f"[DEBUG] Tipo de viral_clips no retorno: {type(viral_clips)}")
            print(f"[DEBUG] Chaves em viral_clips no retorno: {list(viral_clips.keys()) if isinstance(viral_clips, dict) else 'N/A'}")
            print(f"[DEBUG] cortes_virais no retorno: {viral_clips.get('cortes_virais', 'NÃO ENCONTRADO')}")
            
            # Teste de serialização JSON

            
            return jsonify({
                'status': 'success',
                'viral_clips': viral_clips,
                'parametros_corte': parametros_corte
            })
            
        except Exception as e:
            print(f"[ERROR] Erro interno na análise facial: {e}")
            print(f"[DEBUG] Retornando viral_clips sem análise facial: {viral_clips}")

            print(f"[ERROR] Erro na requisição para API de análise facial: {e}")
            print(f"[DEBUG] Retornando viral_clips sem análise facial: {viral_clips}")

            parametros_corte_padrao()
            
            return jsonify({
                'status': 'success',
                'viral_clips': viral_clips,
                'parametros_corte': None
            })

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return jsonify({'status': 'error', 'message': f'Erro ao analisar a legenda: {e}'}), 500


# Em process_clip()
@app.route('/process-clip', methods=['POST'])
def process_clip():
    try:
        data = request.get_json()
        clip_id = int(data.get('clip_id'))
        
        print(f"[DEBUG] process_clip chamado com clip_id: {clip_id}")
        
        # Obter dados necessários da sessão
        filename = session.get('filename')
        parametros_corte = session.get('parametros_corte', {})

        if not filename:
            return jsonify({'status': 'error', 'message': 'Arquivo não encontrado na sessão'}), 400

        # --- NOVA LÓGICA ---
        # Carregar os dados dos trechos do arquivo JSON
        base_name = os.path.splitext(filename)[0]
        clips_data_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
        
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
                    print(f"[DEBUG] Clip encontrado: {clip_encontrado}")
                    break
        else:
            print(f"[DEBUG] 'cortes_virais' não encontrado em viral_clips")
        
        if not clip_encontrado:
            print(f"[DEBUG] Clip com ID {clip_id} não foi encontrado")
            return jsonify({'status': 'error', 'message': 'Trecho não encontrado'}), 404
        
        # Obter dados necessários
        filename = session.get('filename')
        parametros_corte = session.get('parametros_corte', {})
        
        #se parametros_corte for vazio, usar valores padrão
        if not parametros_corte:
            parametros_corte = parametros_corte_padrao()

        if not filename:
            return jsonify({'status': 'error', 'message': 'Arquivo não encontrado na sessão'}), 400
        

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
        #retire caracteres especiais do titulo com regex
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
            # Verificar se o arquivo foi realmente criado

            
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
                words = requests.post(TRANSCRIPTION_API_WORD, files=files, timeout=600) # Timeout aumentado
                
                # Converter a resposta de texto para JSON
                words_data = json.loads(words.text)
                

            size = {"720": 35, "1080": 70}
            height = size[str(parametros_corte['height'])]

            # CORREÇÃO: output_path não é mais passado no construtor.

            thumbnail = {
                "titulo" : clip_encontrado['texto_thumb'],
            }

            captioner = ShortCaptioner(
                video_path=temp_shorts,
                font_path="GothamBlack.ttf",
                font_size=height, # Ajuste dinâmico se necessário
                font_color="yellow",
                stroke_color="black",
                stroke_width=3,
                margin_bottom=parametros_corte['bottom_face']-200, # Ajuste conforme necessário
                thumbnail=thumbnail
            )
            
            # Chama o método para criar o vídeo final
            captioner.create_captioned_video(words_data, output_path)
            
            # 4. Retorna a URL do vídeo final
            final_video_url = url_for('download_file', filename=output_path)

            os.remove(temp_shorts)
            return jsonify({'status': 'success', 'video_url': final_video_url})

        else:

            return jsonify({'status': 'error', 'message': 'Erro ao processar o vídeo'}), 500
            
    except Exception as e:
        print(f"Erro ao processar trecho: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500




@app.route('/check-session')
def check_session():
    """Verifica se há uma sessão ativa e retorna os dados para restaurar o estado."""
    print(f"[DEBUG] check-session chamado. Sessão atual: {dict(session)}")
    
    if 'filename' in session:
        filename = session['filename']
        base_name = os.path.splitext(filename)[0]
        srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.srt")
        srt_content = ''
        try:
            with open(srt_path, 'r', encoding='utf-8') as srt_file:
                srt_content = srt_file.read()
        except Exception as e:
            print(f"[WARN] Não foi possível carregar SRT de sessão ({srt_path}): {e}")
        
        # Carregar viral_clips do arquivo JSON se existir
        clips_data_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
        viral_clips = {}
        try:
            if os.path.exists(clips_data_path):
                with open(clips_data_path, 'r', encoding='utf-8') as f:
                    viral_clips = json.load(f)
                print(f"[DEBUG] Viral clips carregados do arquivo: {len(viral_clips.get('cortes_virais', []))} clipes")
            else:
                print(f"[DEBUG] Arquivo de clipes não encontrado: {clips_data_path}")
        except Exception as e:
            print(f"[WARN] Erro ao carregar viral clips do arquivo: {e}")
            viral_clips = session.get('viral_clips', {})

        video_url = url_for('get_uploaded_file', filename=filename)
        print(f"[DEBUG] URL do vídeo gerada: {video_url}")
        print(f"[DEBUG] Filename na sessão: {filename}")
        print(f"[DEBUG] SRT encontrado: {len(srt_content) if srt_content else 0} caracteres")
        print(f"[DEBUG] Viral clips para retorno: {len(viral_clips.get('cortes_virais', []))} clipes")
        
        return jsonify({
            'status': 'success',
            'has_session': True,
            'filename': filename,
            'video_url': video_url,
            'srt_content': srt_content,
            'viral_clips': viral_clips,
            'parametros_corte': session.get('parametros_corte', {})
        })
    else:
        print(f"[DEBUG] Nenhum filename na sessão. Chaves disponíveis: {list(session.keys())}")
        return jsonify({'status': 'success', 'has_session': False})



@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Serve o vídeo original para pré-visualização."""
    print(f"[DEBUG] get_uploaded_file chamado para: {filename}")
    video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    print(f"[DEBUG] Caminho completo do vídeo: {video_path}")
    
    if os.path.exists(video_path):
        print(f"[DEBUG] Arquivo de vídeo encontrado. Tamanho: {os.path.getsize(video_path)} bytes")
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    else:
        print(f"[ERROR] Arquivo de vídeo não encontrado: {video_path}")
        return jsonify({'error': 'Arquivo não encontrado'}), 404


@app.route('/download/<filename>')
def download_file(filename):
    """Serve arquivos para download."""
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)



@app.route('/get_srt/<filename>')
def get_srt(filename):
    """Retorna o conteúdo SRT de um arquivo específico."""
    try:
        base_name = os.path.splitext(filename)[0]
        srt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}.srt")
        
        if not os.path.exists(srt_path):
            return jsonify({'status': 'error', 'message': 'Arquivo SRT não encontrado'}), 404
            
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            srt_content = srt_file.read()
            
        return jsonify({
            'status': 'success',
            'srt_content': srt_content
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao ler arquivo SRT: {e}'}), 500


@app.route('/clear-session', methods=['POST'])
def clear_user_session():
    """Limpa a sessão do usuário."""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Sessão limpa com sucesso.'})


@app.route('/update_clip_timestamps', methods=['PUT'])
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
        clips_data_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{base_name}_clips.json")
        
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


@app.route('/get_video_duration', methods=['GET'])
def get_video_duration():
    """Retorna a duração do vídeo atual em segundos."""
    try:
        filename = session.get('filename')
        if not filename:
            return jsonify({'status': 'error', 'message': 'Nenhum vídeo na sessão.'}), 400
            
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(video_path):
            return jsonify({'status': 'error', 'message': 'Arquivo de vídeo não encontrado.'}), 404
            
        # Tentar usar MoviePy primeiro
        try:
            from moviepy import VideoFileClip
            with VideoFileClip(video_path) as video:
                duration = video.duration
        except ImportError:
            # Fallback: usar ffprobe se MoviePy não estiver disponível
            import subprocess
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-show_entries', 
                    'format=duration', '-of', 'csv=p=0', video_path
                ], capture_output=True, text=True, check=True)
                duration = float(result.stdout.strip())
            except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
                # Fallback final: retornar duração estimada baseada no tamanho do arquivo
                # Para vídeos típicos, estimar ~1MB por minuto (muito aproximado)
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                duration = file_size_mb * 60  # Estimativa muito grosseira
                print(f"[WARNING] Usando estimativa de duração baseada no tamanho: {duration}s")
            
        return jsonify({
            'status': 'success',
            'duration': duration,
            'filename': filename
        })
    except Exception as e:
        print(f"[ERROR] Erro ao obter duração: {e}")
        return jsonify({'status': 'error', 'message': f'Erro ao obter duração: {e}'}), 500


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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8014)