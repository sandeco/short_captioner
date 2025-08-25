import json
import os
from moviepy import VideoFileClip, CompositeVideoClip, TextClip
from ajust_caption import CaptionProcessor


class ShortCaptioner:
    """
    Classe para adicionar legendas a vídeos usando MoviePy e dados de transcrição JSON.
    
    Esta classe integra com CaptionProcessor para criar legendas sincronizadas
    com timing preciso baseado nos dados de transcrição.
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
                 margin_bottom=100):
        """
        Inicializa o legendador de vídeo.
        
        Args:
            video_path (str): Caminho para o arquivo de vídeo
            font_path (str): Caminho para a fonte TTF/OTF
            font_size (int): Tamanho da fonte
            font_color (str): Cor do texto
            stroke_color (str): Cor do contorno
            stroke_width (int): Largura do contorno
            bg_color (str): Cor de fundo (None para transparente)
            position (tuple): Posição das legendas
            margin_bottom (int): Margem inferior em pixels
        """
        self.video_path = video_path
        self.font_path = self._resolve_font_path(font_path)
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.bg_color = bg_color
        self.position = position
        self.margin_bottom = margin_bottom
        
        # Carrega o vídeo
        self.video = None
        self.caption_processor = CaptionProcessor()
        
    def _resolve_font_path(self, font_path):
        """Resolve o caminho da fonte."""
        if font_path and os.path.exists(font_path):
            return font_path
        
        # Tenta encontrar fonte no diretório fonts/
        if font_path:
            fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
            full_path = os.path.join(fonts_dir, font_path)
            if os.path.exists(full_path):
                return full_path
        
        # Fonte padrão
        default_fonts = [
            os.path.join(os.path.dirname(__file__), "fonts", "Bangers-Regular.ttf"),
            "arial.ttf"
        ]
        
        for font in default_fonts:
            if os.path.exists(font):
                return font
                
        return None  # Usa fonte padrão do sistema
    
    def load_video(self):
        """Carrega o arquivo de vídeo."""
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
        
        self.video = VideoFileClip(self.video_path)
        print(f"Vídeo carregado: {self.video_path}")
        print(f"Duração: {self.video.duration:.2f}s | Resolução: {self.video.w}x{self.video.h}")
    
    def load_words_from_json(self, json_path):
        """
        Carrega dados de palavras de um arquivo JSON.
        
        Args:
            json_path (str): Caminho para o arquivo JSON
            
        Returns:
            list: Lista de dicionários com dados das palavras
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)
        
        print(f"Carregadas {len(words_data)} palavras do arquivo {json_path}")
        return words_data
    
    def create_caption_clips(self, phrases):
        """
        Cria clips de texto para cada frase.
        
        Args:
            phrases (list): Lista de frases processadas
            
        Returns:
            list: Lista de TextClips
        """
        caption_clips = []
        
        for phrase in phrases:
            # Calcula posição baseada na configuração
            if self.position == ("center", "bottom"):
                pos = ("center", self.video.h - self.margin_bottom)
            else:
                pos = self.position
            
            # Cria o TextClip usando os métodos corretos do MoviePy
            text_clip = TextClip(
                text=phrase['text'],
                font_size=self.font_size,
                color=self.font_color,
                font=self.font_path,
                stroke_color=self.stroke_color,
                stroke_width=self.stroke_width,
                bg_color=self.bg_color,
                method='caption',
                size=(self.video.w - 100, None),  # Largura com margem
                text_align='center'
            )
            
            # Define timing e posição usando os métodos corretos
            text_clip = text_clip.with_duration(phrase['duration']).with_position(pos)
            
            # Aplica o timing de início
            text_clip = text_clip.subclipped(0, phrase['duration'])
            text_clip = text_clip.with_start(phrase['start'])
            
            caption_clips.append(text_clip)
        
        return caption_clips
    
    def create_captioned_video(self, words_data, output_path, words_per_line=3):
        """
        Cria vídeo com legendas a partir dos dados de palavras.
        
        Args:
            words_data (list): Dados das palavras (do JSON)
            output_path (str): Caminho para salvar o vídeo final
            words_per_line (int): Número de palavras por linha de legenda
            
        Returns:
            str: Caminho do arquivo de saída
        """
        if self.video is None:
            self.load_video()
        
        # Processa as palavras em frases
        self.caption_processor.words_per_line = words_per_line
        words_with_phases, phrases = self.caption_processor.process_caption_data(words_data)
        
        print(f"Processadas {len(phrases)} frases para legendagem")
        
        # Cria clips de legenda
        caption_clips = self.create_caption_clips(phrases)
        
        # Compõe o vídeo final
        all_clips = [self.video] + caption_clips
        final_video = CompositeVideoClip(all_clips)
        
        # Renderiza o vídeo
        print(f"Renderizando vídeo com legendas...")
        final_video.write_videofile(
            output_path,
            codec="libx264",
            fps=self.video.fps,
            audio_codec="aac",
            logger="bar"
        )
        
        # Limpa recursos
        final_video.close()
        
        print(f"✅ Vídeo com legendas salvo: {output_path}")
        return output_path
    
    def create_from_json_file(self, json_path, output_path, words_per_line=3):
        """
        Método conveniente para criar vídeo legendado diretamente de um arquivo JSON.
        
        Args:
            json_path (str): Caminho para o arquivo JSON com dados das palavras
            output_path (str): Caminho para salvar o vídeo final
            words_per_line (int): Número de palavras por linha
            
        Returns:
            str: Caminho do arquivo de saída
        """
        words_data = self.load_words_from_json(json_path)
        return self.create_captioned_video(words_data, output_path, words_per_line)
    
    def preview_captions(self, words_data, words_per_line=3, max_phrases=5):
        """
        Mostra uma prévia das legendas que serão geradas.
        
        Args:
            words_data (list): Dados das palavras
            words_per_line (int): Número de palavras por linha
            max_phrases (int): Máximo de frases para mostrar
        """
        words_with_phases, phrases = self.caption_processor.process_caption_data(words_data)
        
        print("=== PRÉVIA DAS LEGENDAS ===")
        for i, phrase in enumerate(phrases[:max_phrases]):
            print(f"Frase {phrase['phase']}: '{phrase['text']}'")
            print(f"  ⏱️  {phrase['start']:.2f}s - {phrase['end']:.2f}s ({phrase['duration']:.2f}s)")
            print(f"  📊 Confiança: {phrase['confidence']:.3f} | Palavras: {phrase['word_count']}")
            print()
        
        if len(phrases) > max_phrases:
            print(f"... e mais {len(phrases) - max_phrases} frases")
        
        print(f"Total: {len(phrases)} frases")


    def create_karaoke_clips(self, phrases):
        """
        Cria clipes de karaokê onde cada palavra é destacada individualmente.
        
        Args:
            phrases (list): Lista de frases processadas com dados de palavras
            
        Returns:
            list: Lista de clips de karaokê
        """
        karaoke_clips = []
        
        for phrase in phrases:
            # Calcula posição
            if self.position == ("center", "bottom"):
                pos = ("center", self.video.h - self.margin_bottom)
            else:
                pos = self.position
            
            # Para cada palavra na frase, cria um clip destacado
            for word in phrase['words']:
                # Texto completo da frase
                full_text = phrase['text']
                
                # Cria clip com a palavra destacada usando cor diferente
                # Aproximação: destaca toda a frase durante o tempo da palavra
                text_clip = TextClip(
                    text=full_text,
                    font_size=self.font_size,
                    color="yellow",  # Cor de destaque para karaokê
                    font=self.font_path,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    bg_color=self.bg_color,
                    method='caption',
                    size=(self.video.w - 100, None),
                    text_align='center'
                )
                
                # Define timing da palavra individual
                word_duration = word['end'] - word['start']
                if word_duration <= 0:
                    continue
                
                text_clip = text_clip.with_duration(word_duration).with_position(pos)
                text_clip = text_clip.with_start(word['start'])
                
                karaoke_clips.append(text_clip)
        
        return karaoke_clips
    
    def create_karaoke_video(self, words_data, output_path, words_per_line=3):
        """
        Cria vídeo com efeito karaokê a partir dos dados de palavras.
        
        Args:
            words_data (list): Dados das palavras (do JSON)
            output_path (str): Caminho para salvar o vídeo final
            words_per_line (int): Número de palavras por linha de legenda
            
        Returns:
            str: Caminho do arquivo de saída
        """
        if self.video is None:
            self.load_video()
        
        # Processa as palavras em frases
        self.caption_processor.words_per_line = words_per_line
        words_with_phases, phrases = self.caption_processor.process_caption_data(words_data)
        
        print(f"Processadas {len(phrases)} frases para karaokê")
        
        # Cria clips de karaokê
        karaoke_clips = self.create_karaoke_clips(phrases)
        
        # Compõe o vídeo final
        all_clips = [self.video] + karaoke_clips
        final_video = CompositeVideoClip(all_clips)
        
        # Renderiza o vídeo
        print(f"Renderizando vídeo com efeito karaokê...")
        final_video.write_videofile(
            output_path,
            codec="libx264",
            fps=self.video.fps,
            audio_codec="aac",
            logger="bar"
        )
        
        # Limpa recursos
        final_video.close()
        
        print(f"✅ Vídeo karaokê salvo: {output_path}")
        return output_path


# Exemplo de uso com karaokê
if __name__ == "__main__":
    # Cria o legendador
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
    
    # Carrega dados das palavras
    words_data = captioner.load_words_from_json("words.json")
    
    # Prévia das legendas
    captioner.preview_captions(words_data, words_per_line=3, max_phrases=3)
    
    # Cria vídeo com efeito karaokê
    captioner.create_karaoke_video(
        words_data, 
        "video_karaoke_exemplo.mp4", 
        words_per_line=3
    )
