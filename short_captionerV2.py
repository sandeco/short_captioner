import json
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import TextClip
from ajust_caption import CaptionProcessor


class ShortCaptioner:
    """
    Classe para adicionar legendas a vídeos usando MoviePy e dados de transcrição JSON.
    Refatorada para ser compatível com as versões mais recentes do MoviePy.
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
                 margin_bottom=400,
                 highlight_color="yellow"):
        self.video_path = video_path
        self.font_path = self._resolve_font_path(font_path)
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.bg_color = bg_color
        self.position = position
        self.margin_bottom = margin_bottom
        self.highlight_color = highlight_color
        self.video = None
        
    def _resolve_font_path(self, font_path):
        if font_path and os.path.exists(font_path): return font_path
        if font_path:
            fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
            full_path = os.path.join(fonts_dir, font_path)
            if os.path.exists(full_path): return full_path
        default_fonts = [os.path.join(os.path.dirname(__file__), "fonts", "Bangers-Regular.ttf"), "arial.ttf"]
        for font in default_fonts:
            if os.path.exists(font): return font
        return None

    def load_video(self):
        if not os.path.exists(self.video_path): raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {self.video_path}")
        self.video = VideoFileClip(self.video_path)
        print(f"Vídeo carregado: {self.video_path}")
        print(f"Duração: {self.video.duration:.2f}s | Resolução: {self.video.w}x{self.video.h}")

    def create_caption_clips(self, phrases):
        """Cria clips de texto estáticos para cada frase."""
        caption_clips = []
        for phrase in phrases:
            if self.position == ("center", "bottom"):
                pos = ("center", self.video.h - self.margin_bottom)
            else:
                pos = self.position
            
            text_clip = TextClip(
                text=phrase['text'], font_size=self.font_size, color=self.font_color,
                font=self.font_path, stroke_color=self.stroke_color, stroke_width=self.stroke_width,
                method='caption', size=(self.video.w - 100, None), text_align='center'
            )
            text_clip = text_clip.with_start(phrase['start']).with_duration(phrase['duration']).with_position(pos)
            caption_clips.append(text_clip)
        return caption_clips

    def create_karaoke_clips(self, phrases):
        """Cria clipes compostos para o efeito karaokê palavra por palavra."""
        all_karaoke_clips = []
        
        for phrase in phrases:
            # Calcula posição da frase
            if self.position == ("center", "bottom"):
                pos = ("center", self.video.h - self.margin_bottom)
            else:
                pos = self.position
            
            # Cria o texto completo da frase para cada palavra destacada
            for i, word in enumerate(phrase['words']):
                # Monta o texto completo com destaque na palavra atual
                texto_completo = ""
                for j, w in enumerate(phrase['words']):
                    if j == i:
                        # Palavra atual destacada
                        texto_completo += f"[{w['word']}]"
                    else:
                        # Palavras normais
                        texto_completo += w['word']
                    
                    # Adiciona espaço entre palavras (exceto na última)
                    if j < len(phrase['words']) - 1:
                        texto_completo += " "
                
                # Cria dois clipes: um com texto normal e outro com destaque
                texto_normal = " ".join([w['word'] for w in phrase['words']])
                
                # Clip com texto normal (cor padrão)
                clip_normal = TextClip(
                    text=texto_normal,
                    font_size=self.font_size,
                    color=self.font_color,
                    font=self.font_path,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    method='caption',
                    size=(self.video.w - 100, None),
                    text_align='center'
                )
                
                # Clip com apenas a palavra destacada
                palavra_destacada = word['word']
                clip_destacado = TextClip(
                    text=palavra_destacada,
                    font_size=self.font_size,
                    color=self.highlight_color,
                    font=self.font_path,
                    stroke_color=self.stroke_color,
                    stroke_width=self.stroke_width,
                    method='caption',
                    size=(self.video.w - 100, None),
                    text_align='center'
                )
                
                # Calcula posição da palavra destacada
                # Aproximação simples: divide o texto em palavras e calcula posição relativa
                words_before = phrase['words'][:i]
                if words_before:
                    # Estima posição baseada no número de caracteres antes
                    chars_before = sum(len(w['word']) + 1 for w in words_before)  # +1 para espaço
                    total_chars = sum(len(w['word']) + 1 for w in phrase['words']) - 1  # -1 remove último espaço
                    
                    # Posição relativa da palavra (aproximação)
                    relative_pos = chars_before / total_chars if total_chars > 0 else 0
                    
                    # Ajusta posição horizontal baseada na largura do clip
                    word_x_offset = int((clip_normal.w * relative_pos) - (clip_normal.w * 0.5))
                else:
                    word_x_offset = 0
                
                # Posiciona os clips
                clip_normal = clip_normal.with_position(pos)
                clip_destacado = clip_destacado.with_position((pos[0], pos[1]))
                
                # Cria máscara para mostrar apenas a palavra atual no clip destacado
                # Por simplicidade, vamos usar o clip destacado sobreposto
                composicao_palavra = CompositeVideoClip(
                    [clip_normal, clip_destacado],
                    size=self.video.size
                )
                
                # Define timing da palavra
                word_duration = word['end'] - word['start']
                if word_duration <= 0:
                    continue
                
                composicao_palavra = composicao_palavra.with_start(word['start']).with_duration(word_duration)
                all_karaoke_clips.append(composicao_palavra)
                
        return all_karaoke_clips

    def create_captioned_video_from_phrases(self, phrases, output_path, karaoke=False):
        """Cria vídeo com legendas a partir de frases, com opção de efeito karaokê."""
        if self.video is None:
            self.load_video()
        
        print(f"Renderizando a partir de {len(phrases)} frases...")
        
        if karaoke:
            print("Modo Karaokê ATIVADO.")
            caption_clips = self.create_karaoke_clips(phrases)
        else:
            print("Modo de legenda padrão.")
            caption_clips = self.create_caption_clips(phrases)
        
        final_video = CompositeVideoClip([self.video] + caption_clips, size=self.video.size)
        
        print(f"Renderizando vídeo final...")
        final_video.write_videofile(
            output_path, codec="libx264", fps=self.video.fps, audio_codec="aac", logger="bar"
        )
        
        final_video.close()
        print(f"✅ Vídeo com legendas salvo: {output_path}")
        return output_path

if __name__ == "__main__":
    
    print("--- INICIANDO TESTE DE RENDERIZAÇÃO KARAOKÊ ---")

    try:
        with open("words.json", 'r', encoding='utf-8') as f:
            words_data = json.load(f)
    except FileNotFoundError:
        print("\nERRO: Arquivo 'words.json' não encontrado.")
        exit()

    processor = CaptionProcessor(words_per_line=10)
    _, phrases_para_legendar = processor.process_caption_data(words_data)
    
    captioner = None
    try:
        captioner = ShortCaptioner(
            video_path="shorts-enxame.mp4",
            font_path="fonts/GothamBlack.ttf",
            font_size=90,
            stroke_width=5,
            margin_bottom=350,
            highlight_color="cyan"
        )
        captioner.create_captioned_video_from_phrases(
            phrases=phrases_para_legendar,
            output_path="video_karaoke_final.mp4",
            karaoke=True
        )
        print("\n--- PROCESSO CONCLUÍDO! ---")
    except FileNotFoundError as e:
        print(f"\nERRO: {e}")
        exit()
    finally:
        if captioner and captioner.video:
            captioner.video.close()