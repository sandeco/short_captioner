import os
from typing import Optional, Tuple
from google import genai
from google.genai import types
from dotenv import load_dotenv
import cv2
import numpy as np
import subprocess
import mimetypes
import time


load_dotenv()


class ThumbGenerator:
    """
    Classe para gerar uma nova imagem a partir de uma imagem e um prompt,
    operando com dados em memória (bytes).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash-image-preview"):
        """
        Inicializa o gerador.

        Args:
            api_key: Chave da API do Gemini. Se None, busca na variável de ambiente.
            model_name: Nome do modelo do Gemini a ser usado.
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY_BANANA")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY deve ser fornecida como parâmetro ou variável de ambiente")

        self.client = genai.Client(api_key=self.api_key)

    def generate_thumbnail(
        self,
        image_bytes: bytes,
        mime_type: str,
        prompt: str,
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Gera uma nova imagem a partir de bytes de imagem e um prompt.

        Args:
            image_bytes: A imagem de entrada como um objeto de bytes.
            mime_type: O tipo MIME da imagem de entrada (ex: 'image/jpeg').
            prompt: O prompt para a geração da nova imagem.

        Returns:
            Uma tupla contendo (image_bytes, text).
            - image_bytes: Os bytes da imagem gerada, ou None se falhar.
            - text: O texto retornado pela API, ou None.
        """
        # Preparar conteúdo para a API
        image_part = types.Part(
            inline_data=types.Blob(data=image_bytes, mime_type=mime_type)
        )
        prompt_part = types.Part.from_text(text=prompt)
        contents = [image_part, prompt_part]

        # Configurar e chamar a API
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        print(f"🚀 Gerando thumbnail com o prompt: '{prompt[:50]}...' ")

        stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=generate_content_config,
        )

        # Processar a resposta
        return self._process_api_response(stream)

    def _process_api_response(
        self, stream
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Processa o stream da API para extrair a imagem e o texto.
        """
        generated_image_bytes = None
        api_text_response = None

        for chunk in stream:
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            for part in chunk.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    if generated_image_bytes is None:
                        generated_image_bytes = part.inline_data.data
                elif part.text:
                    api_text_response = part.text

        return generated_image_bytes, api_text_response

    def insert_thumb(self, video_path, thumbnail_path):
        """
        Abre o vídeo e a imagem, ajusta a imagem ao tamanho do vídeo e insere
        a imagem como o primeiro frame do vídeo. Salva o vídeo no mesmo path.
        Observação: utiliza OpenCV para vídeo e ffmpeg para preservar o áudio.
        """

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
        if not os.path.exists(thumbnail_path):
            raise FileNotFoundError(f"Imagem não encontrada: {thumbnail_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")

        writer = None
        temp_output = None
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            if not fps or fps <= 0:
                fps = 30.0

            base, ext = os.path.splitext(video_path)
            temp_output = f"{base}__tmp{ext}"

            # Tenta codecs comuns (mp4v para .mp4/.mov, fallback para avc1/XVID)
            def make_writer(codec_tag: str):
                fourcc = cv2.VideoWriter_fourcc(*codec_tag)
                return cv2.VideoWriter(temp_output, fourcc, fps, (width, height))

            preferred_codecs = ["mp4v", "avc1", "XVID"]
            writer = None
            for tag in preferred_codecs:
                writer = make_writer(tag)
                if writer.isOpened():
                    break
                writer.release()
                writer = None

            if writer is None or not writer.isOpened():
                raise RuntimeError("Não foi possível inicializar o VideoWriter para saída.")

            # Carrega a imagem da thumbnail (com suporte a canal alfa)
            thumb = cv2.imread(thumbnail_path, cv2.IMREAD_UNCHANGED)
            if thumb is None:
                raise ValueError(f"Não foi possível ler a imagem: {thumbnail_path}")

            # Converte para BGR 3 canais, tratando alfa se presente
            if len(thumb.shape) == 2:
                thumb = cv2.cvtColor(thumb, cv2.COLOR_GRAY2BGR)
            elif thumb.shape[2] == 4:
                bgr = thumb[:, :, :3].astype(np.float32)
                alpha = (thumb[:, :, 3].astype(np.float32) / 255.0)[..., None]
                thumb = (bgr * alpha + (1.0 - alpha) * 0).astype(np.uint8)

            th_h, th_w = thumb.shape[:2]
            # Redimensiona para cobrir o quadro mantendo proporção (cover)
            scale = max(width / th_w, height / th_h)
            new_w = int(round(th_w * scale))
            new_h = int(round(th_h * scale))
            interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
            thumb_resized = cv2.resize(thumb, (new_w, new_h), interpolation=interp)

            # Recorte central para (width, height)
            x1 = max(0, (new_w - width) // 2)
            y1 = max(0, (new_h - height) // 2)
            thumb_cropped = thumb_resized[y1:y1 + height, x1:x1 + width]
            if thumb_cropped.shape[0] != height or thumb_cropped.shape[1] != width:
                thumb_cropped = cv2.resize(thumb_resized, (width, height), interpolation=cv2.INTER_AREA)

            # Escreve a imagem como primeiro frame
            writer.write(thumb_cropped)

            # Copia os frames originais
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                writer.write(frame)

            writer.release()
            cap.release()

            # Remux: preserva o áudio original usando ffmpeg
            mux_output = f"{base}__mux{ext}"

            # Detecta se há áudio no original (ffprobe)
            has_audio = False
            try:
                probe = subprocess.run(
                    [
                        'ffprobe', '-v', 'error',
                        '-select_streams', 'a:0',
                        '-show_entries', 'stream=index',
                        '-of', 'csv=p=0',
                        video_path,
                    ],
                    capture_output=True, text=True, check=False
                )
                has_audio = bool(probe.stdout.strip())
            except FileNotFoundError:
                # Se ffprobe não existir, assume que há áudio e deixa o ffmpeg falhar se não houver
                has_audio = True

            try:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_output,  # vídeo (sem áudio)
                    '-i', video_path,   # original (para áudio)
                    '-map', '0:v:0',
                ]
                if has_audio:
                    cmd += ['-map', '1:a:0']
                # Copia streams sem reencodar
                cmd += [
                    '-c:v', 'copy',
                ]
                if has_audio:
                    cmd += ['-c:a', 'copy']
                # Garante que o arquivo final não exceda o menor fluxo
                cmd += ['-shortest', mux_output]

                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Substitui original pelo mux_output
                os.replace(mux_output, video_path)
                # Remove o temporário sem áudio
                try:
                    os.remove(temp_output)
                except Exception:
                    pass
            except Exception:
                # Se o remux falhar, ao menos substitui pelo vídeo sem áudio
                try:
                    os.replace(temp_output, video_path)
                except Exception:
                    pass
                # Limpa mux_output, se existir
                if os.path.exists(mux_output):
                    try:
                        os.remove(mux_output)
                    except Exception:
                        pass
        except Exception:
            # Libera recursos e limpa arquivo temporário em caso de erro
            if 'cap' in locals():
                try:
                    cap.release()
                except Exception:
                    pass
            if writer is not None:
                try:
                    writer.release()
                except Exception:
                    pass
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass
            raise

    def create_thumbnail(self, video_path, thumbnail_details):


        print("🎨 EXEMPLO: Gerador de Thumbnail")
        print("=" * 50)

        try:
            # 1. Carregar a imagem de entrada em bytes
            image_path = "images/sandeco.png"

            with open(image_path, "rb") as f:
                input_bytes = f.read()
        
            # Obter o tipo MIME
            mime_type, _ = mimetypes.guess_type(image_path)

            # 2. Instanciar o gerador
            

            # 3. Definir o prompt e gerar a thumbnail
            prompt = f"""
            Crie uma imagem 9:16 cinematic-style usando
            essa imagem original do homem. Mantenha a 
            proporcão original do homem e escreva o título 
            {thumbnail_details['titulo']} abaixo do rosto do homem
            com a fonte "Extra Bold" na cor branca. 
            Um detalhes importante: 
            o texto deve estar centralizada 
            e somente duas palavras por linha.

            # A descrição da cena tecnológica ultrarrealista:
            A cena deve ser mais ou menos assim: 
            '{thumbnail_details['texto_gerar_thumbnail']}' 
            e o clima da cena deve ser '{thumbnail_details['clima']}'.
            Você pode alterar a expressão do homem para '{thumbnail_details['expressao_facial']}', 
            mas mantenha a proporcão original do homem.
            """
        
            new_image_bytes, text_response = self.generate_thumbnail(
                image_bytes=input_bytes,
                mime_type=mime_type,
                prompt=prompt
            )

            # 4. Processar o resultado
            if new_image_bytes:
                # Salvar a imagem gerada em um arquivo
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                timestamp = int(time.time())
                output_filename = os.path.join(output_dir, f"thumbnail_{timestamp}.png")
                
                with open(output_filename, "wb") as f:
                    f.write(new_image_bytes)

                self.insert_thumb(video_path, output_filename)

                print(f"\n✅ Thumbnail salva com sucesso em: {output_filename}")
            else:
                print("\n⚠️ Não foi possível gerar uma nova imagem.")

            if text_response:
                print(f"💬 Resposta da API: {text_response}")

        except Exception as e:
            print(f"\n❌ Ocorreu um erro: {e}")
