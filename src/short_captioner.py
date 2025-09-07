import json
import os
from moviepy import VideoFileClip, CompositeVideoClip, TextClip

# --- Dependência Simulada (CaptionProcessor) ---
class CaptionProcessor:
    """Classe de exemplo para processar dados de palavras em frases."""
    def __init__(self):
        self.words_per_line = 3

    def process_caption_data(self, words_data):
        """Agrupa palavras em frases com base em 'words_per_line'."""
        phrases = []
        current_phrase_words = []
        phase_counter = 1
        
        if not words_data or not isinstance(words_data, list):
            return [], []

        for i, word_info in enumerate(words_data):
            if not isinstance(word_info, dict):
                continue
            
            current_phrase_words.append(word_info)
            if len(current_phrase_words) == self.words_per_line or i == len(words_data) - 1:
                text = " ".join([w.get('word', '') for w in current_phrase_words]).strip()
                if not text:
                    continue

                # CASTING: Garante que os valores de tempo sejam floats
                start = float(current_phrase_words[0].get('start', 0))
                end = float(current_phrase_words[-1].get('end', start))
                duration = max(0.1, end - start)
                
                phrases.append({
                    'text': text, 'start': start, 'end': end, 'duration': duration,
                    'word_count': len(current_phrase_words), 'phase': phase_counter
                })
                phase_counter += 1
                current_phrase_words = []
        
        return words_data, phrases

# --- Classe Principal Corrigida ---

class ShortCaptioner:
    """
    Classe para adicionar legendas a vídeos usando MoviePy e dados de transcrição JSON.
    """
    
    def __init__(self, 
                 video_path,
                 font_path=None,
                 font_size=60,
                 font_color="white",
                 stroke_color="black", 
                 stroke_width=2,
                 bg_color=None,
                 position=("center", "bottom"),
                 margin_bottom=100,
                 thumbnail=None):
        
        self.video_path = video_path
        self.font_path = self._resolve_font_path(font_path)
        # CASTING: Garante que os parâmetros de pixel sejam inteiros
        self.font_size = int(font_size)
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = int(stroke_width)
        self.bg_color = bg_color
        self.position = position
        self.margin_bottom = int(margin_bottom)
        self.thumbnail = thumbnail
        self.video = None
        self.caption_processor = CaptionProcessor()
        
    def _resolve_font_path(self, font_path):
        """Resolve o caminho da fonte de forma robusta."""
        if font_path and os.path.exists(font_path):
            return font_path
        if font_path:
            try:
                # Procura em uma pasta 'fonts' no mesmo diretório do script
                script_dir = os.path.dirname(__file__)
                full_path = os.path.join(script_dir, "fonts", font_path)
                if os.path.exists(full_path):
                    return full_path
            except NameError:
                 pass
        print("⚠️  Nenhuma fonte personalizada encontrada, MoviePy usará uma fonte padrão do sistema.")
        return None
    
    def load_video(self):
        """Carrega o arquivo de vídeo se ainda não estiver carregado."""
        if self.video is None:
            if not os.path.exists(self.video_path):
                raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
            try:
                self.video = VideoFileClip(self.video_path)
                print(f"Vídeo carregado: {self.video_path} | Duração: {self.video.duration:.2f}s | Resolução: {self.video.size}")
            except Exception as e:
                print(f"❌ Erro ao carregar vídeo: {e}")
                raise

    def close(self):
        """Libera os recursos do vídeo para evitar vazamento de memória."""
        if self.video:
            self.video.close()
            self.video = None
            print("Recursos do vídeo liberados.")

    def create_caption_clips(self, phrases):
        """Cria clips de texto para cada frase usando os parâmetros corretos do MoviePy."""
        self.load_video()
        caption_clips = []
        
        for phrase in phrases:
            try:
                # CASTING: Garante que o cálculo da posição Y resulte num inteiro.
                pos = ('center', int(self.video.h - self.margin_bottom))

                text_clip = TextClip(
                    text=phrase['text'],
                    font_size=self.font_size,
                    color=self.font_color,
                    font=self.font_path,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    bg_color=self.bg_color,
                    method='caption',
                    # CASTING: Converte a largura calculada para um inteiro.
                    size=(int(self.video.w * 0.9), None),
                    text_align='center'
                )
                
                text_clip = (text_clip
                             .with_start(float(phrase['start'])) # CASTING: Garante que o início é float
                             .with_duration(float(phrase['duration'])) # CASTING: Garante que a duração é float
                             .with_position(pos))
                
                caption_clips.append(text_clip)
            except Exception as e:
                print(f"❌ Erro ao criar legenda para '{phrase.get('text', 'N/A')}': {e}")
                continue
        
        return caption_clips

    def create_title_frame(self, duration=0.1):
        """
        Cria um frame de título duplicando o primeiro frame do vídeo.
        
        Args:
            duration (float): Duração do frame de título em segundos (padrão: 2.0s)
            
        Returns:
            VideoClip: Clip com o primeiro frame e título sobreposto
        """
        if not self.thumbnail or not self.thumbnail.get('titulo'):
            print("⚠️ Nenhum título fornecido para o frame de título")
            return None
            
        self.load_video()
        
        try:
            # Duplica o primeiro frame do vídeo
            first_frame = self.video.subclipped(0, 0.1).with_duration(duration)
            
            # Cria o texto do título com fonte dobrada
            title_font_size = int(self.font_size * 2)
            
            # Posição centralizada verticalmente
            title_pos = ('center', 'center')
            
            title_clip = TextClip(
                text=self.thumbnail['titulo'],
                font_size=title_font_size,
                color=self.font_color,
                font=self.font_path,
                stroke_color=self.stroke_color,
                stroke_width=int(self.stroke_width * 1.5),  # Stroke um pouco mais grosso
                bg_color=self.bg_color,
                method='caption',
                size=(int(self.video.w * 0.8), None),  # Um pouco mais estreito para títulos longos
                text_align='center'
            )
            
            title_clip = (title_clip
                         .with_duration(duration)
                         .with_position(title_pos))
            
            # Compõe o frame com o título
            title_frame = CompositeVideoClip([first_frame, title_clip], size=self.video.size)
            
            print(f"✅ Frame de título criado: '{self.thumbnail['titulo']}' | Duração: {duration}s")
            return title_frame
            
        except Exception as e:
            print(f"❌ Erro ao criar frame de título: {e}")
            return None
    
    def create_captioned_video(self, words_data, output_path, words_per_line=3):
        """Cria vídeo com legendas a partir dos dados brutos de palavras."""
        # CASTING: Garante que words_per_line seja um inteiro
        self.caption_processor.words_per_line = int(words_per_line)
        _, phrases = self.caption_processor.process_caption_data(words_data)
        
        return self.create_captioned_video_from_phrases(phrases, output_path)

    def create_captioned_video_from_phrases(self, phrases, output_path):
        """Cria vídeo com legendas a partir de uma lista de frases já processadas."""
        self.load_video()
        
        print(f"Renderizando a partir de {len(phrases)} frases...")
        
        try:
            caption_clips = self.create_caption_clips(phrases)
            
            if not caption_clips:
                print("⚠️ Nenhuma legenda foi criada. O vídeo será salvo sem alterações.")
                self.video.write_videofile(output_path, codec="libx264", audio_codec="aac", logger="bar")
                return output_path
            
            title_frame = self.create_title_frame()
            
            if title_frame:
                final_clips = [title_frame] + [self.video] + caption_clips
            else:
                final_clips = [self.video] + caption_clips
            
            final_video = CompositeVideoClip(final_clips, size=self.video.size)
            
            print(f"Renderizando vídeo final para: {output_path}")
            final_video.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                logger="bar"
            )
            
            final_video.close()
            print(f"✅ Vídeo com legendas salvo em: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erro ao criar vídeo com legendas: {e}")
            raise

