import os
from typing import Optional, Tuple
from google import genai
from google.genai import types
from dotenv import load_dotenv

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


# Exemplo de uso
if __name__ == "__main__":
    import mimetypes
    import time

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
        thumb_gen = ThumbGenerator()

        # 3. Definir o prompt e gerar a thumbnail
        prompt = """
        Crie uma imagem 9:16 cinematic-style usando
        essa imagem original do homem. Mantenha a 
        proporcão original do homem e escreva o título 
        "A grande Novidade" abaixo do rosto do homem
        com a fonte "Extra Bold" na cor branca. 
        Um detalhes importante: 
        o texto deve estar centralizada 
        e somente duas palavras por linha.

        # A descrição da cena tecnológica ultrarrealista:
        A cena deve ser mais ou menos assim: 
        "Uma cena representando uma grande novidade tecnológica.
        tom verde do filme matrix" 
        e o clima da cena deve ser "esperança".
        Você pode alterar a expressão do homem, mas
        mantenha a proporcão original do homem.
        
        """
        
        new_image_bytes, text_response = thumb_gen.generate_thumbnail(
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
            
            print(f"\n✅ Thumbnail salva com sucesso em: {output_filename}")
        else:
            print("\n⚠️ Não foi possível gerar uma nova imagem.")

        if text_response:
            print(f"💬 Resposta da API: {text_response}")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro: {e}")

