from moviepy import *
import uuid
import os


class ShortVideoProcessor:
    """
    Classe para processar vídeos e criar shorts no formato 9:16.
    Responsável por cortar o vídeo no tempo delimitado e aplicar crop 9:16.
    """
    
    def __init__(self, video_path: str, output_path: str):
        """
        Inicializa o processador de vídeo.
        
        Args:
            video_path (str): Caminho para o arquivo de vídeo
        """
        self.video_path = video_path
        self.video = None
        self.output_path = output_path

    
    def load_video(self):
        """Carrega o vídeo usando MoviePy."""
        try:
            self.video = VideoFileClip(self.video_path)
            print(f"Vídeo carregado: {self.video_path}")
            print(f"Duração: {self.video.duration:.2f}s")
            print(f"Resolução: {self.video.w}x{self.video.h}")
            return True
        except Exception as e:
            print(f"Erro ao carregar vídeo: {e}")
            return False
    
    def create_short_video(self, start_time: float, end_time: float,  
                            parametros_corte: dict = None):
        if not self.video:
            if not self.load_video():
                return None
        
        # --- ETAPA 1: Criar um subclip temporário e bem codificado ---
        temp_path = os.path.join("temp", f"{uuid.uuid4()}.mp4")
        
        print(f"Criando subclip temporário de {start_time}s a {end_time}s...")
        clip_temporario = self.video.subclipped(start_time, end_time)
        clip_temporario.write_videofile(temp_path, codec="libx264", audio_codec="aac")

        temp_short = os.path.join("temp", f"short_{uuid.uuid4()}.mp4") 
        

        clip_temporario.close()

        print("Subclip temporário criado. Aplicando corte final...")
        
        # --- ETAPA 2: Abrir o clipe temporário 'limpo' e aplicar o corte ---
        with VideoFileClip(temp_path) as video_limpo:
            
            # Pega os parâmetros calculados e garante que são inteiros
            x1 = parametros_corte['x1']
            y1 = parametros_corte['y1']
            x2 = parametros_corte['x2']
            y2 = parametros_corte['y2']
                    
            # Cria os parâmetros finais e validados para o corte
            corte = {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2)
            }
                        
            clip_final = video_limpo.cropped(**corte)
            
            clip_final.write_videofile(
                temp_short,  
                codec="libx264",  
                audio_codec="aac",
                logger='bar'
            )

        # --- ETAPA 3: Limpar o arquivo temporário ---
        os.remove(temp_path)

        print("\nVídeo cortado salvo com sucesso!")
        return temp_short            
    
    
    def close(self):
        """Fecha o vídeo e libera recursos."""
        if self.video:
            self.video.close()
            self.video = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Exemplo de uso