# --- Exemplo de uso ---
if __name__ == "__main__":
    # --- CONFIGURAÇÃO ---
    # !! IMPORTANTE: O arquivo de entrada e saída DEVEM ser diferentes !!
    INPUT_VIDEO_PATH = "caminho/para/seu/video_de_entrada.mp4"
    OUTPUT_VIDEO_PATH = "caminho/para/seu/video_final_legendado.mp4"
    JSON_WORDS_PATH = "words.json" # Arquivo com a transcrição palavra por palavra

    # --- Criação de um arquivo JSON de exemplo ---
    # Este bloco cria um arquivo 'words.json' para que o exemplo funcione.
    # Em um caso real, este arquivo viria da sua API de transcrição.
    sample_words_data = [
        {'word': 'Olá,', 'start': 0.5, 'end': 0.8, 'confidence': 0.99},
        {'word': 'este', 'start': 0.9, 'end': 1.2, 'confidence': 0.98},
        {'word': 'é', 'start': 1.2, 'end': 1.4, 'confidence': 1.0},
        {'word': 'um', 'start': 1.5, 'end': 1.7, 'confidence': 0.99},
        {'word': 'vídeo', 'start': 1.8, 'end': 2.2, 'confidence': 0.97},
        {'word': 'de', 'start': 2.2, 'end': 2.4, 'confidence': 1.0},
        {'word': 'exemplo.', 'start': 2.5, 'end': 3.1, 'confidence': 0.99},
    ]
    with open(JSON_WORDS_PATH, 'w', encoding='utf-8') as f:
        json.dump(sample_words_data, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(INPUT_VIDEO_PATH):
        print(f"❌ ERRO: Vídeo de entrada não encontrado em '{INPUT_VIDEO_PATH}'")
        print("Por favor, crie um vídeo de teste ou ajuste o caminho do arquivo.")
    else:
        captioner = None
        try:
            captioner = ShortCaptioner(
                video_path=INPUT_VIDEO_PATH,
                font_path="arial.ttf", # Use uma fonte que exista no seu sistema ou forneça o caminho
                font_size=70,
                font_color="yellow",
                stroke_color="black",
                stroke_width=3,
                margin_bottom=150,
                thumbnail={'titulo': 'Título do Vídeo'}
            )
            
            # Supondo que você tenha um arquivo JSON com os dados das palavras
            with open(JSON_WORDS_PATH, 'r', encoding='utf-8') as f:
                 words_data = json.load(f)

            
            captioner.create_captioned_video(
                words_data=words_data, 
                output_path=OUTPUT_VIDEO_PATH, 
                words_per_line=3
            )
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante o processo: {e}")
        finally:
            if captioner:
                captioner.close()
